from pony import orm

# PonyORM set up
db = orm.Database()


class GetOrInsertMixin:
    @classmethod
    def get_or_insert(cls, **kwargs):
        return cls.get(**kwargs) or cls(**kwargs)
