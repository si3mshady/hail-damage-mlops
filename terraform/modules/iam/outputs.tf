output "sagemaker_execution_role_arn" {
  description = "SageMaker execution role ARN"
  value       = aws_iam_role.sagemaker_execution_role.arn
}

output "sagemaker_execution_role_name" {
  description = "SageMaker execution role name"
  value       = aws_iam_role.sagemaker_execution_role.name
}

