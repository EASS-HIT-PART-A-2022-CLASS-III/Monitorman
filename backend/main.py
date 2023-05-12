from fastapi import FastAPI

from .routers import monitors_v1

app = FastAPI()

app.include_router(monitors_v1.router)
