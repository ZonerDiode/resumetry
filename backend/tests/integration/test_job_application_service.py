"""Tests for job_application_service against mocked DynamoDB."""
from datetime import date

from app.models.enums import ApplicationStatus
from app.models.job_application import (
    ApplicationNote,
    JobApplicationCreate,
    JobApplicationUpdate,
)
from app.services import job_application_service as svc


class TestCreateApplication:

    def test_returns_response_with_generated_id(self, dynamodb_mock):
        data = JobApplicationCreate(
            company='Acme', role='Dev', interest_level=2
        )
        result = svc.create_application(data)
        assert result.id is not None
        assert len(result.id) == 36  # UUID format

    def test_returned_fields_match_input(self, dynamodb_mock):
        data = JobApplicationCreate(
            company='Acme', role='Dev', interest_level=3,
            status=ApplicationStatus.SCREEN,
        )
        result = svc.create_application(data)
        assert result.company == 'Acme'
        assert result.role == 'Dev'
        assert result.interest_level == 3
        assert result.status == ApplicationStatus.SCREEN

    def test_defaults_applied(self, dynamodb_mock):
        data = JobApplicationCreate(
            company='Acme', role='Dev', interest_level=1
        )
        result = svc.create_application(data)
        assert result.applied_date == date.today()
        assert result.status == ApplicationStatus.APPLIED
        assert result.notes == []

    def test_with_notes(self, dynamodb_mock):
        data = JobApplicationCreate(
            company='Acme', role='Dev', interest_level=2,
            notes=[ApplicationNote(occur_date=date.today(), description='Applied')],
        )
        result = svc.create_application(data)
        assert len(result.notes) == 1
        assert result.notes[0].description == 'Applied'


class TestGetApplication:

    def test_get_existing(self, dynamodb_mock):
        created = svc.create_application(
            JobApplicationCreate(company='Acme', role='Dev', interest_level=2)
        )
        fetched = svc.get_application(created.id)
        assert fetched is not None
        assert fetched.id == created.id
        assert fetched.company == 'Acme'

    def test_get_nonexistent_returns_none(self, dynamodb_mock):
        result = svc.get_application('nonexistent-id')
        assert result is None


class TestListApplications:

    def test_empty_table(self, dynamodb_mock):
        result = svc.list_applications()
        assert result == []

    def test_multiple_applications(self, dynamodb_mock):
        for i in range(3):
            svc.create_application(
                JobApplicationCreate(
                    company=f'Company{i}', role='Dev', interest_level=1
                )
            )
        result = svc.list_applications()
        assert len(result) == 3

    def test_returns_all_fields(self, dynamodb_mock):
        svc.create_application(
            JobApplicationCreate(
                company='Acme', role='Dev', interest_level=2,
                description='Test role',
            )
        )
        result = svc.list_applications()
        assert result[0].company == 'Acme'
        assert result[0].description == 'Test role'


class TestUpdateApplication:

    def test_update_single_field(self, dynamodb_mock):
        created = svc.create_application(
            JobApplicationCreate(company='Acme', role='Dev', interest_level=2)
        )
        updated = svc.update_application(
            created.id, JobApplicationUpdate(company='NewCo')
        )
        assert updated is not None
        assert updated.company == 'NewCo'
        assert updated.role == 'Dev'

    def test_update_status(self, dynamodb_mock):
        created = svc.create_application(
            JobApplicationCreate(company='Acme', role='Dev', interest_level=2)
        )
        updated = svc.update_application(
            created.id,
            JobApplicationUpdate(status=ApplicationStatus.INTERVIEW),
        )
        assert updated is not None
        assert updated.status == ApplicationStatus.INTERVIEW

    def test_update_nonexistent_returns_none(self, dynamodb_mock):
        result = svc.update_application(
            'nonexistent-id', JobApplicationUpdate(company='NewCo')
        )
        assert result is None

    def test_empty_update_returns_current(self, dynamodb_mock):
        created = svc.create_application(
            JobApplicationCreate(company='Acme', role='Dev', interest_level=2)
        )
        result = svc.update_application(created.id, JobApplicationUpdate())
        assert result is not None
        assert result.company == 'Acme'


class TestDeleteApplication:

    def test_delete_existing_returns_true(self, dynamodb_mock):
        created = svc.create_application(
            JobApplicationCreate(company='Acme', role='Dev', interest_level=2)
        )
        assert svc.delete_application(created.id) is True

    def test_delete_nonexistent_returns_false(self, dynamodb_mock):
        assert svc.delete_application('nonexistent-id') is False

    def test_deleted_item_not_retrievable(self, dynamodb_mock):
        created = svc.create_application(
            JobApplicationCreate(company='Acme', role='Dev', interest_level=2)
        )
        svc.delete_application(created.id)
        assert svc.get_application(created.id) is None
