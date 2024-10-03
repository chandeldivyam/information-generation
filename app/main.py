import os
from fastapi import FastAPI
from app.api.routes import organization, document, question_answer, chat
from app.core.config import settings
from app.core.logging_config import setup_logging
from app.core.logging_config import logging
from app.core.db import db_manager
from app.core.exceptions import app_exception_handler, global_exception_handler, AppException
from app.core.celery_app import celery_app

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title=settings.APP_NAME, version=settings.VERSION)

app.include_router(organization.router, prefix="/api/v1") 
app.include_router(document.router, prefix="/api/v1")
app.include_router(question_answer.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")

app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

@app.on_event("startup")
async def startup_event():
    logger.info(f"Starting {settings.APP_NAME}")
    try:
        os.environ["GOOGLE_API_KEY"] = settings.GOOGLE_API_KEY
        db_manager.connect()
        celery_app.conf.update(broker_url=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0")
    except Exception as e:
        logger.error(f"Failed to connect to ChromeDB: {str(e)}")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info(f"Shutting down {settings.APP_NAME}")
    db_manager.disconnect()

@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {"message": f"Welcome to {settings.APP_NAME}"}