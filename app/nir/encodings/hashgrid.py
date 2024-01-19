import torch
from nir.encodings.encoding_registry import EncodingsRegistry
# import tinycudann as tcnn

@EncodingsRegistry.register("HashGrid")
class HashGrid(torch.nn.Module):
#     def __init__(self, config, n_input_dims):
#         super(HashGrid, self).__init__()
#         self.encoding = tcnn.Encoding(n_input_dims, config)

    def forward(self, x):
        return self.encoding(x)