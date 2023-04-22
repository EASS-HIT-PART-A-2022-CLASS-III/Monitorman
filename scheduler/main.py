from logging.config import dictConfig

from fastapi import FastAPI

from shared.logconfig import LogConfig

from .routers import scheduler

dictConfig(LogConfig().dict())

app = FastAPI()

app.include_router(scheduler.router)
