from fastapi import APIRouter, HTTPException
from ..models import QueryRequest, QueryResponse, Source
from ..core.rag_engine import rag_engine

router = APIRouter()

@router.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """Query the RAG system"""
    try:
        answer, sources, processing_time = rag_engine.query(request.question)
        
        return QueryResponse(
            answer=answer,
            sources=[Source(**s) for s in sources],
            processing_time=processing_time
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))