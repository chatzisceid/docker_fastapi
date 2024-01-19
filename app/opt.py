import argparse

def get_args():
      parser = argparse.ArgumentParser(description="Image benchmark using PyTorch bindings.")
      parser.add_argument("--images", nargs="?", default="/data/image/albert.jpg", help="Image to match")
      parser.add_argument("--config", nargs="?", default="config/config_hash.json", help="JSON config for tiny-cuda-nn")
      parser.add_argument("--n_steps", nargs="?", type=int, default=100, help="Number of training steps")
      parser.add_argument("--result_filename", nargs="?", default="", help="Number of training steps")
      parser.add_argument("--root_dir", nargs="?", type=str, default="/data/brandenburg_gate/",help="root directory of dataset")
      parser.add_argument("--dataset_name", nargs="?", type=str, default="phototourism",choices=["blender", "phototourism"],help="which dataset to train/val")
      parser.add_argument("--img_downscale", nargs="?", type=int, default=1, help="how much to downscale the images for phototourism dataset")
      parser.add_argument("--use_cache", default=False, action="store_true", help="whether to use ray cache (make sure img_downscale is the same)")
      parser.add_argument("--batch_size", nargs="?", type=int, default=1024, help="batch size")
      parser.add_argument("--lr", nargs="?", type=float, default=5e-4, help="learning rate")
      parser.add_argument('--encode_a', default=False, action="store_true", help='whether to encode appearance (NeRF-A)')
      parser.add_argument('--N_a', nargs="?", type=int, default=48, help='number of embeddings for appearance')
      parser.add_argument('--encode_t', default=False, action="store_true", help='whether to encode transient object (NeRF-U)')
      parser.add_argument('--N_tau', nargs="?", type=int, default=16, help='number of embeddings for appearance')
      parser.add_argument('--chunk', type=int, default=32*1024, help='chunk size to split the input to avoid OOM')
      parser.add_argument('--N_emb_xyz', type=int, default=10, help='number of xyz embedding frequencies') 
      parser.add_argument('--N_emb_dir', type=int, default=4, help='number of direction embedding frequencies')
      parser.add_argument('--N_samples', type=int, default=64, help='number of coarse samples')
      parser.add_argument('--N_importance', type=int, default=128, help='number of additional fine samples')
      parser.add_argument('--use_disp', default=False, action="store_true", help='use disparity depth sampling')
      parser.add_argument('--perturb', type=float, default=1.0, help='factor to perturb depth sampling points')
      parser.add_argument('--noise_std', type=float, default=1.0, help='std dev of noise added to regularize sigma')
      parser.add_argument('--num_epochs', type=int, default=16, help='number of training epochs')
      parser.add_argument('--exp_name', type=str, default='exp', help='experiment name')
      parser.add_argument('--n_input_dims', type=int, default=3, help='e')
      parser.add_argument('--n_channels', type=int, default=3, help='number of channels to the MLP')
      parser.add_argument('--n_output_dims', type=int, default=3, help='experiment name')
      parser.add_argument('--N_vocab', type=int, default=1500, help='''number of vocabulary (number of images) in the dataset for nn.Embedding''')
      parser.add_argument('--in_channels_a', type=int, default=66, help='e')
      parser.add_argument('--in_channels_t', type=int, default=30, help='e')
      parser.add_argument('--beta_min', type=float, default=0.03, help='e')
      parser.add_argument('--coef', type=float, default=1, help='e')
      parser.add_argument('--decay_step', nargs='+', type=int, default=[20], help='scheduler decay step')
      parser.add_argument('--decay_gamma', type=float, default=0.1, help='learning rate decay amount')
      parser.add_argument('--scene_name', type=str, default='test', help='scene name, used as output folder name')
      parser.add_argument('--split', type=str, default='val', choices=['val', 'test', 'test_train'])

      args = parser.parse_args()
      return args