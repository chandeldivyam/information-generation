# app/api/routes/document.py

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, BackgroundTasks
from app.services.document_ingestion import DocumentIngestionService
from app.services.vector_db import VectorDBService
from app.schemas.document import DocumentSearch, TaskStatusResponse, DocumentUploadResponse, RelevantDocumentResponse
from app.core.celery_app import celery_app
from celery.exceptions import TimeoutError
import tempfile
import os
import uuid
from langchain_cohere import CohereRerank
from langchain.schema import Document
from app.core.config import settings

from app.core.exceptions import AppException
from app.core.logging_config import logging
from typing import List

router = APIRouter()
logger = logging.getLogger(__name__)


router = APIRouter()

@router.post("/documents/upload", response_model=DocumentUploadResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    ingestion_service: DocumentIngestionService = Depends(),
):
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(await file.read())
        temp_file_path = temp_file.name
    
    # TODO - Get organization from auth headers
    organization_id = 'shipsy'

    # Generate a unique task ID
    task_id = str(uuid.uuid4())

    try:
        # Queue the document processing task
        celery_app.send_task(
            'app.tasks.document.process_document',
            args=[temp_file_path, organization_id, task_id],
            task_id=task_id
        )

        return DocumentUploadResponse(task_id=task_id, message="Document upload queued for processing")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/documents/relevant", response_model=List[Document])
async def get_relevant_documents(
    search_params: DocumentSearch,
    vector_db_service: VectorDBService = Depends()
):
    try:
        logger.info(f"Searching for relevant documents with query: {search_params.query}")
        
        # Fetch initial results from vector store
        results = await vector_db_service.search_documents(
            search_params.organization_id,
            search_params.query,
            k=10  # Fetch top 10 results initially
        )
        
        if not results:
            logger.info("No documents found in initial search")
            return []

        # Initialize CohereRerank
        try:
            os.environ["COHERE_API_KEY"] = settings.COHERE_API_KEY
            cohere_client = CohereRerank(model="rerank-english-v2.0")
        except Exception as e:
            logger.error(f"Failed to initialize CohereRerank: {str(e)}")
            raise AppException(status_code=500, detail="Failed to initialize reranking service")

        # Prepare documents for reranking
        documents = [doc.page_content for doc in results]
        
        # Perform reranking
        try:
            reranked_results = cohere_client.rerank(
                documents=documents,
                query=search_params.query,
                top_n=5  # Return top 5 most relevant results
            )
        except Exception as e:
            logger.error(f"Reranking failed: {str(e)}")
            raise AppException(status_code=500, detail="Document reranking failed")

        # Prepare final response
        try:    
            final_docs = []
            for item in reranked_results:
                idx = item.get('index')
                relevance_score = item.get('relevance_score')
                if idx is None or relevance_score is None:
                    logger.info(f"Continue due to missing index / relevance score")
                    continue
                doc = results[idx]
                doc.metadata['relevance_score'] = relevance_score
                if relevance_score > 0.15:
                    final_docs.append(doc)

            logger.info(f"Successfully retrieved and reranked {len(final_docs)} documents")
            return final_docs
        except Exception as e:
            logger.error(f"Unexpected error in get_relevant_documents: {str(e)}")
            raise HTTPException(status_code=400, detail=f"{str(e)}")

    except AppException as ae:
        raise ae
    except Exception as e:
        logger.error(f"Unexpected error in get_relevant_documents: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

@router.delete("/documents/{source_document_id}")
async def delete_document(
    source_document_id: str,
    vector_db_service: VectorDBService = Depends()
):
    try:
        organization_id = 'shipsy' # TODO - Use auth to extract the org id
        result = await vector_db_service.delete_documents(
            organization_id,
            source_document_id
        )
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        

from celery.exceptions import TimeoutError
from celery.result import AsyncResult

@router.get("/documents/task/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    task = AsyncResult(task_id)
    
    # Check if the task exists in the result backend
    try:
        # This will raise a TimeoutError if the task doesn't exist
        task.get(timeout=1)
    except Exception as e:
        if isinstance(e, TimeoutError):
        # Task doesn't exist or hasn't been registered yet
            raise HTTPException(status_code=404, detail="Task not found or not yet registered")
        else:
            raise HTTPException(status_code=500, detail=str(e))
    
    try:
        if task.state == 'PENDING':
            response = {
                'status': task.state,
                'current': 0,
                'total': 1,
                'status': 'Pending...'
            }
        elif task.state != 'FAILURE':
            response = {
                'status': task.state,
                'current': task.info.get('current', 0) if isinstance(task.info, dict) else 0,
                'total': task.info.get('total', 1) if isinstance(task.info, dict) else 1,
                'status': task.info.get('status', '') if isinstance(task.info, dict) else str(task.info)
            }
            if isinstance(task.info, dict) and 'result' in task.info:
                response['result'] = task.info['result']
        else:
            response = {
                'status': task.state,
                'current': 1,
                'total': 1,
                'status': str(task.info),
            }
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

    