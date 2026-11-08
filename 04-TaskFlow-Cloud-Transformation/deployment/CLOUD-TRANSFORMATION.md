# TaskFlow — Local-to-AWS Cloud Transformation

This document describes how TaskFlow was transformed from a local Docker-based development environment into a two-tier AWS deployment.

## 1. Original Local Architecture

TaskFlow initially ran entirely on a development machine.

```text
Browser
   |
React / Vite
localhost:5173
   |
Spring Boot Docker
localhost:8080
   |
MySQL Docker
```

The local environment used:

- React/Vite
- Spring Boot
- MySQL
- Docker
- Docker networking
- Docker volumes

---

# 2. Problems with the Local Architecture

The original setup was suitable for development but not for public cloud hosting.

Limitations included:

- application only accessible locally
- database tied to a local Docker container
- frontend development server unsuitable for production
- no cloud network isolation
- no managed database
- no public application host
- no AWS security-group based access control

---

# 3. Transformation Objective

The goal was to transform the application into:

```text
Users
   |
Amazon EC2
Docker
Spring Boot + React
   |
Amazon RDS MySQL
```

while keeping costs low and maintaining a simple architecture appropriate for a portfolio deployment.

---

# 4. Frontend Transformation

The React development server was removed from the production architecture.

Original API configuration:

```javascript
const API_URL = "http://localhost:8080/api/tasks";
```

Production configuration:

```javascript
const API_URL = "/api/tasks";
```

The React application was built:

```bash
npm run build
```

The generated files were copied into:

```text
src/main/resources/static/
```

inside Spring Boot.

Spring Boot therefore became responsible for serving:

- React static files
- REST API endpoints

---

# 5. Application Transformation

The Spring Boot application remained containerized.

Local:

```text
Spring Boot Docker
```

AWS:

```text
Amazon EC2
   |
Docker
   |
Spring Boot + React
```

The same application architecture could therefore move from local development to EC2 with minimal code changes.

---

# 6. Database Transformation

Before:

```text
MySQL Docker Container
```

After:

```text
Amazon RDS for MySQL
```

This moved database responsibility from a locally managed container to a managed AWS database service.

Advantages include:

- managed database engine
- persistent managed storage
- database backups and maintenance capabilities
- private VPC networking
- security-group controlled access

---

# 7. Configuration Transformation

Local development used Docker Compose environment variables.

AWS deployment uses EC2 environment configuration.

Spring Boot reads:

```text
SPRING_DATASOURCE_URL
SPRING_DATASOURCE_USERNAME
SPRING_DATASOURCE_PASSWORD
```

No AWS database credentials are stored in source control.

---

# 8. Network Transformation

Before:

```text
Docker Network
```

After:

```text
Amazon VPC
10.0.0.0/16
```

The VPC contains:

```text
Public application subnet
10.0.1.0/24

Private DB subnet A
10.0.2.0/24

Private DB subnet B
10.0.3.0/24
```

---

# 9. Internet Connectivity

The application subnet uses an Internet Gateway.

```text
Internet
   |
Internet Gateway
   |
Public Route Table
   |
EC2
```

The database subnets do not have a direct public internet route.

---

# 10. Security Transformation

Local Docker networking was replaced by AWS Security Groups.

### Application Tier

EC2 security group allows:

```text
HTTP 80
SSH 22 from administrator IP
```

### Database Tier

RDS security group allows:

```text
MySQL 3306
```

only from:

```text
taskflow-ec2-sg
```

This prevents direct public MySQL access.

---

# 11. Deployment Transformation

Before:

```bash
docker compose up
```

After:

```text
Build React
   |
Bundle React into Spring Boot
   |
Build Docker image
   |
Transfer source to EC2
   |
Build container on EC2
   |
Connect to Amazon RDS
   |
Run container
```

---

# 12. Production Container

The AWS container is started using:

```bash
docker run -d \
  --name taskflow-backend \
  --restart unless-stopped \
  -p 80:8080 \
  --env-file ~/taskflow.env \
  taskflow-backend
```

The EC2 host exposes HTTP port `80`.

Spring Boot continues listening internally on:

```text
8080
```

---

# 13. Before vs After

| Component | Local | AWS |
|---|---|---|
| Frontend | React/Vite dev server | React production build |
| Frontend hosting | localhost:5173 | Spring Boot on EC2 |
| Backend | Spring Boot Docker | Spring Boot Docker on EC2 |
| Database | MySQL Docker | Amazon RDS MySQL |
| Network | Docker network | Amazon VPC |
| Application access | localhost | EC2 public IP |
| Database access | Docker network | Private VPC connection |
| Security | local ports | AWS Security Groups |
| Persistence | Docker volume | Amazon RDS |
| Configuration | local environment | EC2 environment file |

---

# 14. End-to-End Verification

The transformed application was tested by creating a task using the public web application.

The request passed through:

```text
Browser
   |
React
   |
Spring Boot REST API
   |
Hibernate / JPA
   |
Amazon RDS MySQL
```

The persisted record was verified directly using:

```sql
USE taskflow;

SELECT * FROM tasks;
```

---

# 15. Final Architecture

```text
                 AWS Cloud
                     |
              TaskFlow VPC
                     |
        +------------+------------+
        |                         |
 Public Application           Private DB
     Subnet                    Subnets
        |                         |
       EC2                       RDS
        |                        MySQL
     Docker                       |
        |                         |
 Spring Boot + React ------------+
          JDBC 3306
```

---

# 16. Cloud Transformation Outcomes

The project demonstrates:

- migration from local infrastructure to AWS
- Docker portability
- frontend production packaging
- EC2 application hosting
- Amazon RDS migration
- custom VPC creation
- public/private subnet design
- Internet Gateway configuration
- route-table configuration
- security-group isolation
- secure application-to-database communication
- environment-based application configuration
- two-tier architecture design
- end-to-end cloud validation

---

# 17. Relationship to Two-Tier Project

The same TaskFlow deployment is documented from two perspectives.

### Two-Tier TaskFlow

Focus:

```text
How the final AWS architecture is structured.
```

Location:

```text
03-Two-Tier-TaskFlow/
```

### TaskFlow Cloud Transformation

Focus:

```text
How the local application was transformed into the AWS deployment.
```

Location:

```text
04-TaskFlow-Cloud-Transformation/
```

The application source code remains maintained separately in the Java and Web Development repositories.
