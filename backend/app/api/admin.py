"""
Admin API endpoints for document management
"""

import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import List
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.responses import JSONResponse

from ..models import UploadResponse, DocumentInfo, User
from ..core.rag_engine import rag_engine
from ..config import get_settings
from .auth import get_current_user

router = APIRouter()
settings = get_settings()

@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Upload and index a new document"""
    try:
        # Validate file type
        allowed_extensions = {'.pdf', '.docx', '.doc', '.xlsx', '.xls'}
        file_ext = Path(file.filename).suffix.lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"File type {file_ext} not allowed. Allowed types: {allowed_extensions}"
            )
        
        # Save file
        upload_dir = settings.upload_dir
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, file.filename)
        
        # Check if file already exists
        if os.path.exists(file_path):
            raise HTTPException(
                status_code=400,
                detail=f"File '{file.filename}' already exists. Please rename or delete the existing file."
            )
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Add to RAG index
        success = rag_engine.add_document(file_path)
        
        if success:
            return UploadResponse(
                filename=file.filename,
                status="success",
                message=f"Document '{file.filename}' uploaded and indexed successfully",
                timestamp=datetime.now()
            )
        else:
            # Remove file if indexing failed
            os.remove(file_path)
            return UploadResponse(
                filename=file.filename,
                status="error",
                message=f"Failed to index document '{file.filename}'",
                timestamp=datetime.now()
            )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents", response_model=List[DocumentInfo])
async def list_documents(current_user: User = Depends(get_current_user)):
    """List all uploaded documents"""
    try:
        upload_dir = settings.upload_dir
        documents = []
        
        if os.path.exists(upload_dir):
            for file_path in Path(upload_dir).iterdir():
                if file_path.is_file():
                    stat = file_path.stat()
                    documents.append(DocumentInfo(
                        filename=file_path.name,
                        type=file_path.suffix,
                        size=stat.st_size,
                        upload_date=datetime.fromtimestamp(stat.st_ctime),
                        indexed=True
                    ))
        
        # Sort by upload date (newest first)
        documents.sort(key=lambda x: x.upload_date, reverse=True)
        
        return documents
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/documents/{filename}")
async def delete_document(
    filename: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a document from filesystem and index"""
    try:
        file_path = os.path.join(settings.upload_dir, filename)
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Delete from filesystem
        os.remove(file_path)
        
        # Delete from vector store (note: this is simplified)
        # In production, you'd want to track document IDs properly
        rag_engine.delete_document(filename)
        
        return {"message": f"Document '{filename}' deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/rebuild-index")
async def rebuild_index(current_user: User = Depends(get_current_user)):
    """Rebuild the entire RAG index from uploaded documents"""
    try:
        success = rag_engine.rebuild_index_from_uploads()
        
        if success:
            return {
                "message": "Index rebuilt successfully",
                "status": "success"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to rebuild index")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_system_stats(current_user: User = Depends(get_current_user)):
    """Get system statistics"""
    try:
        stats = rag_engine.get_index_stats()
        
        # Add upload directory stats
        upload_dir = settings.upload_dir
        if os.path.exists(upload_dir):
            file_count = len(list(Path(upload_dir).iterdir()))
            stats['uploaded_files'] = file_count
        else:
            stats['uploaded_files'] = 0
        
        return stats
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/backup")
async def create_backup(current_user: User = Depends(get_current_user)):
    """Create a backup of the vector store"""
    try:
        backup_path = f"{settings.vector_db_dir}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        success = rag_engine.vector_store_manager.backup_vector_store(backup_path)
        
        if success:
            return {
                "message": "Backup created successfully",
                "backup_path": backup_path
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to create backup")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))