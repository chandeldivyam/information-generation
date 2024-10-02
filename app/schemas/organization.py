# ./information-generation/app/schemas/organization.py

from pydantic import BaseModel

class OrganizationCreate(BaseModel):
    name: str
    description: str

class OrganizationUpdate(BaseModel):
    description: str

class OrganizationResponse(BaseModel):
    name: str
    description: str