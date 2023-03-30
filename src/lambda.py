import boto3
import json
import os
import base64

def lambda_handler(event, context):

    # Get the latest AMI ID
    ec2 = boto3.client('ec2')

    response = ec2.create_fleet(
        SpotOptions={
            'InstanceInterruptionBehavior': 'terminate',
            'SingleInstanceType': True,
            'SingleAvailabilityZone': False,
            'MinTargetCapacity': 1,
        },
        LaunchTemplateConfigs=[
            {
                'LaunchTemplateSpecification': {
                    'LaunchTemplateName': 'small-mc-server',
                    'Version': '$Latest'
                },
                'Overrides': [
                    {
                        'InstanceRequirements': {
                            'VCpuCount': {
                                'Min': 0,
                                # 'Max': 2 
                            },
                            'MemoryMiB': {
                                'Min': 3072,
                                'Max': 4096
                            },
                            'InstanceGenerations': [
                                'current',
                            ],
                        },
                    },
                ]
            },
        ],
        TargetCapacitySpecification={
            'TotalTargetCapacity': 1,
            'SpotTargetCapacity': 1,
            'DefaultTargetCapacityType': 'spot'
        },
        Type='instant',
    )


    # Return the instance public ip
    return {
        'statusCode': 200,
        'body': json.dumps(response)
    }
