import json
import os
import boto3
import hashlib
from http import HTTPStatus
import base64
from botocore.exceptions import BotoCoreError, ClientError

from ..commons import dynamodb_table_connection

BASE_URL = os.getenv("BASE_URL", "https://short.sergidominguez.com/")  # Replace with your domain

def lambda_handler(event, context):
    try:
        event_body = json.loads(event.get("body"))
        original_url = event_body.get("url")

        short_code = _generate_short_code(original_url)
        short_url = f"{BASE_URL}{short_code}"

        # Save to DynamoDB:
        table = dynamodb_table_connection()

        table.put_item(
            Item={
                "short_code": short_code,
                "original_url": original_url
            }
        )

        return _lambda_response(
            status_code=HTTPStatus.OK,
            body=json.dumps(
                {"short_url": short_url,
                 "original_url": original_url
                 }
            )
        )
    except (BotoCoreError, ClientError) as e:
        return _lambda_response(status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                                body=json.dumps({"message": "Error saving to database", "error": str(e)}))
    except Exception as e:
        return _lambda_response(status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                                body=json.dumps({"message": "Internal server error", "error": str(e)}))


def _generate_short_code(url: str) -> str:
    """Generate a short code for the given URL."""
    hash_object = hashlib.sha256(url.encode())
    short_code = base64.urlsafe_b64encode(hash_object.digest()).decode()[:8]  # Take first 8 chars
    return short_code


def _lambda_response(status_code: HTTPStatus, body: str | None = None) -> dict:
    """Return a Lambda-friendly response."""
    body = body or json.dumps({"message": status_code.description})

    return {
        "statusCode": status_code.value,
        "body": body
    }
