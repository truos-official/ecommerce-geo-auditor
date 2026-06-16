# Authenticate GitHub CLI with token

Write-Host "GitHub CLI Authentication" -ForegroundColor Cyan
Write-Host ""
Write-Host "Create token at: https://github.com/settings/tokens/new" -ForegroundColor Yellow
Write-Host "Required scopes: repo, workflow, admin:public_key" -ForegroundColor Yellow
Write-Host ""

$token = Read-Host "Paste your GitHub token" -MaskInput

if ([string]::IsNullOrWhiteSpace($token)) {
    Write-Host "Error: No token provided" -ForegroundColor Red
    exit 1
}

Write-Host "Authenticating..." -ForegroundColor Cyan
$token | gh auth login --with-token

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✓ Authentication successful!" -ForegroundColor Green
    Write-Host ""
    gh auth status
    Write-Host ""
    Write-Host "Next step: .\setup-github.ps1" -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "Authentication failed" -ForegroundColor Red
}
