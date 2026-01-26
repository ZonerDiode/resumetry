"""Tests for service layer helper functions."""
import pytest
from datetime import date, datetime
from decimal import Decimal

from app.models.enums import ApplicationStatus
from app.services.job_application_service import (
    _serialize_for_dynamo,
    _deserialize_from_dynamo,
    _build_update_expression,
    SK_PREFIX,
)


class TestSerializeForDynamo:

    def test_date_to_isoformat(self):
        result = _serialize_for_dynamo({'applied_date': date(2025, 6, 15)})
        assert result['applied_date'] == '2025-06-15'

    def test_datetime_to_isoformat(self):
        dt = datetime(2025, 6, 15, 10, 30, 0)
        result = _serialize_for_dynamo({'updated_at': dt})
        assert result['updated_at'] == '2025-06-15T10:30:00'

    def test_none_values_excluded(self):
        result = _serialize_for_dynamo({'company': 'Acme', 'salary': None})
        assert 'salary' not in result
        assert result['company'] == 'Acme'

    def test_enum_to_value(self):
        result = _serialize_for_dynamo({'status': ApplicationStatus.INTERVIEW})
        assert result['status'] == 'interview'

    def test_nested_dict(self):
        result = _serialize_for_dynamo({
            'outer': {'inner_date': date(2025, 1, 1)}
        })
        assert result['outer']['inner_date'] == '2025-01-01'

    def test_list_of_dicts(self):
        result = _serialize_for_dynamo({
            'notes': [
                {'occur_date': date(2025, 3, 1), 'description': 'Applied'},
                {'occur_date': date(2025, 3, 5), 'description': 'Follow up'},
            ]
        })
        assert result['notes'][0]['occur_date'] == '2025-03-01'
        assert result['notes'][1]['occur_date'] == '2025-03-05'

    def test_plain_values_pass_through(self):
        result = _serialize_for_dynamo({
            'company': 'Acme', 'interest_level': 2
        })
        assert result == {'company': 'Acme', 'interest_level': 2}

    def test_empty_dict(self):
        assert _serialize_for_dynamo({}) == {}

    def test_list_of_scalars(self):
        result = _serialize_for_dynamo({'tags': ['a', 'b', 'c']})
        assert result['tags'] == ['a', 'b', 'c']


class TestDeserializeFromDynamo:

    def test_extracts_id_from_sk(self):
        item = {
            'pk': 'JOB_APPS',
            'sk': f'{SK_PREFIX}abc-123',
            'company': 'Acme',
            'role': 'Dev',
        }
        result = _deserialize_from_dynamo(item)
        assert result['id'] == 'abc-123'

    def test_skips_internal_keys(self):
        item = {
            'pk': 'JOB_APPS',
            'sk': f'{SK_PREFIX}id1',
            'created_at': '2025-01-01T00:00:00',
            'updated_at': '2025-01-01T00:00:00',
            'company': 'Acme',
        }
        result = _deserialize_from_dynamo(item)
        assert 'pk' not in result
        assert 'sk' not in result
        assert 'created_at' not in result
        assert 'updated_at' not in result

    def test_date_fields_parsed(self):
        item = {
            'pk': 'JOB_APPS',
            'sk': f'{SK_PREFIX}id1',
            'applied_date': '2025-06-15',
            'status_date': '2025-06-20',
        }
        result = _deserialize_from_dynamo(item)
        assert result['applied_date'] == date(2025, 6, 15)
        assert result['status_date'] == date(2025, 6, 20)

    def test_interest_level_decimal_to_int(self):
        item = {
            'pk': 'JOB_APPS',
            'sk': f'{SK_PREFIX}id1',
            'interest_level': Decimal('2'),
        }
        result = _deserialize_from_dynamo(item)
        assert result['interest_level'] == 2
        assert isinstance(result['interest_level'], int)

    def test_notes_deserialized(self):
        item = {
            'pk': 'JOB_APPS',
            'sk': f'{SK_PREFIX}id1',
            'notes': [
                {'occur_date': '2025-03-01', 'description': 'Applied'},
                {'occur_date': '2025-03-05', 'description': 'Follow up'},
            ],
        }
        result = _deserialize_from_dynamo(item)
        assert result['notes'][0]['occur_date'] == date(2025, 3, 1)
        assert result['notes'][1]['description'] == 'Follow up'

    def test_other_fields_pass_through(self):
        item = {
            'pk': 'JOB_APPS',
            'sk': f'{SK_PREFIX}id1',
            'company': 'Acme',
            'role': 'Dev',
            'description': 'Great job',
        }
        result = _deserialize_from_dynamo(item)
        assert result['company'] == 'Acme'
        assert result['role'] == 'Dev'
        assert result['description'] == 'Great job'


class TestBuildUpdateExpression:

    def test_single_field(self):
        expr, names, values = _build_update_expression({'company': 'NewCo'})
        assert expr == 'SET #attr0 = :val0'
        assert names['#attr0'] == 'company'
        assert values[':val0'] == 'NewCo'

    def test_multiple_fields(self):
        data = {'company': 'NewCo', 'role': 'Dev', 'salary': '$100k'}
        expr, names, values = _build_update_expression(data)
        assert expr.startswith('SET ')
        assert len(names) == 3
        assert len(values) == 3
        assert set(names.values()) == {'company', 'role', 'salary'}

    def test_placeholders_are_unique(self):
        data = {'a': 1, 'b': 2, 'c': 3}
        expr, names, values = _build_update_expression(data)
        assert '#attr0' in names
        assert '#attr1' in names
        assert '#attr2' in names
        assert ':val0' in values
        assert ':val1' in values
        assert ':val2' in values
