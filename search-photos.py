import boto3
import json
import requests
from requests_aws4auth import AWS4Auth

region = 'us-east-1' 
service = 'es'
credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)

host = 'https://vpc-photos-n3uizwa27344gvd6xp37tktoqa.us-east-1.es.amazonaws.com' 
index = 'lambda-s3-index'
url = host + '/' + index + '/_search'

lex_client = boto3.client('lex-runtime')

#inputText = "Show me Dogs and Cats"
# Lambda execution starts here
def lambda_handler(event, context):

    # Put the user query into the query DSL for more accurate search results.
    # Note that certain fields are boosted (^).
    # query = {
    #     "size": 25,
    #     "query": {
    #         "multi_match": {
    #             "query": event['queryStringParameters']['q'],
    #             "fields": ["fields.title^4", "fields.plot^2", "fields.actors", "fields.directors"]
    #         }
    #     }
    # }
    print(event)
    inputText = event['queryStringParameters']['q']
    
    response_lex = lex_client.post_text(
        botAlias="$LATEST",
        botName="search_photos_bot",
        userId='abc',
        # sessionAttributes=sessionAttributes,
        inputText=inputText
    )
    
    print(response_lex)
    keyword1 = response_lex['slots']['search_pictures']
    if(keyword1 is not None):
        keywords = keyword1
    keyword2 = response_lex['slots']['search_slot']
    if(keyword2 is not None and keyword1 is None):
        keywords = keyword2
    print(keyword1)
    print(keyword2)
    if (keyword1 is not None and keyword2 is not None):
        keywords = keyword1 + ',' + keyword2
    print("keys:", keywords)
    query = {"size": 25, "query": { "multi_match": { "query": keywords}}}
    #print("Query:",query)

    # ES 6.x requires an explicit Content-Type header
    headers = { "Content-Type": "application/json" }

    # Make the signed HTTP request
    r = requests.get(url, auth=awsauth, headers=headers, data=json.dumps(query))
    print(r.text)

    # Create the response and add some extra content to support CORS
    response = {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": '*'
        },
        "isBase64Encoded": False
    }
    

    # Add the search results to the response
    response['body'] = r.text
    return response