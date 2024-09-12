# We want to use AWS
provider "aws" {
    region = var.AWS_REGION
    access_key = var.AWS_ACCESS_KEY
    secret_key = var.AWS_PRIVATE_ACCESS_KEY
}

# Existing resources

## The ECR image for the emails script
data "aws_ecr_image" "c13-oliver-t3-image" {
  repository_name = "c13-oliver-t3"
  image_tag       = "latest"
}

## The cluster we will run tasks on
data "aws_ecs_cluster" "c13-cluster" {
    cluster_name = "c13-ecs-cluster"
}

# Task definition

resource "aws_ecs_task_definition" "c13-oliver-t3-task-definition" {
    family = "c13-oliver-t3-task-definition"
    container_definitions = jsonencode([
        {
            name      = "c13-oliver-t3-task-definition"
            image     = data.aws_ecr_image.c13-oliver-t3-image.image_uri
            essential = true
            memory = 1024
            environment = [
                {
                    name = "AWS_ACCESS_KEY",
                    value = var.AWS_ACCESS_KEY
                },
                {
                    name = "AWS_PRIVATE_ACCESS_KEY",
                    value = var.AWS_PRIVATE_ACCESS_KEY
                },
                {
                    name = "BUCKET_NAME",
                    value = var.BUCKET_NAME
                },
                {
                    name = "DB_HOST",
                    value = var.DB_HOST
                },
                {
                    name = "DB_NAME",
                    value = var.DB_NAME
                },
                {
                    name = "DB_PORT",
                    value = var.DB_PORT
                },
                {
                    name = "DB_USER",
                    value = var.DB_USER
                },
                {
                    name = "DB_PASSWORD",
                    value = var.DB_PASSWORD
                },
                {
                    name = "DB_SCHEMA",
                    value = var.DB_SCHEMA
                },
                {
                    name = "DATA_FILEPATH",
                    value = var.DATA_FILEPATH
                },
                {
                    name = "MERGED_FILE",
                    value = var.MERGED_FILE
                },
                {
                    name = "CLEAN_FILE",
                    value = var.CLEAN_FILE
                },
                {
                    name = "INVALID_TOTALS",
                    value = var.INVALID_TOTALS
                }
            ]
            logConfiguration = {
                logDriver = "awslogs"
                "options": {
                    awslogs-group = "/ecs/c13-oliver-t3-task-definition"
                    awslogs-stream-prefix = "ecs"
                    awslogs-create-group = "true"
                    awslogs-stream-prefix = "ecs"
                    awslogs-region = "eu-west-2"
                }
            }
        }])
    requires_compatibilities = ["FARGATE"]
    network_mode             = "awsvpc"
    cpu                      = "256"
    memory                   = "1024"
    execution_role_arn = "arn:aws:iam::129033205317:role/ecsTaskExecutionRole"
}


data "aws_iam_policy_document" "assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "c13-oliver-exec-role-lambda" {
  name               = "c13-oliver-exec-role-lambda"
  assume_role_policy = data.aws_iam_policy_document.assume_role.json
}

data "aws_ecr_image" "c13-oliver-t3-report-app" {
  repository_name = "c13-oliver-t3"
  image_tag       = "latest"
}

resource "aws_lambda_function" "test_lambda" {
  # If the file is not in the current working directory you will need to include a
  # path.module in the filename.
  function_name = "c13-oliver-report-lambda-function"
  role          = aws_iam_role.c13-oliver-exec-role-lambda.arn
  image_uri = data.aws_ecr_image.c13-oliver-t3-report-app.image_uri
  package_type = "Image"

  environment {
    variables = {
      DB_HOST = var.DB_HOST
      DB_NAME = var.DB_NAME
      DB_PORT = var.DB_PORT
      DB_USER = var.DB_USER
      DB_PASSWORD = var.DB_PASSWORD
    }
  }
}
