param(
  [string]$TemplatePath = "shared-workflow/progress-preview.html",
  [string]$GraphPath = "shared-workflow/skill-graph.json",
  [string]$OutputPath = "spark-output/progress-preview.html"
)

$ErrorActionPreference = "Stop"

function Get-SlashAlias {
  param([string]$SkillId)

  $aliasMap = @{
    "prd-review" = "/prd-review"
    "uxb" = "/uxb"
    "problem-framing" = "/problem-framing"
    "stories" = "/stories"
    "journey-analysis" = "/journey-analysis"
    "experience-blueprint" = "/experience-blueprint"
    "solution-swimlane" = "/solution-swimlane"
    "page-spec" = "/page-spec"
    "edge" = "/edge"
    "board" = "/board"
    "knowledge-wiki" = "/knowledge-wiki"
    "journey-metrics" = "/journey-metrics"
  }

  if ($aliasMap.ContainsKey($SkillId)) {
    return $aliasMap[$SkillId]
  }

  return "/$SkillId"
}

function Get-ContextPath {
  param([string]$SkillId)

  $contextMap = @{
    "prd-review" = "spark-output/context/requirements-baseline.json"
    "uxb" = "spark-output/context/uxb.json"
    "problem-framing" = "spark-output/context/problem-framing.json"
    "stories" = "spark-output/context/stories.json"
    "journey-analysis" = "spark-output/context/journey-analysis.json"
    "experience-blueprint" = "spark-output/context/experience-blueprint.json"
    "solution-swimlane" = "spark-output/solution-swimlane/solution_swimlane.html"
    "page-spec" = "spark-output/context/page-spec.json"
    "edge" = "spark-output/context/edge.json"
    "board" = "spark-output/context/board.json"
    "knowledge-wiki" = "spark-output/context/knowledge-wiki.json"
    "journey-metrics" = "spark-output/context/journey-metrics.json"
  }

  if ($contextMap.ContainsKey($SkillId)) {
    return $contextMap[$SkillId]
  }

  return $null
}

function Get-SectionMeta {
  param([pscustomobject]$Skill)

  $sectionBySkillId = @{
    "prd-review" = [pscustomobject]@{
      id = "requirements-problem"
      number = "01"
      name_zh = "需求与问题"
      name_en = "Requirements & Problem"
      note = "审核需求或基于问题形成业务方案"
      order = 1
    }
    "problem-framing" = [pscustomobject]@{
      id = "requirements-problem"
      number = "01"
      name_zh = "需求与问题"
      name_en = "Requirements & Problem"
      note = "审核需求或基于问题形成业务方案"
      order = 1
    }
    "stories" = [pscustomobject]@{
      id = "task-journey"
      number = "02"
      name_zh = "任务与旅程"
      name_en = "Task & Journey"
      note = "拆解用户任务，梳理用户完成过程"
      order = 2
    }
    "journey-analysis" = [pscustomobject]@{
      id = "task-journey"
      number = "02"
      name_zh = "任务与旅程"
      name_en = "Task & Journey"
      note = "拆解用户任务，梳理用户完成过程"
      order = 2
    }
    "experience-blueprint" = [pscustomobject]@{
      id = "experience-design"
      number = "03"
      name_zh = "体验与设计"
      name_en = "Experience & Design"
      note = "形成体验策略并输出交互方案"
      order = 3
    }
    "solution-swimlane" = [pscustomobject]@{
      id = "experience-design"
      number = "03"
      name_zh = "体验与设计"
      name_en = "Experience & Design"
      note = "形成体验策略并输出交互方案"
      order = 3
    }
    "page-spec" = [pscustomobject]@{
      id = "page-build"
      number = "04"
      name_zh = "页面生成"
      name_en = "Page Build"
      note = "提取设计元素"
      order = 4
    }
    "journey-metrics" = [pscustomobject]@{
      id = "validate"
      number = "05"
      name_zh = "验证"
      name_en = "Validate"
      note = "定义关键节点的埋点与度量口径"
      order = 5
    }
    "knowledge-wiki" = [pscustomobject]@{
      id = "deliver"
      number = "06"
      name_zh = "沉淀"
      name_en = "Archive"
      note = "产物归档、知识沉淀与后续复用"
      order = 6
    }
  }

  if ($sectionBySkillId.ContainsKey($Skill.id)) {
    return $sectionBySkillId[$Skill.id]
  }

  return [pscustomobject]@{
    id = "experience-design"
    number = "03"
    name_zh = "体验与设计"
    name_en = "Experience & Design"
    note = "形成体验策略并输出交互方案"
    order = 3
  }
}

function Test-SkillReady {
  param(
    [pscustomobject]$Skill,
    [hashtable]$DoneMap
  )

  foreach ($dep in @($Skill.required)) {
    if (-not $DoneMap.ContainsKey($dep) -or -not $DoneMap[$dep]) {
      return $false
    }
  }

  return $true
}

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
  $graph = Get-Content -Raw -Encoding UTF8 $GraphPath | ConvertFrom-Json

  $nameMap = @{}
  $doneMap = @{}
  $enhancementMap = @{}
  $mainChainMap = @{}
  $sectionsMap = @{}

  foreach ($skillId in @($graph.main_chain)) {
    $mainChainMap[$skillId] = $true
  }

  foreach ($group in @($graph.enhancements)) {
    foreach ($skillId in @($group.skills)) {
      $enhancementMap[$skillId] = $group.before
    }
  }

  for ($i = 0; $i -lt $graph.skills.Count; $i++) {
    $skill = $graph.skills[$i]
    $nameMap[$skill.id] = Get-SlashAlias -SkillId $skill.id

    $contextPath = Get-ContextPath -SkillId $skill.id
    $doneMap[$skill.id] = $false
    if ($contextPath) {
      $doneMap[$skill.id] = Test-Path $contextPath
    }

    if ($skill.preview_hidden -eq $true) {
      continue
    }

    $sectionMeta = Get-SectionMeta -Skill $skill
    if (-not $sectionsMap.ContainsKey($sectionMeta.id)) {
      $sectionsMap[$sectionMeta.id] = [pscustomobject]@{
        id = $sectionMeta.id
        number = $sectionMeta.number
        name_zh = $sectionMeta.name_zh
        name_en = $sectionMeta.name_en
        note = $sectionMeta.note
        order = $sectionMeta.order
        skills = New-Object System.Collections.Generic.List[object]
      }
    }

    $sectionsMap[$sectionMeta.id].skills.Add($skill)
  }

  $currentSkillId = $null
  foreach ($skillId in @($graph.main_chain)) {
    if (-not $doneMap[$skillId]) {
      $currentSkillId = $skillId
      break
    }
  }

  $sectionStates = @()
  $sortedSections = $sectionsMap.Values | Sort-Object order
  foreach ($section in $sortedSections) {
    $skillStates = @()
    foreach ($skill in $section.skills) {
      $status = "idle"
      if ($doneMap[$skill.id]) {
        $status = "done"
      } elseif ($currentSkillId -and $skill.id -eq $currentSkillId) {
        $status = "current"
      } elseif ($mainChainMap.ContainsKey($skill.id)) {
        $status = "idle"
      } elseif (Test-SkillReady -Skill $skill -DoneMap $doneMap) {
        $status = "ready"
      }

      $skillStates += [pscustomobject]@{
        id = $skill.id
        name_zh = $skill.name_zh
        slash = $nameMap[$skill.id]
        status = $status
        hint_dep = Get-PreviewHint -DependsOn @($skill.required) -DoneMap $doneMap -NameMap $nameMap
        is_enhancement = $enhancementMap.ContainsKey($skill.id)
        enhances_before = $(if ($enhancementMap.ContainsKey($skill.id)) { $enhancementMap[$skill.id] } else { $null })
        standalone_usable = [bool]$skill.standalone_usable
        standalone_note = $skill.standalone_note
      }
    }

    $sectionStates += [pscustomobject]@{
      id = $section.id
      number = $section.number
      name_zh = $section.name_zh
      name_en = $section.name_en
      note = $section.note
      skills = $skillStates
    }
  }

  $state = [pscustomobject]@{
    generated_at = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    main_chain = @($graph.main_chain)
    enhancements = @($graph.enhancements)
    sections = $sectionStates
  }

  $stateJson = $state | ConvertTo-Json -Depth 10
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
