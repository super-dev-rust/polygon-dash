from fastapi import FastAPI
from pony import orm
from .routers import node
from .db import startup_db
from .model.node import Node
from .model.transaction import Transaction

startup_db()

# FastAPI set up
app = FastAPI()
app.include_router(node.router)


@app.get("/")
async def root():
    # fill DB with mock values when calling root just for tests
    with orm.db_session:
        n1 = Node(pubkey='foo')
        n2 = Node(pubkey='bar')
        t1 = Transaction(hash='hash1', creator=n1, created=1111)
        t2 = Transaction(hash='hash2', creator=n1, created=2222)
        t2 = Transaction(hash='hash3', creator=n2, created=3333)
        orm.commit()
    return {"message": "Filled DB"}
