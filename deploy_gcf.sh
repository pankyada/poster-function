#!/bin/bash

# Deploy BuyersMatch Marketing Post Generator to Google Cloud Functions

echo "🚀 Deploying BuyersMatch Marketing Post Generator to Google Cloud Functions"
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ Google Cloud SDK (gcloud) is not installed"
    echo "Please install it from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if user is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | head -n 1 > /dev/null; then
    echo "❌ Not authenticated with Google Cloud"
    echo "Please run: gcloud auth login"
    exit 1
fi

# Set variables
FUNCTION_NAME="buyersmatch-post-generator"
REGION="us-central1"  # Change this to your preferred region
MEMORY="1024MB"       # Increased memory for image processing
TIMEOUT="540s"        # 9 minutes timeout for complex image processing

echo "📋 Deployment Configuration:"
echo "   Function Name: $FUNCTION_NAME"
echo "   Region: $REGION"
echo "   Memory: $MEMORY"
echo "   Timeout: $TIMEOUT"
echo ""

echo "☁️  Deploying to Google Cloud Functions..."

# Deploy the function
gcloud functions deploy $FUNCTION_NAME \
    --gen2 \
    --runtime=python311 \
    --region=$REGION \
    --source=. \
    --entry-point=generate_marketing_post \
    --memory=$MEMORY \
    --timeout=$TIMEOUT \
    --trigger=http \
    --allow-unauthenticated

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Deployment successful!"
    echo ""
    echo "🌐 Function URL:"
    gcloud functions describe $FUNCTION_NAME --region=$REGION --format="value(serviceConfig.uri)"
    echo ""
    echo "🧪 Test your function:"
    FUNCTION_URL=$(gcloud functions describe $FUNCTION_NAME --region=$REGION --format="value(serviceConfig.uri)")
    echo "curl -X POST \"$FUNCTION_URL\" \\"
    echo "  -F \"main_image=@.test/addendum-001.jpg\" \\"
    echo "  -F \"date=15 DEC 2024\" \\"
    echo "  -F \"yield_rate=7.94%\" \\"
    echo "  -F \"purchase_price=\$850,000\" \\"
    echo "  -F \"current_valuation=\$920,000\" \\"
    echo "  --output generated_post.png"
    echo ""
    echo "📊 Monitor function:"
    echo "gcloud functions logs read $FUNCTION_NAME --region=$REGION"
    echo ""
    echo "🔧 Update function:"
    echo "gcloud functions deploy $FUNCTION_NAME --region=$REGION --source=."
else
    echo "❌ Deployment failed!"
    exit 1
fi

# Restore original files
echo "🔄 Restoring original files..."
git checkout template_generator.py requirements.txt 2>/dev/null || true

echo "🎉 Google Cloud Function deployment complete!"
