import json
import os

import boto3
import requests
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

# Create an AWS IoT client
iot = boto3.client('iot', region_name='us-east-1')

# Create the IoT Thing named "Sprinkler"
thing_name = "Sprinkler"
thing_response = iot.create_thing(thingName=thing_name)
thing_arn = thing_response['thingArn']
print(f"Created IoT Thing: {thing_name} (ARN: {thing_arn})")

# Create a folder to store certificates
certificate_folder = "Water_Sprinkler_Cert"
os.makedirs(certificate_folder, exist_ok=True)

# Create keys and certificate for the thing
keys_and_cert = iot.create_keys_and_certificate(setAsActive=True)

# Save the certificate, public key, and private key in the certificates folder
with open(os.path.join(certificate_folder, "certificate.pem.crt"), "w") as cert_file:
    cert_file.write(keys_and_cert['certificatePem'])

with open(os.path.join(certificate_folder, "public.pem.key"), "w") as public_key_file:
    public_key_file.write(keys_and_cert['keyPair']['PublicKey'])

with open(os.path.join(certificate_folder, "private.pem.key"), "w") as private_key_file:
    private_key_file.write(keys_and_cert['keyPair']['PrivateKey'])

# Attach the certificate to the thing
iot.attach_thing_principal(
    thingName=thing_name,
    principal=keys_and_cert['certificateArn']
)

# Create an IoT policy
policy_name = "SprinklerPolicy"
policy_document = {
    "Version": "2012-10-17",
    "Statement": [{
        "Effect": "Allow",
        "Action": "iot:*",
        "Resource": "*"
    }]
}

# Convert the policy document to JSON string
policy_document_json = json.dumps(policy_document)

# Check if the policy already exists
try:
    iot.create_policy(
        policyName=policy_name,
        policyDocument=policy_document_json
    )
    print(f"Created policy: {policy_name}")
except iot.exceptions.ResourceAlreadyExistsException:
    print(f"Policy {policy_name} already exists. Using existing policy.")


# Check if the certificate is already attached to the policy
attached_policies = iot.list_attached_policies(target=keys_and_cert['certificateArn'])['policies']
if not any(policy['policyName'] == policy_name for policy in attached_policies):
    # Attach the policy to the certificate
    iot.attach_policy(
        policyName=policy_name,
        target=keys_and_cert['certificateArn']
    )
    print(f"Attached policy: {policy_name} to certificate: {keys_and_cert['certificateArn']}")
else:
    print(f"Policy {policy_name} is already attached to certificate: {keys_and_cert['certificateArn']}")


# Download the IoT endpoint
endpoint = iot.describe_endpoint(endpointType='iot:Data-ATS')['endpointAddress']

# Save the endpoint in the certificates folder
with open(os.path.join(certificate_folder, "endpoint.txt"), "w") as endpoint_file:
    endpoint_file.write(endpoint)

# Download and save the Amazon Root CA1 certificate
root_ca_url = "https://www.amazontrust.com/repository/AmazonRootCA1.pem"
root_ca_content = requests.get(root_ca_url).text
with open(os.path.join(certificate_folder, "AmazonRootCA1.pem"), "w") as root_ca_file:
    root_ca_file.write(root_ca_content)

print(f"Certificates, endpoint, and Root CA saved in: {certificate_folder}")

# Function to delete the created thing
def delete_thing(thing_name, certificate_arn, policy_name):
    try:
        # Detach the policy from the certificate
        iot.detach_policy(policyName=policy_name, target=certificate_arn)
        print(f"Detached policy: {policy_name} from certificate: {certificate_arn}")

        # Detach the certificate from the thing
        iot.detach_thing_principal(thingName=thing_name, principal=certificate_arn)
        print(f"Detached certificate: {certificate_arn} from thing: {thing_name}")

        # Delete the certificate
        iot.update_certificate(certificateId=certificate_arn.split('/')[-1], newStatus='INACTIVE')
        iot.delete_certificate(certificateId=certificate_arn.split('/')[-1], forceDelete=True)
        print(f"Deleted certificate: {certificate_arn}")

        # List and detach all principals from the policy before deleting it
        principals = iot.list_targets_for_policy(policyName=policy_name)['targets']
        for principal in principals:
            iot.detach_policy(policyName=policy_name, target=principal)
            print(f"Detached policy: {policy_name} from principal: {principal}")

        # Delete the policy
        iot.delete_policy(policyName=policy_name)
        print(f"Deleted policy: {policy_name}")

        # Delete the thing
        iot.delete_thing(thingName=thing_name)
        print(f"Deleted IoT Thing: {thing_name}")
    except iot.exceptions.ResourceNotFoundException:
        print(f"Resource not found.")

# Initialize AWS IoT MQTT Client
mqtt_client = AWSIoTMQTTClient("sprinkler-subscriber")
mqtt_client.configureEndpoint(endpoint, 8883)
mqtt_client.configureCredentials(os.path.join(certificate_folder, "AmazonRootCA1.pem"), os.path.join(certificate_folder, "private.pem.key"), os.path.join(certificate_folder, "certificate.pem.crt"))

# Function to subscribe to a topic and display messages
def subscribe_and_display_messages(topic):
    mqtt_client.connect()
    mqtt_client.subscribe(topic, 1, lambda client, userdata, msg: print(f"Message received on topic '{topic}': {msg.payload.decode()}"))

try:
    # Subscribe to the topic "iot/ws" and display messages
    subscribe_and_display_messages("iot/ws")
    print("Awaiting for messages from topic 'iot/ws' ")
    # Keep the program running to continue receiving messages
    while True:
        pass
        
except KeyboardInterrupt:
    print("Program interrupted. Exiting gracefully.")

    # Prompt the user to destroy resources if needed
    destroy = input("Do you want to destroy the provisioned IoT Thing, policies, and certificates? (y/n) ")

    if destroy.lower() == 'y':
        delete_thing(thing_name, keys_and_cert['certificateArn'], policy_name)
