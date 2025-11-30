# import boto3
# import json
# import urllib
# from datetime import datetime
# from opensearchpy import OpenSearch, RequestsHttpConnection
# import os
# import time
# import base64

# # Initialize clients
# s3 = boto3.client('s3')
# rekognition = boto3.client('rekognition', region_name='us-east-1')

# # ElasticSearch configuration
# es_endpoint = "search-photos-cq5z5g57zek6qmvs5p4lpdub5a.aos.us-east-1.on.aws"
# es_username = "Cloudhw3"
# es_password = "Cloud*hw3"

# es = OpenSearch(
#     hosts=[{'host': es_endpoint, 'port': 443}],
#     http_auth=(es_username, es_password),
#     use_ssl=True,
#     verify_certs=True,
#     connection_class=RequestsHttpConnection
# )

# print("=== Testing OpenSearch Connection ===")
# try:
#     info = es.info()
#     print("OpenSearch info:", info)
# except Exception as e:
#     print("OpenSearch INFO ERROR:", str(e))



# def lambda_handler(event, context):
#     # Get the S3 bucket and key from the event
#     bucket = event['Records'][0]['s3']['bucket']['name']
#     key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'])

#     print("bucket:", bucket)
#     print("key:", key)

#     # Retrieve the object from S3
#     s3_object = s3.get_object(Bucket=bucket, Key=key)
#     image_bytes = s3_object['Body'].read()

#     rekognition_response = rekognition.detect_labels(
#         Image={'Bytes': image_bytes},
#         MaxLabels=10,
#         MinConfidence=80
#     )

#     rekognition_labels = [label['Name'] for label in rekognition_response['Labels']]

#     # Extract custom metadata labels
#     metadata = s3.head_object(Bucket=bucket, Key=key)
#     custom_labels = metadata['ResponseMetadata']['HTTPHeaders'].get('x-amz-meta-customlabels', '').split(',')
#     print("custom_labels:", custom_labels)
#     all_labels = custom_labels + rekognition_labels

#     print("all_labels:", all_labels)

#     if all_labels:
#         # Create document for ElasticSearch
#         document = {
#             "objectKey": key,
#             "bucket": bucket,
#             "createdTimestamp": datetime.now().isoformat(),
#             "labels": all_labels
#         }

#         print("Indexing images")

#         try:
#             response = es.index(
#                 index="photos",
#                 id=key,
#                 body=document,
#                 refresh=True
#             )
#             print("OpenSearch index response:", response)
#         except Exception as e:
#             print("ERROR indexing document:", str(e))


#     # Update the object in S3 with the original content
#     time.sleep(10)  # Delay to ensure operations are completed
#     s3.delete_object(Bucket=bucket, Key=key)
#     s3.put_object(Bucket=bucket, Body=decoded_content, Key=key, ContentType='image/jpg')

#     return {
#         'statusCode': 200,
#         'body': json.dumps('Photo indexed successfully')
#     }

import boto3
import json
import urllib.parse
from datetime import datetime
from opensearchpy import OpenSearch, RequestsHttpConnection

# Initialize clients
s3 = boto3.client('s3')
rekognition = boto3.client('rekognition', region_name='us-east-1')

# OpenSearch configuration
es_endpoint = "search-photos-cq5z5g57zek6qmvs5p4lpdub5a.aos.us-east-1.on.aws"
es_username = "Cloudhw3"
es_password = "Cloud*hw3"

es = OpenSearch(
    hosts=[{'host': es_endpoint, 'port': 443}],
    http_auth=(es_username, es_password),
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection
)


def lambda_handler(event, context):
    print("Received event:", json.dumps(event))

    # 1. Get the S3 bucket and key from the event
    record = event["Records"][0]
    bucket = record["s3"]["bucket"]["name"]
    key = urllib.parse.unquote_plus(record["s3"]["object"]["key"])

    print("Bucket:", bucket)
    print("Key:", key)

    # 2. Get the image bytes from S3
    s3_object = s3.get_object(Bucket=bucket, Key=key)
    image_bytes = s3_object["Body"].read()

    # 3. Detect labels using Rekognition
    rekognition_response = rekognition.detect_labels(
        Image={"Bytes": image_bytes},
        MaxLabels=10,
        MinConfidence=80
    )

    rekognition_labels = [label["Name"] for label in rekognition_response["Labels"]]
    print("Rekognition labels:", rekognition_labels)

    # 4. Extract custom labels from S3 object metadata
    head = s3.head_object(Bucket=bucket, Key=key)
    # When you upload with x-amz-meta-customLabels, S3 stores that as Metadata["customlabels"]
    metadata = head.get("Metadata", {})
    custom_labels_header = metadata.get("customlabels", "")  # lowercase key
    custom_labels = [
        lbl.strip()
        for lbl in custom_labels_header.split(",")
        if lbl.strip()
    ]

    print("Custom labels:", custom_labels)

    # 5. Combine all labels (avoid empty strings)
    all_labels = list({
        lbl for lbl in (rekognition_labels + custom_labels)
        if lbl
    })

    print("All labels:", all_labels)

    if not all_labels:
        print("No labels found, skipping indexing.")
        return {
            "statusCode": 200,
            "body": json.dumps("No labels found; document not indexed")
        }

    # 6. Build document for OpenSearch
    document = {
        "objectKey": key,
        "bucket": bucket,
        "createdTimestamp": datetime.utcnow().isoformat(),
        "labels": all_labels
    }

    print("Indexing document:", document)

    # 7. Index the document into OpenSearch
    try:
        response = es.index(
            index="photos",
            id=key,         # use S3 key as document id
            body=document,
            refresh=True
        )
        print("OpenSearch index response:", response)
    except Exception as e:
        print("ERROR indexing document:", str(e))
        return {
            "statusCode": 500,
            "body": json.dumps(f"Error indexing document: {str(e)}")
        }

    # 8. Return a simple success response (S3 event doesn't really care)
    return {
        "statusCode": 200,
        "body": json.dumps("Photo indexed successfully")
    }
