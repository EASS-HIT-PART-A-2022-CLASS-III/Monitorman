from fastapi import FastAPI

from .routers import monitors

app = FastAPI()

app.include_router(monitors.router)
