# app/services/chat.py

from app.services.document_ingestion import DocumentIngestionService
from app.services.question_answer import QuestionAnswerService
from app.services.vector_db import VectorDBService
from app.schemas.chat import ChatRequest, ChatResponse
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_cohere import CohereRerank
from app.core.config import settings
from app.core.logging_config import logging
import os

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self):
        os.environ["GOOGLE_API_KEY"] = settings.GOOGLE_API_KEY
        os.environ["COHERE_API_KEY"] = settings.COHERE_API_KEY
        self.document_service = DocumentIngestionService()
        self.qa_service = QuestionAnswerService()
        self.vector_db_service = VectorDBService()
        self.llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
        self.reranker = CohereRerank(model="rerank-english-v2.0")

    async def generate_response(self, chat_request: ChatRequest) -> ChatResponse:
        try:
            # Fetch relevant documents
            relevant_docs = await self.vector_db_service.search_documents(
                chat_request.organization_id,
                chat_request.query,
                k=10  # Increase to 10 for better reranking
            )

            # Rerank documents
            reranked_docs = self._rerank_documents(chat_request.query, relevant_docs)

            # Fetch relevant questions
            relevant_questions = await self.qa_service.get_relevant_questions(
                chat_request
            )

            # Prepare context for the LLM
            context = self._prepare_context(reranked_docs, relevant_questions)
            logger.info(f"Prepared context: {context}")

            # Generate response using LLM
            prompt = f"""You are an AI assistant. Use the following context to answer the user's question. If you cannot find a relevant answer in the context, say so politely.

Context:
{context}

User's question: {chat_request.query}

Please provide a concise and relevant answer:"""

            response = self.llm.invoke(prompt)
            response_str = ''
            if isinstance(response.content, str):
                response_str = response.content
            elif isinstance(response.content, list):
                response_str = ", ".join([str(item) for item in response.content if isinstance(item, str)])
            else:
                response_str = str(response.content)

            return ChatResponse(
                answer=response_str,
                relevant_docs=[doc.page_content for doc in reranked_docs],
                relevant_questions=[q.page_content for q in relevant_questions]
            )

        except Exception as e:
            logger.error(f"Error generating chat response: {str(e)}")
            raise

    def _rerank_documents(self, query, docs):
        try:
            documents = [doc.page_content for doc in docs]
            reranked_results = self.reranker.rerank(
                documents=documents,
                query=query,
                top_n=5  # Return top 5 most relevant results
            )

            reranked_docs = []
            for item in reranked_results:
                idx = item.get('index')
                relevance_score = item.get('relevance_score')
                if idx is None or relevance_score is None:
                    continue
                doc = docs[idx]
                doc.metadata['relevance_score'] = relevance_score
                if relevance_score > 0.20:
                    reranked_docs.append(doc)

            return reranked_docs
        except Exception as e:
            logger.error(f"Error in document reranking: {str(e)}")
            return docs  # Return original docs if reranking fails

    def _prepare_context(self, docs, questions):
        context = "Relevant questions and answers:\n"
        for idx, question in enumerate(questions, 1):
            context += f"{question.page_content}\n\n"
        
        context += "Relevant documents:\n"
        for idx, doc in enumerate(docs, 1):
            context += f"{idx}. {doc.page_content}\n\n"
        
        return context