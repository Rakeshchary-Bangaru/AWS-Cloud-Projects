# Real-Time IoT Monitoring & Anomaly Detection

A serverless real-time IoT monitoring and anomaly detection platform built with AWS and React.

The system simulates multiple smart printing devices, publishes telemetry to AWS IoT Core, detects threshold-based anomalies, stores telemetry and anomaly history in DynamoDB, sends SNS alerts, exposes monitoring APIs through API Gateway, and visualizes fleet health through a React dashboard deployed with S3 and CloudFront.

## Architecture

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
 ┌───────────────┬──────────────────┬─────────────────┐
 ↓               ↓                  ↓
PrinterProfiles  TelemetryHistory   AnomalyEvents
        ↓
      SNS
   Email Alerts


React Dashboard
        ↓
CloudFront
        ↓
S3
        ↓
API Gateway
        ↓
PrinterMonitoringApi Lambda
        ↓
DynamoDB
```

## AWS Services

- AWS IoT Core
- AWS Lambda
- Amazon DynamoDB
- Amazon SNS
- Amazon API Gateway
- Amazon EventBridge Scheduler
- Amazon S3
- Amazon CloudFront
- Amazon CloudWatch
- AWS IAM

## Frontend

- React
- Vite
- Recharts
- JavaScript
- CSS

## Features

### Multi-Printer IoT Simulation

The project currently simulates three virtual printing devices:

```text
printer-001
printer-002
printer-003
```

Each printer publishes temperature telemetry to an individual MQTT topic.

```text
iot-monitor/printers/printer-001/telemetry
iot-monitor/printers/printer-002/telemetry
iot-monitor/printers/printer-003/telemetry
```

AWS IoT Core receives the messages and an IoT Rule matches:

```text
iot-monitor/printers/+/telemetry
```

The `+` MQTT wildcard allows telemetry from every simulated printer to flow through the same processing pipeline.

## Serverless Telemetry Simulator

The deployed application uses an EventBridge Scheduler to invoke the `IoTTelemetrySimulator` Lambda periodically.

```text
EventBridge Scheduler
        ↓
IoTTelemetrySimulator
        ↓
AWS IoT Core
```

The simulator generates synthetic temperature readings for every printer and publishes them using `iot:Publish`.

This removes the requirement to continuously run the local Python simulator on a developer machine.

A local Python simulator is also retained for development and testing.

```bash
python3 simulator/emit_json_data.py
```

## Anomaly Detection

Every printer has its own configurable monitoring profile stored in DynamoDB.

Example:

```json
{
  "PrinterId": "printer-001",
  "LowerThreshold": 20,
  "UpperThreshold": 80,
  "Window": 10,
  "OutOfBoundsCount": 0,
  "EventCount": 5
}
```

A reading is considered out of bounds when:

```text
temperature < LowerThreshold
```

or:

```text
temperature > UpperThreshold
```

The system does not immediately create an anomaly event for a single abnormal reading.

Instead, it tracks consecutive out-of-bounds readings.

Example:

```text
Window = 10

Reading 1  → OOB count = 1
Reading 2  → OOB count = 2
...
Reading 10 → anomaly event triggered
```

After an anomaly event:

```text
EventCount += 1
OutOfBoundsCount = 0
```

A normal reading resets the current consecutive OOB counter.

## Anomaly Severity

Triggered anomalies are classified based on how far the sensor value exceeds the configured threshold.

```text
Difference < 10      → MEDIUM
Difference >= 10     → HIGH
Difference >= 20     → CRITICAL
```

Each anomaly event is stored in the `AnomalyEvents` table.

Example:

```json
{
  "PrinterId": "printer-001",
  "SensorType": "temperature",
  "Value": 93.92,
  "LowerThreshold": 20,
  "UpperThreshold": 80,
  "Severity": "HIGH",
  "EventNumber": 5
}
```

## DynamoDB Tables

### PrinterProfiles

Stores the current state and configuration of each printer.

Important attributes:

```text
PrinterId
LowerThreshold
UpperThreshold
Window
OutOfBoundsCount
EventCount
LastSeen
```

### TelemetryHistory

Stores every incoming telemetry reading.

Partition key:

```text
PrinterId
```

Sort key:

```text
Timestamp
```

Attributes include:

```text
SensorType
Value
IsOutOfBounds
```

### AnomalyEvents

Stores confirmed anomaly events.

Partition key:

```text
PrinterId
```

Sort key:

```text
Timestamp
```

Attributes include:

```text
Value
Severity
EventNumber
LowerThreshold
UpperThreshold
```

## Device Health Monitoring

Every telemetry event updates the printer's:

```text
LastSeen
```

timestamp.

The React dashboard uses this timestamp to determine whether a printer is online or offline.

The deployed serverless simulator publishes approximately once every minute, so the frontend uses a grace period before declaring a device offline.

This supports fleet-level metrics including:

```text
Total Printers
Online Printers
Offline Printers
Active Alerts
Total Anomaly Events
```

## Active Alerts

An active alert is shown when:

```text
Printer is online
AND
OutOfBoundsCount > 0
```

This separates current operational issues from historical anomaly events.

Historical anomalies remain available through `EventCount` and the `AnomalyEvents` table.

## SNS Alerts

When an anomaly window is reached, the anomaly processor publishes an SNS notification.

The email includes:

```text
Printer ID
Sensor type
Sensor value
Configured thresholds
Severity
Timestamp
Event number
```

## Monitoring API

The `PrinterMonitoringApi` Lambda exposes read-only monitoring endpoints through API Gateway.

### List printers

```http
GET /printers
```

Returns all printer profiles sorted by anomaly event count.

### Printer profile

```http
GET /printers/{id}
```

Example:

```http
GET /printers/printer-001
```

### Telemetry history

```http
GET /printers/{id}/telemetry
```

Example:

```http
GET /printers/printer-001/telemetry
```

### Anomaly history

```http
GET /printers/{id}/anomalies
```

Example:

```http
GET /printers/printer-001/anomalies
```

## React Monitoring Dashboard

The dashboard provides both fleet-level monitoring and individual printer drill-down.

### Fleet Overview

Displays:

```text
Total Printers
Online Printers
Offline Printers
Active Alerts
Total Anomaly Events
```

### Top Anomalous Printers

Printers are ranked by:

```text
EventCount descending
```

Each entry displays:

```text
Printer ID
Configured threshold
Online/Offline status
Last Seen
Active OOB state
Historical anomaly count
```

### Printer Drill-Down

Users can select an individual printer and view:

- current temperature
- anomaly event count
- current consecutive OOB count
- configured lower threshold
- configured upper threshold
- anomaly window size
- telemetry history
- anomaly history
- online/offline state

## Temperature Visualization

Recent telemetry is visualized using Recharts.

The chart includes:

- temperature history
- lower threshold reference line
- upper threshold reference line

This makes abnormal readings easy to identify visually.

## Automatic Refresh

The React dashboard polls the monitoring API periodically to retrieve updated:

```text
Printer state
Telemetry
Anomaly history
LastSeen
Fleet metrics
```

## Deployment

### Frontend

The React dashboard is built using:

```bash
npm run build
```

Vite generates:

```text
dist/
```

The production assets are uploaded to a private S3 bucket.

CloudFront serves the application over HTTPS using Origin Access Control.

```text
Browser
   ↓
CloudFront
   ↓
Private S3 Bucket
```

### Backend

The backend is entirely serverless.

```text
EventBridge
AWS IoT Core
Lambda
DynamoDB
SNS
API Gateway
```

No continuously running EC2 instance is required.

## CORS

API Gateway allows requests from both local development and the deployed CloudFront frontend.

Example allowed origins:

```text
http://localhost:5173
https://<cloudfront-domain>
```

Allowed method:

```text
GET
```

## Local Development

### React Dashboard

```bash
cd IoT-Monitoring-Dashboard
npm install
npm run dev
```

Default development URL:

```text
http://localhost:5173
```

### Local IoT Simulator

The local simulator can still be used for development:

```bash
python3 simulator/emit_json_data.py
```

The simulator connects to AWS IoT Core using an IoT certificate and private key stored outside the Git repository.

Device credentials must never be committed to source control.

## Security

The project uses least-privilege IAM permissions.

Examples:

### Simulator Lambda

```text
iot:Publish
```

Only for:

```text
iot-monitor/printers/*/telemetry
```

### Monitoring API

Read-only DynamoDB permissions:

```text
dynamodb:GetItem
dynamodb:Query
dynamodb:Scan
```

### Anomaly Processor

Uses only the permissions required for:

```text
DynamoDB reads/writes
SNS publish
CloudWatch logging
```

The S3 frontend bucket remains private and is accessed through CloudFront Origin Access Control.

## Cost-Conscious Architecture

The project intentionally avoids continuously running compute resources.

The architecture primarily uses usage-based serverless services:

- Lambda
- EventBridge Scheduler
- AWS IoT Core
- DynamoDB
- SNS
- API Gateway
- S3
- CloudFront

For portfolio-scale telemetry, usage remains small.

The simulator publishes once per scheduled execution rather than continuously generating high-frequency traffic.

## Project Data Flow

```text
1. EventBridge triggers IoTTelemetrySimulator.

2. Simulator generates temperature telemetry.

3. Lambda publishes telemetry to AWS IoT Core.

4. IoT Rule matches the MQTT topic.

5. PrinterAnomalyProcessor receives the event.

6. Telemetry is stored in TelemetryHistory.

7. Printer thresholds are loaded from PrinterProfiles.

8. Out-of-bounds state is evaluated.

9. Consecutive OOB state is updated.

10. Confirmed anomalies are stored in AnomalyEvents.

11. SNS sends an alert.

12. LastSeen and printer state are updated.

13. PrinterMonitoringApi reads DynamoDB.

14. API Gateway exposes monitoring endpoints.

15. React retrieves monitoring data.

16. CloudFront serves the dashboard to users.
```

## Repository Structure

```text
02-Real-Time-IoT-Monitoring/
├── README.md
├── architecture/
│   └── real-time-iot-monitoring-architecture.png
│
├── deployment/
│   ├── aws-setup.md
│   └── deployment-notes.md
│
├── screenshots/
│   ├── dashboard-live.png
│   ├── fleet-health.png
│   ├── anomaly-events.png
│   ├── dynamodb-profiles.png
│   ├── lambda-simulator.png
│   ├── eventbridge-schedule.png
│   └── cloudfront-dashboard.png
│
├── simulator/
│   └── emit_json_data.py
│
└── lambda/
    ├── IoTTelemetrySimulator.py
    ├── PrinterAnomalyProcessor.py
    └── PrinterMonitoringApi.py
```

## Key Engineering Concepts Demonstrated

- MQTT publish/subscribe architecture
- AWS IoT Core
- event-driven serverless architecture
- Lambda-based processing
- configurable anomaly detection
- consecutive-event windows
- real-time telemetry ingestion
- DynamoDB partition/sort-key design
- historical telemetry storage
- anomaly event persistence
- event severity classification
- fleet health monitoring
- device heartbeat / LastSeen tracking
- REST APIs
- API Gateway CORS
- SNS notifications
- EventBridge scheduling
- least-privilege IAM
- private S3 hosting
- CloudFront Origin Access Control
- React dashboards
- real-time charts
- responsive frontend design

## Future Improvements

Potential extensions include:

- vibration telemetry
- ink-level telemetry
- printer utilization metrics
- additional IoT device types
- configurable dashboard time ranges
- telemetry pagination
- anomaly acknowledgement workflow
- alert resolution state
- WebSocket-based live updates
- DynamoDB Streams
- advanced statistical anomaly detection
- ML-based anomaly detection
- CloudWatch dashboards and alarms
- infrastructure as code using AWS CDK or Terraform
- automated CI/CD

## Project Status

The current implementation includes:

```text
✓ Multi-device telemetry simulation
✓ AWS IoT Core MQTT ingestion
✓ IoT Rules
✓ Lambda anomaly processing
✓ Configurable thresholds
✓ Consecutive anomaly windows
✓ DynamoDB telemetry history
✓ DynamoDB anomaly history
✓ SNS alerts
✓ Multiple simulated printers
✓ LastSeen heartbeat tracking
✓ Fleet online/offline monitoring
✓ Active alert monitoring
✓ API Gateway monitoring API
✓ React monitoring dashboard
✓ Temperature charts
✓ CloudFront deployment
✓ Private S3 origin
✓ Serverless EventBridge simulator
```

The application is fully cloud-hosted and does not require a continuously running local machine for normal operation.
