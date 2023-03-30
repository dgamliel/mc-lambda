#!/bin/ksh

ARN="arn:aws:lambda:us-east-2:195513505392:function:minecraft"

# Get the full path to the parent dir
PARENT_DIR=$(dirname $(pwd))
cd "${PARENT_DIR}/src"

zip -r ../build/lambda.zip lambda.py

cd "${PARENT_DIR}"/scripts

#Update the aws lambda function code using the arn
aws lambda update-function-code \
--function-name "${ARN}" \
--zip-file "fileb://${PARENT_DIR}/build/lambda.zip" \
--region us-east-2 \
--output text

#Invoke the lambda with a body of {} and print the response
aws lambda invoke \
--function-name "${ARN}" \
--payload '{}' \
--region us-east-2 \
response.txt

cat response.txt | jq
