import json
import boto3
from botocore.exceptions import ClientError
import logging
from datetime import datetime
import uuid

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def lambda_handler(event, context, dynamodb=None):
    # If no DynamoDB resource is provided, use the default boto3 resource
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb')

    table = dynamodb.Table("Guestbook")

    try:
        logger.debug(f"Received event: {event}")

        # Determine the operation: create, read, update, delete
        operation = event.get('operation', '')
        
        if operation == 'create':
            return create_comment(table, event['comment_data'])
        elif operation == 'read':
            return read_comment(table, event['comment_id'])
        elif operation == 'update':
            return update_comment(table, event['comment_id'], event['comment_data'])
        elif operation == 'delete':
            return delete_comment(table, event['comment_id'])
        else:
            return respond(400, "Invalid operation")
    except ClientError as e:
        logger.error(f"ClientError: {e.response['Error']['Message']}")
        return respond(500, f"ClientError: {e.response['Error']['Message']}")
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return respond(500, f"Error: {str(e)}")

def create_comment(table, comment_data):
    try:
        # Generate a unique comment_id using UUID
        comment_data['comment_id'] = str(uuid.uuid4())

        # Add the current timestamp to the comment data
        comment_data['timestamp'] = datetime.utcnow().isoformat()

        logger.debug(f"Creating comment: {comment_data}")
        table.put_item(Item=comment_data)
        return respond(200, "Comment created successfully")
    except ClientError as e:
        logger.error(f"Error creating comment: {e.response['Error']['Message']}")
        return respond(500, f"ClientError: {e.response['Error']['Message']}")

def read_comment(table, comment_id):
    try:
        logger.debug(f"Reading comment with ID: {comment_id}")
        response = table.get_item(Key={'comment_id': comment_id})
        if 'Item' in response:
            return respond(200, response['Item'])
        else:
            return respond(404, "Comment not found")
    except ClientError as e:
        logger.error(f"Error reading comment: {e.response['Error']['Message']}")
        return respond(500, f"ClientError: {e.response['Error']['Message']}")

def update_comment(table, comment_id, comment_data):
    try:
        # Add the current timestamp to the update data
        comment_data['timestamp'] = datetime.utcnow().isoformat()

        logger.debug(f"Updating comment with ID: {comment_id} with data: {comment_data}")
        table.update_item(
            Key={'comment_id': comment_id},
            UpdateExpression="set #name = :n, #comment = :c, #timestamp = :t",
            ExpressionAttributeNames={
                '#name': 'name',
                '#comment': 'comment',
                '#timestamp': 'timestamp'
            },
            ExpressionAttributeValues={
                ':n': comment_data['name'],
                ':c': comment_data['comment'],
                ':t': comment_data['timestamp']
            }
        )
        return respond(200, "Comment updated successfully")
    except ClientError as e:
        logger.error(f"Error updating comment: {e.response['Error']['Message']}")
        return respond(500, f"ClientError: {e.response['Error']['Message']}")

def delete_comment(table, comment_id):
    try:
        logger.debug(f"Deleting comment with ID: {comment_id}")
        table.delete_item(Key={'comment_id': comment_id})
        return respond(200, "Comment deleted successfully")
    except ClientError as e:
        logger.error(f"Error deleting comment: {e.response['Error']['Message']}")
        return respond(500, f"ClientError: {e.response['Error']['Message']}")

def respond(status_code, message):
    return {
        'statusCode': status_code,
        'body': json.dumps(message)
    }
