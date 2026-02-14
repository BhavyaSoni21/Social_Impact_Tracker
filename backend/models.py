"""
Data Models for Social Impact Tracker
Defines Pydantic models for API validation and SQLAlchemy models for database
"""

from pydantic import BaseModel, Field, validator
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from typing import Optional

Base = declarative_base()


# SQLAlchemy Database Models
class ProgramDB(Base):
    """Database model for storing program data"""
    __tablename__ = "programs"

    id = Column(Integer, primary_key=True, index=True)
    program_name = Column(String, nullable=False, index=True)
    time_period = Column(String, nullable=False)
    beneficiaries = Column(Integer, nullable=False)
    cost = Column(Float, nullable=False)
    pre_outcome_score = Column(Float, nullable=False)
    post_outcome_score = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Compressed data fields
    compressed_name = Column(String, nullable=True)
    delta_beneficiaries = Column(Integer, nullable=True)


# Pydantic Models for API
class ProgramBase(BaseModel):
    """Base model for program data validation"""
    program_name: str = Field(..., min_length=1, max_length=200, description="Name of the program")
    time_period: str = Field(..., min_length=1, description="Time period of program operation")
    beneficiaries: int = Field(..., gt=0, description="Number of beneficiaries served")
    cost: float = Field(..., gt=0, description="Total cost incurred")
    pre_outcome_score: float = Field(..., ge=0, le=100, description="Pre-intervention outcome score")
    post_outcome_score: float = Field(..., ge=0, le=100, description="Post-intervention outcome score")

    @validator('post_outcome_score')
    def validate_outcome_scores(cls, v, values):
        """Ensure post-outcome is not less than pre-outcome when improvement is expected"""
        if 'pre_outcome_score' in values:
            pre_score = values['pre_outcome_score']
            # Allow flexibility but warn if post is significantly lower
            if v < pre_score - 10:
                raise ValueError(f"Post-outcome score ({v}) is significantly lower than pre-outcome score ({pre_score})")
        return v

    class Config:
        schema_extra = {
            "example": {
                "program_name": "Youth Education Initiative",
                "time_period": "2025-Q1",
                "beneficiaries": 150,
                "cost": 25000.00,
                "pre_outcome_score": 45.5,
                "post_outcome_score": 72.3
            }
        }


class ProgramCreate(ProgramBase):
    """Model for creating a new program"""
    pass


class ProgramResponse(ProgramBase):
    """Model for program response with ID"""
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


class ImpactMetrics(BaseModel):
    """Model for computed impact metrics"""
    program_id: int
    program_name: str
    outcome_improvement: float = Field(..., description="Difference between post and pre outcome scores")
    cost_per_beneficiary: float = Field(..., description="Cost divided by number of beneficiaries")
    growth_rate: Optional[float] = Field(None, description="Beneficiary growth rate compared to previous period")
    composite_impact_score: float = Field(..., description="Weighted composite score")

    class Config:
        schema_extra = {
            "example": {
                "program_id": 1,
                "program_name": "Youth Education Initiative",
                "outcome_improvement": 26.8,
                "cost_per_beneficiary": 166.67,
                "growth_rate": 0.15,
                "composite_impact_score": 78.5
            }
        }


class AnalyticsSummary(BaseModel):
    """Model for dashboard analytics summary"""
    total_programs: int
    total_beneficiaries: int
    average_impact_score: float
    total_cost: float
    average_outcome_improvement: float


class ProgramTrend(BaseModel):
    """Model for program trend data"""
    time_period: str
    beneficiaries: int
    cost: float
    outcome_improvement: float
