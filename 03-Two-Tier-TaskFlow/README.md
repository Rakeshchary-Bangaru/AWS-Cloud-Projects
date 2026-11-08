# TaskFlow — Two-Tier AWS Deployment

TaskFlow is a task-management application deployed on AWS using a two-tier architecture.

The application demonstrates how a React frontend and Spring Boot backend can be packaged together as a single application tier while Amazon RDS provides a separately managed database tier.

## Architecture

```text
Internet
   |
   v
Amazon EC2
Public Subnet
   |
   | Docker
   v
Spring Boot
+ React Production Build
   |
   | TCP 3306
   v
Amazon RDS MySQL
Private DB Subnets
```

## Architecture Classification

- Deployment Architecture: Two-Tier
- Application Style: Monolithic
- Application Tier: Amazon EC2
- Database Tier: Amazon RDS for MySQL
- Container Platform: Docker
- Network: Custom Amazon VPC

## Application Tier

The application tier runs on Amazon EC2.

A Docker container runs the Spring Boot application on port `8080`, while the EC2 host exposes the application through port `80`.

The React production build is bundled into Spring Boot's static resources, allowing Spring Boot to serve both:

- the React user interface
- the REST API

This means the frontend and backend form one deployed application tier.

## Database Tier

Amazon RDS for MySQL provides the database tier.

The database is deployed privately and is not directly accessible from the public internet.

Spring Boot connects to RDS using environment variables for:

- JDBC URL
- database username
- database password

Hibernate automatically manages the `tasks` table using Spring Data JPA.

## AWS Networking

The deployment uses a custom VPC.

### Subnets

- Public subnet for Amazon EC2
- Private database subnet in Availability Zone A
- Private database subnet in Availability Zone B

The EC2 public subnet has a route to an Internet Gateway.

The RDS subnets have no direct internet route.

## Security Groups

### EC2 Security Group

Allows:

- HTTP port `80` from the internet
- SSH port `22` from the administrator IP

### RDS Security Group

Allows:

- MySQL port `3306`
- Source: EC2 security group only

RDS is therefore accessible from the application tier but not from the public internet.

## Technologies

### Application

- React
- Vite
- JavaScript
- Java 21
- Spring Boot
- Spring Data JPA
- Hibernate
- MySQL
- Maven
- Docker

### AWS

- Amazon EC2
- Amazon RDS for MySQL
- Amazon VPC
- Public and private subnets
- Internet Gateway
- Route Tables
- Security Groups

## Deployment Flow

```text
Developer
   |
   | Build React
   v
React dist/
   |
   | Copy into Spring Boot static resources
   v
Spring Boot Application
   |
   | Docker build
   v
Docker Image
   |
   | Deploy
   v
Amazon EC2
   |
   v
Amazon RDS MySQL
```

## Validation

The deployment was validated by:

1. Accessing TaskFlow using the EC2 public IP.
2. Creating a task through the React interface.
3. Processing the request through the Spring Boot REST API.
4. Persisting the task in Amazon RDS MySQL.
5. Querying the `tasks` table directly from the EC2 instance.

Example database flow:

```sql
USE taskflow;
SHOW TABLES;
SELECT * FROM tasks;
```

## Source Code

The application source code is maintained separately from the infrastructure documentation.

- Frontend: `Web-Development-Projects/React/TaskFlow`
- Backend: `Java/TaskFlow-Backend`

This repository focuses specifically on AWS architecture and deployment.
