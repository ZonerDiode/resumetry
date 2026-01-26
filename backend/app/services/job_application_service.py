from datetime import date, datetime
from decimal import Decimal
from typing import Any, cast
from uuid import uuid4

from boto3.dynamodb.conditions import Key

from app.db.dynamodb import get_table
from app.models.job_application import (
    JobApplicationCreate,
    JobApplicationResponse,
    JobApplicationUpdate,
)

PARTITION_KEY = 'JOB_APPS'
SK_PREFIX = 'APP#'


def _serialize_for_dynamo(data: dict[str, Any]) -> dict[str, Any]:
    """Convert Python types to DynamoDB-compatible types."""
    serialized: dict[str, Any] = {}
    for key, value in data.items():
        if value is None:
            continue
        if isinstance(value, (date, datetime)):
            serialized[key] = value.isoformat()
        elif isinstance(value, list):
            serialized[key] = [
                _serialize_for_dynamo(cast(dict[str, Any], item)) if isinstance(item, dict) else item
                for item in cast(list[Any], value)
            ]
        elif isinstance(value, dict):
            serialized[key] = _serialize_for_dynamo(cast(dict[str, Any], value))
        elif hasattr(value, 'value'):
            # Enum
            serialized[key] = value.value
        else:
            serialized[key] = value
    return serialized


def _deserialize_from_dynamo(item: dict[str, Any]) -> dict[str, Any]:
    """Convert DynamoDB item to application dict."""
    app_id = item['sk'].removeprefix(SK_PREFIX)

    result: dict[str, Any] = {
        'id': app_id,
    }

    skip_keys = {'pk', 'sk', 'created_at', 'updated_at'}
    date_fields = {'applied_date', 'status_date'}

    for key, value in item.items():
        if key in skip_keys:
            continue
        if key in date_fields and isinstance(value, str):
            result[key] = date.fromisoformat(value)
        elif key == 'interest_level' and isinstance(value, Decimal):
            result[key] = int(value)
        elif key == 'notes' and isinstance(value, list):
            notes = cast(list[dict[str, Any]], value)
            result[key] = [
                {
                    **note,
                    'occur_date': date.fromisoformat(note['occur_date'])
                    if isinstance(note.get('occur_date'), str) else note.get('occur_date'),
                }
                for note in notes
            ]
        else:
            result[key] = value

    return result


def _build_update_expression(data: dict[str, Any]) -> tuple[str, dict[str, str], dict[str, Any]]:
    """Build DynamoDB SET UpdateExpression with attribute name placeholders."""
    set_parts: list[str] = []
    expression_names: dict[str, str] = {}
    expression_values: dict[str, Any] = {}

    for i, (key, value) in enumerate(data.items()):
        name_placeholder = f'#attr{i}'
        value_placeholder = f':val{i}'
        set_parts.append(f'{name_placeholder} = {value_placeholder}')
        expression_names[name_placeholder] = key
        expression_values[value_placeholder] = value

    expression = 'SET ' + ', '.join(set_parts)
    return expression, expression_names, expression_values


def create_application(data: JobApplicationCreate) -> JobApplicationResponse:
    """Create a new job application in DynamoDB."""
    table = get_table()
    app_id = str(uuid4())
    now = datetime.now().isoformat()

    item_data = _serialize_for_dynamo(data.model_dump())
    item_data['pk'] = PARTITION_KEY
    item_data['sk'] = f'{SK_PREFIX}{app_id}'
    item_data['created_at'] = now
    item_data['updated_at'] = now

    table.put_item(Item=item_data)

    return JobApplicationResponse(**_deserialize_from_dynamo(item_data))


def get_application(app_id: str) -> JobApplicationResponse | None:
    """Get a single job application by ID."""
    table = get_table()
    response = table.get_item(
        Key={
            'pk': PARTITION_KEY,
            'sk': f'{SK_PREFIX}{app_id}',
        }
    )
    item = response.get('Item')
    if not item:
        return None
    return JobApplicationResponse(**_deserialize_from_dynamo(item))


def list_applications() -> list[JobApplicationResponse]:
    """List all job applications."""
    table = get_table()
    items: list[dict[str, Any]] = []
    last_key: dict[str, Any] | None = None

    while True:
        if last_key:
            response = table.query(
                KeyConditionExpression=Key('pk').eq(PARTITION_KEY),
                ExclusiveStartKey=last_key,
            )
        else:
            response = table.query(
                KeyConditionExpression=Key('pk').eq(PARTITION_KEY),
            )
        items.extend(response.get('Items', []))

        last_key = response.get('LastEvaluatedKey')
        if not last_key:
            break

    return [JobApplicationResponse(**_deserialize_from_dynamo(item)) for item in items]


def update_application(app_id: str, data: JobApplicationUpdate) -> JobApplicationResponse | None:
    """Partially update a job application."""
    fields = data.model_dump(exclude_unset=True)
    if not fields:
        return get_application(app_id)

    serialized = _serialize_for_dynamo(fields)
    serialized['updated_at'] = datetime.now().isoformat()

    expression, names, values = _build_update_expression(serialized)

    table = get_table()
    try:
        response = table.update_item(
            Key={
                'pk': PARTITION_KEY,
                'sk': f'{SK_PREFIX}{app_id}',
            },
            UpdateExpression=expression,
            ExpressionAttributeNames=names,
            ExpressionAttributeValues=values,
            ConditionExpression='attribute_exists(pk)',
            ReturnValues='ALL_NEW',
        )
    except table.meta.client.exceptions.ConditionalCheckFailedException:
        return None

    return JobApplicationResponse(**_deserialize_from_dynamo(response['Attributes']))


def delete_application(app_id: str) -> bool:
    """Delete a job application. Returns True if it existed."""
    table = get_table()
    response = table.delete_item(
        Key={
            'pk': PARTITION_KEY,
            'sk': f'{SK_PREFIX}{app_id}',
        },
        ReturnValues='ALL_OLD',
    )
    return bool(response.get('Attributes'))
