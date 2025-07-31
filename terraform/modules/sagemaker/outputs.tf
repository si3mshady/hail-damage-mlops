output "model_name" {
  description = "SageMaker model name"
  value       = var.create_endpoint ? aws_sagemaker_model.hail_damage_model[0].name : "Not created"
}

output "endpoint_name" {
  description = "SageMaker endpoint name"
  value       = var.create_endpoint ? aws_sagemaker_endpoint.hail_damage_endpoint[0].name : "Not created"
}

output "endpoint_config_name" {
  description = "Endpoint configuration name"
  value       = var.create_endpoint ? aws_sagemaker_endpoint_configuration.hail_damage_config[0].name : "Not created"
}

