variable "aws_region" {
  description = "The region of the AWS account"
  type        = string
}

variable "aws_s3_bucket_name" {
  description = "The name of the AWS S3 bucket"
  type        = string
}


## ------------------------------- Task Definition ------------------------------ ## 

variable "family" {
  description = "The family of the task definition"
  type        = string
}

variable "task_definition_execution_role_arn" {
  description = "The ARN of the execution role for the task definition"
  type        = string
}

variable "task_definition_cpu" {
  description = "The CPU of the task definition"
  type        = number
}

variable "task_definition_memory" {
  description = "The memory of the task definition"
  type        = number
}
## ------------------------------- Backend API Container Definitions ------------------------------ ## 

variable "api_container_name" {
  description = "The name of the backend container"
  type        = string
}

variable "api_image_uri" {
  description = "The URI of the backend image"
  type        = string
}

variable "api_port" {
  description = "The port of the backend"
  type        = number
}

variable "api_log_group" {
  description = "The log group of the backend"
  type        = string
}

variable "aws_ecr_repository_name" {
  description = "The name of the AWS ECR repository"
  type        = string
}

## ------------------------------- Database Container Definitions ------------------------------ ## 

variable "database_container_name" {
  description = "The name of the database container"
  type        = string
}

variable "database_image_uri" {
  description = "The URI of the database image"
  type        = string
}

variable "database_host" {
  description = "The host of the database"
  type        = string
}

variable "database_port" {
  description = "The port of the database"
  type        = number
}


## ------------------------------- Network ------------------------------ ## 

variable "vpc_cidr_block" {
  description = "The CIDR block of the VPC"
  type        = string
}

variable "subnet_1_cidr_block" {
  description = "The CIDR block of the subnet"
  type        = string
}

variable "subnet_1_availability_zone" {
  description = "The availability zone of the subnet"
  type        = string
}

variable "subnet_2_cidr_block" {
  description = "The CIDR block of the subnet"
  type        = string
}

variable "subnet_2_availability_zone" {
  description = "The availability zone of the subnet"
  type        = string
}

variable "vpc_name" {
  description = "The name of the VPC"
  type        = string
}

variable "subnet_1_name" {
  description = "The name of the subnet"
  type        = string
}

variable "subnet_2_name" {
  description = "The name of the subnet"
  type        = string
}

variable "igw_name" {
  description = "The name of the internet gateway"
  type        = string
}

variable "public_rt_name" {
  description = "The name of the public route table"
  type        = string
}


variable "ecs_sg_name" {
  description = "The name of the security group"
  type        = string
}

## ------------------------------- ECS ------------------------------ ## 

variable "ecs_service_name" {
  description = "The name of the ECS service"
  type        = string
}


variable "ecs_cluster_arn" {
  description = "The ARN of the ECS cluster"
  type        = string
}
