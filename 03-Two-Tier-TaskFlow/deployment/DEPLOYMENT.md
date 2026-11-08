# TaskFlow — Two-Tier AWS Deployment Guide

This document contains the complete deployment process used to deploy TaskFlow as a two-tier application on AWS.

## Final Architecture

```text
Users
  |
  | HTTP :80
  v
Amazon EC2 — Public Subnet
  |
  | Docker
  v
Spring Boot + React Production Build
  |
  | JDBC / MySQL :3306
  v
Amazon RDS MySQL — Private DB Subnets
```

### Architecture Classification

- Application style: Monolithic
- Deployment architecture: Two-tier
- Application tier: Amazon EC2
- Database tier: Amazon RDS for MySQL
- Container runtime: Docker
- AWS Region: `ap-southeast-2`

---

# 1. Local Application Preparation

TaskFlow consists of:

- React/Vite frontend
- Spring Boot backend
- MySQL database

During local development:

```text
React :5173
   |
Spring Boot :8080
   |
MySQL Docker :3306
```

For AWS deployment, React was bundled into Spring Boot so the frontend and backend could run as one application tier.

---

# 2. Configure React for Production

The frontend originally accessed Spring Boot through:

```javascript
const API_URL = "http://localhost:8080/api/tasks";
```

For production, change this to:

```javascript
const API_URL = "/api/tasks";
```

This allows the browser to send API requests to the same host serving the React application.

---

# 3. Build React

Navigate to the frontend:

```bash
cd ~/Documents/Projects/taskflow/frontend
```

Build the production bundle:

```bash
npm run build
```

Vite creates:

```text
frontend/dist/
```

---

# 4. Bundle React into Spring Boot

Create the Spring Boot static resources directory:

```bash
mkdir -p \
~/Documents/Projects/taskflow/taskflow-backend/src/main/resources/static
```

Copy the React production files:

```bash
cp -R \
~/Documents/Projects/taskflow/frontend/dist/* \
~/Documents/Projects/taskflow/taskflow-backend/src/main/resources/static/
```

Spring Boot can now serve:

```text
/
```

for the React application and:

```text
/api/tasks
```

for REST API requests.

---

# 5. Spring Boot Production Configuration

`application.properties` uses environment variables:

```properties
spring.application.name=taskflow-backend

spring.datasource.url=${SPRING_DATASOURCE_URL}
spring.datasource.username=${SPRING_DATASOURCE_USERNAME}
spring.datasource.password=${SPRING_DATASOURCE_PASSWORD}

spring.jpa.hibernate.ddl-auto=update
spring.jpa.show-sql=true

server.port=8080
```

No production database password is stored in source control.

---

# 6. Dockerfile

TaskFlow Backend uses a multi-stage Docker build.

```dockerfile
FROM eclipse-temurin:21-jdk-alpine AS build

WORKDIR /app

COPY mvnw .
COPY .mvn .mvn
COPY pom.xml .

RUN chmod +x mvnw
RUN ./mvnw dependency:go-offline

COPY src src

RUN ./mvnw clean package -DskipTests

FROM eclipse-temurin:21-jre-alpine

WORKDIR /app

COPY --from=build /app/target/*.jar app.jar

EXPOSE 8080

ENTRYPOINT ["java", "-jar", "app.jar"]
```

---

# 7. AWS VPC

Create a custom VPC.

### VPC

Name:

```text
taskflow-vpc
```

CIDR:

```text
10.0.0.0/16
```

---

# 8. Public Application Subnet

Create:

```text
taskflow-public-subnet-a
```

CIDR:

```text
10.0.1.0/24
```

Availability Zone:

```text
ap-southeast-2a
```

This subnet hosts the EC2 application server.

---

# 9. Private Database Subnets

Create two private subnets for the RDS DB subnet group.

### Private DB Subnet A

```text
Name: taskflow-private-db-subnet-a
CIDR: 10.0.2.0/24
AZ: ap-southeast-2a
```

### Private DB Subnet B

```text
Name: taskflow-private-db-subnet-b
CIDR: 10.0.3.0/24
AZ: ap-southeast-2b
```

The database subnets do not require a public internet route.

---

# 10. Internet Gateway

Create:

```text
taskflow-igw
```

Attach it to:

```text
taskflow-vpc
```

---

# 11. Public Route Table

Create:

```text
taskflow-public-rt
```

Associate it with:

```text
taskflow-public-subnet-a
```

Add:

```text
Destination: 0.0.0.0/0
Target: taskflow-igw
```

This allows EC2 internet access.

---

# 12. EC2 Security Group

Create:

```text
taskflow-ec2-sg
```

Inbound rules:

| Type | Port | Source |
|---|---:|---|
| HTTP | 80 | `0.0.0.0/0` |
| SSH | 22 | Administrator public IP |

Do not expose port `8080` directly to the internet.

Docker will map:

```text
EC2 :80 -> Container :8080
```

---

# 13. RDS Security Group

Create:

```text
taskflow-rds-sg
```

Inbound rule:

| Type | Port | Source |
|---|---:|---|
| MySQL/Aurora | 3306 | `taskflow-ec2-sg` |

Do not configure:

```text
0.0.0.0/0
```

for MySQL access.

The database should only accept connections from the application tier.

---

# 14. RDS DB Subnet Group

Create:

```text
taskflow-db-subnet-group
```

Add:

```text
taskflow-private-db-subnet-a
taskflow-private-db-subnet-b
```

---

# 15. Create Amazon RDS MySQL

Create an Amazon RDS MySQL instance.

Example configuration:

```text
DB identifier: taskflow-db
Engine: MySQL
Database name: taskflow
Master username: taskflow_admin
Public access: No
Port: 3306
VPC: taskflow-vpc
Security group: taskflow-rds-sg
DB subnet group: taskflow-db-subnet-group
Deployment: Single-AZ
```

Use the smallest appropriate database instance class for the project budget.

Do not store the RDS password in Git.

---

# 16. Launch EC2

Launch an Amazon Linux 2023 instance.

Example:

```text
Name: taskflow-app
VPC: taskflow-vpc
Subnet: taskflow-public-subnet-a
Public IPv4: Enabled
Security group: taskflow-ec2-sg
```

Use an existing trusted EC2 key pair or create a new one.

Example SSH connection:

```bash
ssh -i ~/.ssh/ecommerce-backend-key.pem \
ec2-user@<EC2_PUBLIC_IP>
```

---

# 17. Install Docker on EC2

```bash
sudo dnf update -y

sudo dnf install docker -y

sudo systemctl enable docker
sudo systemctl start docker

sudo usermod -aG docker ec2-user
```

Log out:

```bash
exit
```

Reconnect to apply the Docker group membership.

Verify:

```bash
docker --version
docker ps
```

---

# 18. Install MySQL-Compatible Client

On Amazon Linux:

```bash
sudo dnf install mariadb105 -y
```

---

# 19. Download Amazon RDS CA Certificate

```bash
cd ~

curl -O \
https://truststore.pki.rds.amazonaws.com/global/global-bundle.pem
```

Verify:

```bash
ls -l ~/global-bundle.pem
```

---

# 20. Test EC2-to-RDS Connectivity

Run from EC2:

```bash
mysql \
  -h <RDS_ENDPOINT> \
  -P 3306 \
  -u taskflow_admin \
  -p \
  --ssl-ca=/home/ec2-user/global-bundle.pem \
  --ssl-verify-server-cert
```

Enter the database password when prompted.

Verify:

```sql
SHOW DATABASES;
```

Expected database:

```text
taskflow
```

Then:

```sql
USE taskflow;
SHOW TABLES;
```

Before Spring Boot starts for the first time, this may return no tables.

Exit:

```sql
exit;
```

---

# 21. Transfer Application to EC2

From the local Mac:

```bash
scp \
  -i ~/.ssh/ecommerce-backend-key.pem \
  -r ~/Documents/Projects/taskflow/taskflow-backend \
  ec2-user@<EC2_PUBLIC_IP>:~/taskflow-app/
```

Connect to EC2 again.

```bash
ssh \
  -i ~/.ssh/ecommerce-backend-key.pem \
  ec2-user@<EC2_PUBLIC_IP>
```

Navigate to:

```bash
cd ~/taskflow-app/taskflow-backend
```

---

# 22. Build the Docker Image on EC2

```bash
docker build -t taskflow-backend .
```

Verify:

```bash
docker images
```

---

# 23. Create Production Environment File

Create:

```bash
nano ~/taskflow.env
```

Add:

```text
SPRING_DATASOURCE_URL=jdbc:mysql://<RDS_ENDPOINT>:3306/taskflow
SPRING_DATASOURCE_USERNAME=taskflow_admin
SPRING_DATASOURCE_PASSWORD=<RDS_PASSWORD>
```

Protect the file:

```bash
chmod 600 ~/taskflow.env
```

Never commit this file to GitHub.

---

# 24. Run TaskFlow Container

```bash
docker run -d \
  --name taskflow-backend \
  --restart unless-stopped \
  -p 80:8080 \
  --env-file ~/taskflow.env \
  taskflow-backend
```

Explanation:

```text
-d
```

runs the container in detached mode.

```text
-p 80:8080
```

maps EC2 HTTP port `80` to Spring Boot container port `8080`.

```text
--restart unless-stopped
```

allows Docker to restart the application automatically after Docker or EC2 restarts unless the container was explicitly stopped.

---

# 25. Verify Container

```bash
docker ps
```

Expected:

```text
taskflow-backend
```

with a port mapping similar to:

```text
0.0.0.0:80->8080/tcp
```

---

# 26. Check Spring Boot Logs

```bash
docker logs taskflow-backend
```

Or follow the logs:

```bash
docker logs -f taskflow-backend
```

Press:

```text
Ctrl+C
```

to stop following the logs.

This does not stop the Docker container because it is running in detached mode.

Expected successful startup includes:

```text
HikariPool-1 - Start completed
```

and:

```text
Started TaskflowBackendApplication
```

---

# 27. Access Live Application

Open:

```text
http://<EC2_PUBLIC_IP>
```

The browser should display the TaskFlow React interface.

HTTP is used for this demonstration deployment, so the browser may display:

```text
Not Secure
```

HTTPS is outside the scope of this low-cost deployment.

---

# 28. Validate Full Application Flow

Create a task using the React interface.

Example:

```text
Title: Task Deployment
Description: We need to deploy it in AWS
Priority: HIGH
Status: TODO
```

Then connect to RDS again.

```bash
mysql \
  -h <RDS_ENDPOINT> \
  -P 3306 \
  -u taskflow_admin \
  -p \
  --ssl-ca=/home/ec2-user/global-bundle.pem \
  --ssl-verify-server-cert
```

Run:

```sql
USE taskflow;

SHOW TABLES;

SELECT * FROM tasks;
```

The task created from the browser should appear in the RDS database.

This verifies:

```text
Browser
   |
React
   |
Spring Boot
   |
JPA / Hibernate
   |
Amazon RDS MySQL
```

---

# 29. Useful Docker Commands

Check running containers:

```bash
docker ps
```

Check all containers:

```bash
docker ps -a
```

View logs:

```bash
docker logs taskflow-backend
```

Stop application:

```bash
docker stop taskflow-backend
```

Start application:

```bash
docker start taskflow-backend
```

Restart application:

```bash
docker restart taskflow-backend
```

Remove container:

```bash
docker rm -f taskflow-backend
```

---

# 30. Redeployment

After application code changes:

```bash
docker rm -f taskflow-backend
```

Rebuild:

```bash
docker build -t taskflow-backend .
```

Run again:

```bash
docker run -d \
  --name taskflow-backend \
  --restart unless-stopped \
  -p 80:8080 \
  --env-file ~/taskflow.env \
  taskflow-backend
```

---

# 31. Security Practices

The deployment follows several security practices:

- RDS has no public access.
- Database port `3306` is not open to the internet.
- RDS accepts MySQL traffic only from the EC2 security group.
- SSH access is restricted to the administrator IP.
- Database passwords are stored outside Git.
- `.pem` private keys are never committed.
- `.env` files are ignored by Git.
- The application exposes HTTP port `80`, not Spring Boot port `8080`.

---

# 32. Cost Controls

This deployment intentionally avoids infrastructure that would add unnecessary cost for a portfolio project.

Not used:

- NAT Gateway
- Application Load Balancer
- Auto Scaling Group
- Multi-instance EC2 architecture
- Multi-AZ RDS deployment
- Route 53 custom domain

The architecture uses:

- one EC2 instance
- one Single-AZ RDS instance
- custom VPC networking

AWS Billing and Budgets should be monitored regularly.

---

# 33. Deployment Evidence

Recommended screenshots:

```text
01-live-taskflow.png
02-ec2-instance.png
03-docker-container.png
04-rds-instance.png
05-rds-task-data.png
06-security-groups.png
07-vpc-network.png
```

Store them under:

```text
03-Two-Tier-TaskFlow/screenshots/
```

---

# 34. Final Result

TaskFlow was successfully transformed into a functioning AWS two-tier application.

```text
Tier 1
Amazon EC2
Docker
Spring Boot + React

        |

Tier 2
Amazon RDS MySQL
```

The deployment demonstrates practical experience with:

- Amazon EC2
- Amazon RDS
- Amazon VPC
- public/private subnet design
- security groups
- Internet Gateway
- route tables
- Docker
- Spring Boot
- React
- MySQL
- environment-based configuration
- end-to-end cloud deployment
