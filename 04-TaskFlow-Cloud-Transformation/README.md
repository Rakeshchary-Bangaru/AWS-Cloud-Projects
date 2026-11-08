# TaskFlow — Local-to-AWS Cloud Transformation

This project documents the transformation of TaskFlow from a local containerized development environment into an AWS-hosted application.

The purpose of the project is to demonstrate practical cloud migration concepts rather than only deploying an application that was originally designed for AWS.

## Before Transformation

TaskFlow initially ran locally using separate frontend, backend, and database components.

```text
Browser
   |
   v
React / Vite
localhost:5173
   |
   v
Spring Boot
Docker Container
localhost:8080
   |
   v
MySQL
Docker Container
```

The local environment used Docker networking to connect Spring Boot to MySQL.

## Transformation Goals

The cloud transformation focused on:

- replacing local MySQL with managed Amazon RDS
- moving the application workload to Amazon EC2
- separating the public application tier from the private database tier
- protecting database access using security groups
- removing direct public database exposure
- packaging React with Spring Boot for production deployment
- externalizing database configuration using environment variables

## Production Architecture

```text
Internet
   |
   v
Amazon EC2
Public Subnet
   |
   | Docker
   v
Spring Boot + React
   |
   v
Amazon RDS MySQL
Private DB Subnets
```

## Transformation Steps

### 1. Frontend Production Build

The React application was changed to use a relative API path:

```javascript
const API_URL = "/api/tasks";
```

A production build was generated using Vite.

```bash
npm run build
```

The generated frontend assets were copied into Spring Boot's static resources.

This allowed Spring Boot to serve both the web interface and API from the same deployment.

### 2. Containerized Application

The Spring Boot application was packaged using Docker.

The container exposes port `8080`.

On Amazon EC2, the container is mapped to HTTP port `80`.

```text
EC2 Port 80
     |
     v
Docker Port 8080
```

### 3. Managed Database Migration

The local MySQL Docker container was replaced with Amazon RDS for MySQL.

Spring Boot uses environment variables instead of hard-coded database credentials.

```text
SPRING_DATASOURCE_URL
SPRING_DATASOURCE_USERNAME
SPRING_DATASOURCE_PASSWORD
```

### 4. Custom AWS Network

A custom VPC was created with:

- one public application subnet
- two private database subnets
- an Internet Gateway
- public route table
- DB subnet group

Amazon EC2 was deployed in the public subnet.

Amazon RDS was deployed using the private database subnet group.

### 5. Security Isolation

Two security groups separate application and database access.

The EC2 security group permits HTTP access.

The RDS security group permits MySQL traffic only from the EC2 security group.

This means the database cannot be connected to directly from the internet.

## Before vs After

| Area | Local Environment | AWS Environment |
|---|---|---|
| Frontend | React Vite server | React production build served by Spring Boot |
| Backend | Spring Boot Docker | Spring Boot Docker on EC2 |
| Database | MySQL Docker | Amazon RDS MySQL |
| Networking | Docker network | Amazon VPC |
| Database Access | Local container network | Security-group controlled private connection |
| Configuration | Local environment variables | EC2 environment configuration |
| Hosting | Local computer | Amazon EC2 |
| Persistence | Docker volume | Managed Amazon RDS storage |

## Cloud Architecture Classification

The final environment is a two-tier deployment:

### Tier 1 — Application

Amazon EC2 running:

- Docker
- Spring Boot
- React production build

### Tier 2 — Database

Amazon RDS for MySQL.

The application remains monolithic even though the deployment has two tiers.

## End-to-End Validation

The transformation was validated by creating a task through the live AWS-hosted UI and confirming that the record was persisted in Amazon RDS.

```text
Browser
   |
   v
EC2
   |
   v
Docker
   |
   v
Spring Boot
   |
   v
RDS MySQL
```

## Key Learning Outcomes

This project demonstrates:

- local-to-cloud application migration
- Docker-based deployment
- EC2 application hosting
- managed relational databases
- VPC networking
- public and private subnet design
- security-group isolation
- environment-based configuration
- two-tier architecture
- practical cloud transformation

## Source Code

Application source code is maintained separately:

- React frontend: `Web-Development-Projects/React/TaskFlow`
- Spring Boot backend: `Java/TaskFlow-Backend`

This project focuses on documenting the cloud transformation process and AWS architecture.
