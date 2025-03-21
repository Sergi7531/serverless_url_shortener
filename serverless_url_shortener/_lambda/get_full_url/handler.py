import json
from http import HTTPStatus

from serverless_url_shortener._lambda.commons import dynamodb_table_connection


def handler(event, context):
    short_id = event["pathParameters"]["shortened_url_fragment"]

    table = dynamodb_table_connection()

    response = table.get_item(Key={"short_id": short_id})
    item = response.get("Item")

    if not item:
        _lambda_response(status_code=HTTPStatus.NOT_FOUND)

    return _lambda_response(status_code=HTTPStatus.FOUND, headers={"Location": item["original_url"]})


def _lambda_response(status_code: HTTPStatus, message: str | None = None, headers: dict | None = None) -> dict:
    message = message or status_code.description
    headers = headers or {}

    return {
        "statusCode": status_code.value,
        "body": json.dumps({"message": message}),
        "headers": headers
    }
