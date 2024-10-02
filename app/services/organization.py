# ./information-generation/app/services/organization.py

from app.core.db import db_manager
from app.core.exceptions import AppException
from chromadb.api.types import Document, EmbeddingFunction, Embeddings
import re

class OrganizationService:
    def __init__(self):
        self.collection_name = "organizations"

    async def create_organization(self, name: str, description: str):
        if not re.match(r'^[a-z0-9]+(_[a-z0-9]+)*$', name):
            raise ValueError(f"Organization name '{name}' must be in snake case")

        with db_manager.get_client() as client:
            if client is None:
                raise AppException(500, "Failed to connect to the database")
            
            collection = client.get_or_create_collection(self.collection_name)
            existing_org = collection.get(where={"name": name})
            
            if existing_org["ids"]:
                raise ValueError(f"Organization '{name}' already exists")
            
            org_data = f"{description}"
            collection.add(
                documents=[org_data],
                metadatas=[{"organization_id": name}],
                ids=[name]
            )
            return {"name": name, "description": description}

    async def update_organization(self, name: str, description: str):
        with db_manager.get_client() as client:
            if client is None:
                raise AppException(500, "Failed to connect to the database")
            
            collection = client.get_or_create_collection(self.collection_name)
            existing_org = collection.get(where={"organization_id": name})
            
            if not existing_org["ids"]:
                raise ValueError(f"Organization '{name}' not found")
            
            updated_data = f"{description}"
            collection.update(
                documents=[updated_data],
                metadatas=[{"organization_id": name}],
                ids=[name]
            )
            return {"name": name, "description": description}
    
    async def get_organization(self, name: str):
        with db_manager.get_client() as client:
            if client is None:
                raise AppException(500, "Failed to connect to the database")
            
            collection = client.get_or_create_collection(self.collection_name)
            existing_org = collection.get(where={"organization_id": name})
            
            if not existing_org["ids"]:
                raise ValueError(f"Organization '{name}' not found")
            
            return existing_org
        
    async def delete_organization(self, name: str):
        with db_manager.get_client() as client:
            if client is None:
                raise AppException(500, "Failed to connect to the database")
            
            collection = client.get_or_create_collection(self.collection_name)
            existing_org = collection.get(where={"organization_id": name})
            
            if not existing_org["ids"]:
                raise ValueError(f"Organization '{name}' not found")
            
            collection.delete(ids=[name])
            return {"message": f"Organization '{name}' deleted successfully"}