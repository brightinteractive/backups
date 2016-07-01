#!/usr/bin/env python

def mock_aws_response(**kwargs):
    response = { 'HTTPStatusCode': '200',
            'HostId': 'KX19tFhyBOCZfaDAk78nnkLiAvVV8fUgv11LMykrn3aXwZhJcimxZEbqRmUYaalq/beynjJ4Hmw=',
            'RequestId': '609FF741F8386E27' }
    response.update(kwargs)
    return { 'ResponseMetadata': response }
