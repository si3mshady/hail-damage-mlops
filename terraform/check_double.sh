#!/bin/bash
# diagnosis.sh - Complete Terraform resource analysis

echo "🔍 COMPLETE TERRAFORM RESOURCE DIAGNOSIS"
echo "========================================"

echo ""
echo "📁 PROJECT STRUCTURE:"
find . -name "*.tf" -type f | head -20

echo ""
echo "🎯 SAGEMAKER RESOURCES LOCATIONS:"
echo "main.tf:"
grep -n "aws_sagemaker" terraform/main.tf 2>/dev/null || echo "  No SageMaker resources in main.tf"

echo ""
echo "modules:"
find terraform/modules -name "*.tf" -exec grep -l "aws_sagemaker" {} \; 2>/dev/null | while read file; do
    echo "  $file:"
    grep -n "aws_sagemaker" "$file"
done

echo ""
echo "🔐 IAM ROLE LOCATIONS:"
echo "main.tf:"
grep -n "sagemaker.*role\|sagemaker_execution_role" terraform/main.tf 2>/dev/null || echo "  No IAM roles in main.tf"

echo ""
echo "modules:"
find terraform/modules -name "*.tf" -exec grep -l "sagemaker.*role\|sagemaker_execution_role" {} \; 2>/dev/null | while read file; do
    echo "  $file:"
    grep -n "sagemaker.*role\|sagemaker_execution_role" "$file"
done

echo ""
echo "🌐 VPC ENDPOINT LOCATIONS:"
echo "main.tf:"
grep -n "aws_vpc_endpoint" terraform/main.tf 2>/dev/null || echo "  No VPC endpoints in main.tf"

echo ""
echo "modules:"
find terraform/modules -name "*.tf" -exec grep -l "aws_vpc_endpoint" {} \; 2>/dev/null | while read file; do
    echo "  $file:"
    grep -n "aws_vpc_endpoint" "$file"
done

echo ""
echo "☁️  CURRENT AWS RESOURCES (that might conflict):"
echo "IAM Roles with 'hail-damage' or 'sagemaker':"
aws iam list-roles --query "Roles[?contains(RoleName, 'hail-damage') || contains(RoleName, 'sagemaker')].RoleName" --output text 2>/dev/null || echo "  Error checking AWS roles"

echo ""
echo "VPC Endpoints with S3:"
aws ec2 describe-vpc-endpoints --filters "Name=service-name,Values=com.amazonaws.us-east-2.s3" --query "VpcEndpoints[].VpcEndpointId" --output text --region us-east-2 2>/dev/null || echo "  Error checking VPC endpoints"

echo ""
echo "ECR Repositories with 'hail-damage':"
aws ecr describe-repositories --query "repositories[?contains(repositoryName, 'hail-damage')].repositoryName" --output text --region us-east-2 2>/dev/null || echo "  Error checking ECR repos"

echo ""
echo "🏗️ TERRAFORM STATE INFO:"
echo "Current working directory: $(pwd)"
echo "Terraform state exists: $([ -f terraform/terraform.tfstate ] && echo "YES" || echo "NO")"
echo "Terraform lock exists: $([ -f terraform/.terraform.lock.hcl ] && echo "YES" || echo "NO")"

echo ""
echo "📝 CURRENT TERRAFORM RANDOM SUFFIX:"
grep -A2 -B2 "random_string" terraform/main.tf 2>/dev/null || echo "  No random string in main.tf"

echo ""
echo "✅ DIAGNOSIS COMPLETE - Send this output for analysis"

