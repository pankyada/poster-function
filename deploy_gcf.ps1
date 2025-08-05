# Deploy BuyersMatch Marketing Post Generator to Google Cloud Functions

Write-Host "🚀 Deploying BuyersMatch Marketing Post Generator to Google Cloud Functions" -ForegroundColor Green
Write-Host ""

# Check if gcloud is installed
try {
    gcloud --version | Out-Null
} catch {
    Write-Host "❌ Google Cloud SDK (gcloud) is not installed" -ForegroundColor Red
    Write-Host "Please install it from: https://cloud.google.com/sdk/docs/install" -ForegroundColor Yellow
    exit 1
}

# Set variables
$FUNCTION_NAME = "buyersmatch-post-generator"
$REGION = "us-central1"  # Change this to your preferred region
$MEMORY = "1024MB"       # Increased memory for image processing
$TIMEOUT = "540s"        # 9 minutes timeout for complex image processing

Write-Host "📋 Deployment Configuration:" -ForegroundColor Cyan
Write-Host "   Function Name: $FUNCTION_NAME" -ForegroundColor White
Write-Host "   Region: $REGION" -ForegroundColor White
Write-Host "   Memory: $MEMORY" -ForegroundColor White
Write-Host "   Timeout: $TIMEOUT" -ForegroundColor White
Write-Host ""

Write-Host "☁️  Deploying to Google Cloud Functions..." -ForegroundColor Blue

# Deploy the function
$deployResult = gcloud functions deploy $FUNCTION_NAME `
    --gen2 `
    --runtime=python311 `
    --region=$REGION `
    --source=. `
    --entry-point=generate_marketing_post `
    --memory=$MEMORY `
    --timeout=$TIMEOUT `
    --trigger=http `
    --allow-unauthenticated

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Deployment successful!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🌐 Function URL:" -ForegroundColor Cyan
    $functionUrl = gcloud functions describe $FUNCTION_NAME --region=$REGION --format="value(serviceConfig.uri)"
    Write-Host $functionUrl -ForegroundColor White
    Write-Host ""
    Write-Host "🧪 Test your function:" -ForegroundColor Yellow
    Write-Host "curl -X POST `"$functionUrl`" \" -ForegroundColor White
    Write-Host "  -F `"main_image=@.test/addendum-001.jpg`" \" -ForegroundColor White
    Write-Host "  -F `"date=15 DEC 2024`" \" -ForegroundColor White
    Write-Host "  -F `"yield_rate=7.94%`" \" -ForegroundColor White
    Write-Host "  -F `"purchase_price=$850,000`" \" -ForegroundColor White
    Write-Host "  -F `"current_valuation=$920,000`" \" -ForegroundColor White
    Write-Host "  --output generated_post.png" -ForegroundColor White
    Write-Host ""
    Write-Host "📊 Monitor function:" -ForegroundColor Cyan
    Write-Host "gcloud functions logs read $FUNCTION_NAME --region=$REGION" -ForegroundColor White
    Write-Host ""
    Write-Host "🔧 Update function:" -ForegroundColor Cyan
    Write-Host "gcloud functions deploy $FUNCTION_NAME --region=$REGION --source=." -ForegroundColor White
} else {
    Write-Host "❌ Deployment failed!" -ForegroundColor Red
    exit 1
}

# Restore original files
Write-Host "🔄 Restoring original files..." -ForegroundColor Yellow
try {
    git checkout template_generator.py requirements.txt 2>$null
} catch {
    # Ignore git errors
}

Write-Host "🎉 Google Cloud Function deployment complete!" -ForegroundColor Green
