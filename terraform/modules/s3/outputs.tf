output "s3_bucket_name" {
  description = "S3 bucket name"
  value       = aws_s3_bucket.main.id
}

output "s3_bucket_arn" {
  description = "S3 bucket ARN"
  value       = aws_s3_bucket.main.arn
}

output "ecr_training_repository_url" {
  description = "ECR training repository URL"
  value       = aws_ecr_repository.training.repository_url
}

output "ecr_inference_repository_url" {
  description = "ECR inference repository URL"
  value       = aws_ecr_repository.inference.repository_url
}

