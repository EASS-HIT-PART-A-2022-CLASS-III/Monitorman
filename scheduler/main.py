from fastapi import FastAPI
from .routers import scheduler
from fastapi_utils.tasks import repeat_every

from logging.config import dictConfig
from shared.logconfig import LogConfig

dictConfig(LogConfig().dict())

app = FastAPI()

app.include_router(scheduler.router)

@app.on_event('startup')
@repeat_every(seconds=60)
async def check_all():
    await scheduler.check_all()
