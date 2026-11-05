# Deployment Notes

## Region

```text
Asia Pacific (Sydney)
ap-southeast-2
```

## S3

Bucket:

```text
cloudnova-serverless-2026
```

Deployment structure:

```text
index.html
css/style.css
js/contact.js
```

S3 public access is blocked.

CloudFront accesses S3 using Origin Access Control.

## Frontend Deployment

Copy the current JavaScript into the deployment bundle:

```bash
cp ~/Documents/Projects/Web-Development-Projects/JavaScript/CloudNova/contact.js \
~/Documents/Projects/cloudnova-deploy/js/contact.js
```

Deploy files:

```bash
aws s3 sync ~/Documents/Projects/cloudnova-deploy \
s3://cloudnova-serverless-2026
```

After frontend updates, invalidate the relevant CloudFront object or use:

```text
/*
```

for a full cache refresh when appropriate.

## DynamoDB

Table:

```text
ContactMessages
```

Partition key:

```text
id
```

Capacity:

```text
On-demand
```

## Lambda

Function:

```text
CloudNovaContactHandler
```

Runtime:

```text
Node.js 24.x
```

Architecture:

```text
arm64
```

Environment variables:

```text
TABLE_NAME=ContactMessages
OWNER_EMAIL=<verified SES identity>
```

Do not commit the real owner email to public source code if privacy is desired.

## IAM

Execution role:

```text
CloudNovaContactLambdaRole
```

Permissions:

```text
AWSLambdaBasicExecutionRole
dynamodb:PutItem
ses:SendEmail
```

## API Gateway

API:

```text
CloudNovaContactAPI
```

Route:

```text
POST /contact
```

Stage:

```text
$default
```

The API endpoint is intentionally not documented publicly here.

## SES

Current behavior:

```text
Contact form
   |
Lambda
   |
SES
   |
Owner notification
```

Future behavior after SES production access:

```text
SES
├── Owner notification
└── Customer acknowledgement
```

## CloudWatch

Lambda logs:

```text
/aws/lambda/CloudNovaContactHandler
```

Use CloudWatch Logs to diagnose:

- Lambda errors
- IAM permission failures
- DynamoDB failures
- SES failures
- Request processing problems