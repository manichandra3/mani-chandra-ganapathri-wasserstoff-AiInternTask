from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import os
import aiofiles
from datetime import datetime

from ..db.database import get_db
from ..services.document_processor import DocumentProcessor
from ..core.config import settings

router = APIRouter()

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload and process a document."""
    # Validate file type
    allowed_types = ['pdf', 'jpg', 'jpeg', 'png', 'txt']
    file_type = file.filename.split('.')[-1].lower()
    if file_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types: {', '.join(allowed_types)}"
        )
    
    # Create unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{file.filename}"
    file_path = settings.UPLOAD_DIR / filename
    
    # Save uploaded file
    try:
        async with aiofiles.open(file_path, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error saving file: {str(e)}"
        )
    
    # Process document
    try:
        processor = DocumentProcessor(db)
        document = await processor.process_document(str(file_path), filename)
        return {
            "message": "Document processed successfully",
            "document_id": document.id,
            "filename": document.filename
        }
    except Exception as e:
        # Clean up file if processing fails
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing document: {str(e)}"
        )

@router.get("/documents")
async def list_documents(db: Session = Depends(get_db)):
    """List all processed documents."""
    from ..db.models import Document
    documents = db.query(Document).all()
    return [
        {
            "id": doc.id,
            "filename": doc.filename,
            "file_type": doc.file_type,
            "created_at": doc.created_at.isoformat()
        }
        for doc in documents
    ]

@router.get("/documents/{document_id}")
async def get_document(document_id: int, db: Session = Depends(get_db)):
    """Get document details and content."""
    from ..db.models import Document
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return {
        "id": document.id,
        "filename": document.filename,
        "file_type": document.file_type,
        "created_at": document.created_at.isoformat(),
        "pages": [
            {
                "page_number": page.page_number,
                "content": page.content,
                "paragraphs": [
                    {
                        "paragraph_number": p.paragraph_number,
                        "content": p.content
                    }
                    for p in page.paragraphs
                ]
            }
            for page in document.pages
        ]
    } 