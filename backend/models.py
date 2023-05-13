from typing import Dict, Literal, Optional

from bson import ObjectId
from pydantic import BaseModel

from shared.models import CheckModel


class UpdateMonitorModel(BaseModel):
    description: Optional[str]
    url: Optional[str]
    method: Optional[Literal["GET", "POST", "PUT", "DELETE"]]
    body: Optional[str]
    checks: Optional[CheckModel]
    minute_interval: Optional[Literal[1, 2, 5, 10, 30, 60]]

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "description": "short description of the monitor",
                "url": "http://httpbin.org/post",
                "method": "POST",
                "body": '{"hello":"world"}',
                "checks": {
                    "expected_status": 200,
                    "expected_result_regex": "^.+$",
                    "expected_headers_regex": {},
                    "expected_max_duration_ms": 60 * 1000,
                },
                "minute_interval": 5,
            }
        }
