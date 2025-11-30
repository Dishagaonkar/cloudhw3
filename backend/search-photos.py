import json
import boto3
from opensearchpy import OpenSearch, RequestsHttpConnection

lex_client = boto3.client('lexv2-runtime')

BOT_ID = "WVDJVUACUL"
BOT_ALIAS_ID = "TSTALIASID"
LOCALE_ID = "en_US"

es = OpenSearch(
    hosts=[{
        'host': "search-photos-cq5z5g57zek6qmvs5p4lpdub5a.aos.us-east-1.on.aws",
        'port': 443
    }],
    http_auth=("Cloudhw3", "Cloud*hw3"),  # if basic auth
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection
)

def lambda_handler(event, context):
    print("event:", event)

    # Safely get query string parameter ?q=
    qs = event.get("queryStringParameters") or {}
    user_query = qs.get("q", "")
    if not user_query:
        return _response(
            400,
            {"error": "Missing required query parameter 'q'"}
        )

    # Call Lex to extract labels/entities
    lex_response = lex_client.recognize_text(
        botId=BOT_ID,
        botAliasId=BOT_ALIAS_ID,
        localeId=LOCALE_ID,
        sessionId="searchsession",
        text=user_query
    )

    print("lex response:", lex_response)

    slots = lex_response["sessionState"]["intent"]["slots"] or {}

    extracted_labels = []
    for slot in slots.values():
        if slot and "value" in slot and slot["value"].get("interpretedValue"):
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

    return _response(200, image_metadata)


def _response(status_code, body_obj):
    """Helper to add consistent CORS headers."""
    return {
        "statusCode": status_code,
        "headers": {
            # You can replace * with your exact origin if you want tighter security:
            # "http://photo-frontend-hw3.s3-website-us-east-1.amazonaws.com"
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": (
                "Content-Type,X-Amz-Date,Authorization,"
                "X-Api-Key,X-Amz-Security-Token,x-amz-meta-customLabels"
            ),
            "Access-Control-Allow-Methods": "OPTIONS,GET,PUT"
        },
        "body": json.dumps(body_obj)
    }
