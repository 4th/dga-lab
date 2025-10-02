# run-dga-end2end.ps1
# End-to-end via the GATEWAY service using Invoke-RestMethod (handles JSON properly).

$ErrorActionPreference = 'Stop'
$BASE   = "http://localhost:8080"
$domain = "paypa1-login.net"
$batch  = @("secure-bank.co","paypa1-login.net","xkcd.com")

function Show-Step($n, $title) {
  Write-Host ""
  Write-Host ("[{0}] {1}" -f $n, $title) -ForegroundColor Cyan
}

# Probe gateway (FastAPI docs route)
try {
  Invoke-WebRequest -Uri "$BASE/docs" -Method GET -TimeoutSec 5 | Out-Null
} catch {
  Write-Error "Gateway at $BASE is not reachable. Is 'docker compose up' running?"
  exit 1
}

# 1) Ingest
Show-Step 1 "Ingest via gateway"
$ingestBody = @{ batch_id = "demo"; domains = $batch } | ConvertTo-Json -Compress
$ingResp = Invoke-RestMethod -Uri "$BASE/ingest" -Method POST -ContentType 'application/json' -Body $ingestBody
$ingResp | ConvertTo-Json

# 2) Baseline score
Show-Step 2 "Baseline score via gateway"
$scoreBody = @{ domain = $domain } | ConvertTo-Json -Compress
$scoreResp = Invoke-RestMethod -Uri "$BASE/score" -Method POST -ContentType 'application/json' -Body $scoreBody
$scoreResp | ConvertTo-Json

# 3) Mutate
Show-Step 3 "Mutate via gateway"
$mutateBody = @{ domain = $domain; ops = @("insert:pos=3:ch=x") } | ConvertTo-Json -Compress
$mutateResp = Invoke-RestMethod -Uri "$BASE/mutate" -Method POST -ContentType 'application/json' -Body $mutateBody
$mutateResp | ConvertTo-Json

# 4) Evasion
Show-Step 4 "Evasion loop via gateway"
$evalBody = @{ domain = $domain; max_iters = 5; target_conf = 0.25 } | ConvertTo-Json -Compress
$evalResp = Invoke-RestMethod -Uri "$BASE/eval" -Method POST -ContentType 'application/json' -Body $evalBody
$evalResp | ConvertTo-Json

Write-Host ""
Write-Host "Done." -ForegroundColor Green
