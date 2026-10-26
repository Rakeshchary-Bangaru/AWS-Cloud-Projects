# Amazon RDS MySQL Setup

This document describes how the MySQL database tier was deployed using Amazon RDS.

## RDS Configuration

```text
DB identifier: ecommerce-db
Region: ap-southeast-2
Engine: MySQL 8.4
DB instance class: db.t4g.micro
Storage: 20 GB gp3
Deployment: Single-AZ
Public access: Disabled
Port: 3306
```

The database is deployed inside private subnets of the custom e-commerce VPC.

## DB Subnet Group

A database subnet group was created using two private subnets across two Availability Zones.

Example structure:

```text
ecommerce-db-subnet-group
├── Private subnet - ap-southeast-2a
└── Private subnet - ap-southeast-2b
```

Even though the database uses a Single-AZ deployment, RDS requires a DB subnet group containing subnets across multiple Availability Zones.

## Network Security

The RDS instance is not publicly accessible.

Its security group allows MySQL traffic only from the EC2 backend security group.

```text
Protocol: TCP
Port: 3306
Source: ecommerce-ec2-sg
```

This means:

```text
Internet
   X
   |
   v
RDS

EC2 Backend
   |
   | TCP 3306
   v
RDS MySQL
```

## Database Endpoint

The application connects to RDS using the database endpoint.

Example:

```text
ecommerce-db.cdaigqq8m3xr.ap-southeast-2.rds.amazonaws.com
```

The endpoint is used in the Spring datasource configuration instead of a fixed IP address.

Example JDBC URL:

```text
jdbc:mysql://ecommerce-db.cdaigqq8m3xr.ap-southeast-2.rds.amazonaws.com:3306/ecommerce
```

Credentials are stored outside the source code using environment variables.

## Verify EC2 to RDS Connectivity

From EC2, network connectivity can be tested using:

```bash
nc -vz ecommerce-db.cdaigqq8m3xr.ap-southeast-2.rds.amazonaws.com 3306
```

A successful result confirms that:

- DNS resolution works
- the EC2 instance can reach the RDS endpoint
- the security groups allow MySQL traffic

## Install MySQL-Compatible Client on EC2

On Amazon Linux 2023:

```bash
sudo dnf install mariadb105 -y
```

Connect to RDS:

```bash
mysql \
-h ecommerce-db.cdaigqq8m3xr.ap-southeast-2.rds.amazonaws.com \
-P 3306 \
-u admin \
-p
```

The password is entered interactively and is never committed to source control.

## Create Application Database

The application database was created manually:

```sql
CREATE DATABASE ecommerce
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;
```

Verify:

```sql
SHOW DATABASES;
```

## Local Database Migration

The application already contained local MySQL data, so the existing database was migrated instead of creating an empty cloud database.

The local application database was:

```text
ecommerce_db
```

The test database was not migrated.

## Export Local Database

The database was exported from the local development machine using `mysqldump`.

```bash
mysqldump \
-u root \
-p \
--single-transaction \
--routines \
--triggers \
--events \
--set-gtid-purged=OFF \
--no-tablespaces \
ecommerce_db > ~/ecommerce_backup.sql
```

This produces:

```text
ecommerce_backup.sql
```

## Upload Backup to EC2

The SQL dump was transferred to EC2:

```bash
scp -i ~/.ssh/ecommerce-backend-key.pem \
~/ecommerce_backup.sql \
ec2-user@<EC2_PUBLIC_IP>:/home/ec2-user/
```

## Import Backup into RDS

From EC2:

```bash
mysql \
-h ecommerce-db.cdaigqq8m3xr.ap-southeast-2.rds.amazonaws.com \
-P 3306 \
-u admin \
-p \
ecommerce < ecommerce_backup.sql
```

## Verify Migrated Tables

After import:

```sql
USE ecommerce;

SHOW TABLES;
```

Migrated tables include:

```text
customers
inventory
order_items
orders
payments
products
```

Example verification:

```sql
SELECT COUNT(*) FROM customers;
SELECT COUNT(*) FROM products;
SELECT COUNT(*) FROM orders;
```

The migrated environment contained existing customer, product, and order records from the local application database.

## Spring Boot Database Configuration

The Spring Boot application uses environment-based datasource configuration.

Example:

```properties
spring.datasource.url=${SPRING_DATASOURCE_URL}
spring.datasource.username=${SPRING_DATASOURCE_USERNAME}
spring.datasource.password=${SPRING_DATASOURCE_PASSWORD}
```

Database credentials are stored in:

```text
/etc/ecommerce/ecommerce.env
```

on the EC2 instance.

Secrets must never be added to GitHub.

## Hibernate Schema Validation

The deployed application validates the existing database schema rather than relying on Hibernate to recreate the production-style database.

This is useful after migrating an existing schema because unexpected automatic schema changes can be avoided.

## Health Verification

Spring Boot Actuator confirms database connectivity.

Example:

```bash
curl http://localhost:8080/actuator/health
```

The database component should report:

```text
database: MySQL
status: UP
```

## Security Notes

- RDS public access is disabled.
- MySQL port `3306` is not open to the public internet.
- Only the EC2 backend security group can reach RDS.
- Database credentials are externalized from the application.
- Database passwords must never be committed to Git.
- The RDS master password should be rotated if it is ever exposed.

## Cost-Conscious Choices

This first deployment uses:

```text
Single-AZ
db.t4g.micro
20 GB gp3
No RDS Proxy
No Enhanced Monitoring
No Multi-AZ standby
```

These choices keep the database architecture suitable for a learning and portfolio deployment while still demonstrating private networking and managed database usage.

## Result

The application database now runs on Amazon RDS and:

- is isolated from the public internet
- accepts connections only from the EC2 backend
- contains migrated application data
- is monitored through Spring Boot health checks
- persists independently of the EC2 instance
