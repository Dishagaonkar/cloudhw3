import json
import boto3
from opensearchpy import OpenSearch, RequestsHttpConnection

lex_client = boto3.client('lexv2-runtime')
BOT_ID = "WVDJVUACUL"
BOT_ALIAS_ID = "TSTALIASID"
LOCALE_ID = "en_US"

es = OpenSearch(
    hosts=[{'host': "search-photos-cq5z5g57zek6qmvs5p4lpdub5a.aos.us-east-1.on.aws", 'port': 443}],
    http_auth=("Cloudhw3", "Cloud*hw3"),  # only if using basic auth
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection
)

def lambda_handler(event, context):
    print("event", event)

    user_query = event["queryStringParameters"]["q"]

    lex_response = lex_client.recognize_text(
        botId=BOT_ID,
        botAliasId=BOT_ALIAS_ID,
        localeId=LOCALE_ID,
        sessionId="searchsession",
        text=user_query
    )

    print("lex response",lex_response)

    slots = lex_response["sessionState"]["intent"]["slots"]

    extracted_labels = []
    for slot in slots.values():
        if slot and "value" in slot:
            extracted_labels.append(slot["value"]["interpretedValue"])

    image_metadata = []
    for label in extracted_labels:
        query = {
            "query": {
                "match": {
                    "labels": label
                }
            }
        }
        res = es.search(index="photos", body=query)
        for hit in res["hits"]["hits"]:
            image_metadata.append(hit["_source"])

    return {
        "statusCode": 200,
        "body": json.dumps(image_metadata),
        "headers": {"Access-Control-Allow-Origin": "*"}
    }