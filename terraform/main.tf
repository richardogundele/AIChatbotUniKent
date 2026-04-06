terraform {
  required_version = ">= 1.5.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.100"
    }
    github = {
      source  = "integrations/github"
      version = "~> 6.0"
    }
  }
}

provider "azurerm" {
  subscription_id = var.subscription_id
  tenant_id       = var.tenant_id
  features {}
}

provider "github" {
  # Expects GITHUB_TOKEN environment variable
  owner = split("/", var.github_repo)[0]
}

# =============================================================
# GITHUB SECRETS: AUTOMATED CI/CD CONNECTIVITY
# =============================================================

resource "github_actions_secret" "swa_token" {
  repository      = split("/", var.github_repo)[1]
  secret_name     = "AZURE_STATIC_WEB_APPS_API_TOKEN"
  plaintext_value = azurerm_static_web_app.frontend.api_key
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
# COGNITIVE SERVICES: Azure OpenAI
# =============================================================

resource "azurerm_cognitive_account" "openai" {
  name                = "${var.app_name}-openai-${var.environment}"
  location            = "uksouth" # Keep model data in UK for GDPR
  resource_group_name = azurerm_resource_group.main.name
  kind                = "OpenAI"
  sku_name            = var.openai_sku
  tags                = azurerm_resource_group.main.tags
}

resource "azurerm_cognitive_deployment" "gpt" {
  name                 = "gpt-4o-mini"
  cognitive_account_id = azurerm_cognitive_account.openai.id
  model {
    format  = "OpenAI"
    name    = "gpt-4o-mini"
    version = "2024-07-18" # Latest Mini
  }
  sku {
    name     = "Standard"
    capacity = 10 
  }
}

resource "azurerm_cognitive_deployment" "embedding" {
  name                 = "text-embedding-ada-002"
  cognitive_account_id = azurerm_cognitive_account.openai.id
  model {
    format  = "OpenAI"
    name    = "text-embedding-ada-002"
    version = "2"
  }
  sku {
    name     = "Standard"
    capacity = 20
  }
}

# =============================================================
# SEARCH: Azure AI Search (Vector Database)
# =============================================================

resource "azurerm_search_service" "search" {
  name                = "${var.app_name}-search-${var.environment}"
  resource_group_name = azurerm_resource_group.main.name
  location            = "uksouth"
  sku                 = var.search_sku
  # Enabled to allow frontend to speak to search if needed (though we use backend as proxy)
  local_authentication_enabled = true 
  tags                = azurerm_resource_group.main.tags
}

# =============================================================
# BACKEND: Azure App Service (Python FastAPI)
# =============================================================

resource "azurerm_service_plan" "backend" {
  name                = "${var.app_name}-asp-${var.environment}"
  resource_group_name = azurerm_resource_group.main.name
  location            = "westeurope" # Bypassing UK South capacity quotas
  os_type             = "Linux"
  sku_name            = var.app_service_sku # Basic Tier (B1)
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
    always_on        = true # B1 supports always_on, preventing cold starts
    app_command_line = "python main.py"
  }

  app_settings = {
    "WEBSITES_PORT"                  = "8000"
    "CORS_ALLOWED_ORIGINS"           = "https://${azurerm_static_web_app.frontend.default_host_name},http://localhost:5173"
    "SCM_DO_BUILD_DURING_DEPLOYMENT" = "1"
    
    # Auto-linking our new resources
    "AZURE_OPENAI_KEY"               = azurerm_cognitive_account.openai.primary_access_key
    "AZURE_OPENAI_ENDPOINT"          = azurerm_cognitive_account.openai.endpoint
    "AZURE_OPENAI_API_VERSION"       = "2024-02-15-preview"
    "AZURE_GPT_DEPLOYMENT"           = azurerm_cognitive_deployment.gpt.name
    "AZURE_EMBEDDING_DEPLOYMENT"     = azurerm_cognitive_deployment.embedding.name
    "AZURE_SEARCH_KEY"               = azurerm_search_service.search.primary_key
    "AZURE_SEARCH_ENDPOINT"          = "https://${azurerm_search_service.search.name}.search.windows.net"
    "AZURE_SEARCH_INDEX"             = "kent-student-index"
    
    # Telegram Crisis Support
    "TELEGRAM_BOT_TOKEN"             = var.telegram_bot_token
    "TELEGRAM_CHAT_ID"               = var.telegram_chat_id
  }

  tags = azurerm_resource_group.main.tags
}
