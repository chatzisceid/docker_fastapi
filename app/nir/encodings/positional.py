from nir.encodings.encoding_registry import EncodingsRegistry

@EncodingsRegistry.register("PositionalEncoding")
class PositionalEncoding():
    def __init__(self):
        return