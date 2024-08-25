from unittest.mock import patch, MagicMock
from src.pipeline_manager.app import lambda_handler

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
            "comment_id": "123",
            "name": "John Doe",
            "comment": "This is a test comment",
            "timestamp": "2024-08-25T12:00:00Z"
        }
    }

    # Call the lambda function with the mock dynamodb resource
    response = lambda_handler(event, {}, mock_boto_resource.return_value)

    # Check the mock calls
    print("Mock calls:", mock_boto_resource.mock_calls)
    assert response['statusCode'] == 200

    # Ensure the correct method was called
    mock_table.put_item.assert_called_once_with(Item=event['comment_data'])


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
            "comment": "This is an updated test comment",
            "timestamp": "2024-08-26T12:00:00Z"
        }
    }

    # Call the lambda function with the mock dynamodb resource
    response = lambda_handler(event, {}, mock_boto_resource.return_value)

    # Check the mock calls
    print("Mock calls:", mock_boto_resource.mock_calls)
    assert response['statusCode'] == 200

    # Ensure the correct method was called
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
            ':t': event['comment_data']['timestamp']
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
