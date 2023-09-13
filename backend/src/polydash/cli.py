from types import NoneType
from typing import Callable

import click
import uvicorn
import yaml
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

from polydash.cardano.startup import routers_cardano, startup_sequence_cardano
from polydash.common.db import db
from polydash.common.db_start import start_db
from polydash.common.log import LOGGER
from polydash.common.upgrade import upgrade_from_v1
from polydash.dashboard.settings import DashboardSettings
from polydash.polygon.startup import routers_polygon, startup_sequence_polygon


# ACHTUNG!
# The way Click command groups work, you must put common (i.e. '--settings something.yaml')
# parameters BEFORE the actual command (i.e. 'polygon')
@click.group()
@click.option(
    "--settings",
    "-s",
    required=False,
    type=click.Path(exists=True),
    help="Path to the settings file (e.g. settings.yaml)",
)
@click.pass_context
def cli(ctx, settings):
    """This is the main entry point for the command line application"""
    ctx.ensure_object(NoneType)

    if settings is None:
        s = DashboardSettings()
    else:
        with open(settings, "r") as file:
            s = DashboardSettings(**yaml.safe_load(file))
    ctx.obj = Dashboard(s)
    LOGGER.setLevel(s.log_level)


@cli.command()
@click.pass_context
def polygon(ctx):
    ctx.obj.start_dashboard(
        routers_polygon,
        startup_sequence_polygon,
        network_name="polygon")


@cli.command()
@click.pass_context
def cardano(ctx):
    ctx.obj.start_dashboard(
        routers_cardano,
        startup_sequence_cardano,
        network_name="cardano",
    )


@cli.command()
@click.pass_context
def upgrade(ctx):
    db.bind(provider="postgres", **dict(ctx.obj.settings.postgres_connection))
    upgrade_from_v1(db)


class Dashboard:
    def __init__(self, settings: DashboardSettings):
        self.__routers = []
        self.__startup_callback = None
        self.__app = FastAPI()
        self.settings = settings

    def start_dashboard(self,
                        routers: list[APIRouter],
                        startup_callback: Callable,
                        network_name: str = None):
        self.__routers = routers
        self.__startup_callback = startup_callback
        self.__app = FastAPI()

        start_db(self.settings.postgres_connection, network_name)
        self.__startup_callback(self.settings)

        # FastAPI set up
        self.__app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Allows all origins
            allow_credentials=True,
            allow_methods=["*"],  # Allows all methods
            allow_headers=["*"],  # Allows all headers
        )
        for router in self.__routers:
            self.__app.include_router(router)

        uvicorn.run(self.__app, host=self.settings.host, port=self.settings.port)
