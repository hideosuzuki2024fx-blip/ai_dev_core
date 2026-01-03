param(
  [string]$CloudflaredExe = "tools/bin/cloudflared.exe",
  [int]$LocalPort = 8711,
  [string]$OpenApiPath = "actions/openapi.yaml",
  [string]$MetaPath = "",
  [switch]$Commit
)

Set-Location (git rev-parse --show-toplevel)

if (!(Test-Path $CloudflaredExe)) {
  throw "cloudflared.exe not found: $CloudflaredExe (expected local binary; see README section for download)"
}

if (!(Test-Path $OpenApiPath)) {
  throw "OpenAPI file not found: $OpenApiPath"
}

# Start quick tunnel and capture initial output lines to extract URL.
# We do NOT kill the tunnel; this script is meant to be run in its own window.
$psi = New-Object System.Diagnostics.ProcessStartInfo
$psi.FileName = (Resolve-Path $CloudflaredExe).Path
$psi.Arguments = "tunnel --url http://localhost:$LocalPort"
$psi.RedirectStandardOutput = $true
$psi.RedirectStandardError = $true
$psi.UseShellExecute = $false
$psi.CreateNoWindow = $false

$p = New-Object System.Diagnostics.Process
$p.StartInfo = $psi
[void]$p.Start()

$regex = [regex]'https://[a-z0-9\-]+\.trycloudflare\.com'
$url = $null
$buffer = New-Object System.Collections.Generic.List[string]

# read a bunch of lines until URL appears or timeout-ish
for ($i=0; $i -lt 200; $i++) {
  if ($p.HasExited) { break }

  $line = $p.StandardOutput.ReadLine()
  if ($null -eq $line) { Start-Sleep -Milliseconds 50; continue }
  $buffer.Add($line) | Out-Null

  $m = $regex.Match($line)
  if ($m.Success) { $url = $m.Value; break }
}

if (-not $url) {
  Write-Host ($buffer -join "`n")
  throw "Could not extract trycloudflare URL from cloudflared output."
}

Write-Host "Tunnel URL: $url"

# Update first '- url:' in OpenAPI
$lines = Get-Content $OpenApiPath
$done = $false
$lines2 = foreach ($l in $lines) {
  if (-not $done -and $l -match "^\s*-\s*url:\s*") {
    $done = $true
    "  - url: $url"
  } else { $l }
}
$lines2 | Set-Content -Path $OpenApiPath -Encoding utf8

# Meta log path (default: logs/meta/YYYYMMDD_tunnel_url_meta.md)
if (-not $MetaPath -or $MetaPath.Trim().Length -eq 0) {
  $stamp = (Get-Date).ToString("yyyyMMdd")
  $MetaPath = "logs/meta/${stamp}_tunnel_url_meta.md"
}

@"
# Meta: Tunnel URL for Actions (dev)

- Date: $(Get-Date -Format 'yyyy-MM-dd')
- Method: Cloudflare Quick Tunnel (cloudflared.exe)
- Server URL:
  - $url
- Notes:
  - URL may change per run; update actions/openapi.yaml for dev.
  - Do NOT record token values in repo.
"@ | Set-Content -Path $MetaPath -Encoding utf8

if ($Commit) {
  git add $OpenApiPath $MetaPath | Out-Null
  git commit -m "Review: update Actions OpenAPI server URL from quick tunnel (dev)" | Out-Null
  Write-Host "Committed: Review: update Actions OpenAPI server URL from quick tunnel (dev)"
}

Write-Host "cloudflared is still running in this process window. Close window or Ctrl+C to stop."
Wait-Process -Id $p.Id