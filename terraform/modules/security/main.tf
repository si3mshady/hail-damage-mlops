data "aws_caller_identity" "current" {}

# SageMaker Security Group
resource "aws_security_group" "sagemaker" {
  name_prefix = "${var.name_prefix}-sagemaker"
  vpc_id      = var.vpc_id
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = {
    Name = "${var.name_prefix}-sagemaker-sg"
  }
}


# SNS Topic for alerts
resource "aws_sns_topic" "alerts" {
  name         = "${var.name_prefix}-alerts"
  display_name = "ML Pipeline Alerts"
}

