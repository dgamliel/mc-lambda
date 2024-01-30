#!/bin/ksh

ARN="arn:aws:lambda:us-east-2:195513505392:function:minecraft"

PROJ_DIR="/Users/daniel/tmp/minecraft/lambda/"

cd $PROJ_DIR
zip -r $PROJ_DIR/build/lambda.zip ./src/*
cd $PROJ_DIR

#Update the aws lambda function code using the arn
aws lambda update-function-code \
--function-name "${ARN}" \
--zip-file "fileb://$PROJ_DIR/build/lambda.zip" \
--region us-east-2 \
--output text

#Invoke the lambda with a body of {} and print the response
# aws lambda invoke \
# --function-name "${ARN}" \
# --payload '{}' \
# --region us-east-2 \
# response.txt
#
# cat response.txt | jq
