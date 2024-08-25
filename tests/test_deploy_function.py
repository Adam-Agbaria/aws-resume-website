from unittest.mock import patch, MagicMock
from src.deploy_function.app import lambda_handler

def test_deploy_function():
    print("Mocking boto3.client")

    # Create a mock CodeDeploy client
    mock_codedeploy = MagicMock()
    mock_codedeploy.create_deployment.return_value = {"deploymentId": "deployment-1234"}

    with patch('src.deploy_function.app.boto3.client', return_value=mock_codedeploy):
        event = {
            "deployment_group": "MyDeploymentGroup",
            "application_name": "MyApplication",
            "s3_bucket": "my-bucket",
            "s3_key": "my-app.zip"
        }

        # Call the lambda function
        response = lambda_handler(event, None)

        # Check the mock calls
        print("Mock calls:", mock_codedeploy.mock_calls)

        assert response['statusCode'] == 200
        mock_codedeploy.create_deployment.assert_called_once_with(
            applicationName="MyApplication",
            deploymentGroupName="MyDeploymentGroup",
            revision={
                'revisionType': 'S3',
                's3Location': {
                    'bucket': "my-bucket",
                    'key': "my-app.zip",
                    'bundleType': 'zip'
                }
            }
        )

# Sample event data for local testing
sample_event = {
    "deployment_group": "MyDeploymentGroup",
    "application_name": "MyApplication",
    "s3_bucket": "my-bucket",
    "s3_key": "my-artifact.zip"
}
