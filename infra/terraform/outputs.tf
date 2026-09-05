output "application_url" {
  description = "Public Streamlit URL."
  value       = "http://${aws_instance.app.public_ip}:8501"
}

output "instance_id" {
  value = aws_instance.app.id
}

output "public_ip" {
  value = aws_instance.app.public_ip
}

output "artifact_bucket" {
  value = aws_s3_bucket.artifacts.bucket
}

output "github_deploy_role_arn" {
  value = aws_iam_role.github_deploy.arn
}

output "monthly_budget_usd" {
  value = var.monthly_budget_usd
}

