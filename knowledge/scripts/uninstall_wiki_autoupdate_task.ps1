$ErrorActionPreference = "Stop"
$taskName = "KnowledgeWikiAutoUpdate"
$runValueName = "KnowledgeWikiAutoUpdate"
$runKey = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run"
$startupDir = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs\Startup"
$startupCmd = Join-Path $startupDir "KnowledgeWikiAutoUpdate.cmd"
if (Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue) {
  Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
  Write-Output "removed_task=$taskName"
} else {
  Write-Output "task_not_found=$taskName"
}
if ((Get-ItemProperty -Path $runKey -Name $runValueName -ErrorAction SilentlyContinue)) {
  Remove-ItemProperty -Path $runKey -Name $runValueName -ErrorAction SilentlyContinue
  Write-Output "removed_run_key=$runValueName"
}
if (Test-Path $startupCmd) {
  Remove-Item -Path $startupCmd -Force
  Write-Output "removed_startup=$startupCmd"
}
