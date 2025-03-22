{
    "name": "${database_container_name}",
    "image": "${database_image_uri}",
    "cpu": 0,
    "portMappings": [
      {
        "name": "${database_container_name}", 
        "containerPort": ${database_port},
        "hostPort": ${database_port},
        "protocol": "tcp"
      }
    ],
    "essential": true,
    "environmentFiles": [
        {
            "value": "arn:aws:s3:::${aws_s3_bucket_name}/ci/.env",
            "type": "s3"
        }
    ],
    "mountPoints": [],
    "volumesFrom": [],
    "healthCheck": {
      "command": [
        "CMD-SHELL",
        "${database_healthcheck_command}"
      ],
      "interval": ${database_healthcheck_interval},
      "timeout": ${database_healthcheck_timeout},
      "retries": ${database_healthcheck_retries},
      "startPeriod": ${database_healthcheck_start_period}
    },
    "systemControls": []
}