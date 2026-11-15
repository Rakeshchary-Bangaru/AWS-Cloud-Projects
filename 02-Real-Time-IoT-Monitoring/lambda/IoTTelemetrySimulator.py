import json
import random
from datetime import datetime, timezone

import boto3


iot = boto3.client(
    "iot-data",
    region_name="ap-southeast-2"
)


PRINTERS = [
    {
        "id": "printer-001",
        "min_temp": 60,
        "max_temp": 95,
    },
    {
        "id": "printer-002",
        "min_temp": 55,
        "max_temp": 90,
    },
    {
        "id": "printer-003",
        "min_temp": 65,
        "max_temp": 100,
    },
]


def lambda_handler(event, context):
    published = []

    for printer in PRINTERS:
        printer_id = printer["id"]

        temperature = round(
            random.uniform(
                printer["min_temp"],
                printer["max_temp"]
            ),
            2
        )

        timestamp = datetime.now(
            timezone.utc
        ).isoformat()

        payload = {
            "printerId": printer_id,
            "timestamp": timestamp,
            "data": {
                "type": "temperature",
                "value": temperature
            }
        }

        topic = (
            f"iot-monitor/printers/"
            f"{printer_id}/telemetry"
        )

        iot.publish(
            topic=topic,
            qos=1,
            payload=json.dumps(payload)
        )

        print(
            f"Published {printer_id}: "
            f"{temperature} °C"
        )

        published.append({
            "printerId": printer_id,
            "temperature": temperature,
            "timestamp": timestamp
        })

    return {
        "statusCode": 200,
        "published": published
    }
