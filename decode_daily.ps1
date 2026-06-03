[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$ProgressPreference = 'SilentlyContinue'
Add-Type -AssemblyName System.Net.Http
$client = [System.Net.Http.HttpClient]::new()
$client.DefaultRequestHeaders.UserAgent.ParseAdd('Mozilla/5.0')
$bytes = $client.GetByteArrayAsync('https://aihot.virxact.com/api/public/daily').Result
$text = [System.Text.Encoding]::UTF8.GetString($bytes)
Set-Content -Path 'daily_utf8.json' -Value $text -Encoding UTF8
$data = $text | ConvertFrom-Json
$items = foreach ($section in $data.sections) {
  foreach ($item in $section.items) {
    [pscustomobject]@{ section = $section.label; title = $item.title; summary = $item.summary; sourceName = $item.sourceName; sourceUrl = $item.sourceUrl }
  }
}
$items | ConvertTo-Json -Depth 4 | Set-Content -Path 'daily_items_utf8.json' -Encoding UTF8
Get-Content -Path 'daily_items_utf8.json' -TotalCount 120
