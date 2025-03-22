module "ecs" {
  source = "./modules/ecs"

  # API
  api_container_name = var.api_container_name
  api_image_uri      = var.api_image_uri
  api_log_group      = var.api_log_group
  api_port           = var.api_port

  # Database
  database_container_name = var.database_container_name
  database_host           = var.database_host
  database_image_uri      = var.database_image_uri
  database_port           = var.database_port

  # AWS
  aws_ecr_repository_name = var.aws_ecr_repository_name
  aws_region              = var.aws_region
  aws_s3_bucket_name      = var.aws_s3_bucket_name

  # ECS
  ecs_cluster_arn                    = var.ecs_cluster_arn
  ecs_service_name                   = var.ecs_service_name
  ecs_sg_name                        = var.ecs_sg_name
  family                             = var.family
  task_definition_cpu                = var.task_definition_cpu
  task_definition_execution_role_arn = var.task_definition_execution_role_arn
  task_definition_memory             = var.task_definition_memory

  # Network
  igw_name                   = var.igw_name
  public_rt_name             = var.public_rt_name
  subnet_1_name              = var.subnet_1_name
  subnet_1_availability_zone = var.subnet_1_availability_zone
  subnet_1_cidr_block        = var.subnet_1_cidr_block
  subnet_2_name              = var.subnet_2_name
  subnet_2_availability_zone = var.subnet_2_availability_zone
  subnet_2_cidr_block        = var.subnet_2_cidr_block
  vpc_cidr_block             = var.vpc_cidr_block
  vpc_name                   = var.vpc_name
}
