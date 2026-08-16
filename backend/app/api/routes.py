from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.core.security import (
    get_current_user, 
    get_current_officer_or_admin,
    get_current_field_worker_or_officer
)
from app.models.database import User, IssueStatus
from app.schemas.schemas import (
    UserCreate, 
    UserResponse, 
    IssueReportCreate, 
    IssueReportResponse, 
    IssueReportUpdate,
    IssueReportList,
    Token,
    AITriageResult
)
from app.services import issue_service
from datetime import timedelta
from app.core.security import authenticate_user, create_access_token, get_password_hash

router = APIRouter()

# Auth endpoints
@router.post("/auth/register", response_model=UserResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    db_user = User(
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        hashed_password=get_password_hash(user.password)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post("/auth/login", response_model=Token)
async def login(email: str, password: str, db: Session = Depends(get_db)):
    user = authenticate_user(db, email, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.id, "role": user.role.value},
        expires_delta=timedelta(minutes=30)
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/auth/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user

# Issue report endpoints
@router.post("/reports", response_model=IssueReportResponse)
async def create_report(
    report: IssueReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Citizens can create new issue reports."""
    return await issue_service.create_issue_report(db, report, current_user.id)

@router.get("/reports", response_model=IssueReportList)
async def list_reports(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status_filter: Optional[IssueStatus] = None,
    ward_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List issue reports with pagination and filters."""
    reports, total = issue_service.get_issue_reports(
        db, skip=skip, limit=limit, 
        status_filter=status_filter, 
        ward_id=ward_id
    )
    
    pages = (total + limit - 1) // limit
    
    return {
        "reports": reports,
        "total": total,
        "page": (skip // limit) + 1,
        "pages": pages
    }

@router.get("/reports/{report_id}", response_model=IssueReportResponse)
async def get_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific issue report by ID."""
    report = issue_service.get_issue_report_by_id(db, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report

@router.put("/reports/{report_id}", response_model=IssueReportResponse)
async def update_report(
    report_id: int,
    update: IssueReportUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_field_worker_or_officer)
):
    """Update an issue report (assign, change status, upload photos)."""
    try:
        report = issue_service.update_issue_report(db, report_id, update, current_user)
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        return report
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/reports/{primary_id}/merge/{duplicate_id}", response_model=IssueReportResponse)
async def merge_duplicate_reports(
    primary_id: int,
    duplicate_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_officer_or_admin)
):
    """Merge a duplicate report into the primary report."""
    try:
        report = issue_service.merge_duplicates(db, primary_id, duplicate_id, current_user)
        if not report:
            raise HTTPException(status_code=404, detail="Reports not found")
        return report
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/dashboard/stats")
async def get_dashboard_statistics(
    ward_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_officer_or_admin)
):
    """Get dashboard statistics for officers/admins."""
    return issue_service.get_dashboard_stats(db, ward_id)

@router.get("/reports/ai/triage/{report_id}", response_model=AITriageResult)
async def get_ai_triage_suggestion(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_officer_or_admin)
):
    """Get AI triage suggestion for a report (for manual review queue)."""
    report = issue_service.get_issue_report_by_id(db, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Return existing AI analysis
    return AITriageResult(
        suggested_category=report.ai_suggested_category or "general",
        suggested_department=report.ai_suggested_department or "Public Works",
        confidence=report.ai_confidence,
        severity_estimate=report.severity,
        is_duplicate=report.duplicate_of_id is not None,
        duplicate_candidate_id=report.duplicate_of_id
    )
