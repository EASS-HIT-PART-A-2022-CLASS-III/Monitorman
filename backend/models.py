from typing import Literal, Optional
from bson import ObjectId
from pydantic import BaseModel, Field

class UpdateStudentModel(BaseModel):
    description: Optional[str]
    url: Optional[str]
    method: Optional[Literal['GET', 'POST']]
    body: Optional[str]

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "description": "short description of the monitor",
                "url": "http://httpbin.org/post",
                "method": "POST",
                "body": "{\"hello\":\"world\"}",
            }
        }
