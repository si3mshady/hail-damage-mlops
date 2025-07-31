variable "name_prefix" {
  description = "Name prefix for resources"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID"
  type        = string
}

variable "subnet_ids" {
  description = "Subnet IDs"
  type        = list(string)
}

variable "security_group_id" {
  description = "Security group ID"
  type        = string
}

variable "sagemaker_role_arn" {
  description = "SageMaker execution role ARN"
  type        = string
}

variable "s3_bucket_name" {
  description = "S3 bucket name"
  type        = string
}

variable "ecr_training_repo_url" {
  description = "ECR training repository URL"
  type        = string
}

variable "ecr_inference_repo_url" {
  description = "ECR inference repository URL"
  type        = string
}

variable "training_instance_type" {
  description = "Training instance type"
  type        = string
}

variable "inference_instance_type" {
  description = "Inference instance type"
  type        = string
}

variable "enable_spot_training" {
  description = "Enable spot training"
  type        = bool
}

variable "auto_scaling_min_capacity" {
  description = "Auto scaling minimum capacity"
  type        = number
}

variable "auto_scaling_max_capacity" {
  description = "Auto scaling maximum capacity"
  type        = number
}

variable "create_endpoint" {
  description = "Create SageMaker endpoint"
  type        = bool
  default     = false
}

