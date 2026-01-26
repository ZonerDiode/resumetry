import os
from typing import Any
from unittest.mock import patch
from datetime import date

import boto3
import pytest
from moto import mock_aws
from fastapi.testclient import TestClient

from app.config import settings


@pytest.fixture(scope='session')
def aws_credentials():
    """Mocked AWS credentials for moto."""
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'


@pytest.fixture()
def dynamodb_mock(aws_credentials):
    """Create a mocked DynamoDB with the application table."""
    with mock_aws():
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.create_table(
            TableName=settings.dynamodb_table,
            KeySchema=[
                {'AttributeName': 'pk', 'KeyType': 'HASH'},
                {'AttributeName': 'sk', 'KeyType': 'RANGE'},
            ],
            AttributeDefinitions=[
                {'AttributeName': 'pk', 'AttributeType': 'S'},
                {'AttributeName': 'sk', 'AttributeType': 'S'},
            ],
            BillingMode='PAY_PER_REQUEST',
        )
        table.wait_until_exists()

        with patch('app.db.dynamodb.get_dynamodb_resource', return_value=dynamodb):
            yield table


@pytest.fixture()
def client(dynamodb_mock):
    """FastAPI TestClient with mocked DynamoDB."""
    from app.main import app

    with patch('app.main.create_table_if_not_exists'):
        with TestClient(app) as c:
            yield c


@pytest.fixture()
def sample_application_data() -> dict[str, Any]:
    """Minimal valid application payload (camelCase for API)."""
    return {
        'company': 'Acme Corp',
        'role': 'Software Engineer',
        'interestLevel': 2,
    }


@pytest.fixture()
def full_application_data() -> dict[str, Any]:
    """Complete application payload with all fields."""
    return {
        'company': 'TechCo',
        'role': 'Senior Developer',
        'description': 'Full stack role',
        'salary': '$150k',
        'interestLevel': 3,
        'status': 'interview',
        'sourcePage': 'https://linkedin.com/jobs/123',
        'reviewPage': 'https://glassdoor.com/techco',
        'loginHints': 'Use SSO',
        'appliedDate': str(date.today()),
        'statusDate': str(date.today()),
        'notes': [
            {
                'occurDate': str(date.today()),
                'description': 'Applied via website',
            }
        ],
    }


@pytest.fixture()
def created_application(client, sample_application_data) -> dict[str, Any]:
    """Create and return an application via the API."""
    response = client.post('/api/v1/applications', json=sample_application_data)
    assert response.status_code == 201
    return response.json()
