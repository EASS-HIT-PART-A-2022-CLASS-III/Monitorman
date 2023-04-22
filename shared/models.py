from datetime import datetime
from typing import Dict, Literal, Optional
from bson import ObjectId
from pydantic import BaseModel, Field

from .dependencies import PyObjectId


class ResultModel(BaseModel):
    status: int
    time: datetime
    duration_ms: int
    content: str
    headers: Dict[str, str]


class MonitorModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    description: str = ''
    url: str
    method: Literal['GET', 'POST']
    body: str = ''
    expected_status: Optional[int]
    expected_result_regex: Optional[str]
    expected_headers_regex: Optional[Dict[str, str]]
    max_duration_ms: Optional[int]
    results: Optional[list[ResultModel]] = []
    minute_interval: Literal[1, 2, 5, 10, 30, 60] = 5

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "description": "short description of the monitor",
                "url": "http://httpbin.org/post",
                "method": "POST",
                "body": "{\"hello\":\"world\"}",
                "expected_status": 200,
                "expected_result_regex": "^.+$",
                "expected_headers_regex": {},
                "max_duration_ms": 60,
                "minute_interval": 5,
            }
        }
