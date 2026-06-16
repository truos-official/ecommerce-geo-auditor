# GEO Crawler Content Audit

## Purpose

This audit compares the initial HTML returned to a normal browser against the HTML returned when major search and AI crawler user-agent strings are presented.

The objective is to determine whether core product content is technically accessible and materially equivalent across:

- Googlebot — Google Search, AI Overviews, and Gemini grounding through Google Search
- Bingbot — Bing Search and Microsoft Copilot grounding
- OAI-SearchBot — ChatGPT Search
- Claude-SearchBot — Claude search indexing
- PerplexityBot — Perplexity search indexing

**Not a ranking test. Not proof of inclusion. This is an access and content-equivalence test.**

## Audit target

```text
URL: https://www.sigmaaldrich.com/US/en/product/sigma/c22010
Product: Endothelial Cell Growth Medium
Product ID: C-22010
Working directory: C:\Users\X290604\Projects\Crawler Review
Audit script: geo_crawler_content_audit.ps1
```

## Run the audit

```powershell
Set-Location "C:\Users\X290604\Projects\Crawler Review"

powershell.exe -ExecutionPolicy Bypass `
  -File ".\geo_crawler_content_audit.ps1"
```

The script saves crawler-specific HTML, response headers, extracted visible text, Product JSON-LD, CSV summaries, and a consolidated audit report.

## What the audit checks

The comparison matrix evaluates whether each response contains:

- HTTP `200`
- Correct canonical product URL
- No `noindex` directive
- Product JSON-LD
- Product ID
- Product name
- Product description
- Offer, price, currency, and availability
- Additional product properties
- General description
- Application
- Packaging
- Storage temperature
- Next.js product data and application payload

A successful response must contain the core product identity and enough content for a search or AI system to understand the page. A `200 OK` response alone is not sufficient.

---

# Crawler identity and official verification sources

## Crawler URLs and user agents used by the audit

| Platform | Audit label | robots.txt token | User-agent used by the script | Crawler information URL |
|---|---|---|---|---|
| Google | Google | `Googlebot` | `Mozilla/5.0 (Linux; Android 6.0.1; Nexus 5X Build/MMB29P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Mobile Safari/537.36 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)` | `http://www.google.com/bot.html` |
| Microsoft | Bing | `bingbot` | `Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm) Chrome/148.0.0.0 Safari/537.36` | `http://www.bing.com/bingbot.htm` |
| OpenAI | OpenAI | `OAI-SearchBot` | `Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36; compatible; OAI-SearchBot/1.3; +https://openai.com/searchbot` | `https://openai.com/searchbot` |
| Anthropic | Claude | `Claude-SearchBot` | `Claude-SearchBot/1.0 (+https://www.anthropic.com)` | `https://www.anthropic.com` |
| Perplexity | Perplexity | `PerplexityBot` | `Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; PerplexityBot/1.0; +https://perplexity.ai/perplexitybot)` | `https://perplexity.ai/perplexitybot` |

The Chrome version contained in a crawler user-agent can change. Verification should be based on the crawler token plus the provider’s official IP or DNS controls, not on an exact browser-version string.

## Official documentation

| Platform | Official crawler documentation |
|---|---|
| Google | `https://developers.google.com/crawling/docs/crawlers-fetchers/google-common-crawlers` |
| Google verification | `https://developers.google.com/crawling/docs/crawlers-fetchers/verify-google-requests` |
| Bing | `https://www.bing.com/webmasters/help/which-crawlers-does-bing-use-8c184ec0` |
| Bing verification | `https://www.bing.com/toolbox/verify-bingbot` |
| OpenAI | `https://developers.openai.com/api/docs/bots` |
| Anthropic | `https://support.claude.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler` |
| Perplexity | `https://docs.perplexity.ai/docs/resources/perplexity-crawlers` |

---

# Published crawler IP ranges

## Source-of-truth endpoints

The IP ranges below can change. Webmaster and security teams should pull the latest files directly from the provider before implementing or changing a WAF allow rule.

| Crawler | Official current IP source |
|---|---|
| Googlebot common crawlers | `https://developers.google.com/static/crawling/ipranges/common-crawlers.json` |
| Bingbot | `https://www.bing.com/toolbox/bingbot.json` |
| OAI-SearchBot | `https://openai.com/searchbot.json` |
| Anthropic crawlers | `https://claude.com/crawling/bots.json` |
| PerplexityBot | `https://www.perplexity.ai/perplexitybot.json` |

## Refresh and save the current lists locally

Run this from PowerShell before giving the allowlist to the Webmaster or WAF team:

```powershell
$workingDirectory = "C:\Users\X290604\Projects\Crawler Review"
$ipDirectory = Join-Path $workingDirectory "ip-ranges"

New-Item -ItemType Directory -Path $ipDirectory -Force | Out-Null

$ipSources = [ordered]@{
    "google-common-crawlers.json" = "https://developers.google.com/static/crawling/ipranges/common-crawlers.json"
    "bingbot.json"                = "https://www.bing.com/toolbox/bingbot.json"
    "openai-searchbot.json"       = "https://openai.com/searchbot.json"
    "anthropic-bots.json"         = "https://claude.com/crawling/bots.json"
    "perplexitybot.json"          = "https://www.perplexity.ai/perplexitybot.json"
}

foreach ($item in $ipSources.GetEnumerator()) {
    Invoke-WebRequest `
        -Uri $item.Value `
        -OutFile (Join-Path $ipDirectory $item.Key) `
        -UseBasicParsing
}

Get-ChildItem $ipDirectory -Filter "*.json" |
    Select-Object Name, Length, LastWriteTime
```

Extract all CIDR values into a consolidated CSV:

```powershell
$rows = foreach ($file in Get-ChildItem $ipDirectory -Filter "*.json") {
    $json = Get-Content $file.FullName -Raw -Encoding UTF8 | ConvertFrom-Json

    foreach ($prefix in $json.prefixes) {
        $cidr = if ($prefix.ipv4Prefix) {
            $prefix.ipv4Prefix
        }
        elseif ($prefix.ipv6Prefix) {
            $prefix.ipv6Prefix
        }

        if ($cidr) {
            [PSCustomObject]@{
                ProviderFile = $file.Name
                CreationTime = $json.creationTime
                CIDR         = $cidr
            }
        }
    }
}

$rows |
    Sort-Object ProviderFile, CIDR |
    Export-Csv `
        (Join-Path $workingDirectory "crawler-ip-allowlist.csv") `
        -NoTypeInformation `
        -Encoding UTF8

$rows | Format-Table -AutoSize
```

**Recommended control:** refresh these files automatically at least daily or before each deployment. Do not treat a copied spreadsheet or README snapshot as the permanent source of truth.

---

# Current IP snapshot

The following ranges were published by the providers when this README was prepared on **June 14, 2026**. Always compare them with the live endpoints before use.

## Bingbot

```text
157.55.39.0/24
207.46.13.0/24
40.77.167.0/24
13.66.139.0/24
13.66.144.0/24
52.167.144.0/24
13.67.10.16/28
13.69.66.240/28
13.71.172.224/28
139.217.52.0/28
191.233.204.224/28
20.36.108.32/28
20.43.120.16/28
40.79.131.208/28
40.79.186.176/28
52.231.148.0/28
20.79.107.240/28
51.105.67.0/28
20.125.163.80/28
40.77.188.0/22
65.55.210.0/24
199.30.24.0/23
40.77.202.0/24
40.77.139.0/25
20.74.197.0/28
20.15.133.160/27
40.77.177.0/24
40.77.178.0/23
```

For Bing, the stronger validation is still:

1. Use the Bing Verify Bingbot tool, or
2. Perform reverse DNS on the source IP and confirm that the hostname ends in `search.msn.com`.
3. Perform forward DNS on that hostname and confirm it resolves back to the original IP.

Do not approve Bingbot based only on the user-agent or only on a static IP copy.

## OAI-SearchBot

```text
104.210.140.128/28
135.234.64.0/24
172.182.193.224/28
172.182.193.80/28
172.182.194.144/28
172.182.194.32/28
172.182.195.48/28
172.182.209.208/28
172.182.211.192/28
172.182.213.192/28
172.182.224.0/28
172.203.190.128/28
20.14.99.96/28
20.168.18.32/28
20.169.6.224/28
20.169.7.48/28
20.169.77.0/25
20.171.123.64/28
20.171.53.224/28
20.25.151.224/28
20.42.10.176/28
4.227.36.0/25
40.67.175.0/25
40.90.214.16/28
51.8.102.0/24
74.7.175.128/25
74.7.228.0/25
74.7.228.128/25
74.7.229.0/25
74.7.229.128/25
74.7.230.0/25
74.7.241.128/25
74.7.242.128/25
74.7.243.0/25
74.7.244.0/25
```

Approve only when:

- User-agent contains `OAI-SearchBot`
- Source IP matches the current `searchbot.json`
- The request is not being rewritten through an untrusted proxy
- WAF or CDN logs confirm the allow action

## Anthropic crawler ranges

```text
216.73.216.0/22
34.162.230.222/32
34.162.244.71/32
34.162.191.81/32
34.150.241.79/32
34.85.172.162/32
35.245.175.129/32
34.182.222.37/32
34.186.108.163/32
35.245.89.239/32
34.182.161.143/32
34.182.218.27/32
34.182.220.85/32
34.11.34.31/32
34.182.140.95/32
136.107.176.208/32
34.182.226.151/32
34.182.226.221/32
35.221.29.174/32
34.182.225.167/32
```

Anthropic publishes one crawler range list covering its crawler identities. Validate both:

- The exact bot token, such as `Claude-SearchBot`
- Source IP membership in the current `bots.json`

Do not use the general Anthropic API inbound range as a replacement for the crawler list.

## PerplexityBot

```text
107.20.236.150/32
3.224.62.45/32
18.210.92.235/32
3.222.232.239/32
3.211.124.183/32
3.231.139.107/32
18.97.1.228/30
18.97.9.96/29
```

Approve only when:

- User-agent contains `PerplexityBot`
- Source IP matches the current `perplexitybot.json`
- WAF or CDN logs confirm that no challenge, managed block, or rate-limit action was applied

## Googlebot

Google publishes a large and frequently updated IPv4 and IPv6 CIDR set. It is intentionally not hardcoded into this README because a static copy creates an immediate operational risk.

Use the live list:

```text
https://developers.google.com/static/crawling/ipranges/common-crawlers.json
```

For each observed Googlebot IP:

1. Confirm the source IP matches the current `common-crawlers.json`.
2. Perform reverse DNS.
3. Confirm the hostname ends in `googlebot.com` or `geo.googlebot.com`.
4. Perform forward DNS.
5. Confirm it resolves back to the original source IP.

Both the IP-range match and DNS validation should pass before the request is treated as verified Googlebot.

---

# Webmaster validation process

## Minimum validation

The Webmaster, CDN, or security team should validate each crawler through the following evidence chain:

1. **Raw request log**
   - Timestamp
   - Requested URL
   - HTTP method
   - User-agent
   - Source IP
   - Response status
   - Response bytes
   - Cache status
   - WAF action
   - Edge location

2. **True client IP**
   - Use the direct socket IP at origin when available.
   - Behind Cloudflare, Akamai, Fastly, or another trusted proxy, use the provider’s authoritative client-IP field.
   - Do not trust arbitrary `X-Forwarded-For` values unless the header was written by a trusted proxy.

3. **Crawler verification**
   - Match the user-agent token.
   - Match the current provider IP list.
   - Perform reverse and forward DNS where supported.
   - Use the provider’s verified-bot or signed-agent integration where available.

4. **Content response**
   - Confirm the crawler received the intended product HTML rather than a challenge, consent shell, generic error page, or empty application container.
   - Compare core content, not only response size.
   - Confirm canonical, indexing directives, Product JSON-LD, product ID, product name, description, offer, and key attributes.

5. **robots.txt**
   - Confirm the crawler is allowed for the exact URL path.
   - Check every relevant hostname and subdomain.
   - Confirm the production robots.txt is the version served at the edge.

6. **WAF and bot-management rules**
   - Confirm verified crawlers bypass CAPTCHA and JavaScript challenges.
   - Confirm rate limiting is not generating `403`, `429`, `503`, or soft-block `200` responses.
   - Combine user-agent and verified IP or provider bot identity. Never allowlist on user-agent alone.

## Platform-level validation

### Google

Use Google Search Console:

- URL Inspection
- Test Live URL
- View tested HTML
- View screenshot
- Review loaded resources
- Crawl Stats
- Page indexing report

The live test is more authoritative than a local curl simulation because the request originates from Google infrastructure.

### Bing

Use Bing Webmaster Tools:

- URL Inspection
- Crawl information
- Site Scan
- Verify Bingbot
- Server log comparison

Bing verification should use the official verification tool or reverse/forward DNS.

### OpenAI

There is no equivalent public live-fetch console for OAI-SearchBot.

Validation should use:

- Exact `OAI-SearchBot` log entries
- Current `searchbot.json`
- CDN and WAF event logs
- Saved response body from the verified request
- robots.txt review
- Repeated ChatGPT Search testing as supporting evidence, not as deterministic proof

### Anthropic

Validation should use:

- `Claude-SearchBot` server-log entries
- Current `bots.json`
- CDN and WAF event logs
- Saved response body from the verified request
- robots.txt review
- Claude search testing as supporting evidence

### Perplexity

Validation should use:

- `PerplexityBot` server-log entries
- Current `perplexitybot.json`
- CDN and WAF event logs
- Saved response body from the verified request
- robots.txt review
- Perplexity answer and citation testing as supporting evidence

---

# Accuracy limitations and disclaimer

## User-agent spoofing

The PowerShell audit changes only the HTTP user-agent. The request still originates from the local network, not from Google, Microsoft, OpenAI, Anthropic, or Perplexity.

Any client can copy a crawler user-agent. A positive curl result does not prove that the actual crawler can access the page.

## IP- and bot-based response differences

The CDN, WAF, or origin may evaluate:

- Source IP and ASN
- Reverse DNS
- TLS fingerprint
- HTTP protocol
- Header order
- Cookie state
- Bot score
- Geographic location
- Request velocity
- IP reputation
- Verified-bot status

A real crawler can therefore receive a different response from the local user-agent simulation.

## Initial HTML versus rendered page

The audit compares the initial HTTP response body.

It does not fully reproduce:

- JavaScript rendering
- Browser execution
- Lazy-loaded content
- API calls made after page load
- Consent or regional flows
- Hydrated React or Next.js DOM
- Content rendered by Google or Bing after their web-rendering stage

Critical GEO content should be present in the initial HTML or structured data. Depending only on client-side rendering increases risk.

## `HEAD` versus `GET`

A `curl -I` request tests headers only. It does not prove that meaningful page content is returned.

The audit script uses `GET` and saves the body. GEO conclusions should be based on the full `GET` response.

## `200 OK` does not equal access

A challenge page, generic shell, soft error, login page, or consent page can return `200 OK`.

Validate the actual content:

- Correct title
- Correct canonical
- Product identity
- Product schema
- Description
- Product attributes
- No challenge language
- No access-denied content

## Response size is directional, not conclusive

A smaller crawler response does not automatically mean the crawler is blocked. The site may remove analytics, personalization, interactive components, or large JavaScript bundles.

A similar response size does not prove content equivalence.

Compare the actual semantic content.

## Dynamic product data

Price, inventory, availability, location, contract status, and shipping content may vary by:

- Country
- Sales organization
- Customer account
- Cookie
- Session
- Dealer
- Inventory system
- Edge cache
- Time of request

Structured data must match what the crawler and an unauthenticated user can reasonably see.

## Caching and edge behavior

Cloudflare or another CDN can return a cached crawler response that differs from origin behavior.

Review:

- `CF-Cache-Status`
- `Age`
- `Via`
- `X-Cache`
- Edge location
- Cache key
- Bot-specific cache rules
- Origin response logs

## Temporary and non-deterministic behavior

Crawler access can change due to:

- A/B tests
- Deployment timing
- WAF rule changes
- Rate limits
- Traffic spikes
- Regional incidents
- CDN failures
- Origin timeouts
- Stale cache
- Crawler scheduling

Repeat the audit and retain timestamped evidence.

## IP lists change

Published IP ranges are operational data, not permanent configuration.

The Webmaster team should automate refresh of official JSON endpoints and maintain a controlled change process for WAF rules.

## Search and AI systems use more than the live page

AI answers may be grounded through:

- Search indexes
- Cached copies
- Merchant or product feeds
- Sitemaps
- Knowledge graphs
- Third-party search providers
- Previously crawled content
- User-triggered fetches

Crawler accessibility is necessary, but it does not guarantee indexing, ranking, citation, or recommendation.

---

# GEO interpretation

## Pass

- Verified crawler can access the URL
- HTTP response is successful
- No challenge or soft block
- Correct canonical
- Indexing is allowed
- Product name, ID, description, and attributes are available
- Product JSON-LD is present and consistent
- Core content is materially equivalent to the browser response

## Warning

- Product data exists only in JSON-LD but not in readable server-rendered HTML
- Key attributes are missing from crawler HTML
- Crawler receives a materially smaller response
- Dynamic price or inventory differs
- JavaScript is required for core content
- Intermittent `403`, `429`, or `5xx` responses appear
- WAF recognizes the crawler but still challenges or rate-limits it

## Fail

- Verified crawler is blocked
- Wrong canonical
- `noindex`
- Empty application shell
- CAPTCHA or access-denied page
- Missing product identity
- Missing description and key attributes
- Product schema is absent or invalid
- Structured data conflicts with visible content
- Repeated crawl errors appear in provider tools or server logs

---

# Scope distinction

The following agents are separate and should not be treated as equivalents:

| Provider | Search/indexing crawler in this audit | Separate agents not covered by this test |
|---|---|---|
| Google | `Googlebot` | `Google-Extended` is a control token, not a standalone HTTP crawler user-agent |
| OpenAI | `OAI-SearchBot` | `GPTBot` is associated with model development; `ChatGPT-User` is user initiated |
| Anthropic | `Claude-SearchBot` | `ClaudeBot` is associated with model development; `Claude-User` is user initiated |
| Perplexity | `PerplexityBot` | `Perplexity-User` is user initiated |

Do not use the search-crawler result to make conclusions about training crawlers or user-triggered agents.

---

# Required handoff to Webmaster

Provide the Webmaster team with:

- `geo_crawler_content_audit.ps1`
- This README
- `crawler-audit-report.txt`
- `content-matrix.csv`
- `fetch-summary.csv`
- `coverage-summary.csv`
- Saved crawler HTML files
- Saved crawler headers
- Saved Product JSON-LD files
- Current IP-range JSON files
- Server and CDN log extracts for verified crawler requests
- WAF event evidence
- Google Search Console and Bing Webmaster validation screenshots or exports

The final conclusion should be based on the combination of local simulation, verified crawler logs, provider tools, and the actual content returned to verified crawler infrastructure.
