param(
    [string]$Url = "https://www.sigmaaldrich.com/US/en/product/sigma/c22010",
    [string]$WorkingDirectory = "C:\Users\X290604\Projects\Crawler Review",
    [string]$ProductId = "C-22010",
    [string]$ProductName = "Endothelial Cell Growth Medium"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if (-not (Get-Command curl.exe -ErrorAction SilentlyContinue)) {
    throw "curl.exe was not found. Use Windows 10/11 curl.exe or install curl and try again."
}

New-Item -ItemType Directory -Path $WorkingDirectory -Force | Out-Null
Set-Location $WorkingDirectory

# Browser is the normal, non-crawler HTTP response baseline.
# Google uses the mobile crawler because Google primarily uses mobile-first indexing.
$Agents = [ordered]@{
    "Browser" = [ordered]@{
        Slug = "browser"
        UserAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0"
    }
    "Google" = [ordered]@{
        Slug = "googlebot"
        UserAgent = "Mozilla/5.0 (Linux; Android 6.0.1; Nexus 5X Build/MMB29P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Mobile Safari/537.36 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
    }
    "Bing" = [ordered]@{
        Slug = "bingbot"
        UserAgent = "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm) Chrome/148.0.0.0 Safari/537.36"
    }
    "OpenAI" = [ordered]@{
        Slug = "oai-searchbot"
        UserAgent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36; compatible; OAI-SearchBot/1.3; +https://openai.com/searchbot"
    }
    "Claude" = [ordered]@{
        Slug = "claude-searchbot"
        UserAgent = "Claude-SearchBot/1.0 (+https://www.anthropic.com)"
    }
    "Perplexity" = [ordered]@{
        Slug = "perplexitybot"
        UserAgent = "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; PerplexityBot/1.0; +https://perplexity.ai/perplexitybot)"
    }
}

function Read-Utf8File {
    param([Parameter(Mandatory)][string]$Path)

    $utf8 = New-Object System.Text.UTF8Encoding($false)
    return [System.IO.File]::ReadAllText($Path, $utf8)
}

function ConvertTo-VisibleText {
    param([Parameter(Mandatory)][string]$Html)

    $text = [regex]::Replace($Html, '(?is)<script\b[^>]*>.*?</script>', ' ')
    $text = [regex]::Replace($text, '(?is)<style\b[^>]*>.*?</style>', ' ')
    $text = [regex]::Replace($text, '(?is)<noscript\b[^>]*>.*?</noscript>', ' ')
    $text = [regex]::Replace($text, '(?is)<!--.*?-->', ' ')
    $text = [regex]::Replace($text, '(?is)<[^>]+>', ' ')
    $text = [System.Net.WebUtility]::HtmlDecode($text)
    $text = [regex]::Replace($text, '\s+', ' ').Trim()
    return $text
}

function Save-ProductJsonLd {
    param(
        [Parameter(Mandatory)][string]$Html,
        [Parameter(Mandatory)][string]$OutputPath
    )

    $matches = [regex]::Matches(
        $Html,
        '(?is)<script[^>]*type\s*=\s*["'']application/ld\+json["''][^>]*>(.*?)</script>'
    )

    $productBlocks = New-Object System.Collections.Generic.List[string]

    foreach ($match in $matches) {
        $jsonText = [System.Net.WebUtility]::HtmlDecode($match.Groups[1].Value).Trim()
        if ($jsonText -match '(?is)"@type"\s*:\s*"Product"') {
            $productBlocks.Add($jsonText)
        }
    }

    if ($productBlocks.Count -gt 0) {
        [System.IO.File]::WriteAllText(
            $OutputPath,
            ($productBlocks -join "`r`n`r`n"),
            (New-Object System.Text.UTF8Encoding($false))
        )
        return $true
    }

    return $false
}

function Invoke-AgentFetch {
    param(
        [Parameter(Mandatory)][string]$DisplayName,
        [Parameter(Mandatory)][string]$Slug,
        [Parameter(Mandatory)][string]$UserAgent
    )

    $htmlPath = Join-Path $WorkingDirectory "$Slug.html"
    $headersPath = Join-Path $WorkingDirectory "$Slug.headers.txt"
    $visibleTextPath = Join-Path $WorkingDirectory "$Slug.visible-text.txt"
    $schemaPath = Join-Path $WorkingDirectory "$Slug.product-schema.json"

    $writeOut = "%{http_code}`t%{size_download}`t%{url_effective}`t%{content_type}"

    $curlArguments = @(
        "--ssl-revoke-best-effort",
        "-L",
        "--compressed",
        "-sS",
        "--retry", "2",
        "--retry-delay", "2",
        "--connect-timeout", "30",
        "--max-time", "180",
        "-H", "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "-H", "Accept-Language: en-US,en;q=0.9",
        "-H", "Cache-Control: no-cache",
        "-A", $UserAgent,
        "-D", $headersPath,
        "-o", $htmlPath,
        "-w", $writeOut,
        $Url
    )

    Write-Host "Fetching $DisplayName..."
    $curlResult = & curl.exe @curlArguments
    $curlExitCode = $LASTEXITCODE

    if ($curlExitCode -ne 0) {
        throw "curl.exe failed for $DisplayName with exit code $curlExitCode."
    }

    $parts = $curlResult -split "`t", 4
    if ($parts.Count -lt 4) {
        throw "Could not parse curl metrics for $DisplayName. Raw output: $curlResult"
    }

    $html = Read-Utf8File -Path $htmlPath
    $headers = Read-Utf8File -Path $headersPath
    $visibleText = ConvertTo-VisibleText -Html $html

    [System.IO.File]::WriteAllText(
        $visibleTextPath,
        $visibleText,
        (New-Object System.Text.UTF8Encoding($false))
    )

    $schemaSaved = Save-ProductJsonLd -Html $html -OutputPath $schemaPath
    $hash = (Get-FileHash -Path $htmlPath -Algorithm SHA256).Hash

    return [pscustomobject]@{
        Agent = $DisplayName
        Slug = $Slug
        UserAgent = $UserAgent
        Status = [int]$parts[0]
        DownloadBytes = [int64][double]$parts[1]
        HtmlBytes = (Get-Item $htmlPath).Length
        VisibleTextChars = $visibleText.Length
        FinalUrl = $parts[2]
        ContentType = $parts[3]
        Html = $html
        Headers = $headers
        HtmlPath = $htmlPath
        HeadersPath = $headersPath
        VisibleTextPath = $visibleTextPath
        ProductSchemaSaved = $schemaSaved
        ProductSchemaPath = $(if ($schemaSaved) { $schemaPath } else { $null })
        Sha256 = $hash
    }
}

$Responses = [ordered]@{}

foreach ($entry in $Agents.GetEnumerator()) {
    $Responses[$entry.Key] = Invoke-AgentFetch `
        -DisplayName $entry.Key `
        -Slug $entry.Value.Slug `
        -UserAgent $entry.Value.UserAgent

    Start-Sleep -Seconds 1
}

# Save robots.txt as supporting GEO evidence. This script does not attempt to
# fully interpret robots.txt because crawler rule precedence and path matching
# should be validated with each provider's official testing tools.
$targetUri = [Uri]$Url
$robotsUrl = "$($targetUri.Scheme)://$($targetUri.Authority)/robots.txt"
$robotsPath = Join-Path $WorkingDirectory "robots.txt"

& curl.exe `
    --ssl-revoke-best-effort `
    -L `
    --compressed `
    -sS `
    --connect-timeout 30 `
    --max-time 120 `
    -A $Agents["Browser"].UserAgent `
    -o $robotsPath `
    $robotsUrl

if ($LASTEXITCODE -ne 0) {
    Write-Warning "Could not download robots.txt from $robotsUrl"
}

$productIdRegex = [regex]::Escape($ProductId)
$productNameRegex = [regex]::Escape($ProductName)
$canonicalPathRegex = [regex]::Escape($targetUri.AbsolutePath)

# Each check receives one response object containing HTML, headers and status.
$Checks = [ordered]@{
    "HTTP 200" = {
        param($response)
        $response.Status -eq 200
    }
    "Canonical product URL" = {
        param($response)
        $response.Html -match "(?is)<link[^>]+rel\s*=\s*[`"']canonical[`"'][^>]+$canonicalPathRegex"
    }
    "Indexable (no noindex)" = {
        param($response)
        $metaNoIndex = $response.Html -match '(?is)<meta[^>]+name\s*=\s*["''](?:robots|googlebot|bingbot)["''][^>]+content\s*=\s*["''][^"'']*noindex'
        $headerNoIndex = $response.Headers -match '(?im)^X-Robots-Tag\s*:\s*.*noindex'
        -not ($metaNoIndex -or $headerNoIndex)
    }
    "Product JSON-LD" = {
        param($response)
        $response.Html -match '(?is)"@type"\s*:\s*"Product"'
    }
    "Schema product ID" = {
        param($response)
        $response.Html -match "(?is)`"productID`"\s*:\s*`"$productIdRegex`""
    }
    "Schema offer" = {
        param($response)
        $response.Html -match '(?is)"@type"\s*:\s*"Offer"'
    }
    "Product name" = {
        param($response)
        $response.Html -match "(?is)$productNameRegex"
    }
    "Schema description" = {
        param($response)
        $response.Html -match '(?is)"description"\s*:\s*"Ready-to-use kit including Basal Medium and SupplementMix,\s*500 ml"'
    }
    "Additional properties" = {
        param($response)
        $response.Html -match '(?is)"additionalProperty"\s*:'
    }
    "Next.js product ID" = {
        param($response)
        $response.Html -match "(?is)`"productNumber`"\s*:\s*`"$productIdRegex`""
    }
    "General description" = {
        param($response)
        $response.Html -match '(?is)"label"\s*:\s*"General description"'
    }
    "Application" = {
        param($response)
        $response.Html -match '(?is)"label"\s*:\s*"Application"'
    }
    "Packaging" = {
        param($response)
        $response.Html -match '(?is)"(?:name|label)"\s*:\s*"packaging"'
    }
    "Storage temperature" = {
        param($response)
        $response.Html -match '(?is)"(?:name|label)"\s*:\s*"storage temp\."'
    }
    "Next.js payload" = {
        param($response)
        $response.Html -match '(?is)id\s*=\s*["'']__NEXT_DATA__["'']'
    }
}

$Matrix = foreach ($check in $Checks.GetEnumerator()) {
    $row = [ordered]@{
        Check = $check.Key
    }

    foreach ($agentName in $Agents.Keys) {
        $row[$agentName] = [bool](& $check.Value $Responses[$agentName])
    }

    [pscustomobject]$row
}

$browserHtmlBytes = [double]$Responses["Browser"].HtmlBytes
$browserVisibleChars = [double]$Responses["Browser"].VisibleTextChars

$FetchSummary = foreach ($agentName in $Agents.Keys) {
    $response = $Responses[$agentName]

    $htmlPct = if ($browserHtmlBytes -gt 0) {
        [math]::Round(($response.HtmlBytes / $browserHtmlBytes) * 100, 1)
    } else {
        0
    }

    $textPct = if ($browserVisibleChars -gt 0) {
        [math]::Round(($response.VisibleTextChars / $browserVisibleChars) * 100, 1)
    } else {
        0
    }

    [pscustomobject]@{
        Agent = $agentName
        HTTP = $response.Status
        HtmlBytes = $response.HtmlBytes
        HtmlVsBrowserPct = $htmlPct
        VisibleTextChars = $response.VisibleTextChars
        TextVsBrowserPct = $textPct
        ProductSchema = $response.ProductSchemaSaved
        Sha256Prefix = $response.Sha256.Substring(0, 12)
    }
}

# Core coverage compares each crawler with checks that are true in the Browser baseline.
$browserTrueChecks = @(
    foreach ($row in $Matrix) {
        if ($row.Browser) { $row.Check }
    }
)

$Coverage = foreach ($agentName in $Agents.Keys) {
    $matched = 0

    foreach ($row in $Matrix) {
        if (($browserTrueChecks -contains $row.Check) -and $row.$agentName) {
            $matched++
        }
    }

    $coveragePct = if ($browserTrueChecks.Count -gt 0) {
        [math]::Round(($matched / $browserTrueChecks.Count) * 100, 1)
    } else {
        0
    }

    [pscustomobject]@{
        Agent = $agentName
        BrowserChecksAvailable = $browserTrueChecks.Count
        ChecksMatched = $matched
        CoveragePct = $coveragePct
    }
}

$FetchSummary | Export-Csv `
    -Path (Join-Path $WorkingDirectory "fetch-summary.csv") `
    -NoTypeInformation `
    -Encoding UTF8

$Matrix | Export-Csv `
    -Path (Join-Path $WorkingDirectory "content-matrix.csv") `
    -NoTypeInformation `
    -Encoding UTF8

$Coverage | Export-Csv `
    -Path (Join-Path $WorkingDirectory "coverage-summary.csv") `
    -NoTypeInformation `
    -Encoding UTF8

$agentDetails = foreach ($agentName in $Agents.Keys) {
    [pscustomobject]@{
        Agent = $agentName
        UserAgent = $Agents[$agentName].UserAgent
        HtmlFile = $Responses[$agentName].HtmlPath
        HeaderFile = $Responses[$agentName].HeadersPath
        VisibleTextFile = $Responses[$agentName].VisibleTextPath
        ProductSchemaFile = $Responses[$agentName].ProductSchemaPath
    }
}

$agentDetails | Export-Csv `
    -Path (Join-Path $WorkingDirectory "agent-files.csv") `
    -NoTypeInformation `
    -Encoding UTF8

$fetchText = $FetchSummary |
    Format-Table -AutoSize |
    Out-String -Width 240

$matrixText = $Matrix |
    Format-Table -AutoSize |
    Out-String -Width 240

$coverageText = $Coverage |
    Format-Table -AutoSize |
    Out-String -Width 240

$report = @"
GEO CRAWLER CONTENT AUDIT
Generated: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss K")
URL: $Url
Working directory: $WorkingDirectory

FETCH SUMMARY
$fetchText
CONTENT MATRIX
$matrixText
BROWSER-CHECK COVERAGE
$coverageText
NOTES
- Browser means the initial HTML returned to a normal browser user agent; it is not a JavaScript-rendered DOM.
- The crawler requests spoof only the User-Agent header. They do not originate from verified crawler IP ranges.
- Google and Bing can perform later JavaScript rendering, so validate critical findings in Google Search Console and Bing Webmaster Tools.
- robots.txt was saved to: $robotsPath
"@

$reportPath = Join-Path $WorkingDirectory "crawler-audit-report.txt"
[System.IO.File]::WriteAllText(
    $reportPath,
    $report,
    (New-Object System.Text.UTF8Encoding($false))
)

Write-Host ""
Write-Host $report
Write-Host ""
Write-Host "Saved report: $reportPath"
Write-Host "Saved matrix: $(Join-Path $WorkingDirectory 'content-matrix.csv')"
Write-Host "Saved fetch summary: $(Join-Path $WorkingDirectory 'fetch-summary.csv')"
Write-Host "Saved coverage summary: $(Join-Path $WorkingDirectory 'coverage-summary.csv')"
