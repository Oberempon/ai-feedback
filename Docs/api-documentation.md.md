**API Documentation (api-documentation.md)**

**Overview**

This API processes customer feedback using sentiment analysis and stores results in DynamoDB. It follows a serverless architecture with two main endpoints.



**Authentication**

All endpoints are public (no authentication required for this project)



CORS enabled for cross-origin requests from your S3-hosted frontend



**Base URL**

https://3sixpd12p6.execute-api.us-east-1.amazonaws.com

Endpoints

POST /feedback





Submit customer feedback for processing.



Request Headers:





Content-Type: application/json

Request Body:



json

{

&#x20; "name": "Bernard Arhin",

&#x20; "email": "arhinbenny1@gmail.com",

&#x20; "message": "The service was excellent!"

}

Response (200 OK):



json

{

&#x20; "success": true,

&#x20; "id": "abc-123-def",

&#x20; "sentiment": "POSITIVE"

}

Error Responses:



400 Bad Request: Missing required fields



500 Internal Server Error: Server-side error



GET /stats

Retrieve aggregated feedback analytics.



Response (200 OK):



json

{

&#x20; "total": 15,

&#x20; "sentiment\_breakdown": {

&#x20;   "POSITIVE": 8,

&#x20;   "NEUTRAL": 4,

&#x20;   "NEGATIVE": 3

&#x20; },

&#x20; "sentiment\_percentages": {

&#x20;   "POSITIVE": 53.3,

&#x20;   "NEUTRAL": 26.7,

&#x20;   "NEGATIVE": 20.0

&#x20; },

&#x20; "recent": \[

&#x20;   {

&#x20;     "feedback-id": "abc-123",

&#x20;     "name": "Bernard",

&#x20;     "message": "good experience",

&#x20;     "sentiment": "POSITIVE",

&#x20;     "submitted\_at": "2026-07-07T10:30:00Z"

&#x20;   }

&#x20; ]

}



