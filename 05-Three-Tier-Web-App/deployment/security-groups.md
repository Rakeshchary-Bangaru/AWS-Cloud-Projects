# Security Groups

This document describes the security group configuration used in the three-tier AWS deployment.

## Overview

The architecture uses separate security groups for:

- EC2 backend
- RDS database

Traffic is restricted so that only the required components can communicate.

```text
Browser
   |
   | HTTPS
   v
CloudFront
   |
   | TCP 8080
   v
EC2 Spring Boot
   |
   | TCP 3306
   v
RDS MySQL
```

## EC2 Security Group

Security group:

```text
ecommerce-ec2-sg
```

The EC2 instance hosts the Spring Boot backend.

### SSH Access

```text
Type: SSH
Protocol: TCP
Port: 22
Source: My IP
```

SSH access is restricted to the developer's current public IP address.

This prevents unrestricted SSH access from the internet.

### Backend API Access

```text
Type: Custom TCP
Protocol: TCP
Port: 8080
Source: AWS-managed CloudFront origin-facing prefix list
```

AWS-managed prefix list:

```text
com.amazonaws.global.cloudfront.origin-facing
```

This allows CloudFront to communicate with the Spring Boot application without exposing port `8080` to the entire internet.

During deployment and debugging, a temporary rule may also be used:

```text
Port: 8080
Source: My IP
```

This rule can be removed once CloudFront routing has been verified.

## EC2 Outbound Rules

The EC2 instance currently uses the default outbound rule:

```text
All traffic
Destination: 0.0.0.0/0
```

This allows EC2 to:

- download operating system packages
- communicate with AWS services
- reach the RDS database
- perform required outbound network requests

## RDS Security Group

Security group:

```text
ecommerce-rds-sg
```

The RDS database is not publicly accessible.

### MySQL Access

```text
Type: MySQL/Aurora
Protocol: TCP
Port: 3306
Source: ecommerce-ec2-sg
```

The source is another security group rather than an IP address.

This means that resources using the EC2 backend security group can connect to RDS on port `3306`.

The database does not accept MySQL connections directly from the public internet.

## RDS Outbound Rules

The default outbound rule is retained.

RDS does not require public inbound access because connections are initiated by the backend application.

## Security Group Traffic Flow

### User to Frontend

```text
User
  |
  | HTTPS 443
  v
CloudFront
```

CloudFront is the public entry point of the application.

### CloudFront to EC2

```text
CloudFront
  |
  | TCP 8080
  v
EC2 Spring Boot
```

CloudFront uses the AWS-managed origin-facing network ranges.

### EC2 to RDS

```text
EC2
  |
  | TCP 3306
  v
RDS MySQL
```

Only the EC2 security group is trusted by the database security group.

## Why Security Group References Are Used

Using:

```text
ecommerce-ec2-sg
```

as the source for the RDS rule is preferable to using the EC2 private IP address.

The EC2 private IP could potentially change in some deployment scenarios, while the security group association represents the application tier logically.

This creates a cleaner trust relationship:

```text
Application Tier
       |
       v
Database Tier
```

rather than:

```text
Specific IP Address
       |
       v
Database Tier
```

## Stateful Behavior

AWS security groups are stateful.

For example, when EC2 initiates a connection to RDS on port `3306`, the return traffic is automatically allowed.

A separate inbound rule for the response traffic is not required.

## Public Exposure

The architecture intentionally avoids exposing the following directly to the public internet:

```text
RDS MySQL
S3 bucket
```

The application is accessed through:

```text
CloudFront
```

The backend is reachable by CloudFront on port `8080`.

The database remains reachable only from the backend tier.

## Current Rules Summary

### ecommerce-ec2-sg

```text
Inbound:

SSH
TCP 22
Source: My IP

Custom TCP
TCP 8080
Source: CloudFront origin-facing prefix list

Temporary testing:
TCP 8080
Source: My IP
```

### ecommerce-rds-sg

```text
Inbound:

MySQL/Aurora
TCP 3306
Source: ecommerce-ec2-sg
```

## Security Improvements Planned

Future improvements may include:

- removing direct developer access to port `8080`
- implementing Spring Security
- CUSTOMER and ADMIN authorization
- HTTPS between CloudFront and the backend
- AWS Systems Manager Session Manager instead of direct SSH
- AWS Secrets Manager or Parameter Store for credentials
- Application Load Balancer
- Web Application Firewall
- private EC2 application tier
- centralized logging and monitoring

## Result

The security group configuration enforces a controlled traffic path:

```text
Internet
   |
   v
CloudFront
   |
   v
EC2 Backend
   |
   v
RDS Database
```

Each tier only accepts the network traffic required for its role.
