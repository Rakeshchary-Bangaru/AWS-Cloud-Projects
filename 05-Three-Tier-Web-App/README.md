
# Three-Tier Web Application on AWS — ECommerceOrderEngine V7

## Overview

This project demonstrates the deployment of **ECommerceOrderEngine V7**, a secure full-stack e-commerce application using a three-tier architecture on Amazon Web Services (AWS).

The project evolved from a Core Java order-processing system into a React and Spring Boot application featuring authentication, authorization, database transactions, monitoring, logging, and cloud infrastructure.

The deployed application consists of:

- React frontend built with Vite
- Java 21 and Spring Boot REST API backend
- Spring Security with JWT authentication
- Google OAuth2 / OpenID Connect
- Google reCAPTCHA Enterprise
- Role-based and permission-based authorization
- Spring Data JPA and Hibernate
- MySQL database hosted on Amazon RDS
- Spring AOP for auditing and performance monitoring
- Log4j2 for application logging
- Spring Boot Actuator and Micrometer
- Product image management
- AWS networking, security, storage, and CDN configuration

**Current Version:** V7

**Live Application:** https://dsohu6n1v0a1o.cloudfront.net

---

## Architecture

The application follows a three-tier architecture:

1. Presentation Tier — React
2. Application Tier — Spring Boot
3. Database Tier — MySQL

### High-Level AWS Architecture

```text
                         User Browser
                              |
                              | HTTPS
                              v
                       Amazon CloudFront
                              |
                  +-----------+-----------+
                  |                       |
                  v                       v
              Amazon S3              Backend Origin
           React Frontend                 |
                                          v
                                    Nginx (EC2)
                                          |
                                          v
                                    Spring Boot
                                          |
                               +----------+----------+
                               |                     |
                               v                     v
                          Amazon RDS           Product Image
                            MySQL                Storage
```

The React application is delivered through Amazon CloudFront.

Backend API requests and OAuth2 authentication requests are routed through CloudFront to the backend origin.

The backend uses Nginx as a reverse proxy in front of Spring Boot.

MySQL runs in private subnets using Amazon RDS.

---

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
- AWS-managed prefix lists

### AWS Service Responsibilities

| Service | Purpose |
|---|---|
| Amazon VPC | Network isolation |
| Public Subnets | EC2 backend hosting |
| Private Subnets | RDS database isolation |
| Internet Gateway | Internet connectivity |
| Amazon EC2 | Spring Boot application |
| Amazon RDS | MySQL database |
| Amazon S3 | React frontend hosting |
| Amazon CloudFront | HTTPS content delivery and API routing |
| CloudFront OAC | Secure access to private S3 frontend |
| CloudFront Functions | React SPA routing |
| Security Groups | Network-level access restrictions |
| Amazon EBS | EC2 storage |
| AWS Budgets | Cost monitoring |

---

## Application Architecture

### Presentation Tier

The frontend is implemented using:

- React
- JavaScript
- Vite
- React Router
- Context API
- HTML
- CSS

The application is built using Vite and deployed to a private Amazon S3 bucket.

```text
React Source Code
        |
        v
    npm run build
        |
        v
      dist/
        |
        v
    Amazon S3
        |
        v
  Amazon CloudFront
        |
        v
   HTTPS Website
```

Amazon CloudFront serves the frontend over HTTPS.

The S3 bucket is not publicly accessible.

CloudFront accesses the bucket through Origin Access Control.

### Frontend Features

- Homepage
- Product catalogue
- Product search and filtering
- Product availability indicators
- Product image display
- Guest shopping cart
- Authenticated shopping cart
- Cart quantity management
- Checkout interface
- Personal order history
- Login and registration
- Google OAuth2 sign-in
- Customer profile management
- Account settings
- Administrative dashboard
- Seller dashboard
- IT support dashboard
- Role-based navigation

### React SPA Routing

React Router provides client-side navigation.

A CloudFront Function handles SPA routing so that refreshing routes such as:

```text
/shop
/shop/products
/shop/cart
/shop/checkout
/shop/orders
/login
/register
/admin/dashboard
/seller/dashboard
/support/dashboard
```

continues to load the React application.

Frontend navigation requests are internally rewritten to:

```text
/index.html
```

Backend API requests, OAuth2 endpoints, and static assets must not be rewritten to `index.html`.

---

## Application Tier

The Spring Boot backend runs on an Amazon EC2 `t3.micro` instance.

### Backend Configuration

```text
Java Version: 21
Framework: Spring Boot
Packaging: Executable WAR
Instance Type: t3.micro
Operating System: Amazon Linux
Application Port: 8080
Reverse Proxy: Nginx
Process Manager: systemd
```

### Backend Technologies

- Java 21
- Spring Boot
- Spring Web MVC
- Spring Security
- Spring Data JPA
- Hibernate
- Spring AOP
- Log4j2
- Flyway
- Spring Boot Actuator
- Micrometer
- Maven

### Backend Request Flow

```text
User Browser
     |
     v
Amazon CloudFront
     |
     v
Nginx Reverse Proxy
     |
     v
Spring Security Filter Chain
     |
     v
REST Controller
     |
     v
Service Layer
     |
     v
Spring Data JPA
     |
     v
Hibernate ORM
     |
     v
Amazon RDS MySQL
```

The backend is registered as a Linux `systemd` service.

The service:

- Starts automatically when EC2 starts
- Continues running after SSH sessions close
- Restarts automatically after configured application failures
- Provides operational logs through the Linux system journal

### Backend Service Management

```bash
sudo systemctl status ecommerce
sudo systemctl restart ecommerce
sudo journalctl -u ecommerce -f
```

### JVM Memory Configuration

The backend uses memory limits appropriate for the EC2 instance.

```text
-Xms128m
-Xmx512m
```

A 1 GB Linux swap file was configured to provide additional memory headroom.

---

## Database Tier

The application uses Amazon RDS for MySQL.

### Database Configuration

```text
Engine: MySQL 8.4
Instance Class: db.t4g.micro
Storage: 20 GB gp3
Deployment: Single-AZ
Public Access: Disabled
```

The RDS instance is deployed in private subnets.

Only the EC2 backend security group is allowed to connect to MySQL port `3306`.

### Database Architecture

```text
Spring Boot Application
         |
         | MySQL Port 3306
         v
     Amazon RDS
         |
         v
      MySQL 8.4
```

The database is not directly accessible from the public internet.

### Database Technologies

- Spring Data JPA
- Hibernate ORM
- Flyway migrations
- Transaction management
- Database constraints
- Atomic inventory reservation
- Persistent orders and payments

### Flyway Database Migrations

Flyway manages version-controlled database schema changes.

```text
Spring Boot Startup
        |
        v
Flyway Migration Validation
        |
        v
Apply Pending Migrations
        |
        v
Spring Data JPA / Hibernate
        |
        v
Amazon RDS MySQL
```

Flyway helps keep the deployed database schema consistent with the application version.

---

## Network Architecture

The project uses a custom VPC.

### VPC Configuration

```text
VPC CIDR: 10.0.0.0/16

Public Subnets: 2
Private Subnets: 2

Availability Zones: 2

Internet Gateway: Enabled

NAT Gateway: Not Used
```

### Network Diagram

```text
                      AWS VPC
                   10.0.0.0/16
                         |
            +------------+------------+
            |                         |
            v                         v
       Public Subnets            Private Subnets
            |                         |
            v                         v
       EC2 Backend                RDS MySQL
            |                         ^
            |                         |
            +------- MySQL 3306 ------+
```

The EC2 backend runs in a public subnet.

The RDS database runs in private subnets.

The database is not publicly accessible.

The VPC spans two Availability Zones, but the RDS database uses a Single-AZ deployment to minimize costs.

### Why No NAT Gateway?

NAT Gateway introduces additional hourly and data-processing costs.

This deployment avoids NAT Gateway because the private RDS database does not require general internet access for normal application queries.

---

## Security Groups

Security groups provide network-level access control.

Spring Security provides application-level authentication and authorization.

These operate independently and protect different layers.

### EC2 Security Group

The original deployment allowed:

```text
SSH 22
    -> Developer IP

HTTP 8080
    -> CloudFront origin-facing managed prefix list
```

After introducing Nginx, the backend origin's network rules must match the configured Nginx listener and CloudFront origin port.

Direct access to Spring Boot port `8080` should be restricted where Nginx is used as the public-facing reverse proxy.

During development, temporary direct API access may be allowed from a trusted developer IP.

### RDS Security Group

```text
MySQL 3306
    -> EC2 Security Group
```

The RDS database accepts connections from the authorized EC2 application infrastructure.

It does not accept direct internet connections.

---

## CloudFront Routing

CloudFront is responsible for frontend delivery and backend routing.

### Default Origin

```text
/*
   |
   v
Amazon S3
   |
   v
React Frontend
```

### API Origin

```text
/api/*
   |
   v
EC2 Backend Origin
   |
   v
Nginx
   |
   v
Spring Boot
   |
   v
Amazon RDS
```

### OAuth2 Origin Routing

Google OAuth2 requires additional backend paths.

```text
/oauth2/*
   |
   v
Spring Security OAuth2

/login/oauth2/*
   |
   v
Google OAuth2 Callback
```

These requests must reach Spring Boot rather than being rewritten to the React application.

### CloudFront Behaviors

| Path Pattern | Destination |
|---|---|
| Default `*` | Amazon S3 |
| `/api/*` | Backend origin |
| `/oauth2/*` | Backend origin |
| `/login/oauth2/*` | Backend origin |

API and authentication paths must use suitable cache policies.

Authenticated API responses should not be cached as shared public content.

### React SPA Routing

The CloudFront Function rewrites frontend navigation requests to:

```text
/index.html
```

Requests for backend endpoints and static files must remain unchanged.

---

## Spring Security

ECommerceOrderEngine V7 introduces Spring Security for authentication and authorization.

### Security Features

- JWT authentication
- Google OAuth2 / OpenID Connect
- Role-based authorization
- Permission-based authorization
- Resource ownership enforcement
- Customer order isolation
- Account status validation
- Protected administrative endpoints

### Authentication Architecture

```text
React Login
     |
     v
Spring Boot Authentication API
     |
     v
Spring Security
     |
     v
Authentication Validation
     |
     v
JWT Generation
     |
     v
Authenticated React Session
     |
     v
Protected REST APIs
```

### Application Roles

```text
CUSTOMER

SELLER_ADMIN

IT_SUPPORT

ROOT
```

### Role-Based Access Control

| Functionality | CUSTOMER | SELLER_ADMIN | IT_SUPPORT | ROOT |
|---|---|---|---|---|
| Browse Products | Yes | Yes | Yes | Yes |
| Manage Own Cart | Yes | Yes | Yes | Yes |
| Checkout | Yes | Yes | Yes | Yes |
| View Own Orders | Yes | Yes | Yes | Yes |
| Manage Products | No | Owned Products | No | All Products |
| Manage Inventory | No | Owned Products | No | All Products |
| Manage Product Images | No | Owned Products | No | All Products |
| Manage User Accounts | No | No | Authorized Actions | Yes |
| Assign / Remove Roles | No | No | Yes | Yes |
| Full Administrative Access | No | No | No | Yes |

All authenticated roles retain normal shopping capabilities.

Administrative permissions provide additional functionality without removing customer-facing shopping access.

Backend authorization must enforce these permissions independently of React navigation.

### ROOT Role

ROOT is the highest-privilege application role.

ROOT can:

- Manage all products
- Manage global inventory
- Manage all product images
- Manage users and roles
- Access administrative operations

Multiple accounts may hold the ROOT role.

ROOT is not restricted to one hardcoded user.

### SELLER_ADMIN Role

SELLER_ADMIN can manage:

- Products owned by the seller
- Inventory associated with owned products
- Images belonging to owned products
- Authorized seller-specific operations

A SELLER_ADMIN must not manage resources belonging to another seller.

### IT_SUPPORT Role

IT_SUPPORT handles authorized user-account and role-administration operations.

IT_SUPPORT does not receive product inventory management or product image management permissions.

### CUSTOMER Role

CUSTOMER can:

- Browse products
- Add products to cart
- Checkout
- View personal order history
- Manage their own account

Customer order data must remain isolated between accounts.

---

## Google OAuth2 Authentication

V7 integrates Google OAuth2 and OpenID Connect through Spring Security.

### Google Login Flow

```text
React Login Page
       |
       v
Continue with Google
       |
       v
Spring Security OAuth2
       |
       v
Google Authentication
       |
       v
Google OIDC Callback
       |
       v
GoogleOAuth2AccountService
       |
       v
Temporary One-Time Login Code
       |
       v
React GoogleAuthCallback
       |
       v
POST /api/auth/oauth2/exchange
       |
       v
Application JWT
       |
       v
Authenticated User
```

### OAuth2 Security Features

- Verified Google email is required
- Google subject identifier is used for account identity
- New Google users receive CUSTOMER role
- Existing roles are preserved for recognized Google accounts
- Existing local accounts are not automatically linked by matching email
- One-time exchange codes expire after 60 seconds
- Exchange codes are single-use
- Exchange codes are session-bound
- Application JWTs are not placed in redirect URLs

### OAuth2 Routes

```text
GET /oauth2/authorization/google

GET /login/oauth2/code/google

POST /api/auth/oauth2/exchange
```

OAuth2 client secrets remain in backend environment configuration.

They must never be included in React source code or public GitHub repositories.

---

## Google reCAPTCHA Enterprise

Google reCAPTCHA Enterprise is integrated into authentication-related workflows.

### Purpose

- Detect suspicious authentication requests
- Reduce automated abuse
- Provide bot-risk assessment
- Strengthen registration and login protection

### Request Flow

```text
React Authentication Form
          |
          v
Google reCAPTCHA Token
          |
          v
Spring Boot Authentication API
          |
          v
Server-Side Token Assessment
          |
          v
Authentication Processing
```

The backend verifies the assessment rather than trusting the browser alone.

---

## Product Image Management

V7 supports product image upload and management.

### Authorization

- ROOT can manage images for all products
- SELLER_ADMIN can manage images for owned products
- CUSTOMER cannot upload or modify product images
- IT_SUPPORT cannot upload or modify product images

### Upload Workflow

```text
Authorized User
       |
       v
React Product Management
       |
       v
Spring Boot Image API
       |
       v
Validate Image
       |
       v
Verify Role and Ownership
       |
       v
Configured Image Storage
       |
       v
Save Image Metadata in MySQL
```

Product-image metadata is maintained separately from image content.

### Storefront Image Display

The React application uses a reusable `ProductImage` component.

```jsx
<ProductImage
  productId={product.id}
  productName={product.name}
/>
```

Images are displayed in:

```text
/shop
/shop/products
/shop/cart
```

Product identifiers are used internally without needing to display them in customer-facing cart items.

Image content must be served through the configured backend storage and retrieval mechanisms.

---

## Shopping Cart and Checkout

### Cart Persistence

Guest carts use browser session storage.

Authenticated users have account-scoped browser storage.

```text
Guest Cart:
sessionStorage

Authenticated Cart:
localStorage
```

### Checkout

The checkout workflow includes:

- Product selection
- Cart quantity management
- Authenticated checkout
- Server-side product-price validation
- Stock availability checks
- Atomic inventory reservation
- Order creation
- Transaction management
- Personal order history

All authenticated roles are intended to retain shopping functionality.

Backend checkout authorization and customer-profile association must be verified for each administrative role.

### Order Isolation

Personal order history must only expose orders belonging to the authenticated account.

Seller-specific order management is separate from personal shopping history.

---

## Database Migration

The original local MySQL database was exported using:

```bash
mysqldump
```

and imported into Amazon RDS.

The original application data included:

```text
customers
inventory
order_items
orders
payments
products
```

V7 also uses tables supporting:

```text
User accounts and roles
Authentication identities
Product ownership
Product image metadata
```

Flyway manages subsequent database schema changes.

### Database Migration Workflow

```text
Local MySQL
     |
     v
mysqldump Export
     |
     v
Database Backup
     |
     v
Amazon RDS Import
     |
     v
Flyway Migrations
     |
     v
Spring Boot Application
```

This allows the AWS-deployed application to preserve existing data while evolving its schema.

---

## Spring AOP

Spring Aspect-Oriented Programming was introduced during V6.

V7 continues using it for cross-cutting concerns.

### AOP Components

- MethodLoggingAspect
- PerformanceMetricsAspect
- Business operation auditing

### Method Logging

```text
Controller / Service Method
          |
          v
Spring AOP Advice
          |
          +---- Method Entry
          |
          +---- Method Exit
          |
          +---- Exception Information
```

### Performance Measurement

Spring AOP measures selected method execution times.

Example:

```text
ENTER ProductController.getAllProducts

PERFORMANCE ProductController.getAllProducts
Execution Time: 64 ms

EXIT ProductController.getAllProducts
```

### Audit Logging

Business operations such as:

- Product creation
- Product updates
- Product price changes
- Product deletion
- Inventory modifications

can be audited through the relevant application components.

The original deployment used an Excel audit file stored on the EC2 instance.

Authentication-aware audit fields can include the acting user and role, provided the deployed audit implementation explicitly captures those values.

Sensitive credentials must never be included in audit records.

---

## Log4j2 Logging

V7 introduces Log4j2 for application logging.

### Logging Features

- Structured application logging
- Controller and service diagnostics
- Exception logging
- Authentication and authorization diagnostics
- Performance-related events
- Application startup logging
- Operational troubleshooting

### Logging Architecture

```text
Spring Boot Application
         |
         +---- Controllers
         |
         +---- Services
         |
         +---- Security Components
         |
         +---- Spring AOP
         |
         v
       Log4j2
         |
         v
  Application Logs
```

Logs can be inspected through the backend's configured logging output and service journal.

### Sensitive Data Protection

Application logs must not expose:

```text
Passwords
JWT tokens
OAuth2 authorization codes
Google client secrets
Database passwords
API keys
Session cookies
```

---

## Monitoring

Spring Boot Actuator is enabled for application monitoring.

### Health Checks

Monitoring includes:

- Spring Boot application status
- MySQL database connectivity
- Disk space
- Liveness
- Readiness

### Micrometer

Micrometer provides metrics for:

- HTTP requests
- JVM runtime
- Application performance
- Service execution timing
- Operational diagnostics

### Monitoring Architecture

```text
Spring Boot Application
          |
          v
    Spring Boot Actuator
          |
          v
       Micrometer
          |
          v
   Application Metrics
```

Sensitive Actuator endpoints should remain restricted from public access.

Prometheus and Grafana may be evaluated in future versions.

---

## Testing

ECommerceOrderEngine uses automated tests across multiple application layers.

### Test Coverage Areas

- Unit tests
- Service tests
- Repository integration tests
- REST controller tests
- Database transaction tests
- Concurrent checkout tests
- Inventory reservation tests
- Spring Security authorization tests
- Role and permission tests
- OAuth2 authentication tests
- Application startup tests

### Run Backend Tests

```bash
mvn test
```

### Build Backend

```bash
mvn clean package
```

### Build React Frontend

```bash
npm run build
```

Test results should be taken from the latest Maven and frontend build reports.

---

## Backend Service Management

The Spring Boot backend is registered as a Linux systemd service.

### Check Backend Status

```bash
sudo systemctl status ecommerce
```

### Restart Backend

```bash
sudo systemctl restart ecommerce
```

### View Application Logs

```bash
sudo journalctl -u ecommerce -f
```

### Check Nginx

```bash
sudo systemctl status nginx
```

### Verify Nginx Configuration

```bash
sudo nginx -t
```

---

## Frontend Deployment

The React frontend is deployed using Amazon S3 and CloudFront.

### Build React

```bash
npm run build
```

### Upload to Amazon S3

Upload the contents of:

```text
dist/
```

to the existing private frontend bucket.

The generated `index.html` and `assets/` files must be stored at the bucket root.

### CloudFront Invalidation

After uploading the frontend build, create a CloudFront invalidation:

```text
/*
```

This refreshes cached frontend content.

### Existing Production URL

https://dsohu6n1v0a1o.cloudfront.net

---

## Cost-Conscious Design

This deployment uses a deliberately low-cost AWS architecture.

### Current Budget Goal

```text
AWS Monthly Budget: Approximately USD 35
```

### Services Intentionally Avoided

- NAT Gateway
- Application Load Balancer
- Multi-AZ RDS
- Multiple EC2 instances
- RDS Proxy
- AWS WAF

### Cost-Saving Decisions

- Single EC2 application instance
- Single-AZ RDS deployment
- Private S3 static frontend hosting
- CloudFront CDN
- No NAT Gateway
- No load balancer
- Minimal infrastructure complexity

Actual AWS costs depend on instance usage, storage, requests, traffic, regional pricing, and applicable credits.

AWS Budgets provides cost visibility but does not automatically enforce a hard spending limit.

---

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

---

## Current Deployment Status

### V7 Implemented

- React frontend deployment
- Spring Boot backend deployment
- Amazon RDS MySQL integration
- CloudFront HTTPS delivery
- Private S3 frontend hosting
- Spring Security
- JWT authentication
- Google OAuth2
- Google reCAPTCHA Enterprise
- Role-based authorization
- Spring AOP
- Log4j2
- Actuator and Micrometer
- Flyway migrations
- Product image management

### Ongoing Verification

- Product update validation behavior
- Checkout for ROOT, SELLER_ADMIN, and IT_SUPPORT
- Order ownership and account-profile association
- End-to-end regression testing of role permissions

---

## Future Improvements

### V8 — Spring AI

Planned features:

- Spring AI integration
- AI-powered product recommendations
- Conversational shopping assistance
- Natural-language product search
- AI-supported customer interactions

### V9 — Docker and Microservices

Planned features:

- Docker containerization
- Docker Compose
- Microservices architecture
- Service-to-service communication
- Independent service deployment
- Distributed application monitoring
- Service ownership boundaries

Potential microservices include:

```text
Authentication Service
Product Service
Inventory Service
Order Service
Payment Service
```

### V10 — Kubernetes, Docker and Jenkins CI/CD

Planned features:

- Kubernetes orchestration
- Docker image builds
- Jenkins CI/CD pipeline
- Automated testing
- Automated deployment
- Kubernetes Deployments and Services
- Rolling updates
- Health and readiness probes
- Container registry integration
- Scalable application deployment

### Proposed Jenkins Pipeline

```text
Git Push
   |
   v
Jenkins
   |
   +---- Checkout Source
   |
   +---- Build Spring Boot
   |
   +---- Run Automated Tests
   |
   +---- Build React
   |
   +---- Build Docker Images
   |
   +---- Push Images to Registry
   |
   +---- Deploy to Kubernetes
   |
   v
Deployment Verification
```

### Additional Future Improvements

- Prometheus and Grafana monitoring
- HTTPS custom domain
- Infrastructure as Code
- Distributed tracing
- Redis caching
- Kafka-based asynchronous processing
- High-availability infrastructure
- Application Load Balancer
- Multiple EC2 instances

Future infrastructure changes will be evaluated against AWS operating costs before implementation.

---

## Version Roadmap

```text
V1  Core Java
     COMPLETED
       |
       v
V2  Maven + JDBC + MySQL
     COMPLETED
       |
       v
V3  Servlets + JSP + Tomcat
     COMPLETED
       |
       v
V4  Hibernate + JPA
     COMPLETED
       |
       v
V5  Spring Framework + Spring Boot
     COMPLETED
       |
       v
V6  REST APIs + Spring Data JPA
    + React + Spring AOP
     COMPLETED
       |
       v
V7  Spring Security + JWT + OAuth2
    + Log4j2 + Monitoring + AWS
     CURRENT
       |
       v
V8  Spring AI
     PLANNED
       |
       v
V9  Docker + Microservices
     PLANNED
       |
       v
V10 Kubernetes + Docker
    + Jenkins CI/CD
     PLANNED
```

---

## Key Learning Outcomes

This project provided practical experience with:

### Cloud Computing

- AWS VPC networking
- Public and private subnet design
- Availability Zones
- Security Groups
- Amazon EC2 deployment
- Linux systemd services
- Amazon RDS
- Database migration
- Amazon S3 hosting
- Amazon CloudFront
- CloudFront path-based routing
- CloudFront Functions
- Origin Access Control
- AWS-managed prefix lists
- AWS cost optimization

### Backend Engineering

- Java 21
- Spring Boot REST APIs
- Spring Data JPA
- Hibernate ORM
- Database transactions
- Spring Security
- JWT authentication
- Google OAuth2
- Role-based and permission-based access control
- Resource ownership
- Spring AOP
- Log4j2
- Flyway
- Actuator and Micrometer

### Frontend Engineering

- React
- Vite
- React Router
- Context API
- REST API integration
- Authentication flows
- Role-based navigation
- Shopping cart state management
- Responsive UI design
- Production frontend builds

### DevOps and Deployment

- Maven builds
- Linux process management
- Nginx reverse proxy configuration
- S3 artifact deployment
- CloudFront cache invalidation
- Environment configuration
- Log inspection
- Service health checks
- Cloud cost monitoring

---

## Project Summary

**Project:** ECommerceOrderEngine

**Current Version:** V7

**Architecture:** Three-Tier Web Application

**Frontend:** React + Vite

**Backend:** Java 21 + Spring Boot

**Database:** MySQL on Amazon RDS

**Cloud Provider:** AWS

**Authentication:** JWT + Google OAuth2

**Security:** Spring Security + Role-Based Authorization

**Logging:** Log4j2

**Monitoring:** Spring Boot Actuator + Micrometer

**Current Deployment:** Amazon S3 + CloudFront + EC2 + RDS

**Live Application:** https://dsohu6n1v0a1o.cloudfront.net

**Next Version:** V8 — Spring AI

**Future Versions:** V9 — Docker and Microservices; V10 — Kubernetes, Docker and Jenkins CI/CD
