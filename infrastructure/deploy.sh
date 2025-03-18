#!/bin/bash

echo "Logging in to ECR"
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

echo "Building the Backend Docker image"
docker build --no-cache -t $AWS_ECR_REPOSITORY_NAME:$BACKEND_TAG -f backend/Dockerfile ./backend

echo "Tagging the Backend Docker image"
docker tag $AWS_ECR_REPOSITORY_NAME:$BACKEND_TAG $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$AWS_ECR_REPOSITORY_NAME:$BACKEND_TAG

echo "Pushing the Backend Docker image to ECR"
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$AWS_ECR_REPOSITORY_NAME:$BACKEND_TAG
