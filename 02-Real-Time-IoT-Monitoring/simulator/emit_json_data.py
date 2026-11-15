import json
import random
import time
from datetime import datetime, timezone

from awscrt import mqtt
from awsiot import mqtt_connection_builder


ENDPOINT = "a1400aetp7meim-ats.iot.ap-southeast-2.amazonaws.com"

CLIENT_ID = "printer-001"

CERT_PATH = (
    "/Users/rakeshbangaru/.aws-iot/"
    "real-time-iot-monitor/printer-001/device.pem.crt"
)

KEY_PATH = (
    "/Users/rakeshbangaru/.aws-iot/"
    "real-time-iot-monitor/printer-001/private.pem.key"
)

CA_PATH = (
    "/Users/rakeshbangaru/.aws-iot/"
    "real-time-iot-monitor/printer-001/AmazonRootCA1.pem"
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


mqtt_connection = mqtt_connection_builder.mtls_from_path(
    endpoint=ENDPOINT,
    cert_filepath=CERT_PATH,
    pri_key_filepath=KEY_PATH,
    ca_filepath=CA_PATH,
    client_id=CLIENT_ID,
    clean_session=False,
    keep_alive_secs=30,
)


print("Connecting to AWS IoT Core...")

mqtt_connection.connect().result()

print("Connected.")
print("Publishing telemetry for multiple virtual printers.")
print()


try:
    while True:

        for printer in PRINTERS:

            printer_id = printer["id"]

            temperature = round(
                random.uniform(
                    printer["min_temp"],
                    printer["max_temp"]
                ),
                2
            )

            payload = {
                "printerId": printer_id,
                "timestamp": datetime.now(
                    timezone.utc
                ).isoformat(),
                "data": {
                    "type": "temperature",
                    "value": temperature
                }
            }

            topic = (
                f"iot-monitor/printers/"
                f"{printer_id}/telemetry"
            )

            message = json.dumps(payload)

            print(
                f"{printer_id} -> "
                f"{temperature} °C"
            )

            mqtt_connection.publish(
                topic=topic,
                payload=message,
                qos=mqtt.QoS.AT_LEAST_ONCE,
            )

        print("-----------------------------")

        time.sleep(5)


except KeyboardInterrupt:
    print("\nStopping simulator...")


finally:
    mqtt_connection.disconnect().result()
    print("Disconnected from AWS IoT Core.")
