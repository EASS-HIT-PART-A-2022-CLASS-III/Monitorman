from datetime import datetime
import math
from fastapi import APIRouter, HTTPException
import motor.motor_asyncio
from shared.models import MonitorModel, ResultModel
import requests
from dotenv import load_dotenv
import os
import logging

logger = logging.getLogger('app')

load_dotenv('./scheduler/.env')

MONITORS_DB_NAME = 'monitors'

client = motor.motor_asyncio.AsyncIOMotorClient(os.getenv('MONGO_URL'))
db = client.project

router = APIRouter(prefix="/scheduler", tags=["scheduler"])


async def check_all_repeat():
    await check_all()


async def check_all(force_check: bool = False):
    results = []
    logger.info('started checking all')

    async for monitor in db[MONITORS_DB_NAME].find():
        monitorModel = MonitorModel.parse_obj(monitor)

        if force_check or (len(monitorModel.results) >= 1 and (datetime.now()-monitorModel.results[0].time).total_seconds() > monitorModel.minute_interval*60):
            res = await check_and_save(monitorModel)
            results.append(res)

    return results


async def check_and_save(monitorModel: MonitorModel):
    logger.info(f'checking monitor {monitorModel.id}')

    res = requests.request(monitorModel.method,
                           monitorModel.url, data=monitorModel.body)
    ret = ResultModel(status=res.status_code,
                      duration_ms=math.floor(
                          res.elapsed.total_seconds()*1000),
                      time=datetime.now(),
                      content=res.text,
                      headers=res.headers)

    await db[MONITORS_DB_NAME].update_one(
        {"_id": str(monitorModel.id)}, {'$push': {'results': {'$each': [ret.dict()], '$position': 0}}}, upsert=True)

    return ret


@ router.get("/", response_model=list[ResultModel])
async def trigger_check_all() -> list[ResultModel]:
    results = await check_all(True)

    return results


@ router.get("/{monitor_id}", response_model=ResultModel)
async def trigger_monitor(monitor_id: str) -> ResultModel:
    logger.info(f'trigger {monitor_id}')

    if (monitor := await db[MONITORS_DB_NAME].find_one({"_id": monitor_id})) is not None:
        monitorModel = MonitorModel.parse_obj(monitor)

        ret = await check_and_save(monitorModel)

        return ret

    raise HTTPException(
        status_code=404, detail=f"Monitor {monitor_id} not found")
