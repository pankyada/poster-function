#!/bin/bash

# Create and manage API keys for BuyersMatch Marketing Post Generator
# This script creates API keys for API Gateway access

set -e

# Configuration
PROJECT_ID="buyersagent-3f710"
GATEWAY_HOST="buyersmatch-gateway-13ons83o.uc.gateway.dev"

echo "🔐 Creating API Keys for BuyersMatch Marketing API"
echo ""

gcloud config set project $PROJECT_ID

# Function to create an API key
create_api_key() {
    local display_name=$1
    
    echo "🔑 Creating API key: $display_name"
    
    # Create the API key and get the key string directly
    local key_string=$(gcloud services api-keys create \
        --display-name="$display_name" \
        --format="value(keyString)")
    
    if [ $? -eq 0 ]; then
        echo "✅ Created API key: $display_name"
        echo "🔑 Key: $key_string"
        echo ""
        return 0
    else
        echo "❌ Failed to create API key: $display_name"
        echo ""
        return 1
    fi
}

# Create different API keys for different use cases
echo "Creating API keys..."
echo ""

# Admin key - full access
create_api_key "BuyersMatch Admin API Key"

# Client key - limited access  
create_api_key "BuyersMatch Client API Key"

# Development key
create_api_key "BuyersMatch Development API Key"

echo "🎉 API Keys created successfully!"
echo ""
echo "💡 Usage example:"
echo "   curl -H \"X-API-Key: YOUR_KEY_HERE\" https://$GATEWAY_HOST/v1/health"
echo ""
echo "🔧 Manage keys:"
echo "   https://console.cloud.google.com/apis/credentials?project=$PROJECT_ID"
echo ""
echo "⚠️  Store these keys securely and never commit them to version control!"
