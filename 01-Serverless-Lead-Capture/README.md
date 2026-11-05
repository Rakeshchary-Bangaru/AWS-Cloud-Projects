# Serverless Lead Capture on AWS

A hands-on AWS serverless project that demonstrates how to deploy a static website securely using Amazon S3 and CloudFront, and progressively add a serverless backend for capturing customer enquiries.

The application used in this project is **CloudNova**, a fictional cloud and software services website built using HTML, CSS, and JavaScript.

---

## Project Overview

CloudNova contains:

- Home section
- Services section
- Projects section
- About section
- Contact form

The frontend is hosted using AWS services, while the Contact Us form will be connected to a completely serverless backend.

The goal of this project is not only to deploy an application, but also to understand:

- Why each AWS service is used
- Serverless architecture
- Event-driven architecture
- Static vs dynamic applications
- Secure cloud storage
- Content delivery
- API communication
- NoSQL data storage
- Email notifications
- IAM permissions
- Monitoring and logging

---

## Frontend Technologies

The CloudNova frontend is developed using:

- HTML
- CSS
- JavaScript

The original frontend source code is maintained separately in the `Web-Development-Projects` repository.

This AWS repository contains the cloud architecture, backend implementation, deployment documentation, screenshots, and AWS-specific configuration.

---

# AWS Architecture

## Current Architecture - Phase 1

```text
                 User Browser
                      |
                      | HTTPS
                      v
              Amazon CloudFront
                      |
                      | Origin Access Control
                      v
               Private S3 Bucket
                      |
          -------------------------
          |           |           |
      index.html  style.css   contact.js
```

The CloudNova frontend is currently deployed successfully through Amazon CloudFront.

The S3 bucket remains private and cannot be accessed directly from the public internet.

CloudFront is the public entry point to the website.

---

# Final Planned Architecture

```text
                         User
                          |
                          | HTTPS
                          v
                   Amazon CloudFront
                          |
                          v
                    Amazon S3
                Static Frontend
                          |
                          |
                  Contact Form
                          |
                          | HTTPS POST
                          v
                    API Gateway
                          |
                          v
                     AWS Lambda
                    /          \
                   /            \
                  v              v
           Amazon DynamoDB    Amazon SES
             Store Lead       Send Emails
                  |
                  v
            Amazon CloudWatch
             Logs / Metrics
```

---

# AWS Region

Regional AWS resources are deployed in:

```text
Asia Pacific (Sydney)
ap-southeast-2
```

Services planned in Sydney:

- Amazon S3
- AWS Lambda
- Amazon API Gateway
- Amazon DynamoDB
- Amazon SES
- Amazon CloudWatch

Amazon CloudFront is a global AWS service.

This project does not currently use Route 53 because no custom domain is required.

The website uses the default CloudFront HTTPS domain.

---

# Phase 1 - Static Website Deployment

## Amazon S3

Amazon S3 is used to store the CloudNova static frontend files.

Current deployment structure:

```text
S3 Bucket
|
├── index.html
├── css/
│   └── style.css
└── js/
    └── contact.js
```

### Why S3?

CloudNova currently consists of static files:

- HTML
- CSS
- JavaScript

A continuously running server is not required just to serve these files.

S3 provides a simple and scalable storage solution for static web assets.

### Advantages

- No server management
- Highly scalable
- Durable storage
- Simple deployment
- Integrates with CloudFront
- Suitable for static assets

### Disadvantages

- Cannot directly execute backend application code
- Not a traditional application server
- Dynamic functionality requires other AWS services

### Why not EC2?

The frontend does not require:

- Java
- Node.js
- Spring Boot
- PHP
- A continuously running process

Using EC2 only to serve static HTML, CSS, and JavaScript would introduce unnecessary server management.

With EC2, we would need to manage:

```text
Virtual Machine
      |
Operating System
      |
Web Server
      |
Security Updates
      |
Patching
      |
Scaling
```

For a static frontend, S3 is simpler.

---

# Amazon CloudFront

Amazon CloudFront is used as the public delivery layer for CloudNova.

Current request flow:

```text
User
 |
 v
CloudFront
 |
 v
Private S3 Bucket
```

CloudFront communicates with the S3 bucket using **Origin Access Control (OAC)**.

The S3 bucket remains private.

### Why CloudFront?

CloudFront provides:

- HTTPS
- Global content delivery
- Edge caching
- Secure access to private S3 content
- Improved website delivery
- Reduced direct access to the S3 origin

### Advantages

- Global CDN
- HTTPS support
- Caching
- Low-latency delivery
- Integration with S3
- Supports private origins

### Disadvantages

- Additional configuration
- Cached files may need invalidation after updates
- Adds another AWS service to manage

---

# Origin Access Control

CloudFront uses **Origin Access Control (OAC)** to access the private S3 bucket.

Architecture:

```text
Internet
   |
   v
CloudFront
   |
   | Authorized request
   v
Private S3
```

Users cannot directly access the S3 bucket.

This provides a better security model than making the entire bucket publicly readable.

---

# Static vs Dynamic Content

## Static Content

The following parts of CloudNova are static:

- Home
- Services
- Projects
- About
- Contact form UI

These files are delivered from S3 through CloudFront.

```text
Browser
   |
CloudFront
   |
S3
```

---

## Dynamic Content

The Contact Us workflow will become the dynamic portion of the application.

Example:

```text
User enters:

Name
Email
Phone
Message

        |
        v

JavaScript

        |
        v

API Gateway

        |
        v

Lambda

       / \
      /   \
     v     v

DynamoDB  SES
```

The system will dynamically:

1. Receive the customer enquiry
2. Validate the submitted data
3. Generate a unique enquiry ID
4. Store the enquiry in DynamoDB
5. Send a confirmation email to the customer
6. Send a notification email to the administrator
7. Return a response to the frontend
8. Record execution logs in CloudWatch

---

# Why Serverless?

The CloudNova backend is designed as a serverless application.

A Contact Us form does not need a backend server running continuously.

Traffic may be intermittent:

```text
10:00 AM  -> 0 requests
11:00 AM  -> 2 requests
12:00 PM  -> 0 requests
3:00 PM   -> 1 request
```

Running an EC2 instance continuously would mean maintaining compute resources even when there are no requests.

With AWS Lambda:

```text
No Event
   |
No Lambda Execution


Contact Form Submitted
   |
Lambda Executes
   |
Processing Completes
   |
Execution Ends
```

---

# What Does Serverless Mean?

Serverless does **not** mean that servers do not exist.

The servers still exist, but AWS manages the underlying infrastructure.

With a traditional server we manage more infrastructure:

```text
Application
    |
Runtime
    |
Operating System
    |
Virtual Machine
    |
Physical Infrastructure
```

With Lambda we primarily manage:

```text
Application Code
      |
Configuration
      |
Permissions
```

AWS manages most of the underlying compute infrastructure.

---

# Event-Driven Architecture

CloudNova uses an event-driven approach.

An event is something that happens in the application and triggers another action.

For this project:

```text
Contact Form Submitted
        |
        | Event
        v
API Gateway receives request
        |
        v
Lambda executes
        |
        +---- Save enquiry
        |
        +---- Send emails
```

The backend runs because an event occurred.

Other examples of event-driven systems include:

```text
File uploaded to S3
        |
        v
Trigger Lambda


Message added to queue
        |
        v
Process message


Database record changes
        |
        v
Trigger another workflow
```

---

# Planned Serverless Backend

## Amazon API Gateway

API Gateway will expose an HTTP endpoint for the CloudNova frontend.

Example:

```text
POST /contact
```

Request flow:

```text
contact.js
    |
    v
API Gateway
    |
    v
Lambda
```

### Why API Gateway?

A browser needs an HTTP endpoint to communicate with the Lambda backend.

### Advantages

- Managed API service
- HTTPS endpoints
- Integrates with Lambda
- CORS support
- Scalable
- Authentication options

### Disadvantages

- Additional configuration
- CORS must be configured correctly
- Adds another component to the architecture

---

# AWS Lambda

Lambda will contain the contact form business logic.

Planned Lambda responsibilities:

```text
Receive Request
      |
Validate Input
      |
Generate UUID
      |
Save Lead
      |
Send Emails
      |
Return Response
```

### Why Lambda?

The backend only needs to execute when a customer submits the contact form.

### Advantages

- No server management
- Automatic scaling
- Event-driven
- Pay based on usage
- Integrates with other AWS services

### Disadvantages

- Cold starts can occur
- Execution limits exist
- Functions are stateless
- Distributed debugging can be more complex

---

# Amazon DynamoDB

DynamoDB will store submitted contact enquiries.

Planned table:

```text
Table Name:
ContactMessages
```

Partition key:

```text
id
```

Example record:

```json
{
  "id": "generated-uuid",
  "name": "Shiva",
  "email": "shiva@example.com",
  "phone": "9876543210",
  "message": "I need help deploying my application.",
  "createdAt": "2026-11-05T10:30:00Z"
}
```

### Why DynamoDB?

The contact form has a simple data structure.

We do not require:

- SQL joins
- Foreign keys
- Complex relational queries
- Large relational schemas

### Advantages

- Fully managed
- Serverless
- Automatically scalable
- Fast key-based access
- Good Lambda integration

### Disadvantages

- No relational joins
- Requires different data modelling from SQL databases
- Complex queries can be harder than relational databases

---

# Why DynamoDB Instead of RDS?

RDS is better suited to relational systems containing relationships such as:

```text
Customers
   |
Orders
   |
Order Items
   |
Products
   |
Payments
```

CloudNova only needs to store independent contact messages.

Therefore DynamoDB provides a simpler solution for this use case.

---

# Amazon SES

**Amazon Simple Email Service (SES)** will handle application-generated emails.

When someone submits the Contact Us form:

```text
               Lambda
               /    \
              /      \
             v        v
      Customer Email  Admin Email
```

The customer receives an acknowledgement.

Example:

```text
Hi Shiva,

Thank you for contacting CloudNova.

We have received your enquiry and will get back to you soon.

Reference ID: CN-12345
```

The administrator receives the lead information.

Example:

```text
New CloudNova Enquiry

Name: Shiva
Email: shiva@example.com
Phone: 9876543210

Message:
I need help deploying my application.
```

---

# Amazon CloudWatch

CloudWatch will provide monitoring and logging.

It will help inspect:

- Lambda executions
- Errors
- Request processing
- Execution duration
- Application logs

Example:

```text
API Gateway
     |
Lambda
     |
ERROR
     |
CloudWatch Logs
```

---

# IAM

AWS Identity and Access Management will control permissions between services.

The Lambda function should only receive the permissions that it actually needs.

Example:

```text
Lambda
 |
 +-- dynamodb:PutItem
 |
 +-- ses:SendEmail
 |
 +-- CloudWatch logging
```

It should not automatically receive unrelated permissions such as:

```text
Delete S3 buckets
Create EC2 instances
Modify VPC resources
```

This follows the **Principle of Least Privilege**.

---

# Current Project Status

## Phase 1 - Frontend and Static Hosting

- [x] Build CloudNova HTML frontend
- [x] Create CSS styling
- [x] Create JavaScript contact form handling
- [x] Test CloudNova locally
- [x] Create deployment bundle
- [x] Create Amazon S3 bucket
- [x] Keep S3 bucket private
- [x] Upload frontend files to S3
- [x] Create CloudFront distribution
- [x] Configure Origin Access Control
- [x] Configure `index.html` as default root object
- [x] Deploy CloudNova over HTTPS

## Phase 2 - Serverless Backend

- [ ] Create DynamoDB `ContactMessages` table
- [ ] Configure Amazon SES
- [ ] Verify email identities
- [ ] Create Lambda IAM role
- [ ] Create Lambda contact handler
- [ ] Store contact enquiries in DynamoDB
- [ ] Send customer confirmation email
- [ ] Send administrator notification email
- [ ] Configure CloudWatch logging

## Phase 3 - API Integration

- [ ] Create API Gateway
- [ ] Create `POST /contact`
- [ ] Integrate API Gateway with Lambda
- [ ] Configure CORS
- [ ] Test API independently
- [ ] Update `contact.js`
- [ ] Connect frontend using Fetch API
- [ ] Deploy updated JavaScript to S3
- [ ] Invalidate CloudFront cache
- [ ] Perform end-to-end testing

---

# Deployment Structure

```text
cloudnova-deploy/
|
├── index.html
├── css/
│   └── style.css
└── js/
    └── contact.js
```

---

# Repository Structure

```text
AWS-Cloud-Projects/
|
└── 01-Serverless-Lead-Capture/
    |
    ├── README.md
    |
    ├── architecture/
    |
    ├── deployment/
    |
    └── screenshots/
```

---

# Key Learning Outcomes

This project provides practical experience with:

- AWS serverless architecture
- Event-driven architecture
- Amazon S3
- Amazon CloudFront
- Origin Access Control
- AWS Lambda
- API Gateway
- DynamoDB
- Amazon SES
- IAM roles and policies
- CloudWatch
- Static vs dynamic applications
- Server vs serverless architecture
- HTTPS delivery
- API integration
- Cloud security principles

---

# Architecture Decision Summary

| Requirement | AWS Service | Reason |
|---|---|---|
| Static frontend storage | Amazon S3 | No application server required |
| HTTPS and global delivery | CloudFront | CDN, caching and secure S3 access |
| Backend API | API Gateway | Managed HTTP endpoint |
| Business logic | Lambda | Event-driven serverless compute |
| Lead storage | DynamoDB | Simple serverless NoSQL storage |
| Email notifications | SES | Managed application email delivery |
| Permissions | IAM | Least-privilege access control |
| Monitoring | CloudWatch | Logs and metrics |

---

# Future Request Flow

```text
Visitor
  |
  v
CloudFront
  |
  v
S3
  |
  v
CloudNova Contact Form
  |
  | POST /contact
  v
API Gateway
  |
  v
Lambda
  |
  +--------------------------+
  |                          |
  v                          v
DynamoDB                    SES
Store enquiry       Customer + Admin Email
  |
  v
CloudWatch
```

---

## Status

**Phase 1: Completed**

CloudNova is successfully deployed using:

```text
Amazon S3
+
Amazon CloudFront
+
Origin Access Control
+
HTTPS
```

The next phase is implementing the dynamic serverless backend using **DynamoDB, SES, IAM and AWS Lambda**.