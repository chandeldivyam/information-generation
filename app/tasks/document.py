from app.core.celery_app import celery_app
from app.services.document_ingestion import DocumentIngestionService
from app.services.vector_db import VectorDBService
from app.core.logging_config import logging
import asyncio
import os

logger = logging.getLogger(__name__)

@celery_app.task(bind=True)
def process_document(self, file_path: str, organization_id: str, task_id: str):
    logger.info(f"Starting document processing for task {task_id}")
    try:
        ingestion_service = DocumentIngestionService()
        vector_db_service = VectorDBService()

        # Use asyncio to run the asynchronous methods
        loop = asyncio.get_event_loop()
        
        self.update_state(state='PROGRESS', meta={'status': 'Processing document', 'current': 1, 'total': 2})
        processed_docs = loop.run_until_complete(ingestion_service.process_document(file_path, organization_id))
        
        self.update_state(state='PROGRESS', meta={'status': 'Inserting into vector database', 'current': 2, 'total': 2})
        loop.run_until_complete(vector_db_service.insert_documents(processed_docs))

        logger.info(f"Document processing completed for task {task_id}")
        os.unlink(file_path)
        return {"status": "success", "task_id": task_id}
    except Exception as e:
        logger.error(f"Error processing document for task {task_id}: {str(e)}")
        self.update_state(state='FAILURE', meta={'error': str(e)})
        raise

    finally:
        if os.path.exists(file_path):
            os.unlink(file_path)