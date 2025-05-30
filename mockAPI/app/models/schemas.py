from pydantic import BaseModel

class AccessKeyResponse(BaseModel):
    access_key: str
