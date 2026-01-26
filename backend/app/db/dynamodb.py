import boto3
from botocore.exceptions import ClientError
from mypy_boto3_dynamodb.service_resource import DynamoDBServiceResource, Table

from app.config import settings


def get_dynamodb_resource() -> DynamoDBServiceResource:
    """Get DynamoDB resource, configured for local or AWS."""
    kwargs = {
        'region_name': settings.dynamodb_region,
    }
    if settings.dynamodb_endpoint:
        kwargs['endpoint_url'] = settings.dynamodb_endpoint
        # Local DynamoDB requires dummy credentials
        kwargs['aws_access_key_id'] = 'local'
        kwargs['aws_secret_access_key'] = 'local'

    return boto3.resource('dynamodb', **kwargs)


def get_table() -> Table:
    """Get the job applications table."""
    dynamodb = get_dynamodb_resource()
    return dynamodb.Table(settings.dynamodb_table)


def create_table_if_not_exists() -> Table:
    """Create the job applications table if it doesn't exist."""
    dynamodb = get_dynamodb_resource()

    try:
        table = dynamodb.Table(settings.dynamodb_table)
        table.load()
        return table
    except ClientError as e:
        if e.response.get('Error', {}).get('Code') != 'ResourceNotFoundException':
            raise

    # Table doesn't exist, create it
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

    # Wait for table to be created
    table.wait_until_exists()
    return table
