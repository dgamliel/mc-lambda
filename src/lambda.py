#!/usr/bin/env python
import boto3
import json
import os
import base64

spot_opts = {
    'InstanceInterruptionBehavior': 'terminate',
    'SingleInstanceType': True,
    'SingleAvailabilityZone': False,
    'MinTargetCapacity': 1,
}

launch_temp_conf = [
    {
        'LaunchTemplateSpecification': {
            'LaunchTemplateName': 'small-mc-server',
            'Version': '$Latest'
        },
        'Overrides': [
            {
                'InstanceRequirements': {
                    'VCpuCount': {
                        'Min': 1,
                        'Max': 1
                    },
                    'MemoryMiB': {
                        'Min': 1024,
                        'Max': 2048
                    },
                    'InstanceGenerations': [
                        'current',
                    ],
                },
            },
        ]
    },
]

capacity_spec = {
    'TotalTargetCapacity': 1,
    'SpotTargetCapacity': 1,
    'DefaultTargetCapacityType': 'spot'
}

def lambda_handler(event, context):

    # Read the event post body, and get the ACTION
    try:
        body = json.loads(event['body'])
    except:
        body = event['body']

    action = body['action']

    if action == 'START':

        # Get the latest AMI ID
        ec2 = boto3.client('ec2')

        response = ec2.create_fleet(
            SpotOptions=spot_opts,
            LaunchTemplateConfigs=launch_temp_conf,
            TargetCapacitySpecification=capacity_spec,
            Type='instant',
            #Tag the instance with the tag {'User': 'Daniel'}
            TagSpecifications=[
                {
                    'ResourceType': 'instance',
                    'Tags': [
                        {
                            'Key': 'User',
                            'Value': 'Daniel'
                        },
                    ]
                }
            ]
        )

        # Return the instance public ip
        return {
            'statusCode': 200,
            'body': json.dumps(response),
            'headers': {
                'Access-Control-Allow-Origin': '*',        # Allows all domains
                'Access-Control-Allow-Headers': 'Content-Type', # Specific headers you allow
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET' # Allowed HTTP methods
            }
        }

    if action == 'STOP':

        # Get the instance ID
        instance_id = body['instance_id']

        # Stop the instance
        ec2 = boto3.client('ec2')
        response = ec2.stop_instances(
            InstanceIds=[instance_id]
        )

        # Return the instance public ip
        return {
            'statusCode': 200,
            'body': json.dumps(response)
        }

    else:
        return {
            'statusCode': 400,
            'body': json.dumps('Invalid action')
        }
