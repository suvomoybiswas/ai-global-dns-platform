import json
import boto3
import time
import uuid

s3 = boto3.client('s3')

BUCKET = "dns-security-lake-YOUR_SUFFIX"

def lambda_handler(event, context):

    print(json.dumps(event))

    record = {
        "id": str(uuid.uuid4()),
        "timestamp": int(time.time()),
        "raw_event": event
    }

    key = f"logs/{record['id']}.json"

    s3.put_object(
        Bucket=BUCKET,
        Key=key,
        Body=json.dumps(record)
    )

    return {
        "statusCode": 200
    }
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('dns-threats')

def classify(domain):
    suspicious_keywords = ["login", "secure", "verify", "bank"]

    if any(word in domain for word in suspicious_keywords):
        return "MEDIUM"
    return "LOW"
risk = classify(domain)

table.put_item(
    Item={
        "domain": domain,
        "risk": risk,
        "timestamp": int(time.time())
    }
)
bedrock = boto3.client("bedrock-runtime")
def analyze_with_ai(domain, src_ip):

    prompt = f"""
You are a cybersecurity DNS threat detection system.

Analyze this DNS query:

Domain: {domain}
Source IP: {src_ip}

Return JSON:
{
  "risk": "LOW|MEDIUM|HIGH",
  "reason": "...",
  "action": "ALLOW|BLOCK"
}
"""
    response = bedrock.invoke_model(
        modelId="anthropic.claude-3-haiku",
        body=json.dumps({
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        })
    )

    result = json.loads(response['body'].read())
    return result