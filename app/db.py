from pony import orm

# PonyORM set up
db = orm.Database()


def startup_db():
    db.bind(provider='sqlite', filename='database.sqlite', create_db=True)
    db.generate_mapping(create_tables=True)
