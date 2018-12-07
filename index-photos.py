import json
import boto3
import datetime
# import botocore
# from botocore.vendored import requests
import requests
from datetime import datetime
import requests_aws4auth
from requests_aws4auth import AWS4Auth

#python -m pip install requests_aws4auth, virtualenv
#python -m virtualenv
#cd Scripts activate.bat
##pip install requests_aws4auth

# BUCKET = "b2-store-photos"
# KEY = "test.jpg"

region = 'us-east-1'
service = 'es'
credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)

host = 'https://vpc-photos-n3uizwa27344gvd6xp37tktoqa.us-east-1.es.amazonaws.com' # the Amazon ES domain, including https://
index = 'lambda-s3-index'
type = 'lambda-type'
url = host + '/' + index + '/' + type
print(url)

headers = { "Content-Type": "application/json" }

def detect_labels(bucket, key, max_labels=10, min_confidence=90, region="us-east-1"):
    rekognition = boto3.client("rekognition", region)
    response = rekognition.detect_labels(
        Image={
            "S3Object": {
                "Bucket": bucket,
                "Name": key,
            }
        },
        MaxLabels=max_labels,
        MinConfidence=min_confidence,
    )
    # print(response)
    return response['Labels']


def lambda_handler(event, context):
    # TODO implement
    print(event)
    for record in event['Records']:
        BUCKET = record['s3']['bucket']['name']
        KEY = record['s3']['object']['key']
        timestamp = record['eventTime']
    #timestamp = str(datetime.now())
    result_labels = []
    for label in detect_labels(BUCKET, KEY):
        # print("{Name} - {Confidence}".format(**label))
        result_labels.append(label['Name'])
    result = {"objectKey": KEY, "bucket": BUCKET, "createdTimestamp": timestamp, "labels": result_labels}
    print(result)
    r = requests.post(url, auth = awsauth, json=result, headers=headers)
    r.raise_for_status()
    print(r)

    return {'statusCode': 200, 'body': json.dumps('Hello from Lambda!')}
