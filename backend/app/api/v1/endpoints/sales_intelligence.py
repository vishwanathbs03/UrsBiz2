from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from typing import Any

from app.middleware.auth_deps import get_current_user
from app.models.user import User
from app.utils.database import get_db
from app.services.sales_intelligence import SalesIntelligenceService
from app.schemas.sales_intelligence import SalesIntelligenceResponse

router = APIRouter(prefix="/sales-intelligence", tags=["sales-intelligence"])

@router.post(
    "/analyze",
    response_model=SalesIntelligenceResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze uploaded sales data for patterns and forecasts"
)
async def analyze_sales_data(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> SalesIntelligenceResponse:
    # Validate file extension
    ext = file.filename.lower()
    if not (ext.endswith('.csv') or ext.endswith('.xlsx') or ext.endswith('.xls')):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only CSV and Excel files are supported."
        )

    # Limit file size (10 MB)
    MAX_SIZE = 10 * 1024 * 1024
    content = await file.read()
    if len(content) > MAX_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File size exceeds 10 MB limit."
        )

    try:
        service = SalesIntelligenceService()
        return service.analyze(content, file.filename)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        # Log error here in production
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during analysis: {str(e)}"
        )
