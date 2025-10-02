# run-dga-direct.ps1
# End-to-end hitting EACH SERVICE DIRECTLY using Invoke-RestMethod.
# Use this if the gateway is up but misconfigured internally.

$ErrorActionPreference = 'Stop'

$INGEST = "http://localhost:8081/ingest/domains"
$DETECT = "http://localhost:8501/score"
$MUTATE = "http://localhost:8083/mutate"
$EVAL   = "http://localhost:8084/eval"

$domain = "paypa1-login.net"
$batch  = @("secure-bank.co","paypa1-login.net","xkcd.com")

function Show-Step($n, $title) {
  Write-Host ""
  Write-Host ("[{0}] {1}" -f $n, $title) -ForegroundColor Cyan
}

# Probe detector (FastAPI docs route)
try {
  Invoke-WebRequest -Uri "http://localhost:8501/docs" -Method GET -TimeoutSec 5 | Out-Null
} catch {
  Write-Error "Services on localhost ports are not reachable. Are containers up?"
  exit 1
}

# 1) Ingest direct
Show-Step 1 "Ingest (direct)"
$ingestBody = @{ batch_id = "demo"; domains = $batch } | ConvertTo-Json -Compress
$ingResp = Invoke-RestMethod -Uri $INGEST -Method POST -ContentType 'application/json' -Body $ingestBody
$ingResp | ConvertTo-Json

# 2) Baseline score direct
Show-Step 2 "Baseline score (direct)"
$scoreBody = @{ domain = $domain } | ConvertTo-Json -Compress
$scoreResp = Invoke-RestMethod -Uri $DETECT -Method POST -ContentType 'application/json' -Body $scoreBody
$scoreResp | ConvertTo-Json

# 3) Mutate direct
Show-Step 3 "Mutate (direct)"
$mutateBody = @{ domain = $domain; ops = @("insert:pos=3:ch=x") } | ConvertTo-Json -Compress
$mutateResp = Invoke-RestMethod -Uri $MUTATE -Method POST -ContentType 'application/json' -Body $mutateBody
$mutateResp | ConvertTo-Json

# 4) Evasion direct
Show-Step 4 "Evasion (direct)"
$evalBody = @{ domain = $domain; max_iters = 5; target_conf = 0.25 } | ConvertTo-Json -Compress
$evalResp = Invoke-RestMethod -Uri $EVAL -Method POST -ContentType 'application/json' -Body $evalBody
$evalResp | ConvertTo-Json

Write-Host ""
Write-Host "Done." -ForegroundColor Green
