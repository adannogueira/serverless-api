from datetime import datetime
import boto3
import os
import uuid
import json
import logging
import dynamo
import uuid

logger = logging.getLogger()
logger.setLevel(logging.INFO)
dynamodb = boto3.client('dynamodb')
table_name = str(os.environ['DYNAMODB_TABLE'])

def create(event, context):
    logger.info(f'Incoming request is: {event}')
    response = {
        'statusCode': 500,
        'body': 'An error occured while creating the post.'
    }
    post_str = event['body']
    post = json.loads(post_str)
    current_timestamp = datetime.now().isoformat()
    post['createdAt'] = current_timestamp
    post['id'] = str(uuid.uuid4())
    res = dynamodb.put_item(
        TableName=table_name,
        Item=dynamo.to_item(post)
    )
    if res['ResponseMetadata']['HTTPStatusCode'] == 200:
        response = { 'statusCode': 201 }
    return response

def get(event, context):
    logger.info(f'Incoming request is: {event}')
    response = {
        'statusCode': 500,
        'body': 'An error occured while retrieving the post.'
    }
    post_id = event['pathParameters']['postId']
    post_query = dynamodb.get_item(
        TableName=table_name, Key={'id': {'S': post_id}}
    )
    if 'Item' in post_query:
        post = post_query['Item']
        logger.info(f'Post is: {post}')
        response = {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(dynamo.to_dict(post))
        }
    return response

def all(event, context):
    response = {
        'statusCode': 500,
        'body': 'An error occured while retrieving all posts.'
    }
    scan_result = dynamodb.scan(TableName=table_name)['Items']
    posts = []
    for item in scan_result:
        posts.append(dynamo.to_dict(item))
    response = {
        'statusCode': 200,
        'body': json.dumps(posts)
    }
    return response

def update(event, context):
    logger.info(f'Incoming request is: {event}')
    post_id = event['pathParameters']['postId']
    response = {
        'statusCode': 500,
        'body': f'An error occured while updating the post {post_id}.'
    }
    post_str = event['body']
    post = json.loads(post_str)
    res = dynamodb.update_item(
        TableName=table_name,
        Key={
            'id': { 'S': post_id }
        },
        UpdateExpression='set content=:c, author=:a, updatedAt=:u',
        ExpressionAttributeValues={
            ':c': dynamo.to_item(post['content']),
            ':a': dynamo.to_item(post['author']),
            ':u': dynamo.to_item(datetime.now().isoformat())
        },
        ReturnValues='UPDATED_NEW'
    )
    if res['ResponseMetadata']['HTTPStatusCode'] == 200:
        response = { 'statusCode': 200 }
    return response

def delete(event, context):
    logger.info(f'Incoming request is: {event}')
    post_id = event['pathParameters']['postId']
    response = {
        'statusCode': 500,
        'body': f'An error occured while deleting post {post_id}'
    }
    res = dynamodb.delete_item(
        TableName=table_name,
        Key={
            'id': { 'S': post_id }
        }
    )
    if res['ResponseMetadata']['HTTPStatusCode'] == 200:
        response = { 'statusCode': 204 }
    return response