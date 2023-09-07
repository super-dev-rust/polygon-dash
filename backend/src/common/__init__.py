class GetOrInsertMixin:
    @classmethod
    def get_or_insert(cls, **kwargs):
        return cls.get(**kwargs) or cls(**kwargs)
