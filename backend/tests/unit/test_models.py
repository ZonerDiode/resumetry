"""Tests for Pydantic job application models."""
import pytest
from datetime import date
from pydantic import ValidationError

from app.models.enums import ApplicationStatus
from app.models.job_application import (
    ApplicationNote,
    JobApplicationCreate,
    JobApplicationUpdate,
    JobApplicationResponse,
)


class TestApplicationNote:

    def test_valid_note(self):
        note = ApplicationNote(occur_date=date(2025, 6, 1), description='Phone screen')
        assert note.occur_date == date(2025, 6, 1)
        assert note.description == 'Phone screen'

    def test_empty_description_rejected(self):
        with pytest.raises(ValidationError):
            ApplicationNote(occur_date=date.today(), description='')

    def test_missing_description_rejected(self):
        with pytest.raises(ValidationError):
            ApplicationNote(occur_date=date.today())

    def test_missing_occur_date_rejected(self):
        with pytest.raises(ValidationError):
            ApplicationNote(description='note text')

    def test_camel_case_alias(self):
        note = ApplicationNote(**{'occurDate': '2025-06-01', 'description': 'test'})
        assert note.occur_date == date(2025, 6, 1)

    def test_whitespace_stripped(self):
        note = ApplicationNote(occur_date=date.today(), description='  trimmed  ')
        assert note.description == 'trimmed'


class TestJobApplicationCreate:

    def test_minimal_valid_payload(self):
        app = JobApplicationCreate(
            company='Acme', role='Dev', interest_level=2
        )
        assert app.company == 'Acme'
        assert app.role == 'Dev'
        assert app.interest_level == 2

    def test_defaults_applied(self):
        app = JobApplicationCreate(
            company='Acme', role='Dev', interest_level=1
        )
        assert app.applied_date == date.today()
        assert app.status_date == date.today()
        assert app.status == ApplicationStatus.APPLIED
        assert app.description == ''
        assert app.salary == ''
        assert app.source_page == ''
        assert app.review_page == ''
        assert app.login_hints == ''
        assert app.notes == []

    def test_company_min_length(self):
        with pytest.raises(ValidationError):
            JobApplicationCreate(company='', role='Dev', interest_level=1)

    def test_company_max_length(self):
        with pytest.raises(ValidationError):
            JobApplicationCreate(
                company='A' * 256, role='Dev', interest_level=1
            )

    def test_role_min_length(self):
        with pytest.raises(ValidationError):
            JobApplicationCreate(company='Acme', role='', interest_level=1)

    def test_role_max_length(self):
        with pytest.raises(ValidationError):
            JobApplicationCreate(
                company='Acme', role='R' * 256, interest_level=1
            )

    def test_salary_max_length(self):
        with pytest.raises(ValidationError):
            JobApplicationCreate(
                company='Acme', role='Dev', interest_level=1,
                salary='$' * 101
            )

    def test_interest_level_too_low(self):
        with pytest.raises(ValidationError):
            JobApplicationCreate(
                company='Acme', role='Dev', interest_level=0
            )

    def test_interest_level_too_high(self):
        with pytest.raises(ValidationError):
            JobApplicationCreate(
                company='Acme', role='Dev', interest_level=4
            )

    def test_interest_level_boundaries(self):
        app1 = JobApplicationCreate(company='A', role='B', interest_level=1)
        app3 = JobApplicationCreate(company='A', role='B', interest_level=3)
        assert app1.interest_level == 1
        assert app3.interest_level == 3

    def test_valid_status_enum(self):
        for status in ApplicationStatus:
            app = JobApplicationCreate(
                company='Acme', role='Dev', interest_level=2, status=status
            )
            assert app.status == status

    def test_invalid_status_rejected(self):
        with pytest.raises(ValidationError):
            JobApplicationCreate(
                company='Acme', role='Dev', interest_level=2,
                status='not_a_status'
            )

    def test_notes_with_entries(self):
        app = JobApplicationCreate(
            company='Acme', role='Dev', interest_level=2,
            notes=[
                ApplicationNote(occur_date=date.today(), description='Applied'),
                ApplicationNote(occur_date=date.today(), description='Follow up'),
            ],
        )
        assert len(app.notes) == 2

    def test_camel_case_input(self):
        app = JobApplicationCreate(**{
            'company': 'Acme',
            'role': 'Dev',
            'interestLevel': 3,
            'appliedDate': '2025-01-15',
            'statusDate': '2025-01-15',
            'sourcePage': 'https://example.com',
        })
        assert app.interest_level == 3
        assert app.applied_date == date(2025, 1, 15)
        assert app.source_page == 'https://example.com'


class TestJobApplicationUpdate:

    def test_all_fields_optional(self):
        update = JobApplicationUpdate()
        dumped = update.model_dump(exclude_unset=True)
        assert dumped == {}

    def test_single_field_update(self):
        update = JobApplicationUpdate(company='NewCo')
        dumped = update.model_dump(exclude_unset=True)
        assert dumped == {'company': 'NewCo'}

    def test_multiple_field_update(self):
        update = JobApplicationUpdate(
            company='NewCo', interest_level=3, status=ApplicationStatus.OFFER
        )
        dumped = update.model_dump(exclude_unset=True)
        assert 'company' in dumped
        assert 'interest_level' in dumped
        assert 'status' in dumped

    def test_validation_still_applies_company(self):
        with pytest.raises(ValidationError):
            JobApplicationUpdate(company='')

    def test_validation_still_applies_interest_level(self):
        with pytest.raises(ValidationError):
            JobApplicationUpdate(interest_level=5)

    def test_notes_update(self):
        update = JobApplicationUpdate(
            notes=[ApplicationNote(occur_date=date.today(), description='New note')]
        )
        dumped = update.model_dump(exclude_unset=True)
        assert len(dumped['notes']) == 1


class TestJobApplicationResponse:

    def test_requires_id(self):
        with pytest.raises(ValidationError):
            JobApplicationResponse(
                company='Acme', role='Dev', interest_level=2,
                applied_date=date.today(), status_date=date.today(),
            )

    def test_full_response(self):
        resp = JobApplicationResponse(
            id='abc-123',
            company='Acme',
            role='Dev',
            interest_level=2,
            applied_date=date.today(),
            status_date=date.today(),
        )
        assert resp.id == 'abc-123'
        assert resp.company == 'Acme'
        assert resp.notes == []
