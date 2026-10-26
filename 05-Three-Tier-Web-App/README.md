# Three-Tier Web Application on AWS

This project demonstrates the deployment of a full-stack e-commerce application using a three-tier architecture on AWS.

The application consists of:

- React frontend
- Spring Boot REST API backend
- MySQL database
- AWS networking and security configuration

## Architecture

```text
User Browser
     |
     | HTTPS
     v
Amazon CloudFront
     |
     |-----------------------------|
     |                             |
     v                             v
Amazon S3                     /api/*
React Frontend                    |
                                  v
                              Amazon EC2
                              Spring Boot
                                  |
                                  v
                              Amazon RDS
                              MySQL
```

## AWS Services Used

- Amazon VPC
- Public and private subnets
- Internet Gateway
- Amazon EC2
- Amazon RDS for MySQL
- Amazon S3
- Amazon CloudFront
- CloudFront Origin Access Control
- CloudFront Functions
- AWS Security Groups
- Amazon EBS
- AWS Budgets

## Application Architecture

### Presentation Tier

The React application is built using Vite and deployed to a private Amazon S3 bucket.

Amazon CloudFront serves the frontend over HTTPS.

The S3 bucket is not publicly accessible. CloudFront accesses the bucket using Origin Access Control.

A CloudFront Function handles React SPA routing so routes such as:

```text
/shop
/shop/products
/shop/cart
/shop/orders
```

continue to work after refreshing the browser.

### Application Tier

The Spring Boot backend runs on an Amazon EC2 `t3.micro` instance.

The application is packaged as an executable WAR file and runs using Java 21.

The backend is managed using a Linux `systemd` service so that it:

- starts automatically when EC2 starts
- continues running after the SSH session closes
- automatically restarts after application failures

CloudFront routes requests matching:

```text
/api/*
```

to the Spring Boot application running on EC2 port `8080`.

### Database Tier

The application uses Amazon RDS for MySQL.

Configuration:

```text
Engine: MySQL 8.4
Instance class: db.t4g.micro
Storage: 20 GB gp3
Deployment: Single-AZ
Public access: Disabled
```

The RDS database is placed inside private subnets.

Only the EC2 backend security group is allowed to connect to MySQL port `3306`.

The existing local MySQL database was exported using `mysqldump` and migrated to Amazon RDS.

## Network Architecture

The project uses a custom VPC:

```text
VPC CIDR
10.0.0.0/16
```

The VPC contains:

- 2 public subnets
- 2 private subnets
- 2 Availability Zones
- Internet Gateway
- No NAT Gateway

The EC2 backend runs in a public subnet.

The RDS database runs in private subnets and cannot be directly accessed from the public internet.

## Security Groups

### EC2 Security Group

Allows:

```text
SSH 22     → My IP
HTTP 8080  → CloudFront origin-facing managed prefix list
```

During development, port `8080` may also temporarily be allowed from the developer's IP for direct API testing.

### RDS Security Group

Allows:

```text
MySQL 3306 → EC2 Security Group
```

The database is therefore accessible from the backend application but not directly from the internet.

## CloudFront Routing

CloudFront contains two origins.

### Default Origin

```text
/*
   ↓
Amazon S3
   ↓
React frontend
```

### API Origin

```text
/api/*
   ↓
Amazon EC2 :8080
   ↓
Spring Boot
   ↓
Amazon RDS
```

API caching is disabled using the CloudFront `CachingDisabled` policy.

## React SPA Routing

React routes are handled using a CloudFront Function.

Requests such as:

```text
/shop/products
/shop/cart
/shop/orders
```

are rewritten internally to:

```text
/index.html
```

Static assets and `/api/*` requests are not rewritten.

## Backend Service Management

The Spring Boot application is registered as a Linux systemd service.

Example management commands:

```bash
sudo systemctl status ecommerce
sudo systemctl restart ecommerce
sudo journalctl -u ecommerce -f
```

The application runs with JVM memory limits suitable for the `t3.micro` instance.

```text
-Xms128m
-Xmx512m
```

A 1 GB Linux swap file was also configured on the EC2 instance.

## Database Migration

The original local database was exported using:

```bash
mysqldump
```

and imported into Amazon RDS.

Migrated application tables include:

```text
customers
inventory
order_items
orders
payments
products
```

This allowed the cloud-deployed application to continue using existing application data rather than starting with an empty database.

## Monitoring

Spring Boot Actuator is enabled for application monitoring.

Health checks verify:

- Spring Boot application status
- MySQL database connectivity
- disk space
- liveness
- readiness

Custom Micrometer metrics are also implemented for service execution performance.

## Audit Logging

Business operations such as product creation, replacement, price updates, and deletion are audited using Spring AOP.

Audit records are written to an Excel file on the EC2 instance.

Future improvements will integrate Spring Security so audit entries can include authenticated user information such as actor, role, and request information.

## Cost-Conscious Design

This first deployment intentionally uses a low-cost architecture.

The following services were avoided:

- NAT Gateway
- Application Load Balancer
- Multi-AZ RDS
- multiple EC2 instances
- RDS Proxy
- AWS WAF

This keeps the architecture suitable for learning and portfolio demonstration while still demonstrating real AWS networking and deployment concepts.

## Project Documentation

More detailed deployment notes are available in:

```text
deployment/
├── ec2-setup.md
├── rds-setup.md
├── s3-cloudfront-setup.md
└── security-groups.md
```

Architecture diagrams are stored in:

```text
architecture/
```

Deployment screenshots are stored in:

```text
screenshots/
```

## Future Improvements

Planned improvements include:

- Spring Security authentication and authorization
- CUSTOMER and ADMIN roles
- authenticated audit logging
- Spring AI integration
- Docker containerization
- Prometheus and Grafana monitoring
- CI/CD deployment pipeline
- HTTPS custom domain
- high-availability architecture using an Application Load Balancer and multiple EC2 instances

## Key Learning Outcomes

This project provided practical experience with:

- AWS VPC networking
- public and private subnet design
- security groups
- EC2 deployment
- Linux systemd services
- Amazon RDS
- database migration
- S3 static frontend hosting
- CloudFront distributions
- CloudFront path-based routing
- CloudFront Functions
- Origin Access Control
- AWS-managed prefix lists
- full-stack cloud deployment
- AWS cost-conscious architecture
