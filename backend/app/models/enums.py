from enum import Enum


class ApplicationStatus(str, Enum):
    """Status values for job applications."""
    APPLIED = 'APPLIED'
    REJECTED = 'REJECTED'
    SCREEN = 'SCREEN'
    INTERVIEW = 'INTERVIEW'
    OFFER = 'OFFER'
    WITHDRAWN = 'WITHDRAWN'
    NOOFFER = 'NOOFFER'