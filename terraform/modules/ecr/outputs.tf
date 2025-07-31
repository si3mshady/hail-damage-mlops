output "ecr_training_repository_url" {
  description = "ECR training repository URL"
  value       = aws_ecr_repository.training.repository_url
}

output "ecr_inference_repository_url" {
  description = "ECR inference repository URL"
  value       = aws_ecr_repository.inference.repository_url
}

output "ecr_training_repository_name" {
  description = "ECR training repository name"
  value       = aws_ecr_repository.training.name
}

output "ecr_inference_repository_name" {
  description = "ECR inference repository name"
  value       = aws_ecr_repository.inference.name
}

