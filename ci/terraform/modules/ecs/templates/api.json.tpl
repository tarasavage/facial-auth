{
    "name": "${api_container_name}",
    "image": "${api_image_uri}",
    "cpu": 0,
    "portMappings": [
        {
        "name": "${api_container_name}",
        "containerPort": ${api_port},
        "hostPort": ${api_port},
        "protocol": "tcp",
        "appProtocol": "http"
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
    "dependsOn": [
        {
        "containerName": "${database_container_name}",
        "condition": "HEALTHY"
        }
    ],
    "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
        "awslogs-group": "${api_log_group}",
        "mode": "non-blocking",
        "awslogs-create-group": "true",
        "max-buffer-size": "25m",
        "awslogs-region": "${aws_region}",
        "awslogs-stream-prefix": "ecs"
        }
    },
    "systemControls": []
}
