import os
import shutil

from fastapi import APIRouter, UploadFile, File, Form
from app.services.vector_store_service import search_similar_chunks
from app.services.vector_store_service import retrieve_relevant_chunks
from app.services.rag_service import generate_rag_response
from app.agents.document_agents import run_agent_workflow

router = APIRouter()

UPLOAD_DIR = "data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.get("/Health-check")
def health_check():
    return {
        "status": "success",
        "message": "API is up and running"
    }


@router.post("/Upload-Document")
async def upload_document(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    from app.services.document_processor import process_document

    processed_result = process_document(file_path)

    return {
        "status": "success",
        "message": "Document uploaded and processed successfully",
        "upload_details": {
            "filename": file.filename,
            "content_type": file.content_type,
            "file_path": file_path
        },
        "processing_details": processed_result
    }


@router.post("/ask-questions")
async def ask_questions(question: str = Form(...)):
    return {
        "status": "success",
        "question": question,
        "answer": "Placeholder response. LLM integration will be added in the next task."
    }

@router.get("/search")
def search_documents(query: str):
    results = search_similar_chunks(query)

    return {
        "status": "success",
        "query": query,
        "results": results
    }

@router.get("/retrieve")
def retrieve_documents(query: str, top_k: int = 3):
    return retrieve_relevant_chunks(query, top_k)

@router.get("/rag-answer")
def rag_answer(question: str, top_k: int = 3):
    return generate_rag_response(question, top_k)

@router.get("/agent-answer")
def agent_answer(question: str, top_k: int = 3):
    return run_agent_workflow(question, top_k)