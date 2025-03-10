import aws_cdk as core
import aws_cdk.assertions as assertions

from serverless_url_shortener.serverless_url_shortener_stack import ServerlessUrlShortenerStack

# example tests. To run these tests, uncomment this file along with the example
# resource in serverless_url_shortener/serverless_url_shortener_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = ServerlessUrlShortenerStack(app, "serverless-url-shortener")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
