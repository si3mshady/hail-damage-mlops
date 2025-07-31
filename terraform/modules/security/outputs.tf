output "sagemaker_security_group_id" {
  description = "SageMaker security group ID"
  value       = aws_security_group.sagemaker.id
}

output "sagemaker_execution_role_arn" {
  description = "SageMaker execution role ARN"
  value       = aws_iam_role.sagemaker_execution_role.arn
}

output "sns_topic_arn" {
  description = "SNS topic ARN"
  value       = aws_sns_topic.alerts.arn
}

