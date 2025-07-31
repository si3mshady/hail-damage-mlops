terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.1"
    }
  }
}

provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Project     = "hail-damage-detection"
      Environment = "dev"
      Owner       = "ml-engineer"
    }
  }
}

# Variables
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "hail-damage"
}

# Random suffix for unique naming
resource "random_string" "suffix" {
  length  = 6
  special = false
  upper   = false
}

locals {
  name_prefix = "${var.project_name}-${random_string.suffix.result}"
}

# Data sources
data "aws_caller_identity" "current" {}
data "aws_availability_zones" "available" {
  state = "available"
}

# VPC Module
module "vpc" {
  source = "./modules/vpc"
  
  name_prefix = local.name_prefix
  vpc_cidr    = "10.0.0.0/16"
}

# Security Module
module "security" {
  source = "./modules/security"
  
  name_prefix = local.name_prefix
  vpc_id      = module.vpc.vpc_id
}

# S3 Module
module "s3" {
  source = "./modules/s3"
  
  name_prefix = local.name_prefix
}

# ECR Module
module "ecr" {
  source = "./modules/ecr"
  
  name_prefix = local.name_prefix
}

# IAM Module
module "iam" {
  source = "./modules/iam"
  
  name_prefix = local.name_prefix
  s3_bucket_arn = module.s3.s3_bucket_arn
}

# VPC Endpoint for S3 (saves data transfer costs)
resource "aws_vpc_endpoint" "s3" {
  vpc_id       = module.vpc.vpc_id
  service_name = "com.amazonaws.${var.aws_region}.s3"

  route_table_ids = [module.vpc.route_table_id]

  tags = {
    Name = "${local.name_prefix}-s3-endpoint"
  }
}

# SageMaker Resources (COMMENTED OUT - THESE COST MONEY!)
# UNCOMMENT THESE WHEN READY TO DEPLOY MODEL

# SageMaker Model (No cost - just metadata)
 resource "aws_sagemaker_model" "hail_damage_model" {
   name             = "${local.name_prefix}-model"
   execution_role_arn = module.iam.sagemaker_execution_role_arn

   primary_container {
     image          = "${module.ecr.ecr_inference_repository_url}:latest"
     model_data_url = "s3://${module.s3.s3_bucket_name}/models/model.tar.gz"
   }

   vpc_config {
     security_group_ids = [module.security.sagemaker_security_group_id]
     subnets           = module.vpc.public_subnet_ids
   }
 }

# SageMaker Endpoint Configuration (No cost - just configuration)
 resource "aws_sagemaker_endpoint_configuration" "hail_damage_config" {
   name = "${local.name_prefix}-endpoint-config"

   production_variants {
     variant_name           = "AllTraffic"
     model_name            = aws_sagemaker_model.hail_damage_model.name
     initial_instance_count = 1
     instance_type         = "ml.t3.medium"  # Cheapest option
     initial_variant_weight = 1
   }
 }

# SageMaker Endpoint (COSTS $$ - ~$40-60/month running 24/7)
 resource "aws_sagemaker_endpoint" "hail_damage_endpoint" {
   name                 = "${local.name_prefix}-endpoint"
   endpoint_config_name = aws_sagemaker_endpoint_configuration.hail_damage_config.name
 }

# Outputs
output "vpc_id" {
  description = "VPC ID"
  value       = module.vpc.vpc_id
}

output "subnet_ids" {
  description = "Public subnet IDs"
  value       = module.vpc.public_subnet_ids
}

output "s3_bucket_name" {
  description = "S3 bucket name"
  value       = module.s3.s3_bucket_name
}

output "ecr_training_repository_url" {
  description = "ECR training repository URL"
  value       = module.ecr.ecr_training_repository_url
}

output "ecr_inference_repository_url" {
  description = "ECR inference repository URL"
  value       = module.ecr.ecr_inference_repository_url
}

output "sagemaker_execution_role_arn" {
  description = "SageMaker execution role ARN"
  value       = module.iam.sagemaker_execution_role_arn
}

output "aws_region" {
  description = "AWS region"
  value       = var.aws_region
}

output "project_name" {
  description = "Project name with suffix"
  value       = local.name_prefix
}

# output "sagemaker_endpoint_name" {
#   description = "SageMaker endpoint name"
#   value       = aws_sagemaker_endpoint.hail_damage_endpoint.name
# }

