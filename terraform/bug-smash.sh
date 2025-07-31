#!/bin/bash
echo "🔍 LOCATING IAM ROLE CONFLICT SOURCE"
echo "===================================="

ROLE_NAME="hail-damage-uoo0y7-sagemaker-role"

echo "📍 ERROR LOCATION: modules/iam/main.tf line 2"
echo ""

echo "🔍 CHECKING modules/iam/main.tf:"
echo "Line 2 and surrounding context:"
sed -n '1,10p' modules/iam/main.tf | nl
echo ""

echo "🔍 ALL IAM ROLE DEFINITIONS IN PROJECT:"
find . -name "*.tf" -exec grep -l "aws_iam_role" {} \; | while read file; do
    echo "File: $file"
    grep -n "aws_iam_role" "$file" | head -5
    echo ""
done

echo "☁️ CHECKING IF ROLE EXISTS IN AWS:"
aws iam get-role --role-name "$ROLE_NAME" 2>/dev/null && echo "✅ Role EXISTS in AWS" || echo "❌ Role NOT FOUND in AWS"

echo ""
echo "📋 ALL ROLES WITH 'hail-damage' IN AWS:"
aws iam list-roles --query "Roles[?contains(RoleName, 'hail-damage')].[RoleName,CreateDate]" --output table

echo ""
echo "🗂️ TERRAFORM STATE CHECK:"
echo "Does Terraform state know about this role?"
grep -q "$ROLE_NAME" terraform.tfstate 2>/dev/null && echo "✅ Role IN Terraform state" || echo "❌ Role NOT in Terraform state"

echo ""
echo "🔧 TERRAFORM MODULE USAGE:"
echo "How many places reference the IAM module?"
grep -r "module\.iam" . --include="*.tf" | wc -l
echo ""
grep -r "module\.iam" . --include="*.tf"

echo ""
echo "🎯 ROOT CAUSE ANALYSIS:"
echo "1. Role exists in AWS: $(aws iam get-role --role-name "$ROLE_NAME" >/dev/null 2>&1 && echo "YES" || echo "NO")"
echo "2. Role in Terraform state: $(grep -q "$ROLE_NAME" terraform.tfstate 2>/dev/null && echo "YES" || echo "NO")"
echo "3. Terraform trying to create: YES (from error message)"
echo ""
echo "💡 LIKELY CAUSE:"
if aws iam get-role --role-name "$ROLE_NAME" >/dev/null 2>&1; then
    if ! grep -q "$ROLE_NAME" terraform.tfstate 2>/dev/null; then
        echo "Role exists in AWS but NOT in Terraform state - STATE DRIFT!"
    else
        echo "Role exists in both AWS and Terraform state - UNKNOWN ISSUE"
    fi
else
    echo "Role doesn't exist in AWS - TERRAFORM STATE ISSUE"
fi

