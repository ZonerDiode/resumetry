from enum import Enum


class ApplicationStatus(str, Enum):
    """Status values for job applications."""
    APPLIED = 'APPLIED'
    SCREEN = 'SCREEN'
    INTERVIEW = 'INTERVIEW'
    OFFER = 'OFFER'
    REJECTED = 'REJECTED'
    WITHDRAWN = 'WITHDRAWN'
    GHOSTED = 'GHOSTED'