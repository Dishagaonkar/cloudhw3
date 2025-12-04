import boto3
import json
import logging
import urllib
from opensearchpy import OpenSearch, RequestsHttpConnection
import time
import base64

# Configure logger for debugging
log_handler = logging.getLogger()

# Initialize AWS clients and OpenSearch connection
rekognition_client = boto3.client('rekognition', region_name='us-east-1')
s3_service = boto3.client('s3')

# ElasticSearch configuration
es_endpoint = "search-photos-cq5z5g57zek6qmvs5p4lpdub5a.aos.us-east-1.on.aws"
es_username = "Cloudhw3"
es_password = "Cloud*hw3"

search_client = OpenSearch(
    hosts=[{'host': es_endpoint, 'port': 443}],
    http_auth=(es_username, es_password),
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection
)

# Extract bucket name and object key from S3 event
def extract_s3_details(event):
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    object_key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'])
    log_handler.debug(f"Extracted bucket: {bucket_name}, object key: {object_key}")
    return bucket_name, object_key

# Index photo metadata and labels into OpenSearch
def index_photo_metadata(bucket_name, object_key, labels_list):
    log_handler.debug(f"Indexing object '{object_key}' from bucket '{bucket_name}' into OpenSearch")
    document_body = {
        'bucket': bucket_name,
        'key': object_key,
        'createdTimestamp': str(int(time.time())),
        'labels': labels_list
    }
    response = search_client.index(index="photo_metadata", id=object_key, body=document_body, refresh=True)
    log_handler.debug(f"OpenSearch indexing response: {response}")

# Lambda handler function
def lambda_handler(event, context):
    print("event ",event)
    bucket_name, object_key = extract_s3_details(event)
    log_handler.info(f"Processing object '{object_key}' from bucket '{bucket_name}'")

    # Retrieve the object from S3
    s3_object = s3_service.get_object(Bucket=bucket_name, Key=object_key)
    object_content = s3_object['Body'].read()
    decoded_content = base64.b64decode(object_content)

    # Detect labels using Rekognition
    rekognition_response = rekognition_client.detect_labels(
        Image={'Bytes': decoded_content},
        MaxLabels=10,
        MinConfidence=80
    )
    detected_labels = [label['Name'] for label in rekognition_response['Labels']]
    print(f"Detected labels from Rekognition: {detected_labels}")

    # Extract custom metadata labels
    metadata = s3_service.head_object(Bucket=bucket_name, Key=object_key)
    print("metadata", metadata)
    custom_labels = metadata['ResponseMetadata']['HTTPHeaders'].get('x-amz-meta-customlabels', '').split(',')
    print("custom labels", custom_labels)
    all_labels = custom_labels + detected_labels
    print(f"Aggregated labels: {all_labels}")

    # Save metadata and labels to OpenSearch
    if all_labels:
        index_photo_metadata(bucket_name, object_key, all_labels)
        print(f"Successfully indexed object '{object_key}'")

    # Update the object in S3 with the original content
    time.sleep(5)  # Delay to ensure operations are completed
    s3_service.delete_object(Bucket=bucket_name, Key=object_key)
    s3_service.put_object(Bucket=bucket_name, Body=decoded_content, Key=object_key, ContentType='image/jpg')
    print(f"Updated object '{object_key}' in S3")