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
}

# Security Module
module "security" {
  source = "./modules/security"
  
  name_prefix = local.name_prefix
  vpc_id      = module.vpc.vpc_id
}

# S3 Module (NOT storage!)
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

# SageMaker Module (commented out - costs money)
# module "sagemaker" {
#   source = "./modules/sagemaker"
#   
#   name_prefix = local.name_prefix
#   vpc_id = module.vpc.vpc_id
#   subnet_ids = module.vpc.subnet_ids
#   security_group_id = module.security.sagemaker_security_group_id
#   sagemaker_role_arn = module.iam.sagemaker_execution_role_arn
#   ecr_inference_repo_url = module.ecr.ecr_inference_repository_url
#   s3_bucket_name = module.s3.s3_bucket_name
# }

# Outputs
output "vpc_id" {
  description = "VPC ID"
  value       = module.vpc.vpc_id
}

output "subnet_ids" {
  description = "Public subnet IDs"
  value       = module.vpc.subnet_ids
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

