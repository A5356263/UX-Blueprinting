$ErrorActionPreference = "Stop"

if ($args.Count -eq 0) {
  Write-Host "Usage: powershell -ExecutionPolicy Bypass -File .codex/skills/scripts/validate_skills.ps1 <skill_dir> [<skill_dir> ...]"
  exit 1
}

$env:PYTHONUTF8 = "1"
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()

$validator = "C:\Users\HP\.codex\skills\.system\skill-creator\scripts\quick_validate.py"

foreach ($skill in $args) {
  python $validator $skill
  if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
  }
}
