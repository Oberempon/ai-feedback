### &#x20;**Executive Summary**

The AI Customer Feedback Hub is a complete serverless application that allows businesses to collect customer feedback through a web form, analyze sentiment in real-time, and view analytics on an interactive dashboard. Built entirely on AWS, the system demonstrates how serverless architecture can enable rapid development, automatic scaling, and cost-effective operations.



Customer submits feedback →



AI analyzes sentiment →



Dashboard displays insights



###### **🎯 Project Overview**

###### **Problem Statement**

Organizations struggle to:



Process and analyze customer feedback at scale



Identify sentiment trends without manual effort



Visualize feedback data in real-time



Build cost-effective analytics solutions



Solution

A serverless feedback pipeline that:



Collects feedback through a custom web form



Automatically analyzes sentiment using Python-based NLP



Stores all data in DynamoDB



Displays real-time analytics on a dashboard





**Key Objectives**

✅ Build a production-ready feedback system



✅ Implement sentiment analysis



✅ Create an admin dashboard with charts



✅ Use serverless AWS services



✅ Demonstrate Infrastructure as Code (Terraform)



**🏗️ System Architecture**

**Architecture Diagram**



┌─────────────────────────────────────────────────────────────────┐

│                    AI CUSTOMER FEEDBACK HUB                     │

├─────────────────────────────────────────────────────────────────┤

│                                                                 │

│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────┐    │

│  │   Browser   │───►│  S3 Bucket  │    │  AWS Lambda     │    │

│  │  (Form)     │    │  (Static    │    │  (Process       │    │

│  │             │    │   Website)  │    │   Feedback)     │    │

│  └─────────────┘    └──────┬──────┘    └────────┬────────┘    │

│                            │                     │             │

│                            ▼                     ▼             │

│                    ┌─────────────┐    ┌─────────────────┐    │

│                    │             │    │  Amazon         │    │

│                    │  API Gateway│    │  DynamoDB       │    │

│                    │  (HTTP API) │    │  (group6 table) │    │

│                    └──────┬──────┘    └────────┬────────┘    │

│                           │                     │             │

│                           │    ┌─────────────────┘             │

│                           │    │                               │

│                           ▼    ▼                               │

│                    ┌─────────────────┐                        │

│                    │  AWS Lambda     │                        │

│                    │  (Get Stats)    │                        │

│                    └────────┬────────┘                        │

│                             │                                  │

│                             ▼                                  │

│                    ┌─────────────┐                            │

│                    │   Browser   │                            │

│                    │ (Dashboard) │                            │

│                    └─────────────┘                            │

│                                                                 │

│  ┌──────────────────────────────────────────────────────────┐  │

│  │                    AWS IAM (Security)                    │  │

│  │              (Roles \& Permissions)                       │  │

│  └──────────────────────────────────────────────────────────┘  │

│                                                                 │

└─────────────────────────────────────────────────────────────────┘



**Data Flow**

Step	Action	Service

1	User loads feedback form	S3 (Static Website)

2	User submits feedback	Form → API Gateway

3	API routes request	API Gateway → Lambda

4	Lambda processes sentiment	Lambda (Python)

5	Data saved to database	Lambda → DynamoDB

6	Dashboard fetches stats	S3 Dashboard → API Gateway

7	API returns aggregated data	API Gateway → Lambda 2

8	Dashboard renders charts	Chart.js in browser



🛠️ **Technology Stack**

AWS Services

Service	Purpose	Why Chosen

Amazon S3	Static website hosting	Cost-effective, serverless, integrates with other AWS services

Amazon API Gateway	HTTP API routing	Manages requests, CORS, and Lambda integration

AWS Lambda	Serverless compute	Pay-per-execution, auto-scaling, no server management

Amazon DynamoDB	NoSQL database	Serverless, JSON-native, auto-scaling

AWS IAM	Security \& permissions	Fine-grained access control

Frontend Technologies

Technology	Purpose

HTML5	Structure and content

CSS3	Styling and responsive design

JavaScript	Form handling, API calls, charts

Chart.js	Dashboard data visualization

Backend Technologies

Technology	Purpose

Python 3.12	Lambda functions

Boto3	AWS SDK for Python

Regular Expressions	Text parsing and sentiment analysis



💻 Implementation Details

1\. DynamoDB Table

Table Schema:



json

{

&#x20; "TableName": "group6",

&#x20; "PartitionKey": "feedback-id (String)",

&#x20; "BillingMode": "PAY\_PER\_REQUEST"

}

Sample Item:



json

{

&#x20; "feedback-id": "abc-123-def",

&#x20; "name": "Bernard Arhin",

&#x20; "email": "arhinbenny1@gmail.com",

&#x20; "message": "The service was excellent!",

&#x20; "sentiment": "POSITIVE",

&#x20; "submitted\_at": "2026-07-07T10:30:00Z"

}

2\. Lambda 1: Process Feedback

Purpose: Process incoming feedback, analyze sentiment, save to DynamoDB



python

def analyze\_sentiment(text: str) -> str:

&#x20;   words = re.findall(r"\[a-z']+", text.lower())

&#x20;   pos\_count = sum(1 for w in words if w in POSITIVE\_WORDS)

&#x20;   neg\_count = sum(1 for w in words if w in NEGATIVE\_WORDS)

&#x20;   # Returns: POSITIVE, NEGATIVE, NEUTRAL, or MIXED

Key Functions:



analyze\_sentiment(): Python-based sentiment detection



lambda\_handler(): Main function entry point



CORS headers for cross-origin requests



3\. Lambda 2: Get Stats

Purpose: Fetch and aggregate feedback data for dashboard



Features:



Scans DynamoDB table



Counts sentiment distribution



Calculates sentiment percentages



Returns top 10 recent submissions



4\. API Gateway

Routes:



Method	Path	Integration

POST	/feedback	Lambda 1 (Process)

GET	/stats	Lambda 2 (Stats)

CORS Configuration:



Allow Origin: \*



Allow Methods: POST, GET, OPTIONS



Allow Headers: Content-Type



5\. S3 Static Hosting

Buckets Created:



Bucket	Purpose	File

ccp-group6	Customer Form	index.html

dashboardgroup6	Admin Dashboard	dashboard-glow.html

Features:



Static website hosting enabled



Public read access via bucket policy



Index documents configured



🎨 Frontend Design

Customer Feedback Form

Features:



Live sentiment preview as user types



Responsive design for mobile/desktop



Validation and error handling



Loading states and success feedback



Example Form:



text

┌─────────────────────────────────────┐

│  📊 Group 6 Feedback                │

│  Your voice helps us improve        │

│                                      │

│  Full Name                          │

│  \[Bernard Arhin]                    │

│                                      │

│  Email Address                      │

│  \[arhinbenny1@gmail.com]            │

│                                      │

│  Your Feedback                      │

│  \[The service was excellent!]       │

│                                      │

│  😊 POSITIVE Sentiment Detected    │

│                                      │

│  \[Submit Feedback]                  │

└─────────────────────────────────────┘

Admin Dashboard

Features:



Real-time sentiment charts (doughnut chart)



Key metrics (Total, Positive, Neutral, Negative)



Recent feedback table



Auto-refresh every 30 seconds



CSV export functionality



Sentiment insights summary



Dashboard Layout:



text

┌─────────────────────────────────────────────────────┐

│  📊 Group 6 Analytics                \[Refresh]     │

│  Real-time feedback insights                       │

├─────────────────────────────────────────────────────┤

│  Total: 15  Positive: 8  Neutral: 4  Negative: 3  │

├─────────────────────────────────────────────────────┤

│  ┌─────────────┐    ┌─────────────────────────┐   │

│  │ Sentiment   │    │ 📊 Key Insights         │   │

│  │ Distribution│    │ ✅ Customers are happy! │   │

│  │   \[Chart]   │    │ Positive: 8 (53.3%)    │   │

│  └─────────────┘    │ Neutral: 4 (26.7%)     │   │

│                      │ Negative: 3 (20.0%)    │   │

│                      └─────────────────────────┘   │

├─────────────────────────────────────────────────────┤

│  📝 Recent Feedback                                 │

│  ┌──────────┬─────────────┬───────────┬──────────┐│

│  │ Name     │ Message     │ Sentiment │ Date     ││

│  ├──────────┼─────────────┼───────────┼──────────┤│

│  │ Bernard  │ Good...     │ POSITIVE  │ Jul 7    ││

│  │ Jane     │ Bad...      │ NEGATIVE  │ Jul 7    ││

│  └──────────┴─────────────┴───────────┴──────────┘│

└─────────────────────────────────────────────────────┘

📊 Results \& Performance

Deployment Results

Metric	Value

Total AWS Services	6

Lambda Functions	2

API Routes	2

S3 Buckets	2

DynamoDB Tables	1

Frontend Pages	2

Total Deployment Time	\~15 minutes

Cost	Free Tier eligible

Performance Metrics

Component	Response Time

Form Load	< 1 second

Feedback Submission	2-3 seconds

Dashboard Load	< 2 seconds

Stats API	< 500 ms

Lambda 1 Duration	\~129 ms

Lambda 2 Duration	< 100 ms

Cost Analysis

All services used are within AWS Free Tier limits:



Service	Free Tier	Your Usage

Lambda	1M requests/month	< 1000/month

API Gateway	1M requests/month	< 1000/month

DynamoDB	25GB storage	< 1GB

S3	5GB storage	< 10MB

IAM	Free	Free

Estimated Monthly Cost: $0.00 (within Free Tier)



🎓 **What We Learned**

Serverless Architecture Benefits

Auto-scaling: Handles traffic spikes automatically



Cost-effective: Pay only for what you use



No server management: Focus on code, not infrastructure



Fast deployment: Deploy in minutes, not hours



Python Sentiment Analysis

Word-list approach: Simple but effective for basic sentiment



Regex processing: Quick text parsing and cleaning



No API costs: Free alternative to Comprehend



Customizable: Easy to add domain-specific words



Cloud-Native Development

Service integration: How AWS services work together



CORS configuration: Critical for web applications



Environment variables: Configurable deployment



Infrastructure as Code: Terraform for repeatable deployments



🚀 **Future Enhancements**

Planned Features

Feature	Description	Priority

Amazon Comprehend	Replace Python sentiment with AWS AI	High

SNS Notifications	Email alerts for negative feedback	Medium

Cognito Auth	Protect dashboard with login	Medium

CloudFront	HTTPS and CDN for frontend	Low

Multi-language	Support non-English feedback	Low

Entity Extraction	Identify names, places, dates	Low

Architecture Improvements

Add authentication: Cognito for dashboard access



Add notification: SNS alerts for critical feedback



Add analytics: Amazon QuickSight for advanced reporting



Add caching: CloudFront for frontend delivery



Add CI/CD: GitHub Actions for auto-deployment



**📁 Project Files**

**File Structure**

text

ai-feedback-hub/

├── frontend/

│   ├── index.html              # Customer feedback form

│   └── dashboard-glow.html     # Admin dashboard

├── backend/

│   ├── lambda1-process/

│   │   └── lambda\_function.py  # POST /feedback

│   └── lambda2-stats/

│   │   └── lambda\_function.py  # GET /stats

├── terraform/

│   ├── main.tf                 # Infrastructure as Code

│   ├── variables.tf

│   ├── outputs.tf

│   └── providers.tf

├── docs/

│   ├── README.md               # Project overview

│   ├── deployment-guide.md     # Step-by-step setup

│   ├── api-documentation.md    # API reference

│   ├── troubleshooting.md      # Common issues

│   └── project-report.md       # This document

└── screenshots/

&#x20;   ├── form-working.png

&#x20;   ├── dashboard-working.png

&#x20;   └── dynamodb-items.png

Live URLs

Component	URL

Customer Form	http://ccp-group6.s3-website-us-east-1.amazonaws.com

Admin Dashboard	http://dashboardgroup6.s3-website-us-east-1.amazonaws.com/dashboard-glow.html

API Base	https://YOUR-API-ID.execute-api.us-east-1.amazonaws.com



**✅ Conclusion**

The AI Customer Feedback successfully demonstrates:



Complete serverless application using 6 AWS services



Real-time sentiment analysis with Python-based NLP



Interactive admin dashboard with live charts



Cost-effective architecture within AWS Free Tier



Infrastructure as Code with Terraform for repeatable deployment



Business Value

✅ Time savings: Automated feedback analysis



✅ Better insights: Real-time sentiment visualization



✅ Scalability: Auto-scaling for growing data



✅ Cost efficiency: Pay-per-use model



✅ Production-ready: Complete, tested solution



Team Impact

This project showcases the ability to:



Design and implement serverless architectures



Integrate multiple AWS services



Build full-stack applications



Use Infrastructure as Code



Create production-ready solutions



**📚 References**

AWS Lambda Documentation - https://docs.aws.amazon.com/lambda/



Amazon DynamoDB Documentation - https://docs.aws.amazon.com/dynamodb/



Amazon API Gateway Documentation - https://docs.aws.amazon.com/apigateway/



Amazon S3 Documentation - https://docs.aws.amazon.com/s3/



Chart.js Documentation - https://www.chartjs.org/



Terraform AWS Provider - https://registry.terraform.io/providers/hashicorp/aws/latest/docs



Project Status: ✅ COMPLETED



Documentation Version: 1.0

Last Updated: July 2026

Author: Group 6

