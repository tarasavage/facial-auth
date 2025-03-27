#!/bin/bash

set -e

echo "Logging in to ECR"
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

echo "Building the Backend Docker image"
docker build --no-cache -t $AWS_ECR_REPOSITORY_NAME:$BACKEND_TAG -f backend/Dockerfile ./backend

echo "Building the Frontend Docker image"
docker build --no-cache -t $AWS_ECR_REPOSITORY_NAME:$FRONTEND_TAG -f frontend/Dockerfile.prod ./frontend

echo "Tagging the Backend Docker image"
docker tag $AWS_ECR_REPOSITORY_NAME:$BACKEND_TAG $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$AWS_ECR_REPOSITORY_NAME:$BACKEND_TAG

echo "Tagging the Frontend Docker image"
docker tag $AWS_ECR_REPOSITORY_NAME:$FRONTEND_TAG $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$AWS_ECR_REPOSITORY_NAME:$FRONTEND_TAG

echo "Pushing the Backend Docker image to ECR"
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$AWS_ECR_REPOSITORY_NAME:$BACKEND_TAG

echo "Pushing the Frontend Docker image to ECR"
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$AWS_ECR_REPOSITORY_NAME:$FRONTEND_TAG

echo "Creating vars.env file"
cat > vars.env <<EOF
TF_VAR_api_image_uri=$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$AWS_ECR_REPOSITORY_NAME:$BACKEND_TAG
TF_VAR_frontend_image_uri=$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$AWS_ECR_REPOSITORY_NAME:$FRONTEND_TAG
EOF

echo "vars.env file created"
cat vars.env
