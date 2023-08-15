import uvicorn
import yaml
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from polydash.settings import PolydashSettings
from polydash.routers import node, block, dashboard, deanon
from polydash.db import start_db
from polydash.block_retriever.retriever import BlockRetriever
from polydash.rating.live_time_heuristic import start_live_time_heuristic
from polydash.rating.live_time_heuristic_a import start_live_time_heuristic_a
from polydash.deanonymize.deanonymizer import start_deanonymizer
import click

# FastAPI set up
app = FastAPI()
app.include_router(node.router)
app.include_router(block.router)
app.include_router(dashboard.router)
app.include_router(deanon.router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


@click.command()
@click.option('--settings',
              '-s',
              required=False,
              type=click.Path(exists=True),
              help='Path to the settings file (e.g. settings.yaml)')
def start(settings) -> PolydashSettings:
    if settings is None:
        s = PolydashSettings()
    else:
        with open(settings, 'r') as file:
            s = PolydashSettings(**yaml.safe_load(file))

    start_db(s.postgres_connection)
    BlockRetriever(s.block_retriever).start()
    start_live_time_heuristic()
    start_live_time_heuristic_a()
    start_deanonymizer()

    uvicorn.run(app, host=s.host, port=s.port)


@app.get("/")
async def root():
    return {"message": "Nothing here"}


if __name__ == "__main__":
    # Modules set up
    settings = start()
