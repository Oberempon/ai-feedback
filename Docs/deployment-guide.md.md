#### 🖥️ Complete Console-Based Deployment Guide - AI Customer Feedback Hub

#### Step-by-Step AWS Console Walkthrough



###### 📋 Table of Contents

###### Create DynamoDB Table

###### 

###### Create IAM Role

###### 

###### Create Lambda 1 (Process Feedback)

###### 

###### Create Lambda 2 (Get Stats)

###### 

###### Configure API Gateway

###### 

###### Setup S3 Hosting

###### 

###### Update Environment Variables

###### 

###### Final Testing



Clean Up



1\. Create DynamoDB Table

Step 1.1: Navigate to DynamoDB

Log in to AWS Console



Search for DynamoDB in the top search bar



Click on DynamoDB



Step 1.2: Create Table

Click the Create table button (orange)



Table name: Enter group6



Partition key: Enter feedback-id



Data type: Select String from dropdown



Table settings: Leave as Default settings



Scroll down and click Create table



Step 1.3: Wait for Creation

Wait approximately 30 seconds for the table to become active



Status should change from "Creating" to "Active"



✅ Verification

Table is listed in your DynamoDB tables



Status shows "Active"



2\. Create IAM Role

Step 2.1: Navigate to IAM

Search for IAM in the top search bar



Click on IAM (Identity and Access Management)



Step 2.2: Create Role

In the left sidebar, click Roles



Click Create role (blue button)



Step 2.3: Select Trusted Entity

Trusted entity type: Select AWS service



Use case: Click the dropdown and select Lambda



Click Next



Step 2.4: Add Permissions

Search and check these policies one by one:



✅ AWSLambdaBasicExecutionRole



✅ AmazonDynamoDBFullAccess



✅ AmazonS3ReadOnlyAccess



How to add:



Type each policy name in the search bar



Check the box next to it



Repeat for all three



Click Next



Step 2.5: Name the Role

Role name: Enter group6-feedback-role



Description: (Optional) "Role for Lambda functions to process feedback"



Click Create role



✅ Verification

Role appears in the Roles list



Click on it to see attached policies



3\. Create Lambda 1 (Process Feedback)

Step 3.1: Navigate to Lambda

Search for Lambda in the top search bar



Click on Lambda



Step 3.2: Create Lambda Function

Click Create function (orange button)



Choose "Author from scratch"



Function name: Enter group6-process-feedback



Runtime: Select Python 3.12



Architecture: Leave x86\_64



Permissions: Expand "Change default execution role"



Execution role: Select "Use an existing role"



Existing role: Select group6-feedback-role



Click Create function



Step 3.3: Configure Timeout

Go to Configuration tab



Click General configuration (left sidebar)



Click Edit (top right)



Timeout: Change from 3 sec to 30 sec



Memory: Change to 256 MB



Click Save



Step 3.4: Add Environment Variable

In Configuration tab



Click Environment variables (left sidebar)



Click Edit



Click Add environment variable



Key: TABLE\_NAME



Value: group6



Click Save



Step 3.5: Paste the Code

Go to Code tab



Delete the default code (Ctrl+A, Delete)



Paste this code:



python

import boto3

import json

import uuid

import re

from datetime import datetime

import os



\# Configuration

TABLE\_NAME = os.environ.get('TABLE\_NAME', 'group6')

dynamo = boto3.resource('dynamodb')

table = dynamo.Table(TABLE\_NAME)



\# CORS Headers

CORS = {

&#x20;   'Access-Control-Allow-Origin': '\*',

&#x20;   'Access-Control-Allow-Headers': 'Content-Type',

&#x20;   'Access-Control-Allow-Methods': 'POST, OPTIONS',

}



\# Sentiment Word Lists

POSITIVE\_WORDS = {

&#x20;   'good', 'great', 'excellent', 'positive', 'happy', 'love', 'best',

&#x20;   'strong', 'success', 'improve', 'benefit', 'effective', 'reliable',

&#x20;   'recommend', 'pleased', 'satisfied', 'achieve', 'gain', 'advantage',

&#x20;   'opportunity', 'wonderful', 'amazing', 'awesome', 'fantastic',

&#x20;   'perfect', 'nice', 'helpful', 'friendly', 'brilliant'

}



NEGATIVE\_WORDS = {

&#x20;   'bad', 'poor', 'terrible', 'negative', 'hate', 'worst', 'awful',

&#x20;   'fail', 'failure', 'weak', 'problem', 'issue', 'difficult', 'delay',

&#x20;   'risk', 'loss', 'concern', 'disappointed', 'unable', 'error',

&#x20;   'broken', 'decline', 'complaint', 'horrible'

}



def analyze\_sentiment(text: str) -> str:

&#x20;   if not text or len(text.strip()) < 3:

&#x20;       return 'NEUTRAL'

&#x20;   words = re.findall(r"\[a-z']+", text.lower())

&#x20;   if not words:

&#x20;       return 'NEUTRAL'

&#x20;   pos\_count = sum(1 for w in words if w in POSITIVE\_WORDS)

&#x20;   neg\_count = sum(1 for w in words if w in NEGATIVE\_WORDS)

&#x20;   total = pos\_count + neg\_count

&#x20;   if total == 0:

&#x20;       return 'NEUTRAL'

&#x20;   pos\_ratio = pos\_count / total

&#x20;   neg\_ratio = neg\_count / total

&#x20;   if pos\_ratio > 0.6:

&#x20;       return 'POSITIVE'

&#x20;   elif neg\_ratio > 0.6:

&#x20;       return 'NEGATIVE'

&#x20;   elif pos\_ratio > 0 and neg\_ratio > 0 and abs(pos\_ratio - neg\_ratio) <= 0.25:

&#x20;       return 'MIXED'

&#x20;   elif pos\_ratio > neg\_ratio:

&#x20;       return 'POSITIVE'

&#x20;   elif neg\_ratio > pos\_ratio:

&#x20;       return 'NEGATIVE'

&#x20;   else:

&#x20;       return 'NEUTRAL'



def lambda\_handler(event, context):

&#x20;   print(f"📨 Event: {json.dumps(event)\[:500]}")

&#x20;   

&#x20;   if event.get('httpMethod') == 'OPTIONS':

&#x20;       return {'statusCode': 200, 'headers': CORS, 'body': ''}

&#x20;   

&#x20;   try:

&#x20;       body = json.loads(event.get('body', '{}'))

&#x20;       name = body.get('name', 'Anonymous').strip()

&#x20;       email = body.get('email', '').strip()

&#x20;       message = body.get('message', '').strip()\[:5000]

&#x20;       

&#x20;       if not message:

&#x20;           return {

&#x20;               'statusCode': 400,

&#x20;               'headers': CORS,

&#x20;               'body': json.dumps({'error': 'Message is required'})

&#x20;           }

&#x20;       

&#x20;       sentiment = analyze\_sentiment(message)

&#x20;       feedback\_id = str(uuid.uuid4())

&#x20;       timestamp = datetime.utcnow().isoformat()

&#x20;       

&#x20;       table.put\_item(Item={

&#x20;           'feedback-id': feedback\_id,

&#x20;           'name': name,

&#x20;           'email': email,

&#x20;           'message': message,

&#x20;           'sentiment': sentiment,

&#x20;           'submitted\_at': timestamp

&#x20;       })

&#x20;       

&#x20;       return {

&#x20;           'statusCode': 200,

&#x20;           'headers': CORS,

&#x20;           'body': json.dumps({

&#x20;               'success': True,

&#x20;               'id': feedback\_id,

&#x20;               'sentiment': sentiment

&#x20;           })

&#x20;       }

&#x20;       

&#x20;   except Exception as e:

&#x20;       print(f"❌ Error: {str(e)}")

&#x20;       return {

&#x20;           'statusCode': 500,

&#x20;           'headers': CORS,

&#x20;           'body': json.dumps({'error': str(e)})

&#x20;       }

Click Deploy (blue button)



✅ Verification

Check Code tab shows your code



Configuration shows timeout: 30s, memory: 256MB



Environment variables shows TABLE\_NAME=group6



4\. Create Lambda 2 (Get Stats)

Step 4.1: Create Second Lambda

Lambda → Create function



Author from scratch



Function name: group6-get-stats



Runtime: Python 3.12



Permissions: Use existing role → group6-feedback-role



Click Create function



Step 4.2: Configure Timeout

Configuration → General configuration → Edit



Timeout: 10 seconds



Memory: 128 MB



Click Save



Step 4.3: Add Environment Variable

Configuration → Environment variables → Edit



Add environment variable



Key: TABLE\_NAME



Value: group6



Click Save



Step 4.4: Paste Stats Code

Go to Code tab



Delete default code



Paste this:



python

import boto3

import json

from collections import Counter

from decimal import Decimal

from datetime import datetime

import os



\# Configuration

TABLE\_NAME = os.environ.get('TABLE\_NAME', 'group6')

dynamo = boto3.resource('dynamodb')

table = dynamo.Table(TABLE\_NAME)



\# CORS Headers

CORS = {

&#x20;   'Access-Control-Allow-Origin': '\*',

&#x20;   'Access-Control-Allow-Headers': 'Content-Type',

&#x20;   'Access-Control-Allow-Methods': 'GET, OPTIONS',

}



class DecimalEncoder(json.JSONEncoder):

&#x20;   def default(self, obj):

&#x20;       if isinstance(obj, Decimal):

&#x20;           return float(obj)

&#x20;       if isinstance(obj, datetime):

&#x20;           return obj.isoformat()

&#x20;       return super().default(obj)



def lambda\_handler(event, context):

&#x20;   print(f"📨 Event: {json.dumps(event)\[:500]}")

&#x20;   

&#x20;   if event.get('httpMethod') == 'OPTIONS':

&#x20;       return {'statusCode': 200, 'headers': CORS, 'body': ''}

&#x20;   

&#x20;   try:

&#x20;       response = table.scan()

&#x20;       items = response.get('Items', \[])

&#x20;       total = len(items)

&#x20;       

&#x20;       sentiment\_counts = Counter()

&#x20;       for item in items:

&#x20;           sentiment = item.get('sentiment', 'UNKNOWN')

&#x20;           sentiment\_counts\[sentiment] += 1

&#x20;       

&#x20;       sentiment\_percentages = {}

&#x20;       for sentiment, count in sentiment\_counts.items():

&#x20;           sentiment\_percentages\[sentiment] = round((count / total) \* 100, 1) if total > 0 else 0

&#x20;       

&#x20;       recent = sorted(

&#x20;           items,

&#x20;           key=lambda x: x.get('submitted\_at', ''),

&#x20;           reverse=True

&#x20;       )\[:10]

&#x20;       

&#x20;       return {

&#x20;           'statusCode': 200,

&#x20;           'headers': CORS,

&#x20;           'body': json.dumps({

&#x20;               'total': total,

&#x20;               'sentiment\_breakdown': dict(sentiment\_counts),

&#x20;               'sentiment\_percentages': sentiment\_percentages,

&#x20;               'recent': recent

&#x20;           }, cls=DecimalEncoder)

&#x20;       }

&#x20;       

&#x20;   except Exception as e:

&#x20;       print(f"❌ Error: {str(e)}")

&#x20;       return {

&#x20;           'statusCode': 500,

&#x20;           'headers': CORS,

&#x20;           'body': json.dumps({'error': str(e)})

&#x20;       }

Click Deploy



5\. Configure API Gateway

Step 5.1: Create HTTP API

Search for API Gateway



Click Create API



Select HTTP API → Build



API name: group6-feedback-api



Click Next



Step 5.2: Configure Routes

Method: POST



Resource path: /feedback



Integration target: Select group6-process-feedback



Click Next



Step 5.3: Add Another Route

Click Add another route



Method: GET



Resource path: /stats



Integration target: Select group6-get-stats



Click Next



Step 5.4: Configure Stage

Stage name: $default



Click Next



Review and click Create



Step 5.5: Copy API URL

After creation, look at the Invoke URL at the top



Copy this URL - you'll need it!



Example: https://abcdef123.execute-api.us-east-1.amazonaws.com



Step 5.6: Configure CORS

In your API page, click CORS (left sidebar)



Click Configure



Allow origin: \*



Allow methods: Check POST, GET, OPTIONS



Allow headers: Content-Type



Click Save



Step 5.7: Deploy API

Click Deploy API (top right)



Stage: Select $default



Click Deploy



6\. Setup S3 Hosting

Step 6.1: Create Form Bucket

Search for S3



Click Create bucket



Bucket name: ccp-group6



Region: us-east-1



Block Public Access: Uncheck "Block all public access"



Check "I acknowledge..." checkbox



Click Create bucket



Step 6.2: Create Dashboard Bucket

Create bucket again



Bucket name: dashboardgroup6



Region: us-east-1



Block Public Access: Uncheck



Check acknowledgment



Click Create bucket



Step 6.3: Enable Static Hosting for Form Bucket

Click ccp-group6 bucket



Properties tab



Scroll to Static website hosting



Click Edit



Enable: Select "Host a static website"



Index document: index.html



Click Save



Step 6.4: Enable Static Hosting for Dashboard Bucket

Click dashboardgroup6 bucket



Properties → Static website hosting → Edit



Enable: "Host a static website"



Index document: dashboard-glow.html



Click Save



Step 6.5: Make Form Bucket Public

Click ccp-group6 bucket



Permissions tab



Bucket policy → Edit



Paste this:



json

{

&#x20; "Version": "2012-10-17",

&#x20; "Statement": \[

&#x20;   {

&#x20;     "Effect": "Allow",

&#x20;     "Principal": "\*",

&#x20;     "Action": "s3:GetObject",

&#x20;     "Resource": "arn:aws:s3:::ccp-group6/\*"

&#x20;   }

&#x20; ]

}

Click Save



Step 6.6: Make Dashboard Bucket Public

Click dashboardgroup6 bucket



Permissions → Bucket policy → Edit



Paste this:



json

{

&#x20; "Version": "2012-10-17",

&#x20; "Statement": \[

&#x20;   {

&#x20;     "Effect": "Allow",

&#x20;     "Principal": "\*",

&#x20;     "Action": "s3:GetObject",

&#x20;     "Resource": "arn:aws:s3:::dashboardgroup6/\*"

&#x20;   }

&#x20; ]

}

Click Save



Step 6.7: Upload Frontend Files

Step 6.7.1: Create index.html file on your computer



Create index.html:



html

<!DOCTYPE html>

<html lang="en">

<head>

&#x20;   <meta charset="UTF-8" />

&#x20;   <meta name="viewport" content="width=device-width, initial-scale=1.0" />

&#x20;   <title>Group 6 · Feedback</title>

&#x20;   <style>

&#x20;       \* { margin: 0; padding: 0; box-sizing: border-box; }

&#x20;       body {

&#x20;           font-family: 'Inter', -apple-system, sans-serif;

&#x20;           background: #0f172a;

&#x20;           color: #f1f5f9;

&#x20;           min-height: 100vh;

&#x20;           display: flex;

&#x20;           align-items: center;

&#x20;           justify-content: center;

&#x20;           padding: 20px;

&#x20;       }

&#x20;       .container {

&#x20;           max-width: 500px;

&#x20;           width: 100%;

&#x20;           background: #1e293b;

&#x20;           padding: 40px;

&#x20;           border-radius: 20px;

&#x20;           border: 1px solid #334155;

&#x20;           box-shadow: 0 20px 60px rgba(0,0,0,0.5);

&#x20;       }

&#x20;       h1 { color: #38bdf8; margin-bottom: 8px; font-size: 28px; }

&#x20;       .subtitle { color: #94a3b8; margin-bottom: 30px; font-size: 14px; }

&#x20;       label { display: block; margin: 20px 0 8px; font-weight: 600; color: #cbd5e1; }

&#x20;       input, textarea {

&#x20;           width: 100%;

&#x20;           padding: 12px 16px;

&#x20;           border-radius: 10px;

&#x20;           border: 1px solid #334155;

&#x20;           background: #0f172a;

&#x20;           color: #f1f5f9;

&#x20;           font-size: 14px;

&#x20;           transition: all 0.3s;

&#x20;       }

&#x20;       input:focus, textarea:focus { border-color: #38bdf8; outline: none; }

&#x20;       textarea { min-height: 120px; resize: vertical; }

&#x20;       button {

&#x20;           width: 100%;

&#x20;           padding: 14px;

&#x20;           background: linear-gradient(135deg, #38bdf8, #3b82f6);

&#x20;           color: #0f172a;

&#x20;           border: none;

&#x20;           border-radius: 10px;

&#x20;           font-weight: 700;

&#x20;           font-size: 16px;

&#x20;           cursor: pointer;

&#x20;           margin-top: 24px;

&#x20;           transition: transform 0.2s;

&#x20;       }

&#x20;       button:hover { transform: scale(1.02); }

&#x20;       button:disabled { opacity: 0.6; cursor: not-allowed; }

&#x20;       #status { margin-top: 16px; padding: 12px; border-radius: 8px; text-align: center; }

&#x20;       .success { background: #064e3b; color: #6ee7b7; }

&#x20;       .error { background: #7f1d1d; color: #fca5a5; }

&#x20;       .sentiment-preview {

&#x20;           margin-top: 12px;

&#x20;           padding: 12px 16px;

&#x20;           border-radius: 8px;

&#x20;           border: 1px solid #334155;

&#x20;           background: #0f172a;

&#x20;           display: none;

&#x20;       }

&#x20;       .sentiment-preview.visible { display: block; }

&#x20;       .sentiment-preview .label { font-size: 12px; color: #94a3b8; }

&#x20;       .sentiment-preview .value { font-size: 18px; font-weight: 700; }

&#x20;       .sentiment-preview.positive .value { color: #34d399; }

&#x20;       .sentiment-preview.neutral .value { color: #fbbf24; }

&#x20;       .sentiment-preview.negative .value { color: #f87171; }

&#x20;       .sentiment-preview.mixed .value { color: #a78bfa; }

&#x20;   </style>

</head>

<body>

&#x20;   <div class="container">

&#x20;       <h1>📊 Group 6 Feedback</h1>

&#x20;       <p class="subtitle">Your voice helps us improve</p>



&#x20;       <form id="feedbackForm">

&#x20;           <label>Full Name</label>

&#x20;           <input type="text" id="name" placeholder="Enter your name" required />



&#x20;           <label>Email Address</label>

&#x20;           <input type="email" id="email" placeholder="your@email.com" required />



&#x20;           <label>Your Feedback</label>

&#x20;           <textarea id="message" placeholder="Tell us about your experience..." required></textarea>



&#x20;           <div class="sentiment-preview" id="sentimentPreview">

&#x20;               <div class="label">Live Sentiment Analysis</div>

&#x20;               <div class="value" id="sentimentValue">—</div>

&#x20;           </div>



&#x20;           <button type="submit" id="submitBtn">Submit Feedback</button>

&#x20;           <div id="status"></div>

&#x20;       </form>

&#x20;   </div>



&#x20;   <script>

&#x20;       // ⚠️ UPDATE THIS URL after deploying API Gateway

&#x20;       const API\_URL = 'https://YOUR\_API\_ID.execute-api.us-east-1.amazonaws.com/feedback';



&#x20;       const form = document.getElementById('feedbackForm');

&#x20;       const nameInput = document.getElementById('name');

&#x20;       const emailInput = document.getElementById('email');

&#x20;       const messageInput = document.getElementById('message');

&#x20;       const submitBtn = document.getElementById('submitBtn');

&#x20;       const statusDiv = document.getElementById('status');

&#x20;       const sentimentPreview = document.getElementById('sentimentPreview');

&#x20;       const sentimentValue = document.getElementById('sentimentValue');



&#x20;       // Simple sentiment detection (for preview only)

&#x20;       const POSITIVE = \['good', 'great', 'excellent', 'amazing', 'love', 'best', 'awesome', 'fantastic'];

&#x20;       const NEGATIVE = \['bad', 'poor', 'terrible', 'awful', 'hate', 'worst', 'horrible'];



&#x20;       messageInput.addEventListener('input', function() {

&#x20;           const text = this.value.toLowerCase();

&#x20;           if (text.length < 3) {

&#x20;               sentimentPreview.classList.remove('visible');

&#x20;               return;

&#x20;           }



&#x20;           let positive = POSITIVE.filter(w => text.includes(w)).length;

&#x20;           let negative = NEGATIVE.filter(w => text.includes(w)).length;



&#x20;           sentimentPreview.classList.add('visible');

&#x20;           if (positive > negative \&\& positive > 0) {

&#x20;               sentimentValue.textContent = '😊 POSITIVE';

&#x20;               sentimentPreview.className = 'sentiment-preview visible positive';

&#x20;           } else if (negative > positive \&\& negative > 0) {

&#x20;               sentimentValue.textContent = '😔 NEGATIVE';

&#x20;               sentimentPreview.className = 'sentiment-preview visible negative';

&#x20;           } else if (positive > 0 \&\& negative > 0) {

&#x20;               sentimentValue.textContent = '🤔 MIXED';

&#x20;               sentimentPreview.className = 'sentiment-preview visible mixed';

&#x20;           } else {

&#x20;               sentimentValue.textContent = '😐 NEUTRAL';

&#x20;               sentimentPreview.className = 'sentiment-preview visible neutral';

&#x20;           }

&#x20;       });



&#x20;       form.addEventListener('submit', async (e) => {

&#x20;           e.preventDefault();

&#x20;           submitBtn.disabled = true;

&#x20;           submitBtn.textContent = 'Submitting...';

&#x20;           statusDiv.className = '';



&#x20;           const data = {

&#x20;               name: nameInput.value.trim(),

&#x20;               email: emailInput.value.trim(),

&#x20;               message: messageInput.value.trim()

&#x20;           };



&#x20;           try {

&#x20;               const res = await fetch(API\_URL, {

&#x20;                   method: 'POST',

&#x20;                   headers: { 'Content-Type': 'application/json' },

&#x20;                   body: JSON.stringify(data)

&#x20;               });



&#x20;               const result = await res.json();



&#x20;               if (res.ok) {

&#x20;                   statusDiv.textContent = '✅ Thank you! Feedback submitted.';

&#x20;                   statusDiv.className = 'success';

&#x20;                   form.reset();

&#x20;                   sentimentPreview.classList.remove('visible');

&#x20;               } else {

&#x20;                   throw new Error(result.error || 'Submission failed');

&#x20;               }

&#x20;           } catch (error) {

&#x20;               statusDiv.textContent = '❌ ' + error.message;

&#x20;               statusDiv.className = 'error';

&#x20;           } finally {

&#x20;               submitBtn.disabled = false;

&#x20;               submitBtn.textContent = 'Submit Feedback';

&#x20;           }

&#x20;       });

&#x20;   </script>

</body>

</html>

Step 6.7.2: Create dashboard-glow.html



html

<!DOCTYPE html>

<html lang="en">

<head>

&#x20;   <meta charset="UTF-8" />

&#x20;   <meta name="viewport" content="width=device-width, initial-scale=1.0" />

&#x20;   <title>Group 6 · Dashboard</title>

&#x20;   <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800\&display=swap" rel="stylesheet" />

&#x20;   <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css" />

&#x20;   <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>

&#x20;   <style>

&#x20;       \* { margin: 0; padding: 0; box-sizing: border-box; }

&#x20;       body {

&#x20;           font-family: 'Inter', -apple-system, sans-serif;

&#x20;           background: #0f172a;

&#x20;           color: #f1f5f9;

&#x20;           padding: 40px 20px;

&#x20;           min-height: 100vh;

&#x20;       }

&#x20;       .container { max-width: 1200px; margin: 0 auto; }

&#x20;       h1 { color: #38bdf8; font-size: 32px; margin-bottom: 4px; }

&#x20;       .subtitle { color: #94a3b8; margin-bottom: 30px; }

&#x20;       .stats-grid {

&#x20;           display: grid;

&#x20;           grid-template-columns: repeat(4, 1fr);

&#x20;           gap: 20px;

&#x20;           margin-bottom: 30px;

&#x20;       }

&#x20;       .stat-card {

&#x20;           background: #1e293b;

&#x20;           padding: 24px;

&#x20;           border-radius: 16px;

&#x20;           border: 1px solid #334155;

&#x20;       }

&#x20;       .stat-card .label { color: #94a3b8; font-size: 13px; text-transform: uppercase; }

&#x20;       .stat-card .number { font-size: 32px; font-weight: 800; color: #38bdf8; margin-top: 6px; }

&#x20;       .stat-card.positive .number { color: #34d399; }

&#x20;       .stat-card.neutral .number { color: #fbbf24; }

&#x20;       .stat-card.negative .number { color: #f87171; }

&#x20;       .charts-grid {

&#x20;           display: grid;

&#x20;           grid-template-columns: 1fr 1fr;

&#x20;           gap: 20px;

&#x20;           margin-bottom: 30px;

&#x20;       }

&#x20;       .chart-card {

&#x20;           background: #1e293b;

&#x20;           padding: 24px;

&#x20;           border-radius: 16px;

&#x20;           border: 1px solid #334155;

&#x20;       }

&#x20;       .chart-card h3 { color: #cbd5e1; margin-bottom: 4px; }

&#x20;       .chart-card p { color: #94a3b8; font-size: 13px; margin-bottom: 16px; }

&#x20;       .chart-wrapper { height: 250px; }

&#x20;       .table-card {

&#x20;           background: #1e293b;

&#x20;           padding: 24px;

&#x20;           border-radius: 16px;

&#x20;           border: 1px solid #334155;

&#x20;       }

&#x20;       .table-card h3 { margin-bottom: 16px; color: #cbd5e1; }

&#x20;       table { width: 100%; border-collapse: collapse; }

&#x20;       th { text-align: left; padding: 12px 14px; color: #94a3b8; border-bottom: 1px solid #334155; font-size: 12px; text-transform: uppercase; }

&#x20;       td { padding: 12px 14px; border-bottom: 1px solid #1e293b; color: #cbd5e1; }

&#x20;       .badge {

&#x20;           padding: 4px 12px;

&#x20;           border-radius: 20px;

&#x20;           font-size: 12px;

&#x20;           font-weight: 600;

&#x20;           display: inline-block;

&#x20;       }

&#x20;       .badge.POSITIVE { background: #064e3b; color: #6ee7b7; }

&#x20;       .badge.NEGATIVE { background: #7f1d1d; color: #fca5a5; }

&#x20;       .badge.NEUTRAL { background: #1e3a5f; color: #93c5fd; }

&#x20;       .badge.MIXED { background: #78350f; color: #fcd34d; }

&#x20;       .refresh-btn {

&#x20;           background: #38bdf8;

&#x20;           color: #0f172a;

&#x20;           border: none;

&#x20;           padding: 10px 24px;

&#x20;           border-radius: 10px;

&#x20;           font-weight: 700;

&#x20;           cursor: pointer;

&#x20;           margin-bottom: 20px;

&#x20;           transition: all 0.3s;

&#x20;       }

&#x20;       .refresh-btn:hover { background: #3b82f6; transform: translateY(-2px); }

&#x20;       .empty { text-align: center; padding: 40px; color: #94a3b8; }

&#x20;       .empty i { font-size: 48px; margin-bottom: 12px; opacity: 0.5; }

&#x20;       @media (max-width: 768px) {

&#x20;           .stats-grid { grid-template-columns: 1fr 1fr; }

&#x20;           .charts-grid { grid-template-columns: 1fr; }

&#x20;       }

&#x20;   </style>

</head>

<body>

&#x20;   <div class="container">

&#x20;       <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;">

&#x20;           <div>

&#x20;               <h1>📊 Group 6 Analytics</h1>

&#x20;               <p class="subtitle">Real-time feedback insights</p>

&#x20;           </div>

&#x20;           <button class="refresh-btn" onclick="fetchData()">🔄 Refresh</button>

&#x20;       </div>



&#x20;       <div class="stats-grid" id="statsGrid">

&#x20;           <div class="stat-card"><div class="label">Total Feedback</div><div class="number" id="total">0</div></div>

&#x20;           <div class="stat-card positive"><div class="label">Positive</div><div class="number" id="positive">0</div></div>

&#x20;           <div class="stat-card neutral"><div class="label">Neutral</div><div class="number" id="neutral">0</div></div>

&#x20;           <div class="stat-card negative"><div class="label">Negative</div><div class="number" id="negative">0</div></div>

&#x20;       </div>



&#x20;       <div class="charts-grid">

&#x20;           <div class="chart-card">

&#x20;               <h3>Sentiment Distribution</h3>

&#x20;               <p>Customer sentiment breakdown</p>

&#x20;               <div class="chart-wrapper"><canvas id="sentimentChart"></canvas></div>

&#x20;           </div>

&#x20;           <div class="chart-card" id="insightsCard">

&#x20;               <h3>📊 Key Insights</h3>

&#x20;               <p>Summary at a glance</p>

&#x20;               <div id="insights" style="padding:10px 0;"></div>

&#x20;           </div>

&#x20;       </div>



&#x20;       <div class="table-card">

&#x20;           <h3>📝 Recent Feedback</h3>

&#x20;           <div style="overflow-x:auto;">

&#x20;               <table>

&#x20;                   <thead>

&#x20;                       <tr><th>Name</th><th>Message</th><th>Sentiment</th><th>Date</th></tr>

&#x20;                   </thead>

&#x20;                   <tbody id="feedbackTable"></tbody>

&#x20;               </table>

&#x20;           </div>

&#x20;       </div>

&#x20;   </div>



&#x20;   <script>

&#x20;       // ⚠️ UPDATE THIS URL after deploying API Gateway

&#x20;       const API\_URL = 'https://YOUR\_API\_ID.execute-api.us-east-1.amazonaws.com/stats';

&#x20;       let sentimentChart;



&#x20;       function formatDate(ts) {

&#x20;           if (!ts) return '—';

&#x20;           return new Date(ts).toLocaleString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });

&#x20;       }



&#x20;       function getBadge(sentiment) {

&#x20;           const cls = sentiment || 'NEUTRAL';

&#x20;           const label = sentiment || 'Unknown';

&#x20;           return `<span class="badge ${cls}">${label}</span>`;

&#x20;       }



&#x20;       function renderInsights(data) {

&#x20;           const total = data.total || 0;

&#x20;           const breakdown = data.sentiment\_breakdown || {};

&#x20;           

&#x20;           if (total === 0) {

&#x20;               return '<div class="empty"><i class="fas fa-inbox"></i><p>No feedback yet</p></div>';

&#x20;           }



&#x20;           const positive = breakdown.POSITIVE || 0;

&#x20;           const neutral = breakdown.NEUTRAL || 0;

&#x20;           const negative = breakdown.NEGATIVE || 0;

&#x20;           const positivePct = ((positive / total) \* 100).toFixed(1);

&#x20;           const neutralPct = ((neutral / total) \* 100).toFixed(1);

&#x20;           const negativePct = ((negative / total) \* 100).toFixed(1);



&#x20;           let insight = '';

&#x20;           if (positivePct > 50) insight = '✅ Customers are happy!';

&#x20;           else if (negativePct > 50) insight = '⚠️ Needs attention!';

&#x20;           else if (neutralPct > 50) insight = '📊 Room for improvement';

&#x20;           else insight = '📊 Mixed feedback';



&#x20;           return `

&#x20;               <div style="padding:12px 0;border-bottom:1px solid #334155;">

&#x20;                   <span style="font-size:14px;color:#cbd5e1;">${insight}</span>

&#x20;                   <div style="display:flex;gap:20px;margin-top:8px;flex-wrap:wrap;">

&#x20;                       <div><span style="color:#34d399;">●</span> Positive: ${positive} (${positivePct}%)</div>

&#x20;                       <div><span style="color:#fbbf24;">●</span> Neutral: ${neutral} (${neutralPct}%)</div>

&#x20;                       <div><span style="color:#f87171;">●</span> Negative: ${negative} (${negativePct}%)</div>

&#x20;                   </div>

&#x20;               </div>

&#x20;           `;

&#x20;       }



&#x20;       async function fetchData() {

&#x20;           try {

&#x20;               const res = await fetch(API\_URL);

&#x20;               const data = await res.json();



&#x20;               // Update stats

&#x20;               document.getElementById('total').textContent = data.total || 0;

&#x20;               const breakdown = data.sentiment\_breakdown || {};

&#x20;               document.getElementById('positive').textContent = breakdown.POSITIVE || 0;

&#x20;               document.getElementById('neutral').textContent = breakdown.NEUTRAL || 0;

&#x20;               document.getElementById('negative').textContent = breakdown.NEGATIVE || 0;



&#x20;               // Update insights

&#x20;               document.getElementById('insights').innerHTML = renderInsights(data);



&#x20;               // Update chart

&#x20;               const ctx = document.getElementById('sentimentChart').getContext('2d');

&#x20;               const labels = \['Positive', 'Neutral', 'Negative'];

&#x20;               const values = \[

&#x20;                   breakdown.POSITIVE || 0,

&#x20;                   breakdown.NEUTRAL || 0,

&#x20;                   breakdown.NEGATIVE || 0

&#x20;               ];

&#x20;               const colors = \['#34d399', '#fbbf24', '#f87171'];



&#x20;               if (sentimentChart) sentimentChart.destroy();



&#x20;               if (values.every(v => v === 0)) {

&#x20;                   sentimentChart = new Chart(ctx, {

&#x20;                       type: 'doughnut',

&#x20;                       data: {

&#x20;                           labels: \['No Data'],

&#x20;                           datasets: \[{

&#x20;                               data: \[1],

&#x20;                               backgroundColor: \['rgba(148, 163, 184, 0.2)'],

&#x20;                               borderColor: '#1e293b',

&#x20;                               borderWidth: 3

&#x20;                           }]

&#x20;                       },

&#x20;                       options: {

&#x20;                           responsive: true,

&#x20;                           maintainAspectRatio: false,

&#x20;                           plugins: { legend: { labels: { color: '#94a3b8' } } }

&#x20;                       }

&#x20;                   });

&#x20;               } else {

&#x20;                   sentimentChart = new Chart(ctx, {

&#x20;                       type: 'doughnut',

&#x20;                       data: {

&#x20;                           labels: labels,

&#x20;                           datasets: \[{

&#x20;                               data: values,

&#x20;                               backgroundColor: colors,

&#x20;                               borderColor: '#1e293b',

&#x20;                               borderWidth: 3

&#x20;                           }]

&#x20;                       },

&#x20;                       options: {

&#x20;                           responsive: true,

&#x20;                           maintainAspectRatio: false,

&#x20;                           plugins: {

&#x20;                               legend: { 

&#x20;                                   position: 'bottom',

&#x20;                                   labels: { color: '#94a3b8', padding: 20 }

&#x20;                               }

&#x20;                           }

&#x20;                       }

&#x20;                   });

&#x20;               }



&#x20;               // Update table

&#x20;               const recent = data.recent || \[];

&#x20;               const tbody = document.getElementById('feedbackTable');

&#x20;               if (recent.length === 0) {

&#x20;                   tbody.innerHTML = `

&#x20;                       <tr><td colspan="4" class="empty">

&#x20;                           <i class="fas fa-inbox"></i>

&#x20;                           <p>No feedback yet</p>

&#x20;                       </td></tr>

&#x20;                   `;

&#x20;               } else {

&#x20;                   tbody.innerHTML = recent.map(item => `

&#x20;                       <tr>

&#x20;                           <td>${item.name || 'Anonymous'}</td>

&#x20;                           <td style="max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">${item.message || '—'}</td>

&#x20;                           <td>${getBadge(item.sentiment)}</td>

&#x20;                           <td>${formatDate(item.submitted\_at)}</td>

&#x20;                       </tr>

&#x20;                   `).join('');

&#x20;               }



&#x20;           } catch (error) {

&#x20;               console.error('Error fetching data:', error);

&#x20;               document.getElementById('feedbackTable').innerHTML = `

&#x20;                   <tr><td colspan="4" style="text-align:center;padding:40px;color:#f87171;">

&#x20;                       ❌ Error loading data. Check your API URL.

&#x20;                   </td></tr>

&#x20;               `;

&#x20;           }

&#x20;       }



&#x20;       // Load data on page load

&#x20;       fetchData();

&#x20;       // Refresh every 30 seconds

&#x20;       setInterval(fetchData, 30000);

&#x20;   </script>

</body>

</html>

Step 6.7.3: Update API URLs in both files



Find this line in both files:



javascript

const API\_URL = 'https://YOUR\_API\_ID.execute-api.us-east-1.amazonaws.com/feedback';

Replace YOUR\_API\_ID with your actual API ID from API Gateway.



Step 6.7.4: Upload to S3



Go to ccp-group6 bucket → Upload



Click Add files



Select index.html



Click Upload



Go to dashboardgroup6 bucket → Upload



Click Add files



Select dashboard-glow.html



Click Upload



Step 6.8: Get Your URLs

Form URL:



text

http://ccp-group6.s3-website-us-east-1.amazonaws.com

Dashboard URL:



text

http://dashboardgroup6.s3-website-us-east-1.amazonaws.com/dashboard-glow.html

7\. Update Environment Variables

Step 7.1: Lambda 1

Go to Lambda → group6-process-feedback



Configuration → Environment variables



Click Edit



Confirm TABLE\_NAME=group6 is set



Click Save



Step 7.2: Lambda 2

Go to Lambda → group6-get-stats



Configuration → Environment variables



Click Edit



Confirm TABLE\_NAME=group6 is set



Click Save



8\. Final Testing

Test 8.1: Test Lambda Functions

Test Lambda 1:



Go to Lambda → group6-process-feedback



Test tab



Click Create new event



Event name: test-event



Paste this:



json

{

&#x20; "httpMethod": "POST",

&#x20; "body": "{\\"name\\":\\"Bernard\\",\\"email\\":\\"test@test.com\\",\\"message\\":\\"Great service!\\"}"

}

Click Test



✅ Should show "succeeded" with response



Test Lambda 2:



Go to Lambda → group6-get-stats



Test tab



Create new event



Event name: test-stats



Paste this:



json

{

&#x20; "httpMethod": "GET"

}

Click Test



✅ Should show "succeeded" with stats



Test 8.2: Test API Endpoints

Go to API Gateway → group6-feedback-api



Routes tab



Click POST /feedback



Test (if available) or use Postman



OR use curl (in terminal):



bash

curl -X POST https://YOUR\_API\_ID.execute-api.us-east-1.amazonaws.com/feedback \\

&#x20; -H "Content-Type: application/json" \\

&#x20; -d '{"name":"Test","email":"test@test.com","message":"Amazing experience!"}'

Test 8.3: Test Frontend

Open form URL: http://ccp-group6.s3-website-us-east-1.amazonaws.com



Submit feedback



Check DynamoDB: Go to DynamoDB → group6 → Explore table items → Scan



Open dashboard: http://dashboardgroup6.s3-website-us-east-1.amazonaws.com/dashboard-glow.html



✅ Data should appear!



9\. Clean Up

Step 9.1: Delete Lambda Functions

Go to Lambda



Select group6-process-feedback



Actions → Delete



Confirm



Repeat for group6-get-stats



Step 9.2: Delete API Gateway

Go to API Gateway



Select group6-feedback-api



Actions → Delete



Confirm



Step 9.3: Delete DynamoDB Table

Go to DynamoDB



Select group6



Click Delete table



Confirm



Step 9.4: Delete S3 Buckets

Go to S3



Select ccp-group6 → Empty → Delete



Select dashboardgroup6 → Empty → Delete



Step 9.5: Delete IAM Role

Go to IAM → Roles



Select group6-feedback-role



Delete



Confirm



✅ Access URLs

Component	URL

Feedback Form	http://ccp-group6.s3-website-us-east-1.amazonaws.com

Admin Dashboard	http://dashboardgroup6.s3-website-us-east-1.amazonaws.com/dashboard-glow.html

API Base URL	https://YOUR\_API\_ID.execute-api.us-east-1.amazonaws.com

POST Endpoint	https://YOUR\_API\_ID.execute-api.us-east-1.amazonaws.com/feedback

GET Endpoint	https://YOUR\_API\_ID.execute-api.us-east-1.amazonaws.com/stats

🎉 Success!

Your AI Customer Feedback Hub is now fully deployed using only the AWS Console! 🚀



Quick Reference

Form URL: http://ccp-group6.s3-website-us-east-1.amazonaws.com

Dashboard URL: http://dashboardgroup6.s3-website-us-east-1.amazonaws.com/dashboard-glow.html



Next Steps:



Share the form URL with customers



Check dashboard for real-time analytics



Export data for reporting



Documentation version: 1.0 | Last updated: July 2026



text



\---



\## 📥 How to Use This Guide



\### Option 1: Copy and Save

1\. Select \*\*all the text above\*\* (Ctrl+A)

2\. Copy (Ctrl+C)

3\. Open Notepad or VS Code

4\. Paste (Ctrl+V)

5\. Save as `console-deployment-guide.md`



\### Option 2: Download as .md

1\. Go to: https://downgit.github.io/

2\. Paste this entire text

3\. Download as .md file



\### Option 3: View as PDF

1\. Copy the text

2\. Paste into Google Docs

3\. File → Download → PDF (.pdf)



\---



\*\*Now you have the complete console-based deployment guide!\*\*





















#### **With Terraform**







📁 Project Structure

text

ai-feedback-hub-terraform/

├── main.tf              # Main resources

├── variables.tf         # Variables

├── outputs.tf           # Outputs

├── providers.tf         # Provider configuration

├── lambda/

│   ├── process\_feedback/

│   │   └── lambda\_function.py

│   └── get\_stats/

│       └── lambda\_function.py

└── frontend/

&#x20;   ├── index.html

&#x20;   └── dashboard-glow.html

1\. Provider Configuration (providers.tf)

hcl

terraform {

&#x20; required\_providers {

&#x20;   aws = {

&#x20;     source  = "hashicorp/aws"

&#x20;     version = "\~> 5.0"

&#x20;   }

&#x20;   random = {

&#x20;     source  = "hashicorp/random"

&#x20;     version = "\~> 3.0"

&#x20;   }

&#x20;   archive = {

&#x20;     source  = "hashicorp/archive"

&#x20;     version = "\~> 2.0"

&#x20;   }

&#x20; }

}



provider "aws" {

&#x20; region = var.aws\_region

}

2\. Variables (variables.tf)

hcl

variable "aws\_region" {

&#x20; description = "AWS region for all resources"

&#x20; type        = string

&#x20; default     = "us-east-1"

}



variable "project\_name" {

&#x20; description = "Project name for resource naming"

&#x20; type        = string

&#x20; default     = "feedback-hub"

}



variable "environment" {

&#x20; description = "Environment name"

&#x20; type        = string

&#x20; default     = "prod"

}



variable "dynamodb\_table\_name" {

&#x20; description = "DynamoDB table name"

&#x20; type        = string

&#x20; default     = "group6"

}



variable "form\_bucket\_name" {

&#x20; description = "S3 bucket name for feedback form"

&#x20; type        = string

&#x20; default     = "ccp-group6"

}



variable "dashboard\_bucket\_name" {

&#x20; description = "S3 bucket name for dashboard"

&#x20; type        = string

&#x20; default     = "dashboardgroup6"

}



variable "lambda\_role\_name" {

&#x20; description = "IAM role name for Lambda"

&#x20; type        = string

&#x20; default     = "cloudwithshad-feedback-role"

}



variable "api\_name" {

&#x20; description = "API Gateway name"

&#x20; type        = string

&#x20; default     = "cloudwithshad-feedback-api"

}



variable "api\_stage" {

&#x20; description = "API Gateway stage"

&#x20; type        = string

&#x20; default     = "$default"

}

3\. Main Resources (main.tf)

DynamoDB Table

hcl

\# ============================================

\# DYNAMODB TABLE

\# ============================================

resource "aws\_dynamodb\_table" "feedback" {

&#x20; name           = var.dynamodb\_table\_name

&#x20; billing\_mode   = "PAY\_PER\_REQUEST"

&#x20; hash\_key       = "feedback-id"



&#x20; attribute {

&#x20;   name = "feedback-id"

&#x20;   type = "S"

&#x20; }



&#x20; tags = {

&#x20;   Name        = "Feedback Table"

&#x20;   Project     = var.project\_name

&#x20;   Environment = var.environment

&#x20; }

}

IAM Role for Lambda

hcl

\# ============================================

\# IAM ROLE FOR LAMBDA

\# ============================================

data "aws\_iam\_policy\_document" "lambda\_assume\_role" {

&#x20; statement {

&#x20;   effect = "Allow"

&#x20;   principals {

&#x20;     type        = "Service"

&#x20;     identifiers = \["lambda.amazonaws.com"]

&#x20;   }

&#x20;   actions = \["sts:AssumeRole"]

&#x20; }

}



resource "aws\_iam\_role" "lambda\_role" {

&#x20; name               = var.lambda\_role\_name

&#x20; assume\_role\_policy = data.aws\_iam\_policy\_document.lambda\_assume\_role.json



&#x20; tags = {

&#x20;   Project     = var.project\_name

&#x20;   Environment = var.environment

&#x20; }

}



\# Attach policies

resource "aws\_iam\_role\_policy\_attachment" "lambda\_basic" {

&#x20; role       = aws\_iam\_role.lambda\_role.name

&#x20; policy\_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"

}



resource "aws\_iam\_role\_policy\_attachment" "lambda\_dynamodb" {

&#x20; role       = aws\_iam\_role.lambda\_role.name

&#x20; policy\_arn = "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess"

}



resource "aws\_iam\_role\_policy\_attachment" "lambda\_s3" {

&#x20; role       = aws\_iam\_role.lambda\_role.name

&#x20; policy\_arn = "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"

}



\# Custom policy for Lambda to write to specific resources

resource "aws\_iam\_policy" "lambda\_custom" {

&#x20; name        = "lambda-feedback-custom-policy"

&#x20; description = "Custom policy for feedback Lambda functions"



&#x20; policy = jsonencode({

&#x20;   Version = "2012-10-17"

&#x20;   Statement = \[

&#x20;     {

&#x20;       Effect = "Allow"

&#x20;       Action = \[

&#x20;         "dynamodb:PutItem",

&#x20;         "dynamodb:Scan",

&#x20;         "dynamodb:Query",

&#x20;         "dynamodb:GetItem",

&#x20;         "dynamodb:UpdateItem",

&#x20;         "dynamodb:DeleteItem"

&#x20;       ]

&#x20;       Resource = aws\_dynamodb\_table.feedback.arn

&#x20;     }

&#x20;   ]

&#x20; })

}



resource "aws\_iam\_role\_policy\_attachment" "lambda\_custom" {

&#x20; role       = aws\_iam\_role.lambda\_role.name

&#x20; policy\_arn = aws\_iam\_policy.lambda\_custom.arn

}

Lambda Functions

hcl

\# ============================================

\# LAMBDA 1 - PROCESS FEEDBACK

\# ============================================

data "archive\_file" "lambda1\_zip" {

&#x20; type        = "zip"

&#x20; source\_file = "lambda/process\_feedback/lambda\_function.py"

&#x20; output\_path = "lambda1\_payload.zip"

}



resource "aws\_lambda\_function" "process\_feedback" {

&#x20; filename         = data.archive\_file.lambda1\_zip.output\_path

&#x20; function\_name    = "cloudwithshad-process-feedback"

&#x20; role             = aws\_iam\_role.lambda\_role.arn

&#x20; handler          = "lambda\_function.lambda\_handler"

&#x20; runtime          = "python3.12"

&#x20; timeout          = 30

&#x20; memory\_size      = 256



&#x20; environment {

&#x20;   variables = {

&#x20;     TABLE\_NAME = var.dynamodb\_table\_name

&#x20;   }

&#x20; }



&#x20; depends\_on = \[

&#x20;   aws\_iam\_role\_policy\_attachment.lambda\_basic,

&#x20;   aws\_iam\_role\_policy\_attachment.lambda\_dynamodb,

&#x20;   aws\_iam\_role\_policy\_attachment.lambda\_custom

&#x20; ]



&#x20; tags = {

&#x20;   Name        = "Process Feedback"

&#x20;   Project     = var.project\_name

&#x20;   Environment = var.environment

&#x20; }

}



\# ============================================

\# LAMBDA 2 - GET STATS

\# ============================================

data "archive\_file" "lambda2\_zip" {

&#x20; type        = "zip"

&#x20; source\_file = "lambda/get\_stats/lambda\_function.py"

&#x20; output\_path = "lambda2\_payload.zip"

}



resource "aws\_lambda\_function" "get\_stats" {

&#x20; filename         = data.archive\_file.lambda2\_zip.output\_path

&#x20; function\_name    = "cloudwithshad-get-stats"

&#x20; role             = aws\_iam\_role.lambda\_role.arn

&#x20; handler          = "lambda\_function.lambda\_handler"

&#x20; runtime          = "python3.12"

&#x20; timeout          = 10

&#x20; memory\_size      = 128



&#x20; environment {

&#x20;   variables = {

&#x20;     TABLE\_NAME = var.dynamodb\_table\_name

&#x20;   }

&#x20; }



&#x20; depends\_on = \[

&#x20;   aws\_iam\_role\_policy\_attachment.lambda\_basic,

&#x20;   aws\_iam\_role\_policy\_attachment.lambda\_dynamodb,

&#x20;   aws\_iam\_role\_policy\_attachment.lambda\_custom

&#x20; ]



&#x20; tags = {

&#x20;   Name        = "Get Stats"

&#x20;   Project     = var.project\_name

&#x20;   Environment = var.environment

&#x20; }

}

API Gateway 

hcl

\# ============================================

\# API GATEWAY - HTTP API

\# ============================================

resource "aws\_apigatewayv2\_api" "feedback\_api" {

&#x20; name          = var.api\_name

&#x20; protocol\_type = "HTTP"



&#x20; cors\_configuration {

&#x20;   allow\_origins     = \["\*"]

&#x20;   allow\_methods     = \["POST", "GET", "OPTIONS"]

&#x20;   allow\_headers     = \["Content-Type"]

&#x20;   expose\_headers    = \["\*"]

&#x20;   max\_age           = 300

&#x20; }



&#x20; tags = {

&#x20;   Project     = var.project\_name

&#x20;   Environment = var.environment

&#x20; }

}



\# Integration 1: POST /feedback

resource "aws\_apigatewayv2\_integration" "process\_feedback" {

&#x20; api\_id = aws\_apigatewayv2\_api.feedback\_api.id



&#x20; integration\_type = "AWS\_PROXY"

&#x20; integration\_uri  = aws\_lambda\_function.process\_feedback.invoke\_arn

&#x20; integration\_method = "POST"

&#x20; payload\_format\_version = "2.0"

}



\# Integration 2: GET /stats

resource "aws\_apigatewayv2\_integration" "get\_stats" {

&#x20; api\_id = aws\_apigatewayv2\_api.feedback\_api.id



&#x20; integration\_type = "AWS\_PROXY"

&#x20; integration\_uri  = aws\_lambda\_function.get\_stats.invoke\_arn

&#x20; integration\_method = "POST"

&#x20; payload\_format\_version = "2.0"

}



\# Route: POST /feedback

resource "aws\_apigatewayv2\_route" "feedback\_route" {

&#x20; api\_id = aws\_apigatewayv2\_api.feedback\_api.id



&#x20; route\_key = "POST /feedback"

&#x20; target    = "integrations/${aws\_apigatewayv2\_integration.process\_feedback.id}"

}



\# Route: GET /stats

resource "aws\_apigatewayv2\_route" "stats\_route" {

&#x20; api\_id = aws\_apigatewayv2\_api.feedback\_api.id



&#x20; route\_key = "GET /stats"

&#x20; target    = "integrations/${aws\_apigatewayv2\_integration.get\_stats.id}"

}



\# Stage

resource "aws\_apigatewayv2\_stage" "default" {

&#x20; api\_id = aws\_apigatewayv2\_api.feedback\_api.id

&#x20; name   = var.api\_stage

&#x20; auto\_deploy = true

}



\# Lambda Permissions for API Gateway

resource "aws\_lambda\_permission" "apigw\_process" {

&#x20; statement\_id  = "AllowAPIGatewayInvokeProcess"

&#x20; action        = "lambda:InvokeFunction"

&#x20; function\_name = aws\_lambda\_function.process\_feedback.function\_name

&#x20; principal     = "apigateway.amazonaws.com"

&#x20; source\_arn    = "${aws\_apigatewayv2\_api.feedback\_api.execution\_arn}/\*/POST/feedback"

}



resource "aws\_lambda\_permission" "apigw\_stats" {

&#x20; statement\_id  = "AllowAPIGatewayInvokeStats"

&#x20; action        = "lambda:InvokeFunction"

&#x20; function\_name = aws\_lambda\_function.get\_stats.function\_name

&#x20; principal     = "apigateway.amazonaws.com"

&#x20; source\_arn    = "${aws\_apigatewayv2\_api.feedback\_api.execution\_arn}/\*/GET/stats"

}

S3 Buckets

hcl

\# ============================================

\# S3 BUCKETS - Static Hosting

\# ============================================



\# Form Bucket

resource "aws\_s3\_bucket" "form\_bucket" {

&#x20; bucket        = var.form\_bucket\_name

&#x20; force\_destroy = true



&#x20; tags = {

&#x20;   Name        = "Feedback Form"

&#x20;   Project     = var.project\_name

&#x20;   Environment = var.environment

&#x20; }

}



\# Dashboard Bucket

resource "aws\_s3\_bucket" "dashboard\_bucket" {

&#x20; bucket        = var.dashboard\_bucket\_name

&#x20; force\_destroy = true



&#x20; tags = {

&#x20;   Name        = "Feedback Dashboard"

&#x20;   Project     = var.project\_name

&#x20;   Environment = var.environment

&#x20; }

}



\# Enable Static Website Hosting

resource "aws\_s3\_bucket\_website\_configuration" "form\_website" {

&#x20; bucket = aws\_s3\_bucket.form\_bucket.id



&#x20; index\_document {

&#x20;   suffix = "index.html"

&#x20; }

}



resource "aws\_s3\_bucket\_website\_configuration" "dashboard\_website" {

&#x20; bucket = aws\_s3\_bucket.dashboard\_bucket.id



&#x20; index\_document {

&#x20;   suffix = "dashboard-glow.html"

&#x20; }

}



\# Make Buckets Public

resource "aws\_s3\_bucket\_public\_access\_block" "form\_public" {

&#x20; bucket = aws\_s3\_bucket.form\_bucket.id



&#x20; block\_public\_acls       = false

&#x20; block\_public\_policy     = false

&#x20; ignore\_public\_acls      = false

&#x20; restrict\_public\_buckets = false

}



resource "aws\_s3\_bucket\_public\_access\_block" "dashboard\_public" {

&#x20; bucket = aws\_s3\_bucket.dashboard\_bucket.id



&#x20; block\_public\_acls       = false

&#x20; block\_public\_policy     = false

&#x20; ignore\_public\_acls      = false

&#x20; restrict\_public\_buckets = false

}



\# Bucket Policies

resource "aws\_s3\_bucket\_policy" "form\_policy" {

&#x20; bucket = aws\_s3\_bucket.form\_bucket.id

&#x20; policy = jsonencode({

&#x20;   Version = "2012-10-17"

&#x20;   Statement = \[

&#x20;     {

&#x20;       Effect    = "Allow"

&#x20;       Principal = "\*"

&#x20;       Action    = "s3:GetObject"

&#x20;       Resource  = "${aws\_s3\_bucket.form\_bucket.arn}/\*"

&#x20;     }

&#x20;   ]

&#x20; })

&#x20; depends\_on = \[aws\_s3\_bucket\_public\_access\_block.form\_public]

}



resource "aws\_s3\_bucket\_policy" "dashboard\_policy" {

&#x20; bucket = aws\_s3\_bucket.dashboard\_bucket.id

&#x20; policy = jsonencode({

&#x20;   Version = "2012-10-17"

&#x20;   Statement = \[

&#x20;     {

&#x20;       Effect    = "Allow"

&#x20;       Principal = "\*"

&#x20;       Action    = "s3:GetObject"

&#x20;       Resource  = "${aws\_s3\_bucket.dashboard\_bucket.arn}/\*"

&#x20;     }

&#x20;   ]

&#x20; })

&#x20; depends\_on = \[aws\_s3\_bucket\_public\_access\_block.dashboard\_public]

}



\# Upload Frontend Files

resource "aws\_s3\_object" "index\_html" {

&#x20; bucket       = aws\_s3\_bucket.form\_bucket.id

&#x20; key          = "index.html"

&#x20; source       = "${path.module}/frontend/index.html"

&#x20; content\_type = "text/html"

&#x20; etag         = filemd5("${path.module}/frontend/index.html")

&#x20; depends\_on   = \[aws\_s3\_bucket\_public\_access\_block.form\_public]

}



resource "aws\_s3\_object" "dashboard\_html" {

&#x20; bucket       = aws\_s3\_bucket.dashboard\_bucket.id

&#x20; key          = "dashboard-glow.html"

&#x20; source       = "${path.module}/frontend/dashboard-glow.html"

&#x20; content\_type = "text/html"

&#x20; etag         = filemd5("${path.module}/frontend/dashboard-glow.html")

&#x20; depends\_on   = \[aws\_s3\_bucket\_public\_access\_block.dashboard\_public]

}

4\. Outputs (outputs.tf)

hcl

\# ============================================

\# OUTPUTS

\# ============================================

output "api\_gateway\_url" {

&#x20; description = "API Gateway base URL"

&#x20; value       = aws\_apigatewayv2\_api.feedback\_api.api\_endpoint

}



output "feedback\_form\_url" {

&#x20; description = "URL for the customer feedback form"

&#x20; value       = aws\_s3\_bucket\_website\_configuration.form\_website.website\_endpoint

}



output "dashboard\_url" {

&#x20; description = "URL for the admin dashboard"

&#x20; value       = aws\_s3\_bucket\_website\_configuration.dashboard\_website.website\_endpoint

}



output "dynamodb\_table\_name" {

&#x20; description = "DynamoDB table name"

&#x20; value       = aws\_dynamodb\_table.feedback.name

}



output "post\_feedback\_url" {

&#x20; description = "POST endpoint for submitting feedback"

&#x20; value       = "${aws\_apigatewayv2\_api.feedback\_api.api\_endpoint}/feedback"

}



output "get\_stats\_url" {

&#x20; description = "GET endpoint for dashboard stats"

&#x20; value       = "${aws\_apigatewayv2\_api.feedback\_api.api\_endpoint}/stats"

}

5\. Lambda Code Files

Lambda 1: lambda/process\_feedback/lambda\_function.py

python

import boto3

import json

import uuid

import re

from datetime import datetime

import os



\# Configuration

TABLE\_NAME = os.environ.get('TABLE\_NAME', 'group6')

dynamo = boto3.resource('dynamodb')

table = dynamo.Table(TABLE\_NAME)



\# CORS Headers

CORS = {

&#x20;   'Access-Control-Allow-Origin': '\*',

&#x20;   'Access-Control-Allow-Headers': 'Content-Type',

&#x20;   'Access-Control-Allow-Methods': 'POST, OPTIONS',

}



\# Sentiment Word Lists

POSITIVE\_WORDS = {

&#x20;   'good', 'great', 'excellent', 'positive', 'happy', 'love', 'best',

&#x20;   'strong', 'success', 'improve', 'benefit', 'effective', 'reliable',

&#x20;   'recommend', 'pleased', 'satisfied', 'achieve', 'gain', 'advantage',

&#x20;   'opportunity', 'wonderful', 'amazing', 'awesome', 'fantastic',

&#x20;   'perfect', 'nice', 'helpful', 'friendly', 'brilliant'

}



NEGATIVE\_WORDS = {

&#x20;   'bad', 'poor', 'terrible', 'negative', 'hate', 'worst', 'awful',

&#x20;   'fail', 'failure', 'weak', 'problem', 'issue', 'difficult', 'delay',

&#x20;   'risk', 'loss', 'concern', 'disappointed', 'unable', 'error',

&#x20;   'broken', 'decline', 'complaint', 'horrible'

}



def analyze\_sentiment(text: str) -> str:

&#x20;   if not text or len(text.strip()) < 3:

&#x20;       return 'NEUTRAL'

&#x20;   words = re.findall(r"\[a-z']+", text.lower())

&#x20;   if not words:

&#x20;       return 'NEUTRAL'

&#x20;   pos\_count = sum(1 for w in words if w in POSITIVE\_WORDS)

&#x20;   neg\_count = sum(1 for w in words if w in NEGATIVE\_WORDS)

&#x20;   total = pos\_count + neg\_count

&#x20;   if total == 0:

&#x20;       return 'NEUTRAL'

&#x20;   pos\_ratio = pos\_count / total

&#x20;   neg\_ratio = neg\_count / total

&#x20;   if pos\_ratio > 0.6:

&#x20;       return 'POSITIVE'

&#x20;   elif neg\_ratio > 0.6:

&#x20;       return 'NEGATIVE'

&#x20;   elif pos\_ratio > 0 and neg\_ratio > 0 and abs(pos\_ratio - neg\_ratio) <= 0.25:

&#x20;       return 'MIXED'

&#x20;   elif pos\_ratio > neg\_ratio:

&#x20;       return 'POSITIVE'

&#x20;   elif neg\_ratio > pos\_ratio:

&#x20;       return 'NEGATIVE'

&#x20;   else:

&#x20;       return 'NEUTRAL'



def lambda\_handler(event, context):

&#x20;   print(f"📨 Event: {json.dumps(event)\[:500]}")

&#x20;   

&#x20;   if event.get('httpMethod') == 'OPTIONS':

&#x20;       return {'statusCode': 200, 'headers': CORS, 'body': ''}

&#x20;   

&#x20;   try:

&#x20;       body = json.loads(event.get('body', '{}'))

&#x20;       name = body.get('name', 'Anonymous').strip()

&#x20;       email = body.get('email', '').strip()

&#x20;       message = body.get('message', '').strip()\[:5000]

&#x20;       

&#x20;       if not message:

&#x20;           return {

&#x20;               'statusCode': 400,

&#x20;               'headers': CORS,

&#x20;               'body': json.dumps({'error': 'Message is required'})

&#x20;           }

&#x20;       

&#x20;       sentiment = analyze\_sentiment(message)

&#x20;       feedback\_id = str(uuid.uuid4())

&#x20;       timestamp = datetime.utcnow().isoformat()

&#x20;       

&#x20;       table.put\_item(Item={

&#x20;           'feedback-id': feedback\_id,

&#x20;           'name': name,

&#x20;           'email': email,

&#x20;           'message': message,

&#x20;           'sentiment': sentiment,

&#x20;           'submitted\_at': timestamp

&#x20;       })

&#x20;       

&#x20;       return {

&#x20;           'statusCode': 200,

&#x20;           'headers': CORS,

&#x20;           'body': json.dumps({

&#x20;               'success': True,

&#x20;               'id': feedback\_id,

&#x20;               'sentiment': sentiment

&#x20;           })

&#x20;       }

&#x20;       

&#x20;   except Exception as e:

&#x20;       print(f"❌ Error: {str(e)}")

&#x20;       return {

&#x20;           'statusCode': 500,

&#x20;           'headers': CORS,

&#x20;           'body': json.dumps({'error': str(e)})

&#x20;       }

Lambda 2: lambda/get\_stats/lambda\_function.py

python

import boto3

import json

from collections import Counter

from decimal import Decimal

from datetime import datetime

import os



\# Configuration

TABLE\_NAME = os.environ.get('TABLE\_NAME', 'group6')

dynamo = boto3.resource('dynamodb')

table = dynamo.Table(TABLE\_NAME)



\# CORS Headers

CORS = {

&#x20;   'Access-Control-Allow-Origin': '\*',

&#x20;   'Access-Control-Allow-Headers': 'Content-Type',

&#x20;   'Access-Control-Allow-Methods': 'GET, OPTIONS',

}



class DecimalEncoder(json.JSONEncoder):

&#x20;   def default(self, obj):

&#x20;       if isinstance(obj, Decimal):

&#x20;           return float(obj)

&#x20;       if isinstance(obj, datetime):

&#x20;           return obj.isoformat()

&#x20;       return super().default(obj)



def lambda\_handler(event, context):

&#x20;   print(f"📨 Event: {json.dumps(event)\[:500]}")

&#x20;   

&#x20;   if event.get('httpMethod') == 'OPTIONS':

&#x20;       return {'statusCode': 200, 'headers': CORS, 'body': ''}

&#x20;   

&#x20;   try:

&#x20;       response = table.scan()

&#x20;       items = response.get('Items', \[])

&#x20;       total = len(items)

&#x20;       

&#x20;       sentiment\_counts = Counter()

&#x20;       for item in items:

&#x20;           sentiment = item.get('sentiment', 'UNKNOWN')

&#x20;           sentiment\_counts\[sentiment] += 1

&#x20;       

&#x20;       sentiment\_percentages = {}

&#x20;       for sentiment, count in sentiment\_counts.items():

&#x20;           sentiment\_percentages\[sentiment] = round((count / total) \* 100, 1) if total > 0 else 0

&#x20;       

&#x20;       recent = sorted(

&#x20;           items,

&#x20;           key=lambda x: x.get('submitted\_at', ''),

&#x20;           reverse=True

&#x20;       )\[:10]

&#x20;       

&#x20;       return {

&#x20;           'statusCode': 200,

&#x20;           'headers': CORS,

&#x20;           'body': json.dumps({

&#x20;               'total': total,

&#x20;               'sentiment\_breakdown': dict(sentiment\_counts),

&#x20;               'sentiment\_percentages': sentiment\_percentages,

&#x20;               'recent': recent

&#x20;           }, cls=DecimalEncoder)

&#x20;       }

&#x20;       

&#x20;   except Exception as e:

&#x20;       print(f"❌ Error: {str(e)}")

&#x20;       return {

&#x20;           'statusCode': 500,

&#x20;           'headers': CORS,

&#x20;           'body': json.dumps({'error': str(e)})

&#x20;       }

6\. Frontend Files (frontend/)

Copy your index.html and dashboard-glow.html files to this folder. Update the API URLs in both files:



In index.html:



javascript

const API\_URL = '${aws\_apigatewayv2\_api.feedback\_api.api\_endpoint}/feedback';

In dashboard-glow.html:



javascript

const API\_URL = '${aws\_apigatewayv2\_api.feedback\_api.api\_endpoint}/stats';

7\. Deployment Steps

Step 1: Create the Project Structure

bash

\# Create project folder

mkdir ai-feedback-hub-terraform

cd ai-feedback-hub-terraform



\# Create subfolders

mkdir -p lambda/process\_feedback lambda/get\_stats frontend



\# Create all files as shown above

Step 2: Configure AWS Credentials

bash

aws configure

\# Enter your Access Key, Secret Key, region (us-east-1)

Step 3: Initialize Terraform

bash

terraform init

Step 4: Plan the Deployment

bash

terraform plan

Step 5: Apply the Configuration

bash

terraform apply -auto-approve

Step 6: Get the URLs

bash

terraform output

8\. Clean Up

bash

terraform destroy -auto-approve

✅ Access URLs

After deployment, you'll get:



Component	URL

Feedback Form	http://ccp-group6.s3-website-us-east-1.amazonaws.com

Admin Dashboard	http://dashboardgroup6.s3-website-us-east-1.amazonaws.com/dashboard-glow.html

API Base URL	https://your-api-id.execute-api.us-east-1.amazonaws.com

POST Endpoint	https://your-api-id.execute-api.us-east-1.amazonaws.com/feedback

GET Endpoint	https://your-api-id.execute-api.us-east-1.amazonaws.com/stats

🎉 Success!

Your entire infrastructure is now managed as code using Terraform . This approach:



Version Controls your infrastructure 



Automates the entire deployment 



Eliminates manual AWS Console clicks



Enables team collaboration through Git



Makes rollbacks simple and predictable



Next Steps:



Commit all files to GitHub



Share with your group mate



They can clone and run terraform apply to deploy the exact same infrastructure!



Add to your portfolio as Infrastructure as Code example



Your AI Customer Feedback Hub is now fully managed with Terraform! 🚀

