from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_apigateway as api_gateway,
    aws_dynamodb as dynamodb,
    aws_iam as iam,
    aws_ssm as ssm,
    RemovalPolicy
)

from constructs import Construct


class ServerlessUrlShortenerStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        # Create DynamoDB Table
        table = dynamodb.Table(
            self, "URLShortenerTable",
            partition_key=dynamodb.Attribute(name="short_code", type=dynamodb.AttributeType.STRING),
            removal_policy=RemovalPolicy.RETAIN
        )

        # Store Table Name in SSM Parameter Store
        parameter = ssm.StringParameter(
            self, "DynamoDBTableNameParam",
            parameter_name="/urlshortener/dynamodb_table_name",
            string_value=table.table_name
        )

        # IAM Role for Generate Short URL Lambda
        generate_short_url_role = iam.Role(
            self, "GenerateShortUrlRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
        )
        generate_short_url_role.add_to_policy(
            iam.PolicyStatement(
                actions=["ssm:GetParameter", "dynamodb:PutItem", "dynamodb:GetItem"],
                resources=[parameter.parameter_arn, table.table_arn]
            )
        )

        # IAM Role for Get Full URL Lambda
        get_full_url_function_role = iam.Role(
            self, "GetFullUrlRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com")
        )
        get_full_url_function_role.add_to_policy(
            iam.PolicyStatement(
                actions=["ssm:GetParameter", "dynamodb:GetItem"],
                resources=[parameter.parameter_arn, table.table_arn]
            )
        )

        # Lambda for Generating Short URL
        generate_short_url_lambda = _lambda.Function(
            self, "GenerateShortUrlLambda",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="_lambda.generate_short_url.handler.lambda_handler",
            code=_lambda.Code.from_asset("serverless_url_shortener"),
            role=generate_short_url_role
        )

        # Lambda for Getting Full URL
        get_full_url_lambda = _lambda.Function(
            self, "GetFullUrlLambda",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="_lambda.get_full_url.handler.lambda_handler",
            code=_lambda.Code.from_asset("serverless_url_shortener"),
            role=get_full_url_function_role
        )

        # API Gateway
        api = api_gateway.RestApi(self, "UrlShortenerAPI")

        # POST /shorten/ Endpoint
        shorten_resource = api.root.add_resource("shorten")
        shorten_resource.add_method("POST", api_gateway.LambdaIntegration(generate_short_url_lambda))

        # GET /{shortened_url_fragment}/ Endpoint
        get_url_resource = api.root.add_resource("{shortened_url_fragment}")
        get_url_resource.add_method("GET", api_gateway.LambdaIntegration(get_full_url_lambda))
