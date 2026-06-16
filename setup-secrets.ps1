# Setup GitHub Actions secrets for eCommerce GEO Auditor

Write-Host "Setting up GitHub Actions secrets..." -ForegroundColor Cyan
Write-Host ""
Write-Host "You'll be prompted to paste each API key."
Write-Host ""

# Required secrets
Write-Host "OpenAI API Key:" -ForegroundColor Yellow
gh secret set OPENAI_API_KEY

Write-Host "Anthropic API Key:" -ForegroundColor Yellow
gh secret set ANTHROPIC_API_KEY

Write-Host "Google API Key:" -ForegroundColor Yellow
gh secret set GOOGLE_API_KEY

# Optional secrets
$addPerplexity = Read-Host "Add Perplexity API key? (y/n)"
if ($addPerplexity -eq 'y') {
    Write-Host "Perplexity API Key:" -ForegroundColor Yellow
    gh secret set PERPLEXITY_API_KEY
}

$addAzure = Read-Host "Add Azure OpenAI credentials? (y/n)"
if ($addAzure -eq 'y') {
    Write-Host "Azure OpenAI API Key:" -ForegroundColor Yellow
    gh secret set AZURE_OPENAI_API_KEY
    Write-Host "Azure OpenAI Endpoint:" -ForegroundColor Yellow
    gh secret set AZURE_OPENAI_ENDPOINT
}

$addSerpApi = Read-Host "Add SerpAPI key? (y/n)"
if ($addSerpApi -eq 'y') {
    Write-Host "SerpAPI Key:" -ForegroundColor Yellow
    gh secret set SERPAPI_KEY
}

Write-Host ""
Write-Host "Secrets configured!" -ForegroundColor Green
Write-Host ""
Write-Host "View secrets: gh secret list"
Write-Host ""
