import commentjson as json
import numpy as np
import torch
from opt import *
from nir import *
#import tinycudann as tcnn
from nir.utils import read_image, write_image, psnr, visualize_depth
from nir.rendering import render_rays
from torch.utils.data import DataLoader
from collections import defaultdict
from torch.utils.tensorboard import SummaryWriter
import datetime
import os
from main import manager
import base64

args = get_args()

class Nerf(torch.nn.Module):
	def __init__(self,args,config):
		super(Nerf, self).__init__()
		self.writer = SummaryWriter()
		
		self.models_to_train = []

		self.loss = NerfWLoss(args.coef)
		
		# self.embedding_xyz = HashGrid(config, 3).to(device)
		# self.embedding_dir = HashGrid(config, 3).to(device)
		self.embedding_xyz = MultiResHashGrid(3).to(device)
		self.embedding_dir = MultiResHashGrid(3).to(device)
		self.embeddings = {'xyz': self.embedding_xyz, 'dir': self.embedding_dir}
		
		if args.encode_a:
			self.embedding_a = torch.nn.Embedding(args.N_vocab, args.N_a).to(device)
			self.embeddings['a'] = self.embedding_a
			self.models_to_train += [self.embedding_a]
		if args.encode_t:
			self.embedding_t = torch.nn.Embedding(args.N_vocab, args.N_tau).to(device)
			self.embeddings['t'] = self.embedding_t
			self.models_to_train += [self.embedding_t]
		
		# self.nerf_coarse = Mlp('coarse',6*args.N_emb_xyz+6, 6*args.N_emb_dir+6).to(device)
		self.nerf_coarse = Mlp('coarse',6*args.N_emb_xyz, args.N_emb_dir).to(device)
		
		self.models = {'coarse': self.nerf_coarse}

		# if args.N_importance > 0:
		# 	self.nerf_fine = Mlp('fine',
        #                           in_channels_xyz=6*args.N_emb_xyz+6,
        #                           in_channels_dir=6*args.N_emb_dir+6,
        #                           encode_appearance=args.encode_a,
        #                           in_channels_a=args.N_a,
        #                           encode_transient=args.encode_t,
        #                           in_channels_t=args.N_tau,
        #                           beta_min=args.beta_min)
		# 	self.models['fine'] = self.nerf_fine
		# self.models_to_train += [self.models]
		if args.N_importance > 0:
			self.nerf_fine = Mlp('fine',
                                  in_channels_xyz=6*args.N_emb_xyz,
                                  in_channels_dir=args.N_emb_dir,
                                  encode_appearance=args.encode_a,
                                  in_channels_a=args.N_a,
                                  encode_transient=args.encode_t,
                                  in_channels_t=args.N_tau,
                                  beta_min=args.beta_min)
			self.models['fine'] = self.nerf_fine
		self.models_to_train += [self.models]
	
	def forward(self, rays, ts):
		"""Do batched inference on rays using chunk."""
		B = rays.shape[0]
		results = defaultdict(list)
		for i in range(0, B, args.chunk):
			rendered_ray_chunks = \
                render_rays(self.models,
                            self.embeddings,
                            rays[i:i+args.chunk],
                            ts[i:i+args.chunk],
                            args.N_samples,
                            args.use_disp,
                            args.perturb,
                            args.noise_std,
                            args.N_importance,
                            args.chunk) # chunk size is effective in val mode
			for k, v in rendered_ray_chunks.items():
				results[k] += [v]
		for k, v in results.items():
			results[k] = torch.cat(v, 0)
		return results
	
	def get_progress_bar_dict(self):
		items = super().get_progress_bar_dict()
		items.pop("v_num", None)
		return items
		
	def setup(self,stage):

		dataset = PhototourismDataset(args.root_dir, split='train', img_downscale=args.img_downscale, val_num=args.val_num, use_cache=args.use_cache)
		self.train_dataset = dataset(split='train')
		self.val_dataset = dataset(split='val')

	def configure_optimizers(self):
		self.optimizer = torch.optim.Adam(self.nerf_coarse.parameters(), lr=args.lr)
		scheduler = torch.optim.lr_scheduler.MultiStepLR(self.optimizer, milestones=args.decay_step,gamma=args.decay_gamma)
		return [self.optimizer], [scheduler]
	
	def training_step(self, batch, batch_nb):
		rays, rgbs, ts = batch['rays'], batch['rgbs'], batch['ts']
		results = self(rays, ts)
		loss_d = self.loss(results, rgbs)
		loss = sum(l for l in loss_d.values())
		self.writer.add_scalar('Loss/train', loss, self.current_epoch)
		with torch.no_grad():
			typ = 'fine' if 'rgb_fine' in results else 'coarse'
			psnr_ = psnr(results[f'rgb_{typ}'], rgbs)
		self.log('lr', args.lr)
		self.log('train/loss', loss)
		for k, v in loss_d.items():
			self.log(f'train/{k}', v, prog_bar=True)
		self.log('train/psnr', psnr_, prog_bar=True)
		return loss
	
	def validation_step(self, batch, batch_nb):
		rays, rgbs, ts = batch['rays'], batch['rgbs'], batch['ts']
		rays = rays.squeeze() # (H*W, 3)
		rgbs = rgbs.squeeze() # (H*W, 3)
		ts = ts.squeeze() # (H*W)
		results = self(rays, ts)
		loss_d = self.loss(results, rgbs)
		loss = sum(l for l in loss_d.values())
		self.writer.add_scalar('Loss/val', loss, self.current_epoch)
		log = {'val_loss': loss}
		typ = 'fine' if 'rgb_fine' in results else 'coarse'
    
		if  batch_nb == 0:
			if self.hparams.dataset_name == 'phototourism':
				WH = batch['img_wh']
				W, H = WH[0, 0].item(), WH[0, 1].item()
			else:
				W, H = self.hparams.img_wh
			img = results[f'rgb_{typ}'].view(H, W, 3).permute(2, 0, 1).cpu() # (3, H, W)
			img_gt = rgbs.view(H, W, 3).permute(2, 0, 1).cpu() # (3, H, W)
			depth = visualize_depth(results[f'depth_{typ}'].view(H, W)) # (3, H, W)
			stack = torch.stack([img_gt, img, depth]) # (3, 3, H, W)
			self.logger.experiment.add_images('val/GT_pred_depth',
											stack, self.global_step)

		psnr_ = psnr(results[f'rgb_{typ}'], rgbs)
		log['val_psnr'] = psnr_

		return log
	
	def validation_epoch_end(self, outputs):
		mean_loss = torch.stack([x['val_loss'] for x in outputs]).mean()
		mean_psnr = torch.stack([x['val_psnr'] for x in outputs]).mean()

		self.log('val/loss', mean_loss)
		self.log('val/psnr', mean_psnr, prog_bar=True)
		
def train_one_epoch(epoch, model, optimizer, data_loader, device):
	model.train()
	for idx, batch in enumerate(data_loader):
		rays, rgbs, ts = batch['rays'], batch['rgbs'], batch['ts']
		rays, rgbs, ts = rays.to(device), rgbs.to(device), ts.to(device)

		optimizer.zero_grad()
		results = model(rays, ts)
		loss_d = model.loss(results, rgbs)
		loss = sum(l for l in loss_d.values())
		loss.backward()
		optimizer.step()

		#print(f"epoch: {epoch} | loss: {loss.item()}")

		#if idx % 1000 == 0:
		#	percentage = idx / len(data_loader.dataset) * 100
		##	print(f"epoch: {epoch} | loss: {loss.item()} | perc: {formatted_percentage}")

		# ... logging code ...		

	return loss.item()

def validate_one_epoch(epoch, model, data_loader, device):
	model.eval()
	with torch.no_grad():
		for batch in data_loader:
			rays, rgbs, ts = batch['rays'], batch['rgbs'], batch['ts']
			rays, rgbs, ts = rays.to(device).squeeze(0), rgbs.to(device).squeeze(0), ts.to(device).squeeze(0)
			results = model(rays, ts)
	#		loss_d = model.loss(results, rgbs)
	#		loss = sum(l for l in loss_d.values())
            # ... logging code ...
			im_w = batch['img_wh'][0, 0].item()
			im_h = batch['img_wh'][0, 1].item()
			rgbs = rgbs.reshape(im_h, im_w, 3)

			rendered = results["rgb_fine"].detach().reshape(im_h, im_w, 3)
			model.writer.add_image(f"RGB", rgbs.detach().cpu().numpy(), dataformats="HWC")
			model.writer.add_image(f"Rendered RGB/{epoch}", rendered.cpu().numpy(), dataformats="HWC")
		
async def main(args):
	device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

	# with open(args.config) as config_file:
	# 	config = json.load(config_file)
	print("Creating model...")
	nerf = Nerf(args, 'config').to(device)
	print("Creating optimizer...")
	optimizer = torch.optim.Adam(nerf.parameters(), lr=args.lr)
	scheduler = torch.optim.lr_scheduler.MultiStepLR(optimizer, milestones=args.decay_step,gamma=args.decay_gamma)

	print("Creating dataloaders...")
	train_dataset = PhototourismDataset(args.root_dir, split='train', img_downscale=args.img_downscale, use_cache=False)
	val_dataset = PhototourismDataset(args.root_dir, split='val', img_downscale=args.img_downscale, use_cache=False)

	train_loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True, num_workers=0)
	val_loader = DataLoader(val_dataset, batch_size=1, shuffle=False, num_workers=0)
	prev_ckpt_path = None
	print("Starting training...")
	for epoch in range(args.num_epochs):
		print(f"Epoch {epoch + 1} start @ {datetime.datetime.now().strftime('%H%M')}")

#################for fastapi to send progress bar#################
		await manager.broadcast(f"Epoch {epoch+1} / {args.num_epochs} ")
#################for fastapi to send progress bar
#################
		val_loss = validate_one_epoch(epoch,nerf, val_loader, device)
		train_loss = train_one_epoch(epoch, nerf, optimizer, train_loader, device)
		print(f"Epoch {epoch + 1} end, Loss/train: {train_loss}, Loss/validation{val_loss}")
		scheduler.step()
	saved_model = f"trained_model/{args.exp_name}/{datetime.datetime.now().strftime('%m%d%M')}"
	if not os.path.exists(saved_model):
		os.makedirs(saved_model)
	torch.save(nerf.state_dict(), f"{saved_model}/model_weights.pth")

###########################################
	#model = nerf()
	#model.load_state_dict(torch.load('model_weights.pth'))
	#model.eval()
###########################################

device = torch.device("cuda")
import asyncio

async def main_async():
    print(f"Using PyTorch version {torch.__version__} with CUDA {torch.version.cuda}")
    args = get_args()
    await main(args)

if __name__ == "__main__":
    asyncio.run(main_async())