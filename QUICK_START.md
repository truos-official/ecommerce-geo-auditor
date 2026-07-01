# Quick Start Guide

## 1. Authenticate GitHub CLI

Create token: https://github.com/settings/tokens/new
- Scopes: `repo`, `workflow`, `admin:public_key`

**PowerShell:**
```powershell
$token = "YOUR_TOKEN"
$token | gh auth login --with-token
gh auth status
```

**Bash:**
```bash
echo YOUR_TOKEN | gh auth login --with-token
gh auth status
```

## 2. Create GitHub Repository

**PowerShell:**
```powershell
.\setup-github.ps1
```

**Bash:**
```bash
bash setup-github.sh
```

This creates the repo and pushes all code.

## 3. Configure API Keys

### Local Development

**PowerShell:**
```powershell
Copy-Item .env.example .env
notepad .env
```

**Bash:**
```bash
cp .env.example .env
# Edit .env with your API keys
```

### GitHub Actions (CI/CD)

**PowerShell:**
```powershell
.\setup-secrets.ps1
```

**Bash:**
```bash
bash setup-secrets.sh
```

Or manually via UI:
- Go to: https://github.com/YOUR_USERNAME/ecommerce-geo-auditor/settings/secrets/actions
- Click "New repository secret"
- Add each key

**Required:**
- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `GOOGLE_API_KEY`

**Optional:**
- `PERPLEXITY_API_KEY`
- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_ENDPOINT`
- `SERPAPI_KEY`

## 4. Verify Setup

```bash
# Check repo
gh repo view

# Check secrets
gh secret list

# Check CI status
gh workflow list
```

## 5. Start Implementation

```bash
# Follow implementation plan
cat docs/superpowers/plans/2026-06-16-geo-audit-tool.md

# Start with Task 1
# See README for development setup
```
