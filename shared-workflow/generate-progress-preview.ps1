param(
  [string]$TemplatePath = "shared-workflow/progress-preview.html",
  [string]$GraphPath = "shared-workflow/skill-graph.json",
  [string]$OutputPath = "spark-output/progress-preview.html"
)

$ErrorActionPreference = "Stop"

function Get-SlashAlias {
  param([string]$SkillId)

  $aliasMap = @{
    "uxb" = "/uxb"
    "problem-framing" = "/problem-framing"
    "stories" = "/stories"
    "journey-analysis" = "/journey-analysis"
    "experience-blueprint" = "/experience-blueprint"
    "page-spec" = "/page-spec"
    "xft-design" = "/xft-design"
    "edge" = "/edge"
    "check" = "/check"
    "board" = "/board"
    "knowledge-wiki" = "/knowledge-wiki"
    "product-analysis" = "/product-analysis"
    "design-strategy" = "/design-strategy"
    "journey-metrics" = "/journey-metrics"
    "interface-audit" = "/interface-audit"
  }

  if ($aliasMap.ContainsKey($SkillId)) {
    return $aliasMap[$SkillId]
  }

  return "/$SkillId"
}

function Get-ContextPath {
  param([string]$SkillId)

  $contextMap = @{
    "uxb" = "spark-output/context/uxb.json"
    "problem-framing" = "spark-output/context/problem-framing.json"
    "stories" = "spark-output/context/stories.json"
    "journey-analysis" = "spark-output/context/journey-analysis.json"
    "experience-blueprint" = "spark-output/context/experience-blueprint.json"
    "page-spec" = "spark-output/context/page-spec.json"
    "xft-design" = "spark-output/context/xft-design.json"
    "edge" = "spark-output/context/edge.json"
    "check" = "spark-output/context/check.json"
    "board" = "spark-output/context/board.json"
    "knowledge-wiki" = "spark-output/context/knowledge-wiki.json"
    "product-analysis" = "spark-output/context/product-analysis.json"
    "design-strategy" = "spark-output/context/design-strategy.json"
    "journey-metrics" = "spark-output/context/journey-metrics.json"
    "interface-audit" = "spark-output/context/interface-audit.json"
  }

  if ($contextMap.ContainsKey($SkillId)) {
    return $contextMap[$SkillId]
  }

  return $null
}

function Get-SectionMeta {
  param([pscustomobject]$Skill)

  $sectionBySkillId = @{
    "product-analysis" = [pscustomobject]@{
      id = "explore"
      number = "01"
      name_zh = "探索"
      name_en = "Explore"
      note = "需求读取、问题诊断与方向收敛"
      order = 1
    }
    "interface-audit" = [pscustomobject]@{
      id = "explore"
      number = "01"
      name_zh = "探索"
      name_en = "Explore"
      note = "需求读取、问题诊断与方向收敛"
      order = 1
    }
    "design-strategy" = [pscustomobject]@{
      id = "explore"
      number = "01"
      name_zh = "探索"
      name_en = "Explore"
      note = "需求读取、问题诊断与方向收敛"
      order = 1
    }
    "uxb" = [pscustomobject]@{
      id = "explore"
      number = "01"
      name_zh = "探索"
      name_en = "Explore"
      note = "需求读取、问题诊断与方向收敛"
      order = 1
    }
    "problem-framing" = [pscustomobject]@{
      id = "explore"
      number = "01"
      name_zh = "探索"
      name_en = "Explore"
      note = "需求读取、问题诊断与方向收敛"
      order = 1
    }
    "stories" = [pscustomobject]@{
      id = "define"
      number = "02"
      name_zh = "定义"
      name_en = "Define"
      note = "用户故事、旅程结构与需求补全"
      order = 2
    }
    "journey-analysis" = [pscustomobject]@{
      id = "define"
      number = "02"
      name_zh = "定义"
      name_en = "Define"
      note = "用户故事、旅程结构与需求补全"
      order = 2
    }
    "experience-blueprint" = [pscustomobject]@{
      id = "design"
      number = "03"
      name_zh = "设计"
      name_en = "Design"
      note = "方案生成、规格细化与页面落地"
      order = 3
    }
    "board" = [pscustomobject]@{
      id = "design"
      number = "03"
      name_zh = "设计"
      name_en = "Design"
      note = "方案生成、规格细化与页面落地"
      order = 3
    }
    "page-spec" = [pscustomobject]@{
      id = "design"
      number = "03"
      name_zh = "设计"
      name_en = "Design"
      note = "方案生成、规格细化与页面落地"
      order = 3
    }
    "xft-design" = [pscustomobject]@{
      id = "design"
      number = "03"
      name_zh = "设计"
      name_en = "Design"
      note = "方案生成、规格细化与页面落地"
      order = 3
    }
    "edge" = [pscustomobject]@{
      id = "validate"
      number = "04"
      name_zh = "验证"
      name_en = "Validate"
      note = "异常覆盖、质量校验与度量口径"
      order = 4
    }
    "check" = [pscustomobject]@{
      id = "validate"
      number = "04"
      name_zh = "验证"
      name_en = "Validate"
      note = "异常覆盖、质量校验与度量口径"
      order = 4
    }
    "journey-metrics" = [pscustomobject]@{
      id = "validate"
      number = "04"
      name_zh = "验证"
      name_en = "Validate"
      note = "异常覆盖、质量校验与度量口径"
      order = 4
    }
    "knowledge-wiki" = [pscustomobject]@{
      id = "deliver"
      number = "05"
      name_zh = "沉淀"
      name_en = "Archive"
      note = "产物归档、知识沉淀与后续复用"
      order = 5
    }
  }

  if ($sectionBySkillId.ContainsKey($Skill.id)) {
    return $sectionBySkillId[$Skill.id]
  }

  return [pscustomobject]@{
    id = "design"
    number = "03"
    name_zh = "设计"
    name_en = "Design"
    note = "方案生成、规格细化与页面落地"
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
  $skillOrder = @{}
  $mainChainSkills = New-Object System.Collections.Generic.List[object]
  $sectionsMap = @{}

  for ($i = 0; $i -lt $graph.skills.Count; $i++) {
    $skill = $graph.skills[$i]
    $skillOrder[$skill.id] = $i
    $nameMap[$skill.id] = Get-SlashAlias -SkillId $skill.id

    $contextPath = Get-ContextPath -SkillId $skill.id
    $doneMap[$skill.id] = $false
    if ($contextPath) {
      $doneMap[$skill.id] = Test-Path $contextPath
    }

    if ($skill.type -ne "infrastructure" -and $null -ne $skill.phase) {
      $mainChainSkills.Add([pscustomobject]@{
        id = $skill.id
        phase = [double]$skill.phase
        required = @($skill.required)
        order = $i
      })
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

  $sortedMainChain = $mainChainSkills | Sort-Object phase, order
  $currentSkillId = $null
  foreach ($skill in $sortedMainChain) {
    if ($doneMap[$skill.id]) {
      continue
    }

    $ready = $true
    foreach ($dep in @($skill.required)) {
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
      } elseif (Test-SkillReady -Skill $skill -DoneMap $doneMap) {
        $status = "ready"
      }

      $skillStates += [pscustomobject]@{
        id = $skill.id
        name_zh = $skill.name_zh
        slash = $nameMap[$skill.id]
        status = $status
        hint_dep = Get-PreviewHint -DependsOn @($skill.required) -DoneMap $doneMap -NameMap $nameMap
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
