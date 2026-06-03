[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$ProgressPreference = 'SilentlyContinue'
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

function Get-MetaContent {
  param([string]$Html, [string[]]$Patterns)
  foreach ($pattern in $Patterns) {
    $m = [regex]::Match($Html, $pattern, 'IgnoreCase, Singleline')
    if ($m.Success) { return ($m.Groups[1].Value -replace '&amp;','&' -replace '&quot;','"' -replace '&#39;',"'" -replace '<.*?>','').Trim() }
  }
  return $null
}

function Get-PageInfo {
  param([string]$Url)
  try {
    $resp = Invoke-WebRequest -Uri $Url -UseBasicParsing -Headers @{ 'User-Agent' = 'Mozilla/5.0' } -TimeoutSec 40
    $html = [string]$resp.Content
    $title = Get-MetaContent -Html $html -Patterns @('<meta[^>]+property="og:title"[^>]+content="([^"]+)"','<meta[^>]+name="twitter:title"[^>]+content="([^"]+)"','<title>(.*?)</title>')
    $desc = Get-MetaContent -Html $html -Patterns @('<meta[^>]+property="og:description"[^>]+content="([^"]+)"','<meta[^>]+name="description"[^>]+content="([^"]+)"','<meta[^>]+name="twitter:description"[^>]+content="([^"]+)"')
    [pscustomobject]@{ url = $Url; title = $title; description = $desc; status = 'ok' }
  } catch {
    [pscustomobject]@{ url = $Url; title = $null; description = $_.Exception.Message; status = 'error' }
  }
}

$daily = Invoke-WebRequest -Uri 'https://aihot.virxact.com/api/public/daily' -UseBasicParsing -Headers @{ 'User-Agent' = 'Mozilla/5.0' } | Select-Object -ExpandProperty Content
$data = $daily | ConvertFrom-Json
$items = foreach ($section in $data.sections) {
  foreach ($item in $section.items) {
    [pscustomobject]@{ section = $section.label; title = $item.title; summary = $item.summary; sourceName = $item.sourceName; sourceUrl = $item.sourceUrl }
  }
}
$results = foreach ($item in $items) {
  $page = Get-PageInfo -Url $item.sourceUrl
  [pscustomobject]@{
    section = $item.section
    dailyTitle = $item.title
    dailySummary = $item.summary
    sourceName = $item.sourceName
    sourceUrl = $item.sourceUrl
    pageTitle = $page.title
    pageDescription = $page.description
    fetchStatus = $page.status
  }
}
$results | ConvertTo-Json -Depth 5
