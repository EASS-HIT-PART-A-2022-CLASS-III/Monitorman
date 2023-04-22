from typing import Literal, Optional
from bson import ObjectId
from pydantic import BaseModel, Field

class UpdateStudentModel(BaseModel):
    description: Optional[str]
    url: Optional[str]
    method: Optional[Literal['GET', 'POST']]
    body: Optional[str]
    minute_interval: Optional[Literal[1, 2, 5, 10, 30, 60]]
    
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "description": "short description of the monitor",
                "url": "http://httpbin.org/post",
                "method": "POST",
                "body": "{\"hello\":\"world\"}",
                "minute_interval": 5
            }
        }
