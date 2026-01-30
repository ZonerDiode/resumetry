from datetime import date
from typing import Optional

from pydantic import Field

from .base import BaseSchema
from .enums import ApplicationStatus


class ApplicationNote(BaseSchema):
    """A note entry associated with a job application."""
    occur_date: date
    description: str = Field(..., min_length=1)


class StatusItem(BaseSchema):
    """A status change entry associated with a job application."""
    occur_date: date
    status: ApplicationStatus


class JobApplicationBase(BaseSchema):
    """Base schema with common job application fields."""
    company: str = Field(..., min_length=1, max_length=255)
    role: str = Field(..., min_length=1, max_length=255)
    description: str = Field(default='')
    salary: str = Field(default='', max_length=100)
    top_job: bool = Field(default=False)
    source_page: str = Field(default='')
    review_page: str = Field(default='')
    login_hints: str = Field(default='')
    recruiter_name: str = Field(default='', max_length=255)
    recruiter_company: str = Field(default='', max_length=255)


class JobApplicationCreate(JobApplicationBase):
    """Schema for creating a new job application."""
    applied_date: date = Field(default_factory=date.today)
    status: list[StatusItem] = Field(default_factory=lambda: [])
    notes: list[ApplicationNote] = Field(default_factory=lambda: [])


class JobApplicationUpdate(BaseSchema):
    """Schema for partial updates. All fields optional."""
    company: Optional[str] = Field(None, min_length=1, max_length=255)
    role: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    salary: Optional[str] = Field(None, max_length=100)
    top_job: Optional[bool] = None
    source_page: Optional[str] = None
    review_page: Optional[str] = None
    login_hints: Optional[str] = None
    recruiter_name: Optional[str] = Field(None, max_length=255)
    recruiter_company: Optional[str] = Field(None, max_length=255)
    status: Optional[list[StatusItem]] = None
    notes: Optional[list[ApplicationNote]] = None


class JobApplicationResponse(JobApplicationBase):
    """Schema for API responses."""
    id: str
    applied_date: date
    status: list[StatusItem] = Field(default_factory=lambda: [])
    notes: list[ApplicationNote] = Field(default_factory=lambda: [])

