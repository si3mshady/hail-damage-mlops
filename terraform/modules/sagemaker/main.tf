# SageMaker Model (No cost - just metadata)
resource "aws_sagemaker_model" "hail_damage_model" {
  count = var.create_endpoint ? 1 : 0
  
  name             = "${var.name_prefix}-model"
  execution_role_arn = var.sagemaker_role_arn
  
  primary_container {
    image          = "${var.ecr_inference_repo_url}:latest"
    model_data_url = "s3://${var.s3_bucket_name}/models/model.tar.gz"
  }
  
  vpc_config {
    security_group_ids = [var.security_group_id]
    subnets           = var.subnet_ids
  }
}

# SageMaker Endpoint Configuration (No cost - just configuration)
resource "aws_sagemaker_endpoint_configuration" "hail_damage_config" {
  count = var.create_endpoint ? 1 : 0
  
  name = "${var.name_prefix}-endpoint-config"
  
  production_variants {
    variant_name           = "AllTraffic"
    model_name            = aws_sagemaker_model.hail_damage_model[0].name
    initial_instance_count = 1
    instance_type         = var.inference_instance_type
    initial_variant_weight = 1
  }
}

# SageMaker Endpoint (EXPENSIVE - ~$40-60/month)
resource "aws_sagemaker_endpoint" "hail_damage_endpoint" {
  count = var.create_endpoint ? 1 : 0
  
  name                 = "${var.name_prefix}-endpoint"
  endpoint_config_name = aws_sagemaker_endpoint_configuration.hail_damage_config[0].name
}

# Auto Scaling (only if endpoint exists)
resource "aws_appautoscaling_target" "sagemaker_target" {
  count = var.create_endpoint ? 1 : 0
  
  max_capacity       = var.auto_scaling_max_capacity
  min_capacity       = var.auto_scaling_min_capacity
  resource_id        = "endpoint/${aws_sagemaker_endpoint.hail_damage_endpoint[0].name}/variant/AllTraffic"
  scalable_dimension = "sagemaker:variant:DesiredInstanceCount"
  service_namespace  = "sagemaker"
}

resource "aws_appautoscaling_policy" "sagemaker_policy" {
  count = var.create_endpoint ? 1 : 0
  
  name               = "${var.name_prefix}-scaling-policy"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.sagemaker_target[0].resource_id
  scalable_dimension = aws_appautoscaling_target.sagemaker_target[0].scalable_dimension
  service_namespace  = aws_appautoscaling_target.sagemaker_target[0].service_namespace
  
  target_tracking_scaling_policy_configuration {
    target_value = 70.0
    
    predefined_metric_specification {
      predefined_metric_type = "SageMakerVariantInvocationsPerInstance"
    }
    
    scale_in_cooldown  = 300
    scale_out_cooldown = 300
  }
}

