#!/bin/bash
RES=$(curl -X POST \
     -H "Content-Type: application/json" \
     -d '{"action": "START"}' \
     https://ihd4rhh2anov74rz25wbpyhy340cnthg.lambda-url.us-east-2.on.aws/)

INSTANCE_ID=$(echo $RES | jq -r '.Instances[0].InstanceIds[]')
PUBLIC_IP=$(aws ec2 describe-instances --instance-ids $INSTANCE_ID --query 'Reservations[].Instances[].PublicIpAddress' --output text)

echo "Instance ID: $INSTANCE_ID"
echo "Public IP: $PUBLIC_IP"

