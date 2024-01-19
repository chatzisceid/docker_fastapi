from nir.utils.assertion import assert_key_in_dict
from nir.losses.distortion_loss import DistortionLoss
from nir.losses.nerf_loss import NerfWLoss
from nir.losses.losses_registry import LossRegistry

def get_loss(key: str, **kwargs):
    assert_key_in_dict(key, LossRegistry.registry)
    return LossRegistry.registry[key](**kwargs)