#!/bin/bash
# Setup GitHub Actions secrets for eCommerce GEO Auditor

set -e

echo "Setting up GitHub Actions secrets..."
echo ""
echo "You'll be prompted to paste each API key."
echo "Press Ctrl+D after pasting to continue."
echo ""

# Required secrets
echo "OpenAI API Key:"
gh secret set OPENAI_API_KEY

echo "Anthropic API Key:"
gh secret set ANTHROPIC_API_KEY

echo "Google API Key:"
gh secret set GOOGLE_API_KEY

# Optional secrets
read -p "Add Perplexity API key? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Perplexity API Key:"
    gh secret set PERPLEXITY_API_KEY
fi

read -p "Add Azure OpenAI credentials? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Azure OpenAI API Key:"
    gh secret set AZURE_OPENAI_API_KEY
    echo "Azure OpenAI Endpoint:"
    gh secret set AZURE_OPENAI_ENDPOINT
fi

read -p "Add SerpAPI key? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "SerpAPI Key:"
    gh secret set SERPAPI_KEY
fi

echo ""
echo "✓ Secrets configured!"
echo ""
echo "View secrets: gh secret list"
echo ""
