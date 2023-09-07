from typing import Callable

import click
import uvicorn
import yaml
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

from common.dashboard.db import start_db
from polydash.settings import PolydashSettings


class Dashboard:
    def __init__(self,
                 routers: list[APIRouter],
                 startup_callback: Callable):
        self.__routers = routers
        self.__startup_callback = startup_callback
        self.__app = FastAPI()

    @click.command()
    @click.option('--settings',
                  '-s',
                  required=False,
                  type=click.Path(exists=True),
                  help='Path to the settings file (e.g. settings.yaml)')
    def start(self, settings):
        if settings is None:
            s = PolydashSettings()
        else:
            with open(settings, 'r') as file:
                s = PolydashSettings(**yaml.safe_load(file))

        start_db(s.postgres_connection)
        self.__startup_callback(s)

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

        uvicorn.run(self.__app, host=s.host, port=s.port)
