terraform {
  required_version = ">= 1.5.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.100"
    }
  }
}

provider "azurerm" {
  subscription_id = var.subscription_id
  tenant_id       = var.tenant_id
  features {}
}

resource "azurerm_resource_group" "main" {
  name     = var.resource_group_name
  location = var.location
  tags = {
    project     = "ChariotAI"
    environment = var.environment
    managed_by  = "terraform"
    purpose     = "UoK AI Student Support Chatbot (Frontend Only)"
  }
}

resource "azurerm_static_web_app" "frontend" {
  name                = "${var.app_name}-web-${var.environment}"
  resource_group_name = azurerm_resource_group.main.name
  location            = "westeurope"
  sku_tier            = "Free"
  sku_size            = "Free"

  tags = azurerm_resource_group.main.tags
}

resource "azurerm_static_web_app_custom_domain" "chariotai" {
  static_web_app_id = azurerm_static_web_app.frontend.id
  domain_name       = var.chariotai_domain
  validation_type   = "dns-txt-token"
}

# =============================================================
# BACKEND: Azure App Service (Python FastAPI)
# =============================================================

resource "azurerm_service_plan" "backend" {
  name                = "${var.app_name}-asp-${var.environment}"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  os_type             = "Linux"
  sku_name            = var.app_service_sku # Free Tier (F1)
  tags                = azurerm_resource_group.main.tags
}

resource "azurerm_linux_web_app" "backend" {
  name                = "${var.app_name}-api-${var.environment}"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_service_plan.backend.location
  service_plan_id     = azurerm_service_plan.backend.id

  site_config {
    application_stack {
      python_version = "3.12"
    }
    always_on = false # F1 Free tier does not support always_on
  }

  app_settings = {
    "WEBSITES_PORT"                  = "8000"
    "CORS_ALLOWED_ORIGINS"           = var.cors_allowed_origins
    "SCM_DO_BUILD_DURING_DEPLOYMENT" = "1"
  }

  tags = azurerm_resource_group.main.tags
}
