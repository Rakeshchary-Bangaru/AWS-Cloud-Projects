# Deployment Notes

## Deployment Model

The project uses a fully serverless AWS architecture.

No continuously running EC2 instance is required.

## Region

```text
ap-southeast-2
```

## Frontend

The React dashboard is built with Vite.

Production build:

```bash
npm run build
```

Deployment:

```text
Browser
→ CloudFront
→ Private S3 Bucket
```

CloudFront uses Origin Access Control to access the private S3 bucket.

## Backend API

API Gateway exposes a read-only HTTP API.

Routes:

```text
GET /printers
GET /printers/{id}
GET /printers/{id}/telemetry
GET /printers/{id}/anomalies
```

API Gateway invokes:

```text
PrinterMonitoringApi
```

## IoT Pipeline

```text
EventBridge Scheduler
        ↓
IoTTelemetrySimulator Lambda
        ↓
AWS IoT Core
        ↓
IoT Rule
        ↓
PrinterAnomalyProcessor Lambda
        ↓
DynamoDB + SNS
```

## Telemetry Schedule

The serverless telemetry simulator runs:

```text
once per minute
```

The React application uses a larger online/offline grace period so printers are not marked offline between scheduled telemetry events.

## Device Health

Each processed telemetry reading updates:

```text
LastSeen
```

in `PrinterProfiles`.

The frontend determines printer health from this timestamp.

## Active Alerts

A current alert exists when:

```text
Printer is online
AND
OutOfBoundsCount > 0
```

Historical anomaly events remain stored independently.

## DynamoDB Tables

The project uses:

```text
PrinterProfiles
TelemetryHistory
AnomalyEvents
```

## Alerts

Confirmed anomaly events are published to:

```text
PrinterAnomalyAlerts
```

using Amazon SNS.

## Security

The project uses:

- private S3 bucket
- CloudFront Origin Access Control
- least-privilege Lambda IAM roles
- restricted IoT publish permissions
- API Gateway CORS restrictions

## CORS

Allowed frontend origins include:

```text
http://localhost:5173
```

and the deployed CloudFront domain.

## CloudFront

CloudFront serves the React dashboard over HTTPS.

Default root object:

```text
index.html
```

## Updating the Frontend

After frontend code changes:

```bash
npm run build
```

Upload the new `dist/` contents to the S3 bucket.

Then create a CloudFront invalidation:

```text
/*
```

to refresh cached frontend assets.

## Cost Notes

The architecture avoids always-on compute.

Main services are usage-based:

- EventBridge Scheduler
- Lambda
- AWS IoT Core
- DynamoDB
- SNS
- API Gateway
- S3
- CloudFront

At portfolio/demo scale, expected usage is very small.

## Local Simulator

The local Python simulator remains available for development:

```bash
python3 simulator/emit_json_data.py
```

Normal deployed operation uses the serverless Lambda simulator instead.

## Production Data Flow

```text
EventBridge Scheduler
→ IoTTelemetrySimulator Lambda
→ AWS IoT Core
→ IoT Rule
→ PrinterAnomalyProcessor Lambda
→ DynamoDB
→ PrinterMonitoringApi Lambda
→ API Gateway
→ React Dashboard
→ CloudFront
```

SNS runs alongside the processing pipeline for anomaly notifications.
