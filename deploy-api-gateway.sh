#!/bin/bash

# Deploy API Gateway for BuyersMatch Marketing Post Generator
# This script creates and configures the API Gateway

set -e

# Configuration
PROJECT_ID="buyersagent-3f710"
API_ID="buyersmatch-marketing-api"
API_CONFIG_ID="buyersmatch-config-v1"
GATEWAY_ID="buyersmatch-gateway"
REGION="us-central1"
SPEC_FILE="api-spec.yaml"

echo "🚀 Setting up API Gateway for BuyersMatch Marketing Post Generator"
echo ""

# Set the project
gcloud config set project $PROJECT_ID

echo "📋 Configuration:"
echo "   Project ID: $PROJECT_ID"
echo "   API ID: $API_ID"
echo "   Config ID: $API_CONFIG_ID"
echo "   Gateway ID: $GATEWAY_ID"
echo "   Region: $REGION"
echo ""

# Step 1: Create the API
echo "🔧 Step 1: Creating API..."
gcloud api-gateway apis create $API_ID \
    --project=$PROJECT_ID \
    --display-name="BuyersMatch Marketing Post Generator API" || echo "API already exists"

# Step 2: Create API Config
echo "🔧 Step 2: Creating API Configuration..."
gcloud api-gateway api-configs create $API_CONFIG_ID \
    --api=$API_ID \
    --openapi-spec=$SPEC_FILE \
    --project=$PROJECT_ID \
    --display-name="BuyersMatch API Config v1"

# Step 3: Create Gateway
echo "🔧 Step 3: Creating API Gateway..."
gcloud api-gateway gateways create $GATEWAY_ID \
    --api=$API_ID \
    --api-config=$API_CONFIG_ID \
    --location=$REGION \
    --project=$PROJECT_ID \
    --display-name="BuyersMatch Marketing Gateway"

# Wait for gateway to be ready
echo "⏳ Waiting for gateway to be ready..."
sleep 30

# Get gateway URL
GATEWAY_URL=$(gcloud api-gateway gateways describe $GATEWAY_ID \
    --location=$REGION \
    --project=$PROJECT_ID \
    --format="value(defaultHostname)")

if [ -n "$GATEWAY_URL" ]; then
    echo ""
    echo "✅ API Gateway deployed successfully!"
    echo ""
    echo "🌐 Gateway URL: https://$GATEWAY_URL"
    echo ""
    echo "📚 API Endpoints:"
    echo "   POST https://$GATEWAY_URL/v1/generate - Generate marketing post"
    echo "   GET  https://$GATEWAY_URL/v1/health   - Health check"
    echo ""
    echo "🔑 Authentication:"
    echo "   You'll need to create API keys to access the protected endpoints."
    echo "   Run the create-api-keys.sh script to generate them."
    echo ""
    echo "🧪 Test health endpoint:"
    echo "   curl https://$GATEWAY_URL/v1/health"
    echo ""
    echo "📊 Monitor API:"
    echo "   https://console.cloud.google.com/api-gateway/api/$API_ID/overview?project=$PROJECT_ID"
else
    echo "❌ Failed to get gateway URL"
    exit 1
fi

echo ""
echo "🎉 API Gateway setup complete!"
