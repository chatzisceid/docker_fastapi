from nir.utils.assertion import assert_key_in_dict
from nir.dataset.dataset_registry import DatasetRegistry
from nir.dataset.phototourism import PhototourismDataset

def get_dataset(key: str, **kwargs):
    assert_key_in_dict(key, DatasetRegistry.registry)
    return DatasetRegistry.registry[key](**kwargs)