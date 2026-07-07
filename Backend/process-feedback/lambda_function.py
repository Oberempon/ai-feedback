import boto3
import json
import uuid
import re
from datetime import datetime
import os

# ============================================
# CONFIGURATION
# ============================================
TABLE_NAME = os.environ.get('TABLE_NAME', 'group6')
REGION = os.environ.get('AWS_REGION', 'us-east-1')

# Initialize AWS Services
dynamodb = boto3.resource('dynamodb', region_name=REGION)
table = dynamodb.Table(TABLE_NAME)

# ============================================
# CORS HEADERS
# ============================================
CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
}

# ============================================
# SENTIMENT WORD LISTS
# ============================================
POSITIVE_WORDS = {
    'good', 'great', 'excellent', 'positive', 'happy', 'love', 'best',
    'strong', 'success', 'improve', 'benefit', 'effective', 'reliable',
    'recommend', 'pleased', 'satisfied', 'achieve', 'gain', 'advantage',
    'opportunity', 'wonderful', 'amazing', 'awesome', 'fantastic',
    'perfect', 'nice', 'helpful', 'friendly', 'brilliant', 'outstanding'
}

NEGATIVE_WORDS = {
    'bad', 'poor', 'terrible', 'negative', 'hate', 'worst', 'awful',
    'fail', 'failure', 'weak', 'problem', 'issue', 'difficult', 'delay',
    'risk', 'loss', 'concern', 'disappointed', 'unable', 'error',
    'broken', 'decline', 'complaint', 'horrible', 'frustrating'
}

# ============================================
# SENTIMENT ANALYSIS FUNCTION
# ============================================
def analyze_sentiment(text: str) -> str:
    """
    Analyze sentiment using simple word matching.
    Returns: POSITIVE, NEGATIVE, NEUTRAL, or MIXED
    """
    if not text or len(text.strip()) < 3:
        return 'NEUTRAL'
    
    # Clean and split text
    words = re.findall(r"[a-z']+", text.lower())
    
    if not words:
        return 'NEUTRAL'
    
    # Count positive and negative words
    pos_count = sum(1 for w in words if w in POSITIVE_WORDS)
    neg_count = sum(1 for w in words if w in NEGATIVE_WORDS)
    total = pos_count + neg_count
    
    if total == 0:
        return 'NEUTRAL'
    
    # Calculate scores
    pos_ratio = pos_count / total
    neg_ratio = neg_count / total
    
    # Determine sentiment
    if pos_ratio > 0.6:
        return 'POSITIVE'
    elif neg_ratio > 0.6:
        return 'NEGATIVE'
    elif pos_ratio > 0 and neg_ratio > 0 and abs(pos_ratio - neg_ratio) <= 0.25:
        return 'MIXED'
    elif pos_ratio > neg_ratio:
        return 'POSITIVE'
    elif neg_ratio > pos_ratio:
        return 'NEGATIVE'
    else:
        return 'NEUTRAL'

# ============================================
# MAIN LAMBDA HANDLER
# ============================================
def lambda_handler(event, context):
    """
    Main Lambda function handler for processing feedback.
    """
    print(f"🚀 Lambda started - Using table: {TABLE_NAME}")
    print(f"📨 Event: {json.dumps(event)[:500]}")  # Log truncated event
    
    # Handle OPTIONS (CORS preflight)
    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': CORS_HEADERS,
            'body': ''
        }
    
    try:
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        name = body.get('name', 'Anonymous').strip()
        email = body.get('email', '').strip()
        message = body.get('message', '').strip()[:5000]
        
        print(f"👤 Name: {name}")
        print(f"📧 Email: {email}")
        print(f"💬 Message length: {len(message)} chars")
        
        # Validate input
        if not message:
            return {
                'statusCode': 400,
                'headers': CORS_HEADERS,
                'body': json.dumps({'error': 'Message is required'})
            }
        
        # Analyze sentiment
        sentiment = analyze_sentiment(message)
        print(f"📊 Sentiment: {sentiment}")
        
        # Generate unique ID and timestamp
        feedback_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        # ✅ Build item WITHOUT entities field
        item = {
            'feedback-id': feedback_id,
            'name': name,
            'email': email,
            'message': message,
            'sentiment': sentiment,
            'submitted_at': timestamp
        }
        
        print(f"💾 Saving item: {json.dumps(item)}")
        
        # Save to DynamoDB
        table.put_item(Item=item)
        
        print(f"✅ Successfully saved: {feedback_id}")
        
        # Return success response
        return {
            'statusCode': 200,
            'headers': CORS_HEADERS,
            'body': json.dumps({
                'success': True,
                'id': feedback_id,
                'sentiment': sentiment,
                'message': 'Feedback submitted successfully'
            })
        }
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON Parse Error: {str(e)}")
        return {
            'statusCode': 400,
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': 'Invalid JSON payload'})
        }
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        print(f"❌ Stack trace: {traceback.format_exc()}")
        
        return {
            'statusCode': 500,
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': str(e)})
        }