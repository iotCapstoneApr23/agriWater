import argparse
import datetime
import json
import random
import time

import boto3
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

# Define the sensors and their respective workstations
WS_01 = ["SS_01", "SS_02", "SS_03", "SS_04"]
WS_02 = ["SS_05", "SS_06", "SS_07", "SS_08"]
WS_03 = ["SS_09", "SS_10", "SS_11", "SS_12"]
WS_04 = ["SS_13", "SS_14", "SS_15", "SS_16"]
WS_05 = ["SS_17", "SS_18", "SS_19", "SS_20"]

# Dictionary to map WS to their sensors
sprinklers = {
    "WS_01": WS_01,
    "WS_02": WS_02,
    "WS_03": WS_03,
    "WS_04": WS_04,
    "WS_05": WS_05
}

# AWS IoT endpoint
aws_iot_endpoint = "a342xcg8nwn1eo-ats.iot.us-east-1.amazonaws.com"
# aws_iot_endpoint = "Soil_Sensor_Cert\endpoint.txt"
# iot_client = boto3.client('iot', region_name='us-east-1') # Initialize the IoT client
# aws_iot_endpoint = iot_client.describe_endpoint(endpointType='iot:Data-ATS')['endpointAddress'] # Download the IoT endpoint

# Path to the root CA certificate
root_ca_path = "Soil_Sensor_Cert\AmazonRootCA1.pem"  


def create_mqtt_client(sensor_id):
    # Paths to the certificate and private key (unique for each device)
    certificate_path = f"Soil_Sensor_Cert/{sensor_id}_certificate.pem.crt"
    private_key_path = f"Soil_Sensor_Cert/{sensor_id}_private.pem.key"
    
    # Initialize the MQTT client
    mqtt_client = AWSIoTMQTTClient(sensor_id)
    mqtt_client.configureEndpoint(aws_iot_endpoint, 8883)
    mqtt_client.configureCredentials(root_ca_path, private_key_path, certificate_path)

    # Configure the MQTT client
    mqtt_client.configureAutoReconnectBackoffTime(1, 32, 20)
    mqtt_client.configureOfflinePublishQueueing(-1)  # Infinite offline publish queueing
    mqtt_client.configureDrainingFrequency(2)  # Draining: 2 Hz
    mqtt_client.configureConnectDisconnectTimeout(10)  # 10 sec
    mqtt_client.configureMQTTOperationTimeout(5)  # 5 sec

    return mqtt_client

def publish_soil_sensor_data():
    for ws_id, sensors in sprinklers.items():
        for sensor in sensors:
            message = {
                "sprinkler_id": ws_id,
                "sensor_id": sensor,
                "timestamp": str(datetime.datetime.now()),
                "Temperature": random.randint(18, 50),
                "Moisture": int(random.normalvariate(50, 10))
            }
            message_json = json.dumps(message)
            print(message_json)
            # Publish to AWS IoT topic
            try:
                mqtt_client = create_mqtt_client(sensor)
                mqtt_client.connect()
                mqtt_client.publish('iot/ss', message_json, 1)
                mqtt_client.disconnect()
                print(f"Published message to topic iot/ss: {message_json}")
            except Exception as e:
                print(f"Failed to publish message for {sensor}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Publish soil sensor data to AWS IoT")
    parser.add_argument('--count', type=int, default=10, help='Number of times to publish data')
    args = parser.parse_args()

    count = args.count
    present_count = 0

    # Run the function continuously
    while present_count < count:
        publish_soil_sensor_data()
        time.sleep(3)  # Sleep for 3 seconds
        present_count += 1

    print("'Reached max count' hence stopping the publish")

if __name__ == "__main__":
    main()
