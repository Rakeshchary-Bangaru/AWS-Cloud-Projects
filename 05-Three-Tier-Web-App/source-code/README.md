
# Application Source Code

The application source code is maintained separately from this AWS infrastructure and deployment repository.

This folder contains references to the application repositories used for the three-tier AWS deployment.

## Backend

**Technology**

- Java 21
- Spring Boot
- Spring Data JPA
- MySQL
- Maven
- Spring AOP
- Micrometer
- Spring Boot Actuator
- Apache POI
- JUnit 5
- Mockito
- JaCoCo

The backend provides REST APIs for:

- Products
- Customers
- Inventory
- Orders
- Checkout
- Payments

Additional backend features include:

- transactional checkout processing
- inventory validation
- centralized logging using Spring AOP
- method performance monitoring
- Micrometer metrics
- Spring Boot Actuator health checks
- Excel-based audit logging
- unit, controller, repository, and integration testing

The backend is packaged as an executable WAR and deployed to Amazon EC2.

### Backend Repository



```text
https://github.com/Rakeshchary-Bangaru/Java-Projects/tree/main/ECommerceOrderEngine
```

---

## Frontend

**Technology**

- React
- JavaScript
- Vite
- CSS
- React Router
- REST API integration

The frontend provides:

- Customer home page
- Product catalogue
- Stock availability
- Shopping cart
- Checkout
- Order history
- Admin dashboard
- Product management
- Customer management
- Inventory management
- Order management

The production React build is deployed to a private Amazon S3 bucket and served through Amazon CloudFront.

### Frontend Repository



```text
https://github.com/Rakeshchary-Bangaru/Web-Development-Projects/tree/main/React/ecommerce-order-engine-ui
```

---

## Cloud Deployment

The source code is deployed using the following architecture:

```text
React Frontend
      |
      v
Amazon S3
      |
      v
Amazon CloudFront
      |
      | /api/*
      v
Amazon EC2
Spring Boot
      |
      v
Amazon RDS
MySQL
```

Deployment configuration and AWS architecture documentation are available in the parent project:

```text
05-Three-Tier-Web-App/
```

Detailed documentation:

```text
deployment/
├── ec2-setup.md
├── rds-setup.md
├── s3-cloudfront-setup.md
└── security-groups.md
```

## Repository Separation

Application source code and AWS deployment documentation are intentionally maintained separately.

```text
Application repositories
        ↓
Source code and development

AWS-Cloud-Projects
        ↓
Architecture and deployment
```

This keeps the AWS repository focused on cloud infrastructure, networking, security, deployment, and operational configuration rather than duplicating application code.

## Planned Improvements

Future application improvements include:

- Spring Security
- CUSTOMER and ADMIN role-based authorization
- authenticated audit logging
- Spring AI integration
- Docker containerization
- CI/CD
- Prometheus and Grafana monitoring
