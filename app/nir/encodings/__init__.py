from nir.utils.assertion import assert_key_in_dict
from nir.encodings.hashgrid import HashGrid
from nir.encodings.positional import PositionalEncoding
from nir.encodings.encoding_registry import EncodingsRegistry
from nir.encodings.hashgrid_py import HashGrid_py
from nir.encodings.hashgrid_py import MultiResHashGrid

def get_encoding(key: str, **kwargs):
    assert_key_in_dict(key, EncodingsRegistry.registry)
    return EncodingsRegistry.registry[key](**kwargs)