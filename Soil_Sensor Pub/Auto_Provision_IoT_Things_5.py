import json
import os
import time

import boto3
import requests
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

# Create a directory to store the certificates
certs_dir = "Soil_Sensor_Cert"
if not os.path.exists(certs_dir):
    os.makedirs(certs_dir)

# Initialize the IoT client
iot_client = boto3.client('iot', region_name='us-east-1')
# Download the IoT endpoint
endpoint = iot_client.describe_endpoint(endpointType='iot:Data-ATS')['endpointAddress']
# Save the endpoint in the certificates folder
with open(os.path.join(certs_dir, "endpoint.txt"), "w") as endpoint_file:
    endpoint_file.write(endpoint)

# Download and save the Amazon Root CA1 certificate
root_ca_url = "https://www.amazontrust.com/repository/AmazonRootCA1.pem"
root_ca_content = requests.get(root_ca_url).text
with open(os.path.join(certs_dir, "AmazonRootCA1.pem"), "w") as root_ca_file:
    root_ca_file.write(root_ca_content)

print(f"Root CA & endpoint were downloaded and saved in: {certs_dir}")

# Policy document for IoT things (replace this with your actual policy)
policy_document = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "iot:*",
            "Resource": "*"
        }
    ]
}

# Function to create a policy if not exists
def create_policy(policy_name, policy_document):
    try:
        iot_client.create_policy(
            policyName=policy_name,
            policyDocument=policy_document
        )
    except iot_client.exceptions.ResourceAlreadyExistsException:
        print(f"Policy {policy_name} already exists")

policy_name = "SoilSensorPolicy"
create_policy(policy_name, json.dumps(policy_document))

# Create thing type if not exists
thing_type_name = "soil_sensor"

try:
    iot_client.create_thing_type(
        thingTypeName=thing_type_name
    )
    print(f"Thing type {thing_type_name} created")
except iot_client.exceptions.ResourceAlreadyExistsException:
    print(f"Thing type {thing_type_name} already exists")

# Function to create and provision IoT Thing
def provision_thing(thing_name, thing_type_name):
    # Check if the thing already exists
    try:
        response = iot_client.describe_thing(
            thingName=thing_name
        )
        print(f"Thing {thing_name} already exists, skipping creation.")
        return
    except iot_client.exceptions.ResourceNotFoundException:
        pass
    
    # Create the thing with the specified type
    response = iot_client.create_thing(
        thingName=thing_name,
        thingTypeName=thing_type_name
    )
    print(f"Created thing: {thing_name} with type: {thing_type_name}")
    
    # Create keys and certificate
    response = iot_client.create_keys_and_certificate(
        setAsActive=True
    )
    certificate_arn = response['certificateArn']
    certificate_id = response['certificateId']
    certificate_pem = response['certificatePem']
    key_pair = response['keyPair']
    
    # Attach the policy to the certificate
    iot_client.attach_policy(
        policyName=policy_name,
        target=certificate_arn
    )
    
    # Attach the thing to the certificate
    iot_client.attach_thing_principal(
        thingName=thing_name,
        principal=certificate_arn
    )
    
    # Save the certificate and keys locally
    with open(f"{certs_dir}/{thing_name}_certificate.pem.crt", 'w') as f:
        f.write(certificate_pem)
    with open(f"{certs_dir}/{thing_name}_private.pem.key", 'w') as f:
        f.write(key_pair['PrivateKey'])
    with open(f"{certs_dir}/{thing_name}_public.pem.key", 'w') as f:
        f.write(key_pair['PublicKey'])
    
    print(f"Saved certificates and keys for: {thing_name}")

# Provision 20 IoT Things
for i in range(1, 21):
    thing_name = f"SS_{i:02d}"
    provision_thing(thing_name, thing_type_name)

print("Provisioning complete!")

# Code block to destroy provisioned IoT Things, policies, and thing types
def destroy_resources():
    # Delete IoT Things
    things_response = iot_client.list_things()
    things = things_response['things']
    for thing in things:
        thing_name = thing['thingName']
        if thing_name.startswith('SS_'):
            print(f"Detaching certificate from thing: {thing_name}")
            try:
                # Detach the certificate from the thing
                principal_response = iot_client.list_thing_principals(thingName=thing_name)
                principals = principal_response['principals']
                for principal in principals:
                    iot_client.detach_thing_principal(thingName=thing_name, principal=principal)

                print(f"Deleting thing: {thing_name}")
                iot_client.delete_thing(thingName=thing_name)
            except iot_client.exceptions.ResourceNotFoundException:
                print(f"Thing {thing_name} not found, skipping deletion.")

    # Detach and delete policies
    policies_response = iot_client.list_policies()
    policies = policies_response['policies']
    for policy in policies:
        policy_name = policy['policyName']
        if policy_name == "SoilSensorPolicy":
            print(f"Detaching policy: {policy_name}")
            targets_response = iot_client.list_policy_principals(policyName=policy_name)
            targets = targets_response['principals']
            for target in targets:
                iot_client.detach_policy(policyName=policy_name, target=target)
            print(f"Deleting policy: {policy_name}")
            iot_client.delete_policy(policyName=policy_name)

    # Deprecate the thing type
    print(f"Deprecating thing type: {thing_type_name}")
    iot_client.deprecate_thing_type(thingTypeName=thing_type_name)

    # Wait for 5 minutes after deprecation
    print("Waiting for 5 minutes before deleting the thing type...")
    time.sleep(300)

    # Delete the deprecated thing type
    print(f"Deleting thing type: {thing_type_name}")
    iot_client.delete_thing_type(thingTypeName=thing_type_name)

    print("Destruction of resources complete!")

# Prompt the user to destroy resources if needed
destroy = input("Do you want to destroy the provisioned IoT Things, policies, and thing types? (y/n) ")
if destroy.lower() == 'y':
    destroy_resources()