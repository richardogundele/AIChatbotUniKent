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
