{
    "name": "${frontend_container_name}",
    "image": "${frontend_image_uri}",
    "cpu": 0,
    "portMappings": [
        {
            "name": "${frontend_container_name}",
            "containerPort": ${frontend_port},
            "hostPort": ${frontend_port},
            "protocol": "tcp",
            "appProtocol": "http"
        }
    ],
    "essential": true,
    "environment": [],
    "environmentFiles": [
        {
            "value": "arn:aws:s3:::${aws_s3_bucket_name}/ci/frontend.env",
            "type": "s3"
        }
    ],
    "mountPoints": [],
    "volumesFrom": [],
    "ulimits": [],
    "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
            "awslogs-group": "${frontend_log_group}",
            "mode": "non-blocking",
            "awslogs-create-group": "true",
            "max-buffer-size": "25m",
            "awslogs-region": "${aws_region}",
            "awslogs-stream-prefix": "ecs"
        },
        "secretOptions": []
    },
    "systemControls": []
}