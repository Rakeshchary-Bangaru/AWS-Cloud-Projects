# EC2 Backend Deployment

This document describes how the Spring Boot backend was deployed to Amazon EC2.

## EC2 Configuration

```text
Instance name: ecommerce-backend
Region: ap-southeast-2
AMI: Amazon Linux 2023
Instance type: t3.micro
Storage: 8 GB gp3
Java version: Amazon Corretto 21
Application port: 8080
```

The EC2 instance is deployed inside a public subnet of the custom e-commerce VPC.

## SSH Access

The instance is accessed using an RSA key pair.

Example:

```bash
ssh -i ~/.ssh/ecommerce-backend-key.pem ec2-user@<EC2_PUBLIC_IP>
```

The private key permissions must be restricted:

```bash
chmod 400 ~/.ssh/ecommerce-backend-key.pem
```

## Install Java 21

Update the system:

```bash
sudo dnf update -y
```

Install Amazon Corretto 21:

```bash
sudo dnf install java-21-amazon-corretto-headless -y
```

Verify:

```bash
java -version
```

## Configure Swap Memory

The `t3.micro` instance has limited memory, so a 1 GB swap file was configured.

```bash
sudo fallocate -l 1G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

Persist swap after reboot:

```bash
echo '/swapfile swap swap defaults 0 0' | sudo tee -a /etc/fstab
```

Verify:

```bash
free -h
```

## Build Spring Boot Application

The application is built locally using Maven.

```bash
mvn clean package -DskipTests
```

The generated executable WAR file is located under:

```text
target/
```

Example:

```text
ecommerce-order-engine-6.0-SNAPSHOT.war
```

## Upload Application to EC2

The WAR file is uploaded using SCP:

```bash
scp -i ~/.ssh/ecommerce-backend-key.pem \
target/ecommerce-order-engine-6.0-SNAPSHOT.war \
ec2-user@<EC2_PUBLIC_IP>:/home/ec2-user/
```

## Database Environment Variables

Database credentials are stored outside the application source code.

The application uses environment variables such as:

```text
SPRING_DATASOURCE_URL
SPRING_DATASOURCE_USERNAME
SPRING_DATASOURCE_PASSWORD
```

The environment file is stored at:

```text
/etc/ecommerce/ecommerce.env
```

Its permissions are restricted:

```bash
sudo chmod 600 /etc/ecommerce/ecommerce.env
```

Database passwords and other secrets must never be committed to GitHub.

## systemd Service

The backend runs as a Linux systemd service.

Service file:

```text
/etc/systemd/system/ecommerce.service
```

Configuration:

```ini
[Unit]
Description=ECommerce Spring Boot Backend
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/home/ec2-user
EnvironmentFile=/etc/ecommerce/ecommerce.env

ExecStart=/usr/bin/java -Xms128m -Xmx512m \
-jar /home/ec2-user/ecommerce-order-engine-6.0-SNAPSHOT.war

Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Reload systemd:

```bash
sudo systemctl daemon-reload
```

Enable application startup during boot:

```bash
sudo systemctl enable ecommerce
```

Start the application:

```bash
sudo systemctl start ecommerce
```

Check status:

```bash
sudo systemctl status ecommerce
```

## Application Logs

View live application logs using:

```bash
sudo journalctl -u ecommerce -f
```

Restart application:

```bash
sudo systemctl restart ecommerce
```

Stop application:

```bash
sudo systemctl stop ecommerce
```

## Health Check

Spring Boot Actuator is used to verify application health:

```bash
curl http://localhost:8080/actuator/health
```

A successful response should report:

```text
status: UP
```

## API Verification

Test the products API locally from EC2:

```bash
curl http://localhost:8080/api/products
```

During initial testing, direct public access was also verified using:

```text
http://<EC2_PUBLIC_IP>:8080/api/products
```

In the final architecture, CloudFront routes `/api/*` traffic to the EC2 backend.

## Security Considerations

- SSH access is restricted to the developer's IP.
- RDS accepts MySQL traffic only from the EC2 security group.
- Port `8080` is allowed from the AWS-managed CloudFront origin-facing prefix list.
- Database secrets are not stored in Git.
- The EC2 instance uses a private key for SSH authentication.

## Result

The Spring Boot backend now:

- runs continuously on EC2
- starts automatically after EC2 reboot
- connects securely to RDS
- is reachable through CloudFront
- can be monitored through systemd and Spring Boot Actuator
