# =============================================================
# FILE: variables.tf
# PROJECT: ChariotAI — AI Powered Student Support Chatbot
# PURPOSE: Declares all input variables for the ChariotAI
#          Terraform infrastructure. Values are set in
#          terraform.tfvars (never commit that file to Git).
#
# VARIABLES:
#   subscription_id      — Azure subscription (MICORAZON)
#   tenant_id            — Azure AD tenant
#   location             — uksouth (GDPR: data stays in UK)
#   resource_group_name  — rg-chariotai-uok
#   app_name             — chariotai (used as prefix for all resources)
#   environment          — prod
#   openai_sku           — S0 (standard Azure OpenAI)
#   search_sku           — free (Azure AI Search prototype tier)
#   app_service_sku      — B1 (~$13/mo, keeps API always warm)
#   chariotai_domain     — chariotai.org (custom SWA domain)
#   cors_allowed_origins — Allowed origins for FastAPI CORS
# =============================================================

variable "subscription_id" {
  description = "Azure Subscription ID (run: az account show --query id)"
  type        = string
}

variable "tenant_id" {
  description = "Azure Tenant ID (run: az account show --query tenantId)"
  type        = string
}

variable "location" {
  description = "Azure region — UK South for GDPR compliance"
  type        = string
  default     = "uksouth"
}

variable "resource_group_name" {
  type    = string
  default = "rg-chariotai-uok"
}

variable "app_name" {
  type    = string
  default = "chariotai"
}

variable "environment" {
  type    = string
  default = "prod"
}

variable "openai_sku" {
  description = "Azure OpenAI SKU"
  type        = string
  default     = "S0"
}

variable "search_sku" {
  description = "Azure AI Search SKU — 'free' for prototype"
  type        = string
  default     = "free"
}

variable "app_service_sku" {
  description = "App Service Plan SKU — B1 (~$13/mo)"
  type        = string
  default     = "B1"
}

variable "chariotai_domain" {
  description = "Your ChariotAI custom domain"
  type        = string
  default     = "chariotai.org"
}

variable "cors_allowed_origins" {
  description = "Allowed CORS origins for the FastAPI backend"
  type        = string
  default     = "https://chariotai.org,https://www.chariotai.org,http://localhost:5173,https://delightful-coast-0e2e5d103.6.azurestaticapps.net"
}

variable "github_repo" {
  description = "GitHub repository (owner/repo) to upload secrets to"
  type        = string
  default     = "richardogundele/AIChatbotUniKent"
}
