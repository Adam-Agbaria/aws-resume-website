import json
import boto3
import logging
from botocore.exceptions import ClientError
from unittest.mock import MagicMock
import os

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def lambda_handler(event, context):
    try:
        logger.debug(f"Received event: {event}")

        deployment_group = event['deployment_group']
        application_name = event['application_name']
        s3_bucket = event['s3_bucket']
        s3_key = event['s3_key']

        # Check if running locally
        if os.environ.get('AWS_SAM_LOCAL'):
            logger.debug("Running locally. Using mock for CodeDeploy.")
            # Mock boto3 client for local testing
            codedeploy = MagicMock()
            codedeploy.create_deployment.return_value = {
                'deploymentId': 'd-EXAMPLE123'
            }
        else:
            # Use the actual boto3 client for production
            codedeploy = boto3.client('codedeploy')

        # Create a deployment using CodeDeploy
        response = codedeploy.create_deployment(
            applicationName=application_name,
            deploymentGroupName=deployment_group,
            revision={
                'revisionType': 'S3',
                's3Location': {
                    'bucket': s3_bucket,
                    'key': s3_key,
                    'bundleType': 'zip'
                }
            }
        )

        return respond(200, response)
    except ClientError as e:
        logger.error(f"ClientError: {e.response['Error']['Message']}")
        return respond(500, f"ClientError: {e.response['Error']['Message']}")
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return respond(500, f"Error: {str(e)}")

def respond(status_code, message):
    return {
        'statusCode': status_code,
        'body': json.dumps(message)
    }
