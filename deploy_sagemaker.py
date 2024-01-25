
import datetime
import os
import sys
import time

import boto3
import pytz
from botocore.config import Config


def sagemaker_client():
    """
    Function to get sagemaker client
    """
    return boto3.client(
        'sagemaker',
        config=Config(
            region_name = 'ap-southeast-1'
        )
    )


def create_sagemaker_model(client, model_spec):
    # list all models
    models = client.list_models()
    all_models = models['Models']
    while 'NextToken' in models:
        models = client.list_models(NextToken=models['NextToken'])
        all_models += models['Models']

    print(f"List of models {all_models}")

    # if model already exists, delete it
    for model in all_models:
        if model['ModelName'] == model_spec['CapabilityName']:
            try:
                client.delete_model(
                    ModelName=model['ModelName']
                )
            except Exception as e:
                print(f"Failed to delete model in Sagemaker. Error: {e}")
                return False

    # try create model
    try:
        client.create_model(
            ModelName=f"{model_spec['CapabilityName']}",
            PrimaryContainer={
                'Image':model_spec['Image'],
                'Mode': 'SingleModel'
            },
            ExecutionRoleArn=model_spec['ExecutionRoleArn'],
            Tags = [
                {'Key':'Model','Value':str(model_spec['CapabilityName'])}
            ]
        )
    except Exception as e:
        print(f"Failed to create model in Sagemaker. Error: {e}")
        return False

    return True

def create_endpoint(client, current_time, endpoint_spec):
    """
    create endpoint with necessary details like updatetime, version name
    """
    
    version_name = "{}-{}".format(
            endpoint_spec['EndpointName'],
            str(current_time.strftime('%d-%m-%Y-%H-%M-%S'))
        )
    print("Endpoint Version Name:", version_name)
    
    try:
        _ = client.create_endpoint_config(
            EndpointConfigName=version_name,
            ProductionVariants=endpoint_spec['ProductionVariants'],
        )
    except Exception as e:
        print(f"Failed to create endpoint config in Sagemaker. Error: {e}")
        return False

    try:
        _ = client.delete_endpoint(
            EndpointName=endpoint_spec['EndpointName']
        )
        time.sleep(240)
    except Exception as e:
        print(f"No endpoint to delete in Sagemaker. Error: {e}")

    try:
        _ = client.create_endpoint(
            EndpointName = endpoint_spec['EndpointName'],
            EndpointConfigName= version_name,
        )
    except Exception as e:
        print(f"Failed to create endpoint in Sagemaker. Error: {e}")
        return False
   
    return True


if __name__ == "__main__":
    ecr_docker_image_path = str(sys.argv[1])
    stage = 'dev'
    print(f"Stage: {stage}")
    current_time = datetime.datetime.now(tz=pytz.timezone('Asia/Singapore'))

    client = sagemaker_client()

    model_name = f'minimal-sagemaker-inference-{stage}'

    model_spec = {
        "Image": ecr_docker_image_path,
        "ExecutionRoleArn": 'arn:aws:iam::302932544810:role/service-role/AmazonSageMaker-ExecutionRole-20240119T152467', # Execution Role created via console
        "CapabilityName": model_name,
        "StageName": stage
    }

    model_success = create_sagemaker_model(client, model_spec)

    if model_success:
        print("Model successfully deployed in Sagemaker.")

        endpoint_spec = {
            "EndpointName": model_name,
            "ProductionVariants":[
                {
                    "VariantName": model_name,
                    "ModelName": model_name,
                    "InitialInstanceCount": 1,
                    "InstanceType": "ml.g4dn.xlarge",
                    "InitialVariantWeight": 1.0
                }
            ]
        }

        endpoint_success = create_endpoint(client, current_time, endpoint_spec)

        if endpoint_success:
            print("Endpoint successfully deployed in Sagemaker.")
