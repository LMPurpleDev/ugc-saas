from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import FileResponse
from typing import List, Optional
from app.models import Report, ReportCreate, User
from app.auth import get_current_active_user
from app.database import get_database
from bson import ObjectId
import logging
import os

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/reports", tags=["reports"])

@router.get("/", response_model=List[Report])
async def get_my_reports(
    current_user: User = Depends(get_current_active_user),
    limit: int = 10,
    skip: int = 0
):
    """Get current user's reports"""
    try:
        db = get_database()
        
        # Get user's profile
        # Comentário: current_user.id já é um ObjectId após a refatoração de PyObjectId.
        profile = db.profiles.find_one({"user_id": current_user.id})
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )
        
        profile_id = profile["_id"]
        
        # Get reports
        reports_cursor = db.reports.find(
            {"profile_id": profile_id}
        ).sort("created_at", -1).skip(skip).limit(limit)
        
        reports = []
        for report_data in reports_cursor:
            # Comentário: A instanciação de Report a partir de report_data funciona com Pydantic v2.
            reports.append(Report(**report_data))
        
        return reports
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting reports: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/{report_id}", response_model=Report)
async def get_report(
    report_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific report"""
    try:
        db = get_database()
        
        # Get user's profile
        # Comentário: current_user.id já é um ObjectId após a refatoração de PyObjectId.
        profile = db.profiles.find_one({"user_id": current_user.id})
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )
        
        profile_id = profile["_id"]
        
        # Get report
        report_data = db.reports.find_one({
            "_id": ObjectId(report_id),
            "profile_id": profile_id
        })
        
        if not report_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not found"
            )
        
        # Comentário: A instanciação de Report a partir de report_data funciona com Pydantic v2.
        return Report(**report_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting report: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/{report_id}/download")
async def download_report(
    report_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Download a report PDF"""
    try:
        db = get_database()
        
        # Get user's profile
        # Comentário: current_user.id já é um ObjectId após a refatoração de PyObjectId.
        profile = db.profiles.find_one({"user_id": current_user.id})
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )
        
        profile_id = profile["_id"]
        
        # Get report
        report_data = db.reports.find_one({
            "_id": ObjectId(report_id),
            "profile_id": profile_id
        })
        
        if not report_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not found"
            )
        
        if not report_data.get("is_ready") or not report_data.get("file_path"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Report is not ready for download"
            )
        
        file_path = report_data["file_path"]
        
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report file not found"
            )
        
        return FileResponse(
            path=file_path,
            filename=f"report_{report_id}.pdf",
            media_type="application/pdf"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading report: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/generate", response_model=dict)
async def generate_report(
    report_data: ReportCreate,
    current_user: User = Depends(get_current_active_user)
):
    """Request generation of a new report"""
    try:
        db = get_database()
        
        # Get user's profile
        # Comentário: current_user.id já é um ObjectId após a refatoração de PyObjectId.
        profile = db.profiles.find_one({"user_id": current_user.id})
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )
        
        profile_id = profile["_id"]
        
        # Create report record
        from app.models import ReportInDB
        # Comentário: Atualizado report_data.dict() para report_data.model_dump() para Pydantic v2.
        report = ReportInDB(
            **report_data.model_dump(),
            profile_id=profile_id
        )
        
        # Comentário: Atualizado report.dict(by_alias=True) para report.model_dump(by_alias=True) para Pydantic v2.
        result = db.reports.insert_one(report.model_dump(by_alias=True))
        
        if result.inserted_id:
            # TODO: Send task to worker to generate the report
            # This would be implemented in the worker phase
            return {
                "message": "Report generation requested",
                "report_id": str(result.inserted_id)
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create report"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


