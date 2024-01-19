from nir.modules.module_registry import ModuleRegistry
from nir.encodings import *
import torch
import json

@ModuleRegistry.register("Mlp")
class Mlp(torch.nn.Module):
    def __init__(self, typ, in_channels_xyz = 66, in_channels_dir = 30, in_channels_a=48, in_channels_t=16 , encode_appearance=False, encode_transient=False, beta_min=0.03, D=8, W=256, skips=[4]):
        super(Mlp, self).__init__()

        self.typ = typ
        self.D = D
        self.W = W
        self.skips = skips
        self.beta_min = beta_min
        self.in_channels_xyz = in_channels_xyz
        self.in_channels_dir = in_channels_dir
        self.encode_appearance = False if typ=='coarse' else encode_appearance
        self.in_channels_a = in_channels_a if encode_appearance else 0
        self.encode_transient = False if typ=='coarse' else encode_transient
        self.in_channels_t = in_channels_t

        #self.network = tcnn.Network(encoding['xyz'].encoding.n_output_dims, n_output_dims, config["network"])
        #self.encoding_xyz = encoding['xyz'].encoding
        # self.model = torch.nn.Sequential(encoding['xyz'].encoding, self.network)

        # xyz encoding layers
        for i in range(D):
            if i == 0:
                layer = torch.nn.Linear(in_channels_xyz, W)
            elif i in skips:
                layer = torch.nn.Linear(W+in_channels_xyz, W)
            else:
                layer = torch.nn.Linear(W, W)
            layer = torch.nn.Sequential(layer, torch.nn.ReLU(True))
            setattr(self, f"xyz_encoding_{i+1}", layer)
        self.xyz_encoding_final = torch.nn.Linear(W, W)

        # direction encoding layers
        self.dir_encoding = torch.nn.Sequential(
                        torch.nn.Linear(W+in_channels_dir+self.in_channels_a, W//2), torch.nn.ReLU(True))

        # static output layers
        self.static_sigma = torch.nn.Sequential(torch.nn.Linear(W, 1), torch.nn.Softplus())
        self.static_rgb = torch.nn.Sequential(torch.nn.Linear(W//2, 3), torch.nn.Sigmoid())

        if self.encode_transient:
            # transient encoding layers
            self.transient_encoding = torch.nn.Sequential(
                                        torch.nn.Linear(W+in_channels_t, W//2), torch.nn.ReLU(True),
                                        torch.nn.Linear(W//2, W//2), torch.nn.ReLU(True),
                                        torch.nn.Linear(W//2, W//2), torch.nn.ReLU(True),
                                        torch.nn.Linear(W//2, W//2), torch.nn.ReLU(True))
            # transient output layers
            self.transient_sigma = torch.nn.Sequential(torch.nn.Linear(W//2, 1), torch.nn.Softplus())
            self.transient_rgb = torch.nn.Sequential(torch.nn.Linear(W//2, 3), torch.nn.Sigmoid())
            self.transient_beta = torch.nn.Sequential(torch.nn.Linear(W//2, 1), torch.nn.Softplus())


    def forward(self,x,sigma_only=False, output_transient=True):

        """
        Encodes input (xyz+dir) to rgb+allsigma (not ready to render yet).
        For rendering this ray, please see rendering.py

        Inputs:
            x: the embedded vector of position (+ direction + appearance + transient)
            sigma_only: whether to infer sigma only.
            has_transient: whether to infer the transient component.

        Outputs (concatenated):
            if sigma_ony:
                static_sigma
            elif output_transient:
                static_rgb, static_sigma, transient_rgb, transient_sigma, transient_beta
            else:
                static_rgb, static_sigma
        """
        if sigma_only:
            input_xyz = x
        elif output_transient:
            input_xyz, input_dir_a, input_t = \
                torch.split(x, [self.in_channels_xyz,
                                self.in_channels_dir+self.in_channels_a,
                                self.in_channels_t], dim=-1)
        else:
            input_xyz, input_dir_a = \
                torch.split(x, [self.in_channels_xyz,
                                self.in_channels_dir+self.in_channels_a], dim=-1)
            

        xyz_ = input_xyz
        xyz_ = xyz_.to(torch.float32)
        for i in range(self.D):
            if i in self.skips:
                xyz_ = torch.cat([input_xyz, xyz_], 1)
            xyz_ = getattr(self, f"xyz_encoding_{i+1}")(xyz_)

        static_sigma = self.static_sigma(xyz_) # (B, 1)
        if sigma_only:
            return static_sigma

        xyz_encoding_final = self.xyz_encoding_final(xyz_)
        dir_encoding_input = torch.cat([xyz_encoding_final, input_dir_a], 1)
        dir_encoding = self.dir_encoding(dir_encoding_input)
        static_rgb = self.static_rgb(dir_encoding) # (B, 3)
        static = torch.cat([static_rgb, static_sigma], 1) # (B, 4)

        if not output_transient:
            return static

        transient_encoding_input = torch.cat([xyz_encoding_final, input_t], 1)
        transient_encoding = self.transient_encoding(transient_encoding_input)
        transient_sigma = self.transient_sigma(transient_encoding) # (B, 1)
        transient_rgb = self.transient_rgb(transient_encoding) # (B, 3)
        transient_beta = self.transient_beta(transient_encoding) # (B, 1)

        transient = torch.cat([transient_rgb, transient_sigma,
                               transient_beta], 1) # (B, 5)

        return torch.cat([static, transient], 1) # (B, 9)
        #x = self.model()
        #x = self.encoding_xyz(x)
        #x = self.network(x)
        #return x