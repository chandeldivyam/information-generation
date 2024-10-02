# app/services/vector_db.py

from app.core.db import db_manager
from app.schemas.document import DocumentCreate
from typing import List
import uuid

class VectorDBService:
    def __init__(self):
        self.collection_name = "documents"

    async def insert_documents(self, documents: List[DocumentCreate]):
        with db_manager.get_client() as client:
            if not client:
                raise Exception("Failed to connect to the database")
            
            collection = client.get_or_create_collection(self.collection_name)
            
            for doc in documents:
                collection.add(
                    documents=[doc.content],
                    embeddings=[doc.embedding],
                    metadatas=[{
                        "organization_id": doc.organization_id,
                        "source_file_name": doc.source_file_name,
                        "source_file_path": doc.source_file_path,
                        "source_document_id": doc.source_document_id
                    }],
                    ids=[str(uuid.uuid4())]
                )

    async def search_documents(self, organization_id: str):
        with db_manager.get_client() as client:
            if not client:
                raise Exception("Failed to connect to the database")
            
            collection = client.get_or_create_collection(self.collection_name)
            results = collection.get(
                where={"organization_id": organization_id}
            )
            return results

    async def delete_documents(self, organization_id: str, source_document_id: str):
        with db_manager.get_client() as client:
            if not client:
                raise Exception("failed to connect to the database")
            
            collection = client.get_or_create_collection(self.collection_name)
            collection.delete(
                where={"source_document_id": source_document_id}
            )
            return {"message": "Documents deleted successfully"}