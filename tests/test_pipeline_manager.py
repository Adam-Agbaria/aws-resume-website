from unittest.mock import patch, MagicMock
from src.pipeline_manager.app import lambda_handler
from datetime import datetime
import uuid

@patch('src.pipeline_manager.app.boto3.resource')
def test_create_comment(mock_boto_resource):
    print("Mocking boto3.resource")

    # Create a mock DynamoDB Table
    mock_table = MagicMock()
    mock_boto_resource.return_value.Table.return_value = mock_table
    mock_table.put_item.return_value = {}

    event = {
        "operation": "create",
        "comment_data": {
            "name": "John Doe",
            "comment": "This is a test comment"
            # comment_id and timestamp will be generated automatically
        }
    }

    # Call the lambda function with the mock dynamodb resource
    response = lambda_handler(event, {}, mock_boto_resource.return_value)

    # Capture the generated UUID and timestamp from the put_item call
    put_item_args = mock_table.put_item.call_args[1]["Item"]
    generated_comment_id = put_item_args["comment_id"]
    generated_timestamp = put_item_args["timestamp"]

    # Check the mock calls
    print("Mock calls:", mock_boto_resource.mock_calls)
    assert response['statusCode'] == 200

    # Ensure that put_item was called with the correct structure, including UUID and timestamp
    assert uuid.UUID(generated_comment_id)  # Valid UUID
    assert datetime.fromisoformat(generated_timestamp)  # Valid ISO 8601 timestamp
    mock_table.put_item.assert_called_once()


@patch('src.pipeline_manager.app.boto3.resource')
def test_read_comment(mock_boto_resource):
    print("Mocking boto3.resource")

    # Create a mock DynamoDB Table
    mock_table = MagicMock()
    mock_boto_resource.return_value.Table.return_value = mock_table
    mock_table.get_item.return_value = {'Item': {"comment_id": "123", "name": "John Doe", "comment": "This is a test comment"}}

    event = {
        "operation": "read",
        "comment_id": "123"
    }

    # Call the lambda function with the mock dynamodb resource
    response = lambda_handler(event, {}, mock_boto_resource.return_value)

    # Check the mock calls
    print("Mock calls:", mock_boto_resource.mock_calls)
    assert response['statusCode'] == 200
    mock_table.get_item.assert_called_once_with(Key={'comment_id': '123'})


@patch('src.pipeline_manager.app.boto3.resource')
def test_update_comment(mock_boto_resource):
    print("Mocking boto3.resource")

    # Create a mock DynamoDB Table
    mock_table = MagicMock()
    mock_boto_resource.return_value.Table.return_value = mock_table
    mock_table.update_item.return_value = {}

    event = {
        "operation": "update",
        "comment_id": "123",
        "comment_data": {
            "name": "Jane Doe",
            "comment": "This is an updated test comment"
            # timestamp will be generated automatically
        }
    }

    # Call the lambda function with the mock dynamodb resource
    response = lambda_handler(event, {}, mock_boto_resource.return_value)

    # Capture the generated timestamp from the update_item call
    update_item_args = mock_table.update_item.call_args[1]["ExpressionAttributeValues"]
    generated_timestamp = update_item_args[":t"]

    # Check the mock calls
    print("Mock calls:", mock_boto_resource.mock_calls)
    assert response['statusCode'] == 200

    # Ensure the correct method was called and timestamp was updated
    assert datetime.fromisoformat(generated_timestamp)  # Valid ISO 8601 timestamp
    mock_table.update_item.assert_called_once_with(
        Key={'comment_id': '123'},
        UpdateExpression="set #name = :n, #comment = :c, #timestamp = :t",
        ExpressionAttributeNames={
            '#name': 'name',
            '#comment': 'comment',
            '#timestamp': 'timestamp'
        },
        ExpressionAttributeValues={
            ':n': event['comment_data']['name'],
            ':c': event['comment_data']['comment'],
            ':t': generated_timestamp
        }
    )


@patch('src.pipeline_manager.app.boto3.resource')
def test_delete_comment(mock_boto_resource):
    print("Mocking boto3.resource")

    # Create a mock DynamoDB Table
    mock_table = MagicMock()
    mock_boto_resource.return_value.Table.return_value = mock_table
    mock_table.delete_item.return_value = {}

    event = {
        "operation": "delete",
        "comment_id": "123"
    }

    # Call the lambda function with the mock dynamodb resource
    response = lambda_handler(event, {}, mock_boto_resource.return_value)

    # Check the mock calls
    print("Mock calls:", mock_boto_resource.mock_calls)
    assert response['statusCode'] == 200

    # Ensure the correct method was called
    mock_table.delete_item.assert_called_once_with(Key={'comment_id': '123'})
