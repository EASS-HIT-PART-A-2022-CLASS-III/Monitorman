import os

import pymongo
import requests
from dotenv import load_dotenv
from fastapi import APIRouter, Body, Depends, HTTPException, Response, status
from fastapi.encoders import jsonable_encoder

from shared.models import MonitorModel
from shared.mongoparams import MONGO_DB_NAME, MONITORS_COLLECTION_NAME

from ..models import UpdateMonitorModel

load_dotenv('./backend/.env')


def get_prod_client():
    return pymongo.MongoClient(host=os.getenv('MONGO_URL'))


router = APIRouter(prefix="/monitors", tags=["monitors"])


@router.get("/getmonitors/{with_results}", response_model=list[MonitorModel])
def get_monitors(with_results: bool, client: pymongo.MongoClient = Depends(get_prod_client)) -> list[MonitorModel]:
    db = client[MONGO_DB_NAME]
    monitors = list(db[MONITORS_COLLECTION_NAME].find(
        {}, projection={} if with_results else {'results': False}))

    return monitors


@router.get("/{monitor_id}", response_model=MonitorModel)
def get_monitor(monitor_id: str, client: pymongo.MongoClient = Depends(get_prod_client)) -> MonitorModel:
    db = client[MONGO_DB_NAME]

    if (monitor := db[MONITORS_COLLECTION_NAME].find_one({"_id": monitor_id})) is not None:
        return MonitorModel.parse_obj(monitor)

    raise HTTPException(
        status_code=404, detail=f"Monitor {monitor_id} not found")


@router.post("/", response_description="Add new monitor", response_model=MonitorModel)
def create_monitor(response: Response, client: pymongo.MongoClient = Depends(get_prod_client), monitor: MonitorModel = Body(...)):
    db = client[MONGO_DB_NAME]
    monitor = jsonable_encoder(monitor)
    new_monitor = db[MONITORS_COLLECTION_NAME].insert_one(monitor)

    requests.get(
        f'{os.getenv("SCHEDULER_URL")}/scheduler/{new_monitor.inserted_id}')

    created_monitor = db[MONITORS_COLLECTION_NAME].find_one(
        {"_id": new_monitor.inserted_id})

    response.status_code = status.HTTP_201_CREATED

    return created_monitor


@router.put("/{id}", response_description="Update a monitor", response_model=MonitorModel)
def update_monitor(id: str, client: pymongo.MongoClient = Depends(get_prod_client), monitor: UpdateMonitorModel = Body(...)):
    db = client[MONGO_DB_NAME]
    monitor = {k: v for k, v in monitor.dict().items() if v is not None}

    if len(monitor) >= 1:
        update_result = db[MONITORS_COLLECTION_NAME].update_one(
            {"_id": id}, {"$set": monitor})

        if update_result.modified_count == 1:
            requests.get(f'{os.getenv("SCHEDULER_URL")}/scheduler/{id}')

            if (
                updated_monitor := db[MONITORS_COLLECTION_NAME].find_one({"_id": id})
            ) is not None:
                return updated_monitor

    if (existing_monitor := db[MONITORS_COLLECTION_NAME].find_one({"_id": id})) is not None:
        return existing_monitor

    raise HTTPException(status_code=404, detail=f"Monitor {id} not found")


@router.delete("/{id}", response_description="Delete a monitor")
def delete_monitor(id: str, client: pymongo.MongoClient = Depends(get_prod_client)):
    db = client[MONGO_DB_NAME]
    delete_result = db[MONITORS_COLLECTION_NAME].delete_one({"_id": id})

    if delete_result.deleted_count == 1:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=404, detail=f"Monitor {id} not found")
