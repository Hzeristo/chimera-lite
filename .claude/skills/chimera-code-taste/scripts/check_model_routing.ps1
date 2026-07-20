#!/usr/bin/env pwsh
# Tier-1 static self-check for the model-routing rules (docs/audits/model-routing-gaps.md).
# Usage: .claude/skills/chimera-code-taste/scripts/check_model_routing.ps1
#
# Verifies ONLY the mechanically-enforced pieces — the ones a grep can actually prove:
#   1. Every chimera agent def carries a `model:` pin, and none is `opus`.
#   2. Fidelity guard: chimera-verbatim-verifier stays pinned `sonnet` (never downgraded).
#   3. The three pinned dev-worker types exist.
#   4. Regime-(b) fragility is absent from skills: no inline `{model:}` param, no
#      `general-purpose` spawn, no `opus` worker.
#   5. The W1/W2 orchestration skills carry an <expected_model> guardrail.
#
# It CANNOT verify the advisory "Opus is an orchestrator" posture — that is behavioral,
# measured in token telemetry, not by inspection. Do not pretend otherwise here.
#
# Exit-code contract (matches check_taste.ps1): 0 = every check passed; 1 = one or more
# failed. Runs all checks (not fail-fast) so a single run reports every problem.

$ErrorActionPreference = 'Stop'

# cwd-independent: resolve repo root from this script's location (skill lives 4 deep).
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..' '..' '..' '..')).Path
$agentsDir = Join-Path $repoRoot '.claude/agents'
$skillsDir = Join-Path $repoRoot '.claude/skills'

$fail = 0
function Pass($m) { Write-Host "[PASS] $m" -ForegroundColor Green }
function Fail($m) { Write-Host "[FAIL] $m" -ForegroundColor Red; $script:fail++ }
function Section($m) { Write-Host "`n=== $m ===" -ForegroundColor Cyan }

# --- Check 1: agent pins present + never opus ---------------------------------------
Section "1. agent model pins (regime-(a))"
$agentFiles = Get-ChildItem -Path (Join-Path $agentsDir 'chimera-*.md') -File
if (-not $agentFiles) { Fail "no chimera-*.md agent defs found under $agentsDir" }
foreach ($a in $agentFiles) {
    $raw = Get-Content $a.FullName -Raw
    if ($raw -match '(?m)^model:\s*(.+?)\s*$') {
        $model = $Matches[1].Trim().Trim('"').Trim("'")
        if ($model -eq 'opus') {
            Fail "$($a.Name): pinned to opus — a worker must never be Opus"
        } elseif ($model -in @('sonnet', 'haiku')) {
            Pass "$($a.Name): pinned $model"
        } else {
            Fail "$($a.Name): model '$model' not in {sonnet, haiku}"
        }
    } else {
        Fail "$($a.Name): no 'model:' pin — would inherit the session model"
    }
}

# --- Check 2: fidelity guard — verbatim-verifier stays sonnet -----------------------
Section "2. fidelity guard (verbatim-verifier)"
$vv = Join-Path $agentsDir 'chimera-verbatim-verifier.md'
if (Test-Path $vv) {
    if ((Get-Content $vv -Raw) -match '(?m)^model:\s*sonnet\s*$') {
        Pass "chimera-verbatim-verifier pinned sonnet (fidelity-critical; do not downgrade)"
    } else {
        Fail "chimera-verbatim-verifier must stay pinned sonnet — do NOT downgrade to haiku"
    }
} else {
    Fail "chimera-verbatim-verifier.md missing"
}

# --- Check 3: pinned dev-worker types exist -----------------------------------------
Section "3. pinned dev-worker types exist"
foreach ($t in 'chimera-sprint-executor', 'chimera-verify-runner', 'chimera-repo-scout') {
    if (Test-Path (Join-Path $agentsDir "$t.md")) { Pass "exists: $t" }
    else { Fail "missing pinned agent type: $t" }
}

# --- Check 4: no regime-(b) fragility in skills -------------------------------------
Section "4. no regime-(b) call-site binding in skills"
$skillMd = Get-ChildItem -Path $skillsDir -Recurse -File -Filter *.md
$patterns = [ordered]@{
    'inline {model:} param'   = '\{model:\s*["'']'
    'general-purpose spawn'   = 'subagent_type:\s*["'']?general-purpose'
    'opus worker pin'         = 'model:\s*["'']?opus'
}
foreach ($name in $patterns.Keys) {
    $hits = $skillMd | Select-String -Pattern $patterns[$name] -CaseSensitive:$false
    if ($hits) {
        foreach ($h in $hits) {
            $rel = $h.Path.Replace($repoRoot, '').TrimStart('\', '/')
            Fail "regime-(b) [$name] $rel`:$($h.LineNumber) -> $($h.Line.Trim())"
        }
    } else {
        Pass "no regime-(b) [$name] in skills"
    }
}

# --- Check 5: W1/W2 orchestration skills carry <expected_model> ---------------------
Section "5. W1/W2 orchestration guardrail"
foreach ($s in 'chimera-w1-verify', 'chimera-w2-map') {
    $p = Join-Path $skillsDir "$s/SKILL.md"
    if ((Test-Path $p) -and ((Get-Content $p -Raw) -match '<expected_model>')) {
        Pass "$s has <expected_model>"
    } else {
        Fail "$s missing <expected_model> guardrail"
    }
}

# --- Verdict ------------------------------------------------------------------------
if ($fail -eq 0) {
    Write-Host "`n=== model-routing check complete: all passed ===" -ForegroundColor Green
    exit 0
} else {
    Write-Host "`n=== model-routing check FAILED: $fail problem(s) ===" -ForegroundColor Red
    exit 1
}
