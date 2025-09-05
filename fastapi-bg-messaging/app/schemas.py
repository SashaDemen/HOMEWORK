from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class User(BaseModel):
    email: EmailStr
    name: Optional[str] = None

class SendEmailIn(BaseModel):
    user: User
    subject: str = Field(min_length=1)
    body: str = Field(min_length=1)

class TaskOut(BaseModel):
    id: str
    name: str
    status: str
    result: Optional[str] = None
    error: Optional[str] = None

class UploadOut(BaseModel):
    task_ids: list[str]

