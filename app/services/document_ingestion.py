# app/services/document_ingestion.py

import os
import uuid
from typing import List
import requests
from langchain_unstructured import UnstructuredLoader
from langchain_experimental.text_splitter import SemanticChunker
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from unstructured_client import UnstructuredClient
from unstructured_client.utils import BackoffStrategy, RetryConfig
from app.core.config import settings
from app.schemas.document import DocumentCreate
from langchain.schema import Document
import os

class DocumentIngestionService:
    def __init__(self):
        os.environ["GOOGLE_API_KEY"] = settings.GOOGLE_API_KEY
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", task_type="retrieval_document")
        self.semantic_chunker = SemanticChunker(
            self.embeddings,
            breakpoint_threshold_type="interquartile",
            min_chunk_size=250
        )
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
        )
        self.unstructured_client = self._create_unstructured_client()

    def _create_unstructured_client(self):
        return UnstructuredClient(
            api_key_auth=settings.UNSTRUCTURED_API_KEY,
            client=requests.Session(),
            server_url=settings.UNSTRUCTURED_API_URL + "/general/v0/general",
            retry_config=RetryConfig(
                strategy="backoff",
                retry_connection_errors=True,
                backoff=BackoffStrategy(
                    initial_interval=500,
                    max_interval=60000,
                    exponent=1.5,
                    max_elapsed_time=900000,
                ),
            ),
        )

    async def process_document(self, file_path: str, organization_id: str) -> List[Document]:
        loader = UnstructuredLoader(
            file_path,
            partition_via_api=True,
            client=self.unstructured_client,
            chunking_strategy="by_title",
            max_characters=5000,
        )
        docs = loader.load()
        semantic_chunks = self.semantic_chunker.create_documents([d.page_content for d in docs])
        
        overall_doc_content = ' '.join([doc.page_content for doc in semantic_chunks])
        keywords = await self.extract_keywords(overall_doc_content)
        
        processed_docs = []
        source_document_id = str(uuid.uuid4())
        
        for idx, chunk in enumerate(semantic_chunks):
            doc = Document(
                page_content=f"Relevant Topics Covered: {keywords}\nContent: {chunk.page_content}",
                metadata={
                    "organization_id": organization_id,
                    "source_file_name": os.path.basename(file_path),
                    "source_file_path": file_path, # TODO - We need s3 link here
                    "source_document_id": source_document_id,
                    "part_number": idx+1,
                },
            )
            processed_docs.append(doc)
        
        return processed_docs

    async def extract_keywords(self, content: str) -> str:
        prompt = f"""I am building a RAG based application and this is a document provided by the user. Can you please give me topics being covered in the document? Please write everything in order and do not miss topics. Mention the most important headings being covered in the document which will help in retrieval later.
        Respond as a comma-separated string.
        {content}
        """
        response = self.llm.invoke(prompt)
        
        # Extract the content from the response
        if isinstance(response.content, str):
            return response.content
        elif isinstance(response.content, list):
            # If it's a list, join all string elements
            return ", ".join([str(item) for item in response.content if isinstance(item, str)])
        else:
            # If it's neither a string nor a list, convert to string
            return str(response.content)