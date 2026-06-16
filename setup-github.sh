#!/bin/bash
# GitHub repo setup script for eCommerce GEO Auditor

set -e

echo "Creating GitHub repository..."

# Create repo and push
gh repo create ecommerce-geo-auditor \
  --public \
  --description "Python CLI tool for auditing eCommerce product pages for Generative Engine Optimization (GEO)" \
  --source=. \
  --remote=origin \
  --push

echo ""
echo "Repository created: https://github.com/$(gh api user --jq .login)/ecommerce-geo-auditor"
echo ""

# Create .env template
cat > .env.example << 'EOF'
# OpenAI API
OPENAI_API_KEY=sk-...

# Anthropic API
ANTHROPIC_API_KEY=sk-ant-...

# Google AI API
GOOGLE_API_KEY=...

# Perplexity API (optional)
PERPLEXITY_API_KEY=pplx-...

# Azure OpenAI (optional, for Bing grounding)
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/

# Bing Search (optional)
BING_SEARCH_ENDPOINT=https://api.bing.microsoft.com/

# SerpAPI (for sibling discovery)
SERPAPI_KEY=...
EOF

git add .env.example
git commit -m "chore: add .env.example template"
git push

echo ""
echo "✓ Repository setup complete!"
echo ""
echo "Next steps:"
echo "1. Add GitHub Actions secrets via web UI or gh CLI:"
echo "   gh secret set OPENAI_API_KEY"
echo "   gh secret set ANTHROPIC_API_KEY"
echo "   gh secret set GOOGLE_API_KEY"
echo ""
echo "2. Copy .env.example to .env and add your API keys"
echo ""
