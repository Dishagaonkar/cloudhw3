Photo Album Application A cloud-based photo album application that enables users to upload images and search through them using natural language queries. The application leverages AWS services including Rekognition for image analysis, Lex for natural language processing, and OpenSearch for efficient image retrieval.

Architecture Overview The application follows a serverless architecture pattern using the following AWS services:

S3: Stores the frontend assets and image files Lambda: Handles image indexing and search functionality API Gateway: Provides REST API endpoints Amazon Lex: Processes natural language search queries Amazon Rekognition: Detects objects and scenes in images OpenSearch Service: Indexes and searches image metadata CloudFormation: Defines infrastructure as code CodePipeline: Automates deployment workflows

Features Image Upload: Upload photos with custom labels Image Analysis: Automatic object and scene detection using Amazon Rekognition Natural Language Search: Search photos using conversational language Responsive UI: Modern, responsive interface for browsing and searching photos

API Reference The application exposes the following API endpoints:

PUT /upload/{bucket}/{filename} Uploads an image to the S3 bucket.

Path Parameters:

bucket: The S3 bucket name (e.g., "my-b2-photos") filename: The name of the file to be uploaded Headers:

Content-Type: image/jpeg (or other image types) x-amz-meta-customLabels: Comma-separated list of custom labels GET /search Searches for photos based on query text.

Parameters:

q: Search query (e.g., "Show me pictures of dogs")


s3 link: http://photo-frontend-hw3.s3-website-us-east-1.amazonaws.com
