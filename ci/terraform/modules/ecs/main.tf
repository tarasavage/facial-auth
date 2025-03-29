locals {
  api_template = templatefile("${path.module}/templates/api.json.tpl", {
    aws_region              = var.aws_region
    aws_s3_bucket_name      = var.aws_s3_bucket_name

    api_container_name = var.api_container_name
    api_image_uri      = var.api_image_uri
    api_log_group      = var.api_log_group
    api_port           = var.api_port

    database_container_name           = var.database_container_name
  })

  database_template = templatefile("${path.module}/templates/database.json.tpl", {
    aws_s3_bucket_name      = var.aws_s3_bucket_name
    database_container_name           = var.database_container_name
    database_image_uri                = var.database_image_uri
    database_port                     = var.database_port
    database_healthcheck_command      = "pg_isready -U postgres || exit 1"
    database_healthcheck_interval     = 30
    database_healthcheck_timeout      = 5
    database_healthcheck_retries      = 3
    database_healthcheck_start_period = 40
  })

  frontend_template = templatefile("${path.module}/templates/frontend.json.tpl", {
    aws_region              = var.aws_region
    aws_s3_bucket_name      = var.aws_s3_bucket_name

    frontend_container_name = var.frontend_container_name
    frontend_image_uri      = var.frontend_image_uri
    frontend_log_group      = var.frontend_log_group
    frontend_port           = var.frontend_port
  })
}

resource "aws_ecs_task_definition" "definition" {
  family                   = var.family
  execution_role_arn       = var.task_definition_execution_role_arn
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.task_definition_cpu
  memory                   = var.task_definition_memory

  container_definitions = jsonencode([
    jsondecode(local.api_template),
    jsondecode(local.database_template),
    jsondecode(local.frontend_template)
  ])
}

resource "aws_vpc" "fq_vpc" {
  cidr_block           = var.vpc_cidr_block
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name = var.vpc_name
  }
}

resource "aws_subnet" "fq_subnet_1" {
  vpc_id                  = aws_vpc.fq_vpc.id
  availability_zone       = var.subnet_1_availability_zone
  cidr_block              = var.subnet_1_cidr_block
  map_public_ip_on_launch = true

  tags = {
    Name = var.subnet_1_name
  }
}

resource "aws_subnet" "fq_subnet_2" {
  vpc_id                  = aws_vpc.fq_vpc.id
  availability_zone       = var.subnet_2_availability_zone
  cidr_block              = var.subnet_2_cidr_block
  map_public_ip_on_launch = true

  tags = {
    Name = var.subnet_2_name
  }
}

resource "aws_internet_gateway" "fq_igw" {
  vpc_id = aws_vpc.fq_vpc.id

  tags = {
    Name = var.igw_name
  }
}

resource "aws_route_table" "fq_public_rt" {
  vpc_id = aws_vpc.fq_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.fq_igw.id
  }

  tags = {
    Name = var.public_rt_name
  }
}

resource "aws_route_table_association" "fq_subnet_1_association" {
  subnet_id      = aws_subnet.fq_subnet_1.id
  route_table_id = aws_route_table.fq_public_rt.id
}

resource "aws_route_table_association" "fq_subnet_2_association" {
  subnet_id      = aws_subnet.fq_subnet_2.id
  route_table_id = aws_route_table.fq_public_rt.id
}

resource "aws_security_group" "ecs_sg" {
  name        = var.ecs_sg_name
  description = "Security group for FaceLinq ECS tasks"
  vpc_id      = aws_vpc.fq_vpc.id

  # Allow inbound HTTP traffic
  ingress {
    protocol    = "tcp"
    from_port   = var.api_port
    to_port     = var.api_port
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Allow inbound Postgres traffic
  ingress {
    protocol    = "tcp"
    from_port   = var.database_port
    to_port     = var.database_port
    cidr_blocks = [var.vpc_cidr_block]
  }

  # Allow all outbound traffic
  egress {
    protocol    = "-1"
    from_port   = 0
    to_port     = 0
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = var.ecs_sg_name
  }
}


resource "aws_ecs_service" "service" {
  name            = var.ecs_service_name
  cluster         = var.ecs_cluster_arn
  task_definition = aws_ecs_task_definition.definition.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = [aws_subnet.fq_subnet_1.id, aws_subnet.fq_subnet_2.id]
    security_groups  = [aws_security_group.ecs_sg.id]
    assign_public_ip = true
  }
}
