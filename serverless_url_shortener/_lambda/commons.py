import boto3


def _dynamodb_table_name() -> str:
    """Get the DynamoDB table name from SSM Parameter Store."""
    ssm = boto3.client("ssm")
    response = ssm.get_parameter(Name="/urlshortener/dynamodb_table_name")

    return response["Parameter"]["Value"]


def dynamodb_table_connection() -> boto3.client:
    """Establishes a connection to the DynamoDB table."""
    dynamodb = boto3.resource("dynamodb")

    return dynamodb.Table(_dynamodb_table_name())

