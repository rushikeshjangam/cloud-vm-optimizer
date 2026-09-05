variable "aws_region" {
  description = "AWS region for the complete demo stack."
  type        = string
  default     = "ap-south-1"
}

variable "project_name" {
  description = "Stable name used for resources and tags."
  type        = string
  default     = "cloud-vm-optimizer"
}

variable "environment" {
  description = "Deployment environment tag."
  type        = string
  default     = "demo"
}

variable "owner_tag" {
  description = "Owner tag required by the application's AWS safety rules."
  type        = string
  default     = "college-demo"
}

variable "instance_type" {
  description = "Small burstable host; t3.small gives the scientific Python stack 2 GiB RAM."
  type        = string
  default     = "t3.small"
}

variable "root_volume_gb" {
  description = "Encrypted gp3 root volume size."
  type        = number
  default     = 12
}

variable "allowed_app_cidr" {
  description = "CIDR allowed to open the Streamlit demo on port 8501."
  type        = string
  default     = "0.0.0.0/0"
}

variable "github_owner" {
  description = "GitHub account or organization that owns the repository."
  type        = string
}

variable "github_repository" {
  description = "GitHub repository name used in the OIDC trust policy."
  type        = string
  default     = "cloud-vm-optimizer"
}

variable "monthly_budget_usd" {
  description = "Monthly AWS cost budget in USD."
  type        = number
  default     = 15
}

variable "budget_alert_email" {
  description = "Optional email for the 80% forecast/actual budget alerts. Keep it in terraform.tfvars, not Git."
  type        = string
  default     = ""
  sensitive   = true
}

