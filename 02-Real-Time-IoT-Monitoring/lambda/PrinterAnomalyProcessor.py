import boto3
from decimal import Decimal

dynamodb = boto3.resource("dynamodb")
sns = boto3.client("sns")

SNS_TOPIC_ARN = (
    "arn:aws:sns:ap-southeast-2:311937350747:"
    "PrinterAnomalyAlerts"
)

profiles_table = dynamodb.Table("PrinterProfiles")
telemetry_table = dynamodb.Table("TelemetryHistory")
anomaly_table = dynamodb.Table("AnomalyEvents")


def get_severity(value, lower, upper):
    if value > upper:
        difference = value - upper
    elif value < lower:
        difference = lower - value
    else:
        return "NORMAL"

    if difference >= 20:
        return "CRITICAL"
    elif difference >= 10:
        return "HIGH"
    else:
        return "MEDIUM"


def lambda_handler(event, context):
    printer_id = event["printerId"]
    timestamp = event["timestamp"]

    sensor_type = event["data"]["type"]
    value = float(event["data"]["value"])

    response = profiles_table.get_item(
        Key={"PrinterId": printer_id}
    )

    profile = response.get("Item")

    if not profile:
        print(f"No profile found for {printer_id}")

        return {
            "statusCode": 404,
            "message": "Printer profile not found",
        }

    lower = float(profile["LowerThreshold"])
    upper = float(profile["UpperThreshold"])
    window = int(profile["Window"])
    out_of_bounds_count = int(
        profile["OutOfBoundsCount"]
    )
    event_count = int(profile["EventCount"])

    is_out_of_bounds = (
        value < lower or value > upper
    )

    # Store every telemetry reading
    telemetry_table.put_item(
        Item={
            "PrinterId": printer_id,
            "Timestamp": timestamp,
            "SensorType": sensor_type,
            "Value": Decimal(str(value)),
            "IsOutOfBounds": is_out_of_bounds,
        }
    )

    if is_out_of_bounds:
        out_of_bounds_count += 1

        print(
            f"{printer_id}: Out of bounds "
            f"{out_of_bounds_count}/{window}"
        )

        if out_of_bounds_count >= window:
            event_count += 1
            out_of_bounds_count = 0

            severity = get_severity(
                value,
                lower,
                upper,
            )

            # Store anomaly event
            anomaly_table.put_item(
                Item={
                    "PrinterId": printer_id,
                    "Timestamp": timestamp,
                    "SensorType": sensor_type,
                    "Value": Decimal(str(value)),
                    "LowerThreshold": Decimal(
                        str(lower)
                    ),
                    "UpperThreshold": Decimal(
                        str(upper)
                    ),
                    "Severity": severity,
                    "EventNumber": event_count,
                }
            )

            # Send SNS alert
            sns.publish(
                TopicArn=SNS_TOPIC_ARN,
                Subject=(
                    f"Printer anomaly detected: "
                    f"{printer_id}"
                ),
                Message=(
                    f"Printer: {printer_id}\n"
                    f"Sensor: {sensor_type}\n"
                    f"Value: {value}\n"
                    f"Threshold: "
                    f"{lower} - {upper}\n"
                    f"Severity: {severity}\n"
                    f"Timestamp: {timestamp}\n"
                    f"Event Count: {event_count}"
                ),
            )

            print(
                f"ANOMALY EVENT TRIGGERED "
                f"severity={severity}, "
                f"eventCount={event_count}"
            )

    else:
        out_of_bounds_count = 0

        print(
            f"{printer_id}: Reading normal."
        )

    # Update printer state + heartbeat timestamp
    profiles_table.update_item(
        Key={
            "PrinterId": printer_id
        },
        UpdateExpression=(
            "SET OutOfBoundsCount = :o, "
            "EventCount = :e, "
            "LastSeen = :l"
        ),
        ExpressionAttributeValues={
            ":o": out_of_bounds_count,
            ":e": event_count,
            ":l": timestamp,
        },
    )

    return {
        "printerId": printer_id,
        "value": value,
        "isOutOfBounds": is_out_of_bounds,
        "outOfBoundsCount": out_of_bounds_count,
        "eventCount": event_count,
        "lastSeen": timestamp,
    }
