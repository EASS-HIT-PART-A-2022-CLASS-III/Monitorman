from fastapi import APIRouter, Body, HTTPException, Response, status
import motor.motor_asyncio
from fastapi.encoders import jsonable_encoder
from shared.models import MonitorModel
from ..models import UpdateStudentModel
from dotenv import load_dotenv
import requests
import os

load_dotenv('./backend/.env')

MONITORS_DB_NAME = 'monitors'

client = motor.motor_asyncio.AsyncIOMotorClient(os.getenv('MONGO_URL'))
db = client.project

router = APIRouter(prefix="/monitors", tags=["monitors"])


@router.get("/getmonitors/{with_results}", response_model=list[MonitorModel])
async def get_monitors(with_results: bool) -> list[MonitorModel]:
    monitors = await db[MONITORS_DB_NAME].find({}, projection={} if with_results else {'results': False}).to_list(1000)

    return monitors


@router.get("/{monitor_id}", response_model=MonitorModel)
async def get_monitor(monitor_id: str) -> MonitorModel:
    if (monitor := await db[MONITORS_DB_NAME].find_one({"_id": monitor_id})) is not None:
        return MonitorModel.parse_obj(monitor)

    raise HTTPException(
        status_code=404, detail=f"Monitor {monitor_id} not found")


@router.post("/", response_description="Add new monitor", response_model=MonitorModel)
async def create_monitor(response: Response, monitor: MonitorModel = Body(...)):
    monitor = jsonable_encoder(monitor)
    new_monitor = await db[MONITORS_DB_NAME].insert_one(monitor)

    requests.get(
        f'{os.getenv("SCHEDULER_URL")}/scheduler/{new_monitor.inserted_id}')

    created_monitor = await db[MONITORS_DB_NAME].find_one({"_id": new_monitor.inserted_id})

    response.status_code = status.HTTP_201_CREATED

    return created_monitor


@router.put("/{id}", response_description="Update a monitor", response_model=MonitorModel)
async def update_monitor(id: str, monitor: UpdateStudentModel = Body(...)):
    monitor = {k: v for k, v in monitor.dict().items() if v is not None}

    if len(monitor) >= 1:
        update_result = await db[MONITORS_DB_NAME].update_one({"_id": id}, {"$set": monitor})

        if update_result.modified_count == 1:
            requests.get(f'{os.getenv("SCHEDULER_URL")}/scheduler/{id}')

            if (
                updated_monitor := await db[MONITORS_DB_NAME].find_one({"_id": id})
            ) is not None:
                return updated_monitor

    if (existing_monitor := await db[MONITORS_DB_NAME].find_one({"_id": id})) is not None:
        return existing_monitor

    raise HTTPException(status_code=404, detail=f"Student {id} not found")


@router.delete("/{id}", response_description="Delete a monitor")
async def delete_monitor(id: str):
    delete_result = await db[MONITORS_DB_NAME].delete_one({"_id": id})

    if delete_result.deleted_count == 1:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=404, detail=f"Student {id} not found")
