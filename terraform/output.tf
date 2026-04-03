# =============================================================
# FILE: output.tf
# PROJECT: ChariotAI — AI Powered Student Support Chatbot
# PURPOSE: Exposes key resource values after terraform apply.
#          Sensitive outputs (API keys, tokens) are masked in
#          terminal but accessible via: terraform output -json
#
# OUTPUTS:
#   frontend_url         — Azure SWA default URL
#   resource_group       — Resource group name
#   swa_deployment_token — [SENSITIVE] GitHub Actions deploy token
# =============================================================

output "frontend_url" {
  value       = azurerm_static_web_app.frontend.default_host_name
  description = "ChariotAI React frontend (Azure SWA)"
}

output "resource_group" {
  value       = azurerm_resource_group.main.name
  description = "Azure Resource Group"
}

output "swa_deployment_token" {
  value       = azurerm_static_web_app.frontend.api_key
  description = "Token for GitHub Actions SWA deployment"
  sensitive   = true
}

output "custom_domain_validation_token" {
  value       = azurerm_static_web_app_custom_domain.chariotai.validation_token
  description = "TXT Record value to add to your DNS for chariotai.org verification"
  sensitive   = true
}

output "backend_url" {
  value       = "https://${azurerm_linux_web_app.backend.default_hostname}"
  description = "ChariotAI Python FastAPI Backend Live URL"
}

output "azure_openai_endpoint" {
  value = azurerm_cognitive_account.openai.endpoint
}

output "azure_search_endpoint" {
  value = "https://${azurerm_search_service.search.name}.search.windows.net"
}

output "azure_search_admin_key" {
  value     = azurerm_search_service.search.primary_key
  sensitive = true
}
