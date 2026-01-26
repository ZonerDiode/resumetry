from enum import Enum


class ApplicationStatus(str, Enum):
    """Status values for job applications."""
    APPLIED = 'applied'
    SCREEN = 'screen'
    INTERVIEW = 'interview'
    OFFER = 'offer'
    REJECTED = 'rejected'
    WITHDRAWN = 'withdrawn'
    GHOSTED = 'ghosted'
