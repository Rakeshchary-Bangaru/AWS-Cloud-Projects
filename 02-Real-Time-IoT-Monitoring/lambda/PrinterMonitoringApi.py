import json
import boto3
from boto3.dynamodb.conditions import Key
from decimal import Decimal

dynamodb = boto3.resource("dynamodb")

profiles_table = dynamodb.Table("PrinterProfiles")
telemetry_table = dynamodb.Table("TelemetryHistory")
anomaly_table = dynamodb.Table("AnomalyEvents")


def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)

    raise TypeError


def response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps(body, default=decimal_default)
    }


def lambda_handler(event, context):

    print(json.dumps(event))

    raw_path = event.get("rawPath", "")
    path_parameters = event.get("pathParameters") or {}

    printer_id = path_parameters.get("id")

    # GET /printers
    if raw_path == "/printers":
        result = profiles_table.scan()

        printers = result.get("Items", [])

        printers.sort(
            key=lambda item: int(item.get("EventCount", 0)),
            reverse=True
        )

        return response(200, printers)

    # GET /printers/{id}
    if (
        printer_id
        and raw_path == f"/printers/{printer_id}"
    ):
        result = profiles_table.get_item(
            Key={
                "PrinterId": printer_id
            }
        )

        item = result.get("Item")

        if not item:
            return response(
                404,
                {
                    "message": "Printer not found"
                }
            )

        return response(200, item)

    # GET /printers/{id}/telemetry
    if (
        printer_id
        and raw_path == f"/printers/{printer_id}/telemetry"
    ):
        result = telemetry_table.query(
            KeyConditionExpression=Key(
                "PrinterId"
            ).eq(printer_id),
            ScanIndexForward=False,
            Limit=50
        )

        return response(
            200,
            result.get("Items", [])
        )

    # GET /printers/{id}/anomalies
    if (
        printer_id
        and raw_path == f"/printers/{printer_id}/anomalies"
    ):
        result = anomaly_table.query(
            KeyConditionExpression=Key(
                "PrinterId"
            ).eq(printer_id),
            ScanIndexForward=False,
            Limit=50
        )

        return response(
            200,
            result.get("Items", [])
        )

    return response(
        404,
        {
            "message": "Route not found"
        }
    )
