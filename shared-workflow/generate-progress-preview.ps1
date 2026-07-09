param(
  [string]$TemplatePath = "shared-workflow/progress-preview.html",
  [string]$OutputPath = "spark-output/progress-preview.html"
)

$ErrorActionPreference = "Stop"

function Get-PreviewHint {
  param(
    [string[]]$DependsOn,
    [hashtable]$DoneMap,
    [hashtable]$NameMap
  )

  if (-not $DependsOn -or $DependsOn.Count -eq 0) {
    return $null
  }

  foreach ($dep in $DependsOn) {
    if (-not $DoneMap.ContainsKey($dep) -or -not $DoneMap[$dep]) {
      if ($NameMap.ContainsKey($dep)) {
        return $NameMap[$dep]
      }
      return $null
    }
  }

  return $null
}

try {
  $templateRaw = Get-Content -Raw -Encoding UTF8 $TemplatePath
  $configJson = @'
{
  "phases": [
    {
      "id": "explore",
      "number": "01",
      "name_zh": "\u63a2\u7d22",
      "name_en": "Explore",
      "skills": [
        {
          "id": "uxb",
          "name_zh": "\u9700\u6c42\u5b9a\u6848",
          "slash": "/uxb",
          "context": "spark-output/context/uxb.json",
          "depends_on": []
        }
      ]
    },
    {
      "id": "define",
      "number": "02",
      "name_zh": "\u5b9a\u4e49",
      "name_en": "Define",
      "skills": [
        {
          "id": "journey-analysis",
          "name_zh": "\u7528\u6237\u65c5\u7a0b",
          "slash": "/journey",
          "context": "spark-output/context/journey-analysis.json",
          "depends_on": ["uxb"]
        },
        {
          "id": "experience-blueprint",
          "name_zh": "\u4f53\u9a8c\u84dd\u56fe",
          "slash": "/blueprint",
          "context": "spark-output/context/experience-blueprint.json",
          "depends_on": ["uxb"]
        },
        {
          "id": "page-spec",
          "name_zh": "\u9875\u9762\u89c4\u683c",
          "slash": "/page-spec",
          "context": "spark-output/context/page-spec.json",
          "depends_on": ["experience-blueprint"]
        }
      ]
    },
    {
      "id": "design",
      "number": "03",
      "name_zh": "\u8bbe\u8ba1",
      "name_en": "Design",
      "skills": [
        {
          "id": "xft-design",
          "name_zh": "\u9875\u9762\u539f\u578b",
          "slash": "/xft-design",
          "context": "spark-output/context/xft-design.json",
          "depends_on": ["page-spec"]
        },
        {
          "id": "edge",
          "name_zh": "\u5f02\u5e38\u6001",
          "slash": "/edge",
          "context": "spark-output/context/edge.json",
          "depends_on": ["experience-blueprint"]
        },
        {
          "id": "board",
          "name_zh": "\u89c6\u89c9\u60c5\u7eea\u677f",
          "slash": "/board",
          "context": "spark-output/context/board.json",
          "depends_on": ["experience-blueprint"]
        },
        {
          "id": "check",
          "name_zh": "\u8bbe\u8ba1\u8d70\u67e5",
          "slash": "/check",
          "context": "spark-output/context/check.json",
          "depends_on": ["experience-blueprint"]
        }
      ]
    }
  ]
}
'@
  $config = $configJson | ConvertFrom-Json

  $nameMap = @{}
  $doneMap = @{}
  $orderedSkills = New-Object System.Collections.Generic.List[object]

  foreach ($phase in $config.phases) {
    foreach ($skill in $phase.skills) {
      $nameMap[$skill.id] = $skill.slash
      $doneMap[$skill.id] = Test-Path $skill.context
      $orderedSkills.Add([pscustomobject]@{
        id = $skill.id
        depends_on = @($skill.depends_on)
      })
    }
  }

  $currentSkillId = $null
  foreach ($skill in $orderedSkills) {
    if ($doneMap[$skill.id]) {
      continue
    }

    $ready = $true
    foreach ($dep in @($skill.depends_on)) {
      if (-not $doneMap.ContainsKey($dep) -or -not $doneMap[$dep]) {
        $ready = $false
        break
      }
    }

    if ($ready) {
      $currentSkillId = $skill.id
      break
    }
  }

  $phaseStates = @()
  foreach ($phase in $config.phases) {
    $skills = @()
    foreach ($skill in $phase.skills) {
      $status = "idle"
      if ($doneMap[$skill.id]) {
        $status = "done"
      } elseif ($currentSkillId -and $skill.id -eq $currentSkillId) {
        $status = "current"
      }

      $skills += [pscustomobject]@{
        id = $skill.id
        name_zh = $skill.name_zh
        slash = $skill.slash
        status = $status
        hint_dep = Get-PreviewHint -DependsOn @($skill.depends_on) -DoneMap $doneMap -NameMap $nameMap
      }
    }

    $phaseStates += [pscustomobject]@{
      id = $phase.id
      number = $phase.number
      name_zh = $phase.name_zh
      name_en = $phase.name_en
      skills = $skills
    }
  }

  $state = [pscustomobject]@{
    generated_at = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    phases = $phaseStates
  }

  $stateJson = $state | ConvertTo-Json -Depth 8
  $injectScript = "<script>window.__PREVIEW_STATE__ = $stateJson;</script>"
  $html = $templateRaw.Replace("<!--__PREVIEW_STATE_INJECT__-->", $injectScript)

  $outputDir = Split-Path -Parent $OutputPath
  if (-not (Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir | Out-Null
  }

  $resolvedOutputDir = (Resolve-Path $outputDir).Path
  $resolvedOutputPath = Join-Path $resolvedOutputDir (Split-Path -Leaf $OutputPath)
  [System.IO.File]::WriteAllText($resolvedOutputPath, $html, [System.Text.Encoding]::UTF8)

  Write-Output "OK: $resolvedOutputPath"
}
catch {
  Write-Warning "Progress preview refresh skipped: $($_.Exception.Message)"
}
