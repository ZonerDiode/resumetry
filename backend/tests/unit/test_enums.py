"""Tests for ApplicationStatus enum."""
import pytest

from app.models.enums import ApplicationStatus


class TestApplicationStatus:

    def test_all_expected_values_exist(self):
        expected = {'applied', 'screen', 'interview', 'offer',
                    'rejected', 'withdrawn', 'ghosted'}
        actual = {s.value for s in ApplicationStatus}
        assert actual == expected

    def test_enum_is_str_subclass(self):
        assert isinstance(ApplicationStatus.APPLIED, str)
        assert ApplicationStatus.APPLIED == 'applied'

    def test_enum_from_value(self):
        assert ApplicationStatus('interview') == ApplicationStatus.INTERVIEW

    def test_invalid_value_raises(self):
        with pytest.raises(ValueError):
            ApplicationStatus('hired')
