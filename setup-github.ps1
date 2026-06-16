# GitHub repo setup script for eCommerce GEO Auditor

Write-Host "Creating GitHub repository..." -ForegroundColor Cyan

# Create repo and push
gh repo create ecommerce-geo-auditor `
  --public `
  --description "Python CLI tool for auditing eCommerce product pages for Generative Engine Optimization (GEO)" `
  --source=. `
  --remote=origin `
  --push

if ($LASTEXITCODE -eq 0) {
    $username = gh api user --jq .login
    Write-Host ""
    Write-Host "Repository created: https://github.com/$username/ecommerce-geo-auditor" -ForegroundColor Green
    Write-Host ""
    Write-Host "✓ Repository setup complete!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:"
    Write-Host "1. Add GitHub Actions secrets:"
    Write-Host "   .\setup-secrets.ps1"
    Write-Host ""
    Write-Host "2. Copy .env.example to .env and add your API keys"
    Write-Host ""
} else {
    Write-Host "Error creating repository" -ForegroundColor Red
}
