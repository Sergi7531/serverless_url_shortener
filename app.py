#!/usr/bin/env python3
import os

import aws_cdk as cdk

from serverless_url_shortener.serverless_url_shortener_stack import ServerlessUrlShortenerStack


app = cdk.App()
ServerlessUrlShortenerStack(app, "ServerlessUrlShortenerStack")
app.synth()
