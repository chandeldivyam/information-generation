# app/schemas/document.py

from pydantic import BaseModel
from typing import List, Optional

class DocumentCreate(BaseModel):
    content: str
    organization_id: str
    source_file_name: str
    source_file_path: str
    source_document_id: str
    part_number: int
    embedding: List[float]

class DocumentSearch(BaseModel):
    organization_id: str

class DocumentUploadResponse(BaseModel):
    task_id: str
    message: str

class TaskStatusResponse(BaseModel):
    status: str
    current: int
    total: int
    status: str
    result: Optional[str] = None
