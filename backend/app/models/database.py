from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Enum, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import enum
from datetime import datetime

Base = declarative_base()

class IssueStatus(enum.Enum):
    PENDING = "pending"
    TRIAGED = "triaged"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    VERIFIED = "verified"
    REJECTED = "rejected"

class UserRole(enum.Enum):
    CITIZEN = "citizen"
    OFFICER = "officer"
    FIELD_WORKER = "field_worker"
    ADMIN = "admin"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    role = Column(Enum(UserRole), default=UserRole.CITIZEN)
    ward_id = Column(Integer, nullable=True)  # For officers/workers
    created_at = Column(DateTime, default=datetime.utcnow)
    
    reports = relationship("IssueReport", back_populates="reporter", foreign_keys="IssueReport.reporter_id")
    assigned_issues = relationship("IssueReport", back_populates="assignee")

class IssueReport(Base):
    __tablename__ = "issue_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    category = Column(String)  # e.g., "pothole", "garbage", "streetlight"
    severity = Column(Integer, default=1)  # 1-5 scale
    priority_score = Column(Float, default=0.0)
    status = Column(Enum(IssueStatus), default=IssueStatus.PENDING)
    ai_confidence = Column(Float, default=0.0)
    ai_suggested_category = Column(String)
    ai_suggested_department = Column(String)
    
    reporter_id = Column(Integer, ForeignKey("users.id"))
    assignee_id = Column(Integer, ForeignKey("users.id"))
    ward_id = Column(Integer)
    
    photo_before_url = Column(String)
    photo_after_url = Column(String)
    
    duplicate_of_id = Column(Integer, ForeignKey("issue_reports.id"), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
    
    reporter = relationship("User", back_populates="reports", foreign_keys=[reporter_id])
    assignee = relationship("User", back_populates="assigned_issues", foreign_keys=[assignee_id])
    duplicates = relationship("IssueReport", remote_side=[duplicate_of_id])

class Ward(Base):
    __tablename__ = "wards"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    population = Column(Integer)
