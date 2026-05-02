#requires -Version 5.1
# Smoke test for guard.ps1. Not part of the harness -- run manually.

$ErrorActionPreference = "Continue"
$hook = Join-Path $PSScriptRoot "guard.ps1"
$cwd  = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)  # repo root

function RunCase {
    param([string]$Name, [string]$Json, [int]$Expected, [string]$Pattern = $null)
    $tmp = New-TemporaryFile
    Set-Content -LiteralPath $tmp.FullName -Value $Json -Encoding utf8 -NoNewline
    $err = Get-Content -LiteralPath $tmp.FullName | & powershell -NoProfile -ExecutionPolicy Bypass -File $hook 2>&1
    $exit = $LASTEXITCODE
    Remove-Item -LiteralPath $tmp.FullName -Force
    $errStr = ($err | Out-String).Trim()
    $pass = ($exit -eq $Expected)
    if ($Pattern -and $exit -eq 2) { $pass = $pass -and ($errStr -match $Pattern) }
    $tag = if ($pass) { "PASS" } else { "FAIL" }
    Write-Host "[$tag] $Name (exit=$exit expected=$Expected)"
    if (-not $pass -and $errStr) { Write-Host "       stderr: $errStr" }
}

# Snapshot the existing pin (if any) so the test can restore it on exit.
# Running the smoke test must not silently break an active job.
$pin = Join-Path $cwd ".claude/active_job"
$savedPin = $null
if (Test-Path -LiteralPath $pin) {
    $savedPin = (Get-Content -LiteralPath $pin -Raw)
    Remove-Item -LiteralPath $pin -Force
}

Write-Host ""
Write-Host "=== Sandpit containment ==="
RunCase "Edit setup.r (in sandpit, no jobs/)" `
    (@{tool_name="Edit"; cwd=$cwd; tool_input=@{file_path="$cwd\setup.r"}} | ConvertTo-Json -Compress) `
    0

RunCase "Edit C:\Users\.Rprofile (outside sandpit) -- should BLOCK" `
    (@{tool_name="Edit"; cwd=$cwd; tool_input=@{file_path="C:\Users\arthu\Documents\.Rprofile"}} | ConvertTo-Json -Compress) `
    2 `
    "outside\s+the\s+sandpit"

RunCase "Write to ../escape.txt (parent escape) -- should BLOCK" `
    (@{tool_name="Write"; cwd=$cwd; tool_input=@{file_path="..\escape.txt"}} | ConvertTo-Json -Compress) `
    2 `
    "outside\s+the\s+sandpit"

Write-Host ""
Write-Host "=== Per-job isolation ==="
RunCase "Edit jobs/test-job with NO pin -- should BLOCK" `
    (@{tool_name="Edit"; cwd=$cwd; tool_input=@{file_path="$cwd\jobs\test-job\outputs\report_draft.md"}} | ConvertTo-Json -Compress) `
    2 `
    "no active job is pinned"

Set-Content -LiteralPath $pin -Value 'test-job' -NoNewline
RunCase "Edit jobs/test-job WITH pin=test-job -- should ALLOW" `
    (@{tool_name="Edit"; cwd=$cwd; tool_input=@{file_path="$cwd\jobs\test-job\outputs\report_draft.md"}} | ConvertTo-Json -Compress) `
    0

RunCase "Edit jobs/other-job WITH pin=test-job -- should BLOCK" `
    (@{tool_name="Edit"; cwd=$cwd; tool_input=@{file_path="$cwd\jobs\other-job\outputs\x.md"}} | ConvertTo-Json -Compress) `
    2 `
    "active job is 'test-job'"

Write-Host ""
Write-Host "=== Bash scanning ==="
RunCase "Bash echo > C:\Users\..\evil.txt -- should BLOCK" `
    (@{tool_name="Bash"; cwd=$cwd; tool_input=@{command="echo hello > C:\Users\arthu\Desktop\evil.txt"}} | ConvertTo-Json -Compress) `
    2 `
    "outside\s+the\s+sandpit"

RunCase "Bash curl to RStudio (no write target) -- should ALLOW" `
    (@{tool_name="Bash"; cwd=$cwd; tool_input=@{command="curl -X POST http://127.0.0.1:8787/run -d data.json"}} | ConvertTo-Json -Compress) `
    0

RunCase "Bash rm -rf inside active job -- should ALLOW" `
    (@{tool_name="Bash"; cwd=$cwd; tool_input=@{command="rm -rf $cwd\jobs\test-job\outputs\.claim_check_cache"}} | ConvertTo-Json -Compress) `
    0

RunCase "Bash rm -rf into OTHER job -- should BLOCK" `
    (@{tool_name="Bash"; cwd=$cwd; tool_input=@{command="rm -rf $cwd\jobs\other-job\outputs\foo"}} | ConvertTo-Json -Compress) `
    2 `
    "jobs/other-job"

RunCase "Bash Set-Content writing outside sandpit -- should BLOCK" `
    (@{tool_name="Bash"; cwd=$cwd; tool_input=@{command="Set-Content -Path C:\Users\arthu\Desktop\out.txt -Value 'x'"}} | ConvertTo-Json -Compress) `
    2 `
    "outside\s+the\s+sandpit"

RunCase "Bash python claim-check script (inside sandpit) -- should ALLOW" `
    (@{tool_name="Bash"; cwd=$cwd; tool_input=@{command="python .claude/skills/claim-check/scripts/extract_claims.py jobs/test-job/outputs/report_draft.md"}} | ConvertTo-Json -Compress) `
    0

Write-Host ""
Write-Host "=== Other tools (matcher excludes Read/Grep, but verify hook ALLOW) ==="
RunCase "Read outside sandpit (defensive -- matcher would skip in prod) -- should ALLOW" `
    (@{tool_name="Read"; cwd=$cwd; tool_input=@{file_path="C:\Users\arthu\Documents\.Rprofile"}} | ConvertTo-Json -Compress) `
    0

Write-Host ""
Write-Host "=== Plan-mode system carve-out ==="
$plan_path = Join-Path $env:USERPROFILE ".claude\plans\test.md"
RunCase "Write to ~/.claude/plans/*.md (plan mode) -- should ALLOW" `
    (@{tool_name="Write"; cwd=$cwd; tool_input=@{file_path=$plan_path}} | ConvertTo-Json -Compress) `
    0

$nonplan_path = Join-Path $env:USERPROFILE ".claude\settings.json"
RunCase "Write to ~/.claude/settings.json (NOT a plan file) -- should BLOCK" `
    (@{tool_name="Write"; cwd=$cwd; tool_input=@{file_path=$nonplan_path}} | ConvertTo-Json -Compress) `
    2 `
    "outside\s+the\s+sandpit"

# Clean up: restore the snapshot pin if there was one, otherwise leave the pin file absent.
Remove-Item -LiteralPath $pin -Force -ErrorAction SilentlyContinue
if ($null -ne $savedPin) {
    Set-Content -LiteralPath $pin -Value $savedPin -NoNewline
    Write-Host ""
    Write-Host "=== Tests done. Pin restored to '$($savedPin.Trim())'. ==="
} else {
    Write-Host ""
    Write-Host "=== Tests done. No prior pin; pin file left absent. ==="
}
