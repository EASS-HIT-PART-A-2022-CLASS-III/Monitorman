from datetime import datetime
import math
from fastapi import APIRouter, Depends, HTTPException
import pymongo
from shared.models import MonitorModel, ResultModel
import requests
from dotenv import load_dotenv
import os
import logging
from fastapi_utils.tasks import repeat_every

logger = logging.getLogger('app')

load_dotenv('./scheduler/.env')

router = APIRouter(prefix="/scheduler", tags=["scheduler"])

MONITORS_COLLECTION_NAME = 'monitors'
MONGO_DB_NAME = 'project'


def get_prod_client():
    return pymongo.MongoClient(host=os.getenv('MONGO_URL'))


@router.on_event('startup')
@repeat_every(seconds=60)
def check_all():
    check_all(get_prod_client())


def check_all(client: pymongo.MongoClient, force_check: bool = False):
    logger.info('started checking all')
    db = client[MONGO_DB_NAME]
    results = []

    for monitor in db[MONITORS_COLLECTION_NAME].find():
        monitorModel = MonitorModel.parse_obj(monitor)

        if force_check or (len(monitorModel.results) >= 1 and (datetime.now()-monitorModel.results[0].time).total_seconds() > monitorModel.minute_interval*60):
            res = check_and_save(client, monitorModel)
            results.append(res)

    return results


def check_and_save(client: pymongo.MongoClient, monitorModel: MonitorModel):
    logger.info(f'checking monitor {monitorModel.id}')
    db = client[MONGO_DB_NAME]

    res = requests.request(monitorModel.method,
                           monitorModel.url, data=monitorModel.body)
    ret = ResultModel(status=res.status_code,
                      duration_ms=math.floor(
                          res.elapsed.total_seconds()*1000),
                      time=datetime.now(),
                      content=res.text,
                      headers=res.headers)

    db[MONITORS_COLLECTION_NAME].update_one(
        {"_id": str(monitorModel.id)}, {'$push': {'results': {'$each': [ret.dict()], '$position': 0}}}, upsert=True)

    return ret


@router.get("/", response_model=list[ResultModel])
def trigger_check_all(client: pymongo.MongoClient = Depends(get_prod_client)) -> list[ResultModel]:
    results = check_all(client, True)

    return results


@ router.get("/{monitor_id}", response_model=ResultModel)
def trigger_monitor(monitor_id: str, client: pymongo.MongoClient = Depends(get_prod_client)) -> ResultModel:
    logger.info(f'trigger {monitor_id}')
    db = client[MONGO_DB_NAME]

    if (monitor := db[MONITORS_COLLECTION_NAME].find_one({"_id": monitor_id})) is not None:
        monitorModel = MonitorModel.parse_obj(monitor)

        ret = check_and_save(client, monitorModel)

        return ret

    raise HTTPException(
        status_code=404, detail=f"Monitor {monitor_id} not found")
