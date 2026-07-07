**Troubleshooting Guide - AI Customer Feedback Hub**

**📋 Table of Contents**

**Common Issues \& Solutions**



Form Submission Issues



Lambda Issues



DynamoDB Issues



API Gateway Issues



S3 Hosting Issues



Dashboard Issues



Terraform Issues



Error Codes Reference



Debugging Commands



Quick Fix Checklist



🔥 Common Issues \& Solutions

Issue 1: Form Submits but No Data in DynamoDB

Symptom	"✓ Thank you!" appears but nothing in DynamoDB

Cause	Incorrect table name or environment variable

Solution	Check Lambda environment variable TABLE\_NAME

Step-by-Step Fix:



Go to Lambda → cloudwithshad-process-feedback



Configuration → Environment variables



Check TABLE\_NAME = group6



If missing, add it and click Save



Issue 2: CORS Error in Browser

Symptom	Access-Control-Allow-Origin error in console

Cause	CORS not configured in API Gateway

Solution	Enable CORS in API Gateway

Step-by-Step Fix:



Go to API Gateway → cloudwithshad-feedback-api



Click CORS



Configure:



Allow origin: \*



Allow methods: POST, GET, OPTIONS



Allow headers: Content-Type



Click Save



Issue 3: Lambda Timeout

Symptom	Task timed out in CloudWatch logs

Cause	Lambda timeout too short (default 3s)

Solution	Increase timeout to 30 seconds

Step-by-Step Fix:



Go to Lambda → cloudwithshad-process-feedback



Configuration → General configuration



Click Edit



Timeout: Set to 30 seconds



Memory: Set to 256 MB



Click Save



📝 Form Submission Issues

Issue 1.1: "Failed to fetch" Error

Symptom	Failed to fetch in browser console

Cause 1	Wrong API URL in form

Cause 2	API Gateway not deployed

Cause 3	Network connectivity issue

Solution:



javascript

// Check your API URL in index.html

const API\_URL = 'https://YOUR-API-ID.execute-api.us-east-1.amazonaws.com/feedback';

Fix:



Verify API Gateway URL is correct



Ensure API is deployed



Check internet connection



Test API with curl:



bash

curl -X POST https://YOUR-API-ID.execute-api.us-east-1.amazonaws.com/feedback \\

&#x20; -H "Content-Type: application/json" \\

&#x20; -d '{"name":"Test","email":"test@test.com","message":"Test"}'

Issue 1.2: "404 Not Found"

Symptom	404 Not Found when submitting

Cause	Wrong path in API URL

Solution:



javascript

// ❌ WRONG - missing /feedback

const API\_URL = 'https://YOUR-API-ID.execute-api.us-east-1.amazonaws.com';



// ✅ CORRECT

const API\_URL = 'https://YOUR-API-ID.execute-api.us-east-1.amazonaws.com/feedback';

Issue 1.3: "Name 'feedback' is not defined"

Symptom	Python error in Lambda logs

Cause	Variable naming error in Lambda code

Solution:



python

\# ❌ WRONG - 'feedback' not defined

return {

&#x20;   'body': json.dumps({'id': feedback})  # ← error!

}



\# ✅ CORRECT - use 'feedback\_id'

return {

&#x20;   'body': json.dumps({'id': feedback\_id})  # ← correct!

}

⚡ Lambda Issues

Issue 2.1: "AccessDeniedException"

Symptom	AccessDeniedException in CloudWatch logs

Cause	IAM role missing required permissions

Solution:



Go to IAM → Roles → cloudwithshad-feedback-role



Permissions → Attach policies



Add these policies:



✅ AWSLambdaBasicExecutionRole



✅ AmazonDynamoDBFullAccess



✅ AmazonS3ReadOnlyAccess



Wait 30 seconds for propagation



Issue 2.2: "ResourceNotFoundException"

Symptom	ResourceNotFoundException in logs

Cause	DynamoDB table name is wrong

Solution:



Check DynamoDB table name in Lambda code:



python

\# ✅ Check this line

table = dynamo.Table('group6')  # Must match your table name

Verify environment variable:



python

TABLE\_NAME = os.environ.get('TABLE\_NAME', 'group6')

Confirm table exists:



bash

aws dynamodb list-tables --region us-east-1

Issue 2.3: "ValidationException"

Symptom	ValidationException when writing to DynamoDB

Cause	Partition key mismatch

Solution:



python

\# ❌ WRONG - key name doesn't match

item = {

&#x20;   'feedback\_id': feedback\_id,  # ← wrong!

}



\# ✅ CORRECT - key name matches table

item = {

&#x20;   'feedback-id': feedback\_id,  # ← matches DynamoDB!

}

🗄️ DynamoDB Issues

Issue 3.1: Table Not Found

Symptom	ResourceNotFoundException

Cause	Table doesn't exist

Solution:



bash

\# Create the table

aws dynamodb create-table \\

&#x20; --table-name group6 \\

&#x20; --attribute-definitions AttributeName=feedback-id,AttributeType=S \\

&#x20; --key-schema AttributeName=feedback-id,KeyType=HASH \\

&#x20; --billing-mode PAY\_PER\_REQUEST \\

&#x20; --region us-east-1

Issue 3.2: No Items Appear

Symptom	Table empty after submissions

Cause 1	Lambda not writing to DynamoDB

Cause 2	Wrong table name in Lambda

Solution:



Check Lambda logs for errors



Verify TABLE\_NAME environment variable



Test Lambda directly:



Lambda → cloudwithshad-process-feedback



Test tab



Create test event



Run test



Issue 3.3: "ConditionalCheckFailedException"

Symptom	Error in CloudWatch logs

Cause	Item already exists with same key

Solution:



Use uuid.uuid4() to generate unique IDs:



python

import uuid

feedback\_id = str(uuid.uuid4())

🔗 API Gateway Issues

Issue 4.1: "Invalid API Key"

Symptom	Invalid API Key error

Cause	API key required but not provided

Solution:



For this project, disable API keys:



API Gateway → Your API



Routes → Click route



Edit → API key required: Uncheck



Deploy API



Issue 4.2: "Missing Authentication Token"

Symptom	Missing Authentication Token error

Cause	API not deployed to a stage

Solution:



API Gateway → Your API



Click Deploy API



Stage: $default



Click Deploy



Issue 4.3: CORS Preflight Fails

Symptom	OPTIONS request fails

Cause	CORS not properly configured

Solution:



API Gateway → CORS



Configure:



json

{

&#x20; "allowOrigins": \["\*"],

&#x20; "allowMethods": \["POST", "GET", "OPTIONS"],

&#x20; "allowHeaders": \["Content-Type"]

}

In Lambda, handle OPTIONS:



python

if event.get('httpMethod') == 'OPTIONS':

&#x20;   return {'statusCode': 200, 'headers': CORS, 'body': ''}

📁 S3 Hosting Issues

Issue 5.1: 403 Forbidden

Symptom	403 Forbidden when accessing website

Cause	Bucket not public

Solution:



Add bucket policy:



json

{

&#x20; "Version": "2012-10-17",

&#x20; "Statement": \[

&#x20;   {

&#x20;     "Effect": "Allow",

&#x20;     "Principal": "\*",

&#x20;     "Action": "s3:GetObject",

&#x20;     "Resource": "arn:aws:s3:::YOUR-BUCKET-NAME/\*"

&#x20;   }

&#x20; ]

}

Issue 5.2: 404 Not Found

Symptom	404 Not Found for website

Cause 1	File name doesn't match index document

Cause 2	Static hosting not enabled

Solution:



S3 → Your bucket → Properties



Static website hosting → Enable



Index document: index.html or dashboard-glow.html



Save



📊 Dashboard Issues

Issue 6.1: Dashboard Shows No Data

Symptom	Dashboard loads but shows 0 data

Cause 1	No feedback submitted yet

Cause 2	API URL is wrong

Solution:



Submit feedback through form



Check API URL in dashboard:



javascript

const API\_URL = 'https://YOUR-API-ID.execute-api.us-east-1.amazonaws.com/stats';

Test API:



bash

curl https://YOUR-API-ID.execute-api.us-east-1.amazonaws.com/stats

Issue 6.2: Chart Not Rendering

Symptom	Dashboard loads but charts are blank

Cause	Chart.js failed to load

Solution:



Check these CDN links in your HTML:



html

<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>

<script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2.2.0/dist/chartjs-plugin-datalabels.min.js"></script>

🏗️ Terraform Issues

Issue 7.1: "Provider not installed"

Symptom	Provider not installed error

Cause	Terraform init not run

Solution:



bash

terraform init

Issue 7.2: "Bucket already exists"

Symptom	BucketAlreadyOwnedByYou error

Cause	Bucket name already taken

Solution:



Change bucket name in variables.tf:



hcl

variable "form\_bucket\_name" {

&#x20; default = "ccp-group6-UNIQUE-SUFFIX"  # Add random suffix

}

Run:



bash

terraform plan

terraform apply

Issue 7.3: "AccessDenied" in Terraform

Symptom	AccessDenied when applying

Cause	AWS credentials not configured

Solution:



bash

aws configure

\# Enter valid Access Key and Secret Key

📝 Error Codes Reference

Error Code	Meaning	Solution

400	Bad Request	Check request format

403	Forbidden	Check IAM permissions

404	Not Found	Check API URL and routes

500	Internal Error	Check Lambda logs

502	Bad Gateway	Check Lambda timeout

CORS	CORS Error	Configure CORS in API Gateway

ResourceNotFoundException	DynamoDB	Check table name and region

AccessDeniedException	IAM	Attach required policies

ValidationException	DynamoDB	Check partition key name

TimeoutError	Lambda	Increase timeout

🔍 Debugging Commands

AWS CLI Commands

bash

\# List DynamoDB tables

aws dynamodb list-tables --region us-east-1



\# Scan DynamoDB table

aws dynamodb scan --table-name group6 --region us-east-1



\# Get Lambda logs

aws logs describe-log-groups

aws logs get-log-events --log-group-name /aws/lambda/cloudwithshad-process-feedback



\# Test Lambda

aws lambda invoke \\

&#x20; --function-name cloudwithshad-process-feedback \\

&#x20; --payload '{"body":"{\\"name\\":\\"Test\\",\\"email\\":\\"test@test.com\\",\\"message\\":\\"Test\\"}","httpMethod":"POST"}' \\

&#x20; --region us-east-1 \\

&#x20; response.json



\# Test API Gateway

curl -X POST https://YOUR-API-ID.execute-api.us-east-1.amazonaws.com/feedback \\

&#x20; -H "Content-Type: application/json" \\

&#x20; -d '{"name":"Test","email":"test@test.com","message":"Testing"}'



curl https://YOUR-API-ID.execute-api.us-east-1.amazonaws.com/stats



\# Check S3 bucket

aws s3 ls s3://ccp-group6/

aws s3 cp s3://ccp-group6/index.html ./ --region us-east-1



\# Terraform commands

terraform init

terraform plan

terraform apply

terraform destroy

CloudWatch Logs

How to View:



Lambda → Your function → Monitor → View CloudWatch logs



Look for error messages (red text)



Check for:



ERROR or ❌ emojis



Python stack traces



Access denied messages



✅ Quick Fix Checklist

Form Not Working

API URL correct in index.html



CORS configured in API Gateway



API Gateway deployed



Lambda timeout: 30 seconds



Environment variable TABLE\_NAME=group6



Lambda Errors

IAM role has all required policies



DynamoDB table exists



Table name matches in code



Partition key is feedback-id



Code has no syntax errors



DynamoDB Empty

Lambda writing correctly



Environment variable set



Table name matches



Partition key matches



Dashboard Not Loading

API URL correct



S3 static hosting enabled



Bucket policy public



Chart.js CDN loading



Terraform Fails

AWS credentials configured



Terraform init ran



Bucket names unique



Valid IAM permissions



🆘 Still Stuck?

Step 1: Check CloudWatch Logs

bash

aws logs get-log-events \\

&#x20; --log-group-name /aws/lambda/cloudwithshad-process-feedback \\

&#x20; --limit 20

Step 2: Test Lambda Directly

Go to Lambda → Function



Test tab



Create test event



Click Test



Look at Execution result



Step 3: Check DynamoDB

bash

aws dynamodb scan --table-name group6 --region us-east-1

Step 4: Test API Gateway

bash

curl -X POST https://YOUR-API-ID.execute-api.us-east-1.amazonaws.com/feedback \\

&#x20; -H "Content-Type: application/json" \\

&#x20; -d '{"name":"Test","email":"test@test.com","message":"Testing"}'

Step 5: Recreate Resources

If all else fails:



Delete all resources



Start fresh with Terraform:



bash

terraform destroy -auto-approve

terraform apply -auto-approve

📚 Additional Resources

Resource	Link

AWS Lambda Docs	https://docs.aws.amazon.com/lambda

DynamoDB Docs	https://docs.aws.amazon.com/dynamodb

API Gateway Docs	https://docs.aws.amazon.com/apigateway

S3 Docs	https://docs.aws.amazon.com/s3

Terraform Docs	https://www.terraform.io/docs

Documentation Version: 1.0

Last Updated: July 2026

Author: Group 6

