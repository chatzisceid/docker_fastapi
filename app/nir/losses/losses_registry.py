class LossRegistry:
    registry = { }

    @classmethod
    def register(cls, name):
        def decorator(klass):
            cls.registry[name] = klass 
            return klass
        return decorator