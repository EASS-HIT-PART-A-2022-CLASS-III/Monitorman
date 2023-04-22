from fastapi import FastAPI
from .routers import scheduler

from logging.config import dictConfig
from shared.logconfig import LogConfig

dictConfig(LogConfig().dict())

app = FastAPI()

app.include_router(scheduler.router)
