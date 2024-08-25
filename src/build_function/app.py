import boto3
import os
import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def lambda_handler(event, context):
    try:
        logger.debug(f"Received event: {event}")
        project_name = event["project_name"]
        s3_bucket = event["s3_bucket"]

        # Get source directory from the context or default to /tmp (which is always writable in AWS Lambda)
        source_directory = getattr(context, "source_directory", "/tmp")
        if not os.path.exists(source_directory):
            logger.debug(f"Source directory does not exist, using /tmp instead.")
            source_directory = "/tmp"  # Default to /tmp if the provided directory doesn't exist


        # Initialize the S3 client
        s3 = boto3.client('s3')

        # Walk through the source directory and upload files to S3
        for root, dirs, files in os.walk(source_directory):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                s3_key = os.path.relpath(file_path, source_directory)
                logger.debug(f"Uploading {file_path} to s3://{s3_bucket}/{s3_key}")
                s3.upload_file(file_path, s3_bucket, s3_key)

        return {
            'statusCode': 200,
            'body': f"Files from {source_directory} uploaded successfully to {s3_bucket}."
        }
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': str(e)
        }
