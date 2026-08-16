from sqlalchemy.orm import Session
from sqlalchemy import func, text
from datetime import datetime
from typing import List, Optional
from app.models.database import IssueReport, IssueStatus, User
from app.schemas.schemas import IssueReportCreate, IssueReportUpdate
from app.services.ai_service import triage_issue_with_ai, check_for_duplicates

def calculate_priority_score(severity: int, latitude: float, longitude: float, 
                             created_at: datetime, ward_id: Optional[int] = None) -> float:
    """
    Calculate priority score based on:
    - Severity (1-5)
    - Location criticality (near schools, hospitals, etc.)
    - Age of complaint (older = higher priority)
    
    Returns a score from 0-100
    """
    # Base score from severity (max 50 points)
    severity_score = severity * 10
    
    # Location criticality (max 30 points) - simplified for MVP
    # In production, check against known critical locations
    location_score = 15  # Default moderate score
    
    # Age score (max 20 points) - increases with time
    age_hours = (datetime.utcnow() - created_at).total_seconds() / 3600
    age_score = min(20, age_hours / 2)  # Max out after 40 hours
    
    return min(100, severity_score + location_score + age_score)

async def create_issue_report(db: Session, report: IssueReportCreate, reporter_id: int) -> IssueReport:
    """
    Create a new issue report with AI triage and duplicate detection.
    """
    # Check for duplicates first
    duplicate_id = await check_for_duplicates(
        db, report.latitude, report.longitude,
        report.title, report.description or ""
    )
    
    # Run AI triage
    ai_result = await triage_issue_with_ai(
        report.title,
        report.description or "",
        report.photo_url
    )
    
    # Create the report
    db_report = IssueReport(
        title=report.title,
        description=report.description,
        latitude=report.latitude,
        longitude=report.longitude,
        location=f"POINT({report.longitude} {report.latitude})",
        category=ai_result["suggested_category"],
        severity=ai_result["severity_estimate"],
        status=IssueStatus.PENDING if ai_result["confidence"] < 0.5 else IssueStatus.TRIAGED,
        ai_confidence=ai_result["confidence"],
        ai_suggested_category=ai_result["suggested_category"],
        ai_suggested_department=ai_result["suggested_department"],
        reporter_id=reporter_id,
        photo_before_url=report.photo_url,
        duplicate_of_id=duplicate_id
    )
    
    # Calculate initial priority score
    db_report.priority_score = calculate_priority_score(
        db_report.severity,
        db_report.latitude,
        db_report.longitude,
        db_report.created_at
    )
    
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    
    return db_report

def get_issue_reports(db: Session, skip: int = 0, limit: int = 20, 
                      status_filter: Optional[IssueStatus] = None,
                      ward_id: Optional[int] = None) -> tuple[List[IssueReport], int]:
    """
    Get paginated list of issue reports with optional filters.
    """
    query = db.query(IssueReport)
    
    if status_filter:
        query = query.filter(IssueReport.status == status_filter)
    
    if ward_id is not None:
        query = query.filter(IssueReport.ward_id == ward_id)
    
    total = query.count()
    reports = query.order_by(IssueReport.priority_score.desc(), IssueReport.created_at.desc())\
                   .offset(skip).limit(limit).all()
    
    return reports, total

def get_issue_report_by_id(db: Session, report_id: int) -> Optional[IssueReport]:
    """Get a single issue report by ID."""
    return db.query(IssueReport).filter(IssueReport.id == report_id).first()

def update_issue_report(db: Session, report_id: int, update: IssueReportUpdate, 
                        user: User) -> Optional[IssueReport]:
    """
    Update an issue report with RBAC checks.
    """
    db_report = get_issue_report_by_id(db, report_id)
    if not db_report:
        return None
    
    # RBAC: Only officers can assign, only field workers can mark resolved
    if update.assignee_id is not None and user.role not in ["officer", "admin"]:
        raise Exception("Only officers can assign issues")
    
    if update.photo_after_url is not None and user.role not in ["field_worker", "officer", "admin"]:
        raise Exception("Only field workers can upload resolution photos")
    
    # Update fields
    update_data = update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_report, field, value)
    
    # Auto-update status based on actions
    if update.photo_after_url and not db_report.resolved_at:
        db_report.status = IssueStatus.RESOLVED
        db_report.resolved_at = datetime.utcnow()
    
    if update.status == IssueStatus.ASSIGNED and not db_report.assignee_id:
        raise Exception("Assignee must be provided when assigning")
    
    # Recalculate priority score
    db_report.priority_score = calculate_priority_score(
        db_report.severity,
        db_report.latitude,
        db_report.longitude,
        db_report.created_at
    )
    
    db.commit()
    db.refresh(db_report)
    return db_report

def merge_duplicates(db: Session, primary_id: int, duplicate_id: int, 
                     officer: User) -> Optional[IssueReport]:
    """
    Merge a duplicate report into the primary report.
    Only officers can perform this action.
    """
    if officer.role not in ["officer", "admin"]:
        raise Exception("Only officers can merge duplicates")
    
    primary = get_issue_report_by_id(db, primary_id)
    duplicate = get_issue_report_by_id(db, duplicate_id)
    
    if not primary or not duplicate:
        return None
    
    if duplicate.duplicate_of_id:
        raise Exception("This report is already marked as a duplicate")
    
    duplicate.duplicate_of_id = primary_id
    duplicate.status = IssueStatus.REJECTED  # Or keep as pending but linked
    
    db.commit()
    db.refresh(primary)
    return primary

def get_dashboard_stats(db: Session, ward_id: Optional[int] = None) -> dict:
    """
    Get dashboard statistics for officers/admins.
    """
    query = db.query(IssueReport)
    if ward_id:
        query = query.filter(IssueReport.ward_id == ward_id)
    
    total = query.count()
    pending = query.filter(IssueReport.status == IssueStatus.PENDING).count()
    in_progress = query.filter(IssueReport.status == IssueStatus.IN_PROGRESS).count()
    resolved = query.filter(IssueReport.status == IssueStatus.RESOLVED).count()
    verified = query.filter(IssueReport.status == IssueStatus.VERIFIED).count()
    
    # Average resolution time (for resolved issues)
    avg_resolution = db.query(
        func.avg(IssueReport.resolved_at - IssueReport.created_at)
    ).filter(IssueReport.status == IssueStatus.RESOLVED).scalar()
    
    return {
        "total_reports": total,
        "pending": pending,
        "in_progress": in_progress,
        "resolved": resolved,
        "verified": verified,
        "avg_resolution_hours": float(avg_resolution.total_seconds() / 3600) if avg_resolution else 0
    }
