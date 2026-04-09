$ErrorActionPreference = "Stop"
$taskName = "KnowledgeWikiAutoUpdate"
$runValueName = "KnowledgeWikiAutoUpdate"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$runner = Join-Path $scriptDir "run_auto_update_wiki.ps1"
$runKey = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run"
$runCommand = "powershell.exe -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$runner`""

if (Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue) {
  Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
}
if (Get-ItemProperty -Path $runKey -Name $runValueName -ErrorAction SilentlyContinue) {
  Remove-ItemProperty -Path $runKey -Name $runValueName -ErrorAction SilentlyContinue
}

try {
  $action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$runner`""
  $triggerLogon = New-ScheduledTaskTrigger -AtLogOn
  $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -Hidden -RestartCount 999 -RestartInterval (New-TimeSpan -Minutes 1)
  $principal = New-ScheduledTaskPrincipal -UserId "$($env:USERDOMAIN)\$($env:USERNAME)" -LogonType Interactive -RunLevel Limited
  Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $triggerLogon -Settings $settings -Principal $principal -Force | Out-Null
  Start-ScheduledTask -TaskName $taskName
  Write-Output "installed_task=$taskName"
}
catch {
  Set-ItemProperty -Path $runKey -Name $runValueName -Value $runCommand
  Start-Process -WindowStyle Hidden -FilePath "powershell.exe" -ArgumentList "-NoProfile","-WindowStyle","Hidden","-ExecutionPolicy","Bypass","-File",$runner | Out-Null
  Write-Output "installed_run_key=$runValueName"
}
