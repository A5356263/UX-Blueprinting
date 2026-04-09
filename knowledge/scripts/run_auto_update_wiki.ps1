$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$knowledgeRoot = Split-Path -Parent $scriptDir
$autoScript = Join-Path $scriptDir "auto_update_wiki.py"
$reportsDir = Join-Path $knowledgeRoot "outputs\reports"
$runnerLog = Join-Path $reportsDir "auto_update_runner.log"
New-Item -ItemType Directory -Path $reportsDir -Force | Out-Null
Set-Location $knowledgeRoot
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if ($pythonCmd) {
  $pythonExe = $pythonCmd.Source
  $pythonArgs = @($autoScript, "--run-on-start")
} else {
  $pythonExe = "py"
  $pythonArgs = @("-3", $autoScript, "--run-on-start")
}
while ($true) {
  $startAt = (Get-Date).ToString("s")
  Add-Content -Path $runnerLog -Encoding UTF8 -Value "[$startAt] runner_start exe=$pythonExe"
  & $pythonExe @pythonArgs
  $exitCode = $LASTEXITCODE
  $exitAt = (Get-Date).ToString("s")
  Add-Content -Path $runnerLog -Encoding UTF8 -Value "[$exitAt] runner_exit code=$exitCode"
  Start-Sleep -Seconds 10
}
