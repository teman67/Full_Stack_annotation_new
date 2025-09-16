from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
import asyncio

from app.core.database import get_db
from app.dependencies import get_current_user
from app.models import Annotation, Document, Project, Tag, User
from app.schemas import (
    AnnotationCreate, AnnotationUpdate, Annotation as AnnotationSchema,
    LLMAnnotationRequest, LLMAnnotationResponse, AnnotationJobStatus,
    ValidationRequest, ValidationResponse
)
from app.services.llm_service import annotation_service

router = APIRouter()

@router.get("/document/{document_id}", response_model=List[AnnotationSchema])
async def get_document_annotations(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all annotations for a document"""
    # Verify document access
    document = db.query(Document).join(Project).filter(
        Document.id == document_id,
        Project.owner_id == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    annotations = db.query(Annotation).filter(Annotation.document_id == document_id).all()
    return annotations

@router.post("/", response_model=AnnotationSchema)
async def create_annotation(
    annotation_data: AnnotationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new annotation"""
    # Verify document access
    document = db.query(Document).join(Project).filter(
        Document.id == annotation_data.document_id,
        Project.owner_id == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Verify tag exists
    tag = db.query(Tag).filter(Tag.id == annotation_data.tag_id).first()
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )
    
    # Validate annotation position
    if (annotation_data.start_pos < 0 or 
        annotation_data.end_pos > len(document.content) or
        annotation_data.start_pos >= annotation_data.end_pos):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid annotation position"
        )
    
    # Verify text matches
    expected_text = document.content[annotation_data.start_pos:annotation_data.end_pos]
    if expected_text != annotation_data.text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Annotation text doesn't match document position"
        )
    
    db_annotation = Annotation(
        document_id=annotation_data.document_id,
        user_id=current_user.id,
        tag_id=annotation_data.tag_id,
        text=annotation_data.text,
        start_pos=annotation_data.start_pos,
        end_pos=annotation_data.end_pos,
        confidence=annotation_data.confidence,
        source=annotation_data.source
    )
    
    db.add(db_annotation)
    db.commit()
    db.refresh(db_annotation)
    
    return db_annotation

@router.post("/llm-annotate", response_model=LLMAnnotationResponse)
async def run_llm_annotation(
    request: LLMAnnotationRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Run LLM annotation on a document"""
    # Verify document access
    document = db.query(Document).join(Project).filter(
        Document.id == request.document_id,
        Project.owner_id == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Get tag set
    from app.models import TagSet
    tag_set = db.query(TagSet).filter(TagSet.id == request.tag_set_id).first()
    if not tag_set:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag set not found"
        )
    
    # Generate task ID
    import uuid
    task_id = str(uuid.uuid4())
    
    # Start background task
    background_tasks.add_task(
        process_llm_annotation_task,
        task_id,
        document.id,
        document.content,
        tag_set.tags_json,
        request.provider,
        request.model,
        request.temperature,
        request.max_tokens,
        request.chunk_size,
        current_user.id,
        db
    )
    
    return LLMAnnotationResponse(
        task_id=task_id,
        status="started",
        message="LLM annotation task started"
    )

@router.get("/llm-job/{task_id}", response_model=AnnotationJobStatus)
async def get_llm_job_status(task_id: str):
    """Get status of LLM annotation job"""
    # TODO: Implement proper job tracking with Redis/Celery
    # For now, return a placeholder
    return AnnotationJobStatus(
        task_id=task_id,
        status="completed",
        progress=100,
        result=[],
        error=None
    )

@router.put("/{annotation_id}", response_model=AnnotationSchema)
async def update_annotation(
    annotation_id: int,
    annotation_data: AnnotationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an annotation"""
    annotation = db.query(Annotation).join(Document).join(Project).filter(
        Annotation.id == annotation_id,
        Project.owner_id == current_user.id
    ).first()
    
    if not annotation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Annotation not found"
        )
    
    # Update fields if provided
    if annotation_data.text is not None:
        annotation.text = annotation_data.text
    if annotation_data.start_pos is not None:
        annotation.start_pos = annotation_data.start_pos
    if annotation_data.end_pos is not None:
        annotation.end_pos = annotation_data.end_pos
    if annotation_data.tag_id is not None:
        annotation.tag_id = annotation_data.tag_id
    if annotation_data.confidence is not None:
        annotation.confidence = annotation_data.confidence
    
    db.commit()
    db.refresh(annotation)
    
    return annotation

@router.delete("/{annotation_id}")
async def delete_annotation(
    annotation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an annotation"""
    annotation = db.query(Annotation).join(Document).join(Project).filter(
        Annotation.id == annotation_id,
        Project.owner_id == current_user.id
    ).first()
    
    if not annotation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Annotation not found"
        )
    
    db.delete(annotation)
    db.commit()
    
    return {"message": "Annotation deleted successfully"}

@router.post("/validate", response_model=ValidationResponse)
async def validate_annotations(
    request: ValidationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Validate annotations"""
    # TODO: Implement annotation validation logic
    # This would use the enhanced_validation.py logic from your current app
    
    results = []
    for annotation_id in request.annotation_ids:
        # Placeholder validation result
        results.append({
            "annotation_id": annotation_id,
            "status": "valid",
            "error_message": None,
            "fixed_automatically": False,
            "suggestions": None
        })
    
    return ValidationResponse(
        results=results,
        summary={"valid": len(results), "invalid": 0, "fixed": 0}
    )

async def process_llm_annotation_task(
    task_id: str,
    document_id: int,
    text: str,
    tag_definitions: dict,
    provider: str,
    model: str,
    temperature: float,
    max_tokens: int,
    chunk_size: int,
    user_id: int,
    db: Session
):
    """Background task to process LLM annotations"""
    try:
        # Process annotations using the service
        annotations = await annotation_service.process_document_annotations(
            text=text,
            tag_definitions=tag_definitions,
            provider=provider,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            chunk_size=chunk_size
        )
        
        # Save annotations to database
        for ann_data in annotations:
            # Find matching tag
            tag = db.query(Tag).filter(Tag.name == ann_data['tag']).first()
            if tag:
                db_annotation = Annotation(
                    document_id=document_id,
                    user_id=user_id,
                    tag_id=tag.id,
                    text=ann_data['text'],
                    start_pos=ann_data['start'],
                    end_pos=ann_data['end'],
                    confidence=ann_data.get('confidence', 0.8),
                    source='llm'
                )
                db.add(db_annotation)
        
        db.commit()
        
        # TODO: Update job status in Redis/database
        
    except Exception as e:
        # TODO: Update job status with error
        print(f"LLM annotation task failed: {e}")
