from nir.utils import assert_key_in_dict
from nir.modules.module_registry import ModuleRegistry
from nir.modules.mlp import Mlp

def get_module(key: str, **kwargs):
    assert_key_in_dict(key, ModuleRegistry.registry)
    return ModuleRegistry.registry[key](**kwargs)