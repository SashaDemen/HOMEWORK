from pydantic import BaseModel
from typing import List, Optional

class UploadResult(BaseModel):
    items: List[dict]
    task_ids: List[str]

class TaskOut(BaseModel):
    id: str
    name: str
    status: str
    result: Optional[str] = None
    error: Optional[str] = None
