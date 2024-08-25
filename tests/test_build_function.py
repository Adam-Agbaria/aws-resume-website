from src.build_function.app import lambda_handler
from unittest.mock import patch, MagicMock
import os

class MockContext:
    source_directory = os.path.normpath("/mock/directory")

@patch('src.build_function.app.os.path.exists')
@patch('src.build_function.app.os.walk')
@patch('src.build_function.app.boto3.client')
def test_lambda_handler(mock_boto_client, mock_os_walk, mock_os_path_exists):
    print("Mocking S3 client, OS walk, and path.exists")

    # Mock the os.walk to simulate a directory with files
    mock_os_walk.return_value = [
        (os.path.normpath('/mock/directory'), ('subdir',), ('index.html', 'style.css'))
    ]

    # Mock the os.path.exists to simulate that the directory exists
    mock_os_path_exists.return_value = True

    # Create a mock S3 client
    mock_s3_client = MagicMock()
    mock_boto_client.return_value = mock_s3_client

    event = {
        "project_name": "MyWebsiteProject",
        "s3_bucket": "my-website-bucket"
    }
    
    # Use the mock context with the source directory
    context = MockContext()

    # Call the lambda function
    response = lambda_handler(event, context)

    # Check the mock calls
    print("Mock S3 client calls:", mock_s3_client.mock_calls)

    assert response['statusCode'] == 200
    
    # Normalize the paths for the assertions
    mock_s3_client.upload_file.assert_any_call(os.path.normpath('/mock/directory/index.html'), 'my-website-bucket', 'index.html')
    mock_s3_client.upload_file.assert_any_call(os.path.normpath('/mock/directory/style.css'), 'my-website-bucket', 'style.css')
