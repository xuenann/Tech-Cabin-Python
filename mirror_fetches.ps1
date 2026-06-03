[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$ProgressPreference = 'SilentlyContinue'

function Get-MirrorText {
  param([string]$Url)
  $mirror = 'https://r.jina.ai/http://' + ($Url -replace '^https?://','')
  try {
    $content = Invoke-WebRequest -Uri $mirror -UseBasicParsing -Headers @{ 'User-Agent'='Mozilla/5.0' } -TimeoutSec 40 | Select-Object -ExpandProperty Content
    $lines = $content -split "`r?`n" | Where-Object { $_.Trim() -ne '' }
    $title = ($lines | Where-Object { $_ -like 'Title:*' } | Select-Object -First 1)
    $bodyStart = [Array]::IndexOf($lines, 'Markdown Content:')
    if ($bodyStart -ge 0) {
      $body = ($lines[($bodyStart+1)..([Math]::Min($bodyStart+18, $lines.Length-1))] -join " ").Trim()
    } else {
      $body = ($lines | Select-Object -First 12) -join " "
    }
    [pscustomobject]@{ mirrorTitle=$title; mirrorBody=$body; mirrorStatus='ok' }
  } catch {
    [pscustomobject]@{ mirrorTitle=$null; mirrorBody=$_.Exception.Message; mirrorStatus='error' }
  }
}

$items = Get-Content 'daily_items_utf8.json' -Raw | ConvertFrom-Json
$results = foreach ($item in $items) {
  if ($item.sourceUrl -match 'x\.com/' -or $item.sourceUrl -match 'openai\.com/' -or $item.sourceUrl -match 'bloomberg\.com/' -or $item.sourceUrl -match 'whitehouse\.gov/') {
    $m = Get-MirrorText -Url $item.sourceUrl
    [pscustomobject]@{ title=$item.title; url=$item.sourceUrl; mirrorTitle=$m.mirrorTitle; mirrorBody=$m.mirrorBody; status=$m.mirrorStatus }
  }
}
$results | ConvertTo-Json -Depth 4 | Set-Content -Path 'mirror_fetches.json' -Encoding UTF8
Get-Content 'mirror_fetches.json' -TotalCount 260
