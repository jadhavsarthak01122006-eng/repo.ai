from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class IssueStatusEnum(str, Enum):
    PENDING = "pending"
    TRIAGED = "triaged"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    VERIFIED = "verified"
    REJECTED = "rejected"

class UserRoleEnum(str, Enum):
    CITIZEN = "citizen"
    OFFICER = "officer"
    FIELD_WORKER = "field_worker"
    ADMIN = "admin"

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    role: UserRoleEnum = UserRoleEnum.CITIZEN

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    ward_id: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# Issue Report Schemas
class IssueReportBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    category: Optional[str] = None
    severity: int = Field(default=1, ge=1, le=5)

class IssueReportCreate(IssueReportBase):
    photo_url: Optional[str] = None

class IssueReportUpdate(BaseModel):
    status: Optional[IssueStatusEnum] = None
    assignee_id: Optional[int] = None
    category: Optional[str] = None
    severity: Optional[int] = Field(None, ge=1, le=5)
    photo_after_url: Optional[str] = None
    duplicate_of_id: Optional[int] = None

class AITriageResult(BaseModel):
    suggested_category: str
    suggested_department: str
    confidence: float = Field(ge=0, le=1)
    severity_estimate: int
    is_duplicate: bool = False
    duplicate_candidate_id: Optional[int] = None

class IssueReportResponse(IssueReportBase):
    id: int
    status: IssueStatusEnum
    priority_score: float
    ai_confidence: float
    ai_suggested_category: Optional[str]
    ai_suggested_department: Optional[str]
    reporter_id: int
    assignee_id: Optional[int]
    ward_id: Optional[int]
    photo_before_url: Optional[str]
    photo_after_url: Optional[str]
    duplicate_of_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class IssueReportList(BaseModel):
    reports: List[IssueReportResponse]
    total: int
    page: int
    pages: int

# Auth Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
    user_id: Optional[int] = None
    role: Optional[str] = None
