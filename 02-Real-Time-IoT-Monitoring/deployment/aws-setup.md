# AWS Setup

## Region

This project is deployed in:

```text
ap-southeast-2
```

## 1. Create AWS IoT Thing

Create an AWS IoT Thing representing a virtual printer.

Example:

```text
printer-001
```

Create and download:

- device certificate
- private key
- Amazon Root CA

Keep private keys and certificates outside the Git repository.

## 2. Create IoT Policy

Allow the simulated device or simulator Lambda to publish telemetry to:

```text
iot-monitor/printers/*/telemetry
```

Example IAM/IoT permission:

```text
iot:Publish
```

## 3. Create PrinterProfiles Table

Create DynamoDB table:

```text
PrinterProfiles
```

Partition key:

```text
PrinterId
```

Each item stores:

- LowerThreshold
- UpperThreshold
- Window
- OutOfBoundsCount
- EventCount
- LastSeen

## 4. Create TelemetryHistory Table

Create DynamoDB table:

```text
TelemetryHistory
```

Partition key:

```text
PrinterId
```

Sort key:

```text
Timestamp
```

Stores every incoming sensor reading.

## 5. Create AnomalyEvents Table

Create DynamoDB table:

```text
AnomalyEvents
```

Partition key:

```text
PrinterId
```

Sort key:

```text
Timestamp
```

Stores confirmed anomaly events.

## 6. Create PrinterAnomalyProcessor Lambda

Create:

```text
PrinterAnomalyProcessor
```

Runtime:

```text
Python 3.13
```

The function:

- reads printer configuration
- stores telemetry
- evaluates thresholds
- tracks consecutive OOB readings
- creates anomaly events
- updates LastSeen
- sends SNS alerts

## 7. Create AWS IoT Rule

Use:

```text
SELECT * FROM 'iot-monitor/printers/+/telemetry'
```

Target:

```text
PrinterAnomalyProcessor
```

## 8. Create SNS Topic

Create:

```text
PrinterAnomalyAlerts
```

Add an email subscription and confirm the subscription.

## 9. Create PrinterMonitoringApi Lambda

Create:

```text
PrinterMonitoringApi
```

This Lambda reads printer profiles, telemetry history, and anomaly history from DynamoDB.

## 10. Create API Gateway HTTP API

Expose:

```text
GET /printers
GET /printers/{id}
GET /printers/{id}/telemetry
GET /printers/{id}/anomalies
```

## 11. Configure CORS

Allow:

```text
http://localhost:5173
```

and the deployed CloudFront origin.

Allow method:

```text
GET
```

Allow headers:

```text
*
```

## 12. Build React Dashboard

From the frontend project:

```bash
npm install
npm run build
```

The production build is created in:

```text
dist/
```

## 13. Create Private S3 Bucket

Upload the contents of `dist/` to a private S3 bucket.

Keep:

```text
Block all public access = ON
```

Do not expose the bucket publicly.

## 14. Create CloudFront Distribution

Use the S3 bucket as the origin.

Enable Origin Access Control.

Set:

```text
Default root object = index.html
```

Use HTTPS for viewers.

## 15. Create IoTTelemetrySimulator Lambda

Create:

```text
IoTTelemetrySimulator
```

Runtime:

```text
Python 3.13
```

This Lambda generates telemetry for:

```text
printer-001
printer-002
printer-003
```

and publishes it to AWS IoT Core.

## 16. Grant IoT Publish Permission

The simulator Lambda execution role needs:

```text
iot:Publish
```

for:

```text
iot-monitor/printers/*/telemetry
```

## 17. Create EventBridge Schedule

Create a recurring schedule:

```text
rate(1 minute)
```

Target:

```text
IoTTelemetrySimulator
```

Flexible time window:

```text
Off
```

## 18. Verify End-to-End Flow

Expected flow:

```text
EventBridge
→ IoTTelemetrySimulator
→ AWS IoT Core
→ IoT Rule
→ PrinterAnomalyProcessor
→ DynamoDB / SNS
→ PrinterMonitoringApi
→ API Gateway
→ CloudFront
→ React Dashboard
```

Verify:

- telemetry appears in DynamoDB
- LastSeen updates
- online/offline status changes correctly
- anomaly events are stored
- SNS alerts are delivered
- CloudFront dashboard displays live fleet data
