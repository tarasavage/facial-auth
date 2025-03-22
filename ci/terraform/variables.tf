variable "aws_region" {
  description = "The region of the AWS account"
  type        = string
  default     = "us-east-1"
}

variable "backend_s3_bucket_name" {
  type        = string
  description = "The name of the S3 bucket to use for the backend"
  default     = "linqqq"
}

variable "backend_s3_bucket_region" {
  type        = string
  description = "The region of the S3 bucket to use for the backend"
  default     = "us-east-1"
}

variable "backend_s3_bucket_key" {
  type        = string
  description = "The key of the S3 bucket to use for the backend"
  default     = "ci/terraform.tfstate"
}

variable "aws_s3_bucket_name" {
  description = "The name of the AWS S3 bucket"
  type        = string
  default     = "linqqq"
}


## ------------------------------- Task Definition ------------------------------ ## 

variable "family" {
  description = "The family of the task definition"
  type        = string
  default     = "facelinq-task-definition"
}

variable "task_definition_execution_role_arn" {
  description = "The ARN of the execution role for the task definition"
  type        = string
  default     = "arn:aws:iam::636387821925:role/ECSTaskExecutionRoleWithS3Access"
}

variable "task_definition_cpu" {
  description = "The CPU of the task definition"
  type        = number
  default     = 1024
}

variable "task_definition_memory" {
  description = "The memory of the task definition"
  type        = number
  default     = 3072
}
## ------------------------------- Backend API Container Definitions ------------------------------ ## 

variable "api_container_name" {
  description = "The name of the backend container"
  type        = string
  default     = "fast-api"
}

variable "api_image_uri" {
  description = "The URI of the backend image"
  type        = string
}

variable "api_port" {
  description = "The port of the backend"
  type        = number
  default     = 8000
}

variable "api_log_group" {
  description = "The log group of the backend"
  type        = string
  default     = "/ecs/facelinq-backend"
}

variable "aws_ecr_repository_name" {
  description = "The name of the AWS ECR repository"
  type        = string
  default     = "facelinq"
}

## ------------------------------- Database Container Definitions ------------------------------ ## 

variable "database_container_name" {
  description = "The name of the database container"
  type        = string
  default     = "database"
}

variable "database_image_uri" {
  description = "The URI of the database image"
  type        = string
  default     = "postgres:17.1"
}

variable "database_host" {
  description = "The host of the database"
  type        = string
  default     = "localhost"
}

variable "database_port" {
  description = "The port of the database"
  type        = number
  default     = 5432
}

## ------------------------------- Network ------------------------------ ## 

variable "vpc_cidr_block" {
  description = "The CIDR block of the VPC"
  type        = string
  default     = "172.31.0.0/16"
}

variable "subnet_1_cidr_block" {
  description = "The CIDR block of the subnet"
  type        = string
  default     = "172.31.0.0/24"
}

variable "subnet_1_availability_zone" {
  description = "The availability zone of the subnet"
  type        = string
  default     = "us-east-1a"
}

variable "subnet_2_cidr_block" {
  description = "The CIDR block of the subnet"
  type        = string
  default     = "172.31.1.0/24"
}

variable "subnet_2_availability_zone" {
  description = "The availability zone of the subnet"
  type        = string
  default     = "us-east-1b"
}

variable "vpc_name" {
  description = "The name of the VPC"
  type        = string
  default     = "fq-vpc"
}

variable "subnet_1_name" {
  description = "The name of the subnet"
  type        = string
  default     = "fq-subnet-1"
}

variable "subnet_2_name" {
  description = "The name of the subnet"
  type        = string
  default     = "fq-subnet-2"
}

variable "igw_name" {
  description = "The name of the internet gateway"
  type        = string
  default     = "fq-igw"
}

variable "public_rt_name" {
  description = "The name of the public route table"
  type        = string
  default     = "fq-public-rt"
}


variable "ecs_sg_name" {
  description = "The name of the security group"
  type        = string
  default     = "fq-ecs-security-group"
}

## ------------------------------- ECS ------------------------------ ## 

variable "ecs_service_name" {
  description = "The name of the ECS service"
  type        = string
  default     = "fq-service"
}


variable "ecs_cluster_arn" {
  description = "The ARN of the ECS cluster"
  type        = string
  default     = "arn:aws:ecs:us-east-1:636387821925:cluster/FQ"
}

