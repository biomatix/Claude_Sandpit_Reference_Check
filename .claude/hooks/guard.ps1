#requires -Version 5.1
<#
PreToolUse safety guard for the reference-check sandpit.

Purpose:
  1. Block Edit / Write / NotebookEdit tool calls whose target file is
     outside the sandpit root.
  2. Block Edit / Write / NotebookEdit tool calls whose target is
     jobs/<other-slug>/... when the active job is <slug>.
  3. Best-effort scan of Bash commands for obvious write-out-of-bounds
     patterns (redirects, tee, Set-Content, Out-File, Add-Content,
     New-Item -Path, rm -rf with absolute paths).

Protocol:
  Reads the Claude Code hook JSON from stdin.
  Exits 0 to allow.
  Exits 2 with a reason on stderr to block (Claude sees the message).
#>

$ErrorActionPreference = "Stop"
[Console]::InputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# ---------- Read the hook payload ----------
$raw = [Console]::In.ReadToEnd()
if ([string]::IsNullOrWhiteSpace($raw)) { exit 0 }

try {
    $hook = $raw | ConvertFrom-Json
} catch {
    # If parsing fails, fail open with a stderr note so the user sees the
    # broken hook rather than a silent block.
    [Console]::Error.WriteLine("guard.ps1: could not parse hook JSON: $_")
    exit 0
}

$tool = [string]$hook.tool_name
$cwd  = [string]$hook.cwd

# ---------- Locate the sandpit root ----------
# The sandpit is identified by the presence of `.claude/CLAUDE.md`. Walk
# upward from cwd; if not found, fall back to cwd itself.
function Find-SandpitRoot {
    param([string]$StartDir)
    if ([string]::IsNullOrWhiteSpace($StartDir)) { return $null }
    $dir = $StartDir
    while ($true) {
        $candidate = Join-Path $dir ".claude/CLAUDE.md"
        if (Test-Path -LiteralPath $candidate) { return $dir }
        $parent = Split-Path -Parent $dir
        if ([string]::IsNullOrWhiteSpace($parent) -or $parent -eq $dir) { return $null }
        $dir = $parent
    }
}

$sandpit_root = Find-SandpitRoot $cwd
if ($null -eq $sandpit_root) {
    # No sandpit detected. Open behaviour: don't enforce. The hook is meant
    # to run inside the sandpit; if it doesn't, the user is doing something
    # else and we shouldn't interfere.
    exit 0
}
$sandpit_root = (Resolve-Path -LiteralPath $sandpit_root).Path

function Get-CanonicalPath {
    param([string]$Path, [string]$BaseDir)
    if ([string]::IsNullOrWhiteSpace($Path)) { return $null }
    if ([System.IO.Path]::IsPathRooted($Path)) {
        $abs = $Path
    } else {
        $abs = Join-Path $BaseDir $Path
    }
    # GetFullPath resolves .., ., and slashes without requiring the file to exist.
    return [System.IO.Path]::GetFullPath($abs)
}

function Test-PathInSandpit {
    param([string]$Path)
    if ($null -eq $Path) { return $true }
    $canonical = (Get-CanonicalPath $Path $sandpit_root).TrimEnd('\').ToLower()
    $root = $sandpit_root.TrimEnd('\').ToLower()
    return ($canonical -eq $root) -or $canonical.StartsWith($root + '\')
}

function Get-PathJobSlug {
    # Returns the job slug if the path resolves under jobs/<slug>/, else $null.
    param([string]$Path)
    if ($null -eq $Path) { return $null }
    $canonical = (Get-CanonicalPath $Path $sandpit_root).ToLower()
    $jobs_root = (Join-Path $sandpit_root 'jobs').ToLower()
    if ($canonical.StartsWith($jobs_root + '\')) {
        $rel = $canonical.Substring($jobs_root.Length + 1)
        return ($rel.Split('\') | Select-Object -First 1)
    }
    return $null
}

function Get-ActiveJob {
    $pin = Join-Path $sandpit_root '.claude/active_job'
    if (Test-Path -LiteralPath $pin) {
        $content = (Get-Content -LiteralPath $pin -Raw).Trim()
        if (-not [string]::IsNullOrWhiteSpace($content)) { return $content.ToLower() }
    }
    return $null
}

function Test-PathIsClaudeSystemFile {
    # Plan-mode writes plan files into ~/.claude/plans/*.md, which lives
    # outside any project sandpit. Treat that exact subdirectory as a
    # system carve-out so plan mode functions correctly.
    param([string]$Path)
    if ($null -eq $Path) { return $false }
    $canonical = (Get-CanonicalPath $Path $sandpit_root).TrimEnd('\').ToLower()
    $home_dir = $env:USERPROFILE
    if ([string]::IsNullOrWhiteSpace($home_dir)) { return $false }
    $plans_dir = (Join-Path $home_dir '.claude/plans').ToLower().TrimEnd('\')
    return $canonical.StartsWith($plans_dir + '\') -and $canonical.EndsWith('.md')
}

function Test-PathIsTempFile {
    # Carve-out for system temp directories. The harness sometimes stages
    # short-lived files (heredoc fragments, downloads in flight); these
    # belong in TEMP, not the sandpit.
    # Allowed roots:
    #   - /tmp (POSIX / MinGW bash on Windows; matched on the RAW path
    #     because Windows GetFullPath silently rebases /tmp onto the
    #     current drive)
    #   - $env:TEMP and $env:TMP (Windows; typically ...\AppData\Local\Temp)
    # The carve-out applies to files inside these roots, not the roots
    # themselves, and is independent of file extension.
    param([string]$Path)
    if ($null -eq $Path) { return $false }

    # Raw-path check first, BEFORE canonicalisation, so the POSIX /tmp
    # token is recognised on Windows (where GetFullPath would otherwise
    # rebase it to the current drive's \tmp).
    $normRaw = $Path.Replace('\', '/').ToLower()
    if ($normRaw.StartsWith('/tmp/')) { return $true }

    $canonical = (Get-CanonicalPath $Path $sandpit_root).TrimEnd('\').ToLower()
    foreach ($var in @($env:TEMP, $env:TMP)) {
        if ([string]::IsNullOrWhiteSpace($var)) { continue }
        try {
            $root = ([System.IO.Path]::GetFullPath($var)).TrimEnd('\').ToLower()
            if ($canonical.StartsWith($root + '\')) { return $true }
        } catch { }
    }
    return $false
}

function Reject {
    param([string]$Reason)
    [Console]::Error.WriteLine($Reason)
    exit 2
}

# ---------- Edit / Write / NotebookEdit ----------
if ($tool -in @('Edit', 'Write', 'NotebookEdit', 'MultiEdit')) {
    $path = $null
    if ($null -ne $hook.tool_input.file_path) { $path = [string]$hook.tool_input.file_path }
    elseif ($null -ne $hook.tool_input.path)  { $path = [string]$hook.tool_input.path }
    elseif ($null -ne $hook.tool_input.notebook_path) { $path = [string]$hook.tool_input.notebook_path }

    if ($null -eq $path -or [string]::IsNullOrWhiteSpace($path)) { exit 0 }

    # System carve-out: plan-mode writes into ~/.claude/plans/*.md.
    if (Test-PathIsClaudeSystemFile $path) { exit 0 }

    # Temp-dir carve-out: short-lived staging files in $env:TEMP, $env:TMP,
    # or /tmp are fine — they're not part of the sandpit's archived state.
    if (Test-PathIsTempFile $path) { exit 0 }

    if (-not (Test-PathInSandpit $path)) {
        Reject "BLOCKED by guard.ps1: $tool target '$path' resolves outside the sandpit root '$sandpit_root'. Sandpit-bound writes only."
    }

    $target_job = Get-PathJobSlug $path
    if ($null -ne $target_job) {
        $active = Get-ActiveJob
        if ($null -eq $active) {
            Reject "BLOCKED by guard.ps1: $tool target '$path' is in jobs/$target_job/ but no active job is pinned. Run /switch-job <slug> or /new-job <slug> first."
        }
        if ($target_job -ne $active) {
            Reject "BLOCKED by guard.ps1: $tool target '$path' is in jobs/$target_job/, but the active job is '$active'. Use /switch-job to change before writing to a different job."
        }
    }
    exit 0
}

# ---------- Bash: best-effort write-out-of-bounds detection ----------
if ($tool -eq 'Bash') {
    $cmd = [string]$hook.tool_input.command
    if ([string]::IsNullOrWhiteSpace($cmd)) { exit 0 }

    $active = Get-ActiveJob

    # Patterns that indicate a write is intended; capture the target path token.
    # We look for tokens of two shapes: drive-rooted (e.g. C:/Users/x or C:\Users\x)
    # and POSIX-rooted (/Users/x). We also handle relative paths inside redirect
    # constructs.
    $pathToken = '("[^"]+"|''[^'']+''|[^\s"''<>|;&]+)'

    # Builders for write-target patterns. Each pattern's group 1 is the path.
    $writePatterns = @(
        # > path  and  >> path
        ">{1,2}\s+$pathToken",
        # tee path / tee -a path
        "\btee\b(?:\s+-a)?\s+$pathToken",
        # PowerShell explicit write cmdlets
        "Out-File\s+(?:-FilePath\s+)?$pathToken",
        "Set-Content\s+(?:-(?:LiteralP|P)ath\s+)?$pathToken",
        "Add-Content\s+(?:-(?:LiteralP|P)ath\s+)?$pathToken",
        "New-Item\s+(?:-(?:LiteralP|P)ath\s+)?$pathToken",
        # rm with absolute path
        "\brm\b(?:\s+-[A-Za-z]+)*\s+$pathToken",
        "Remove-Item\s+(?:-(?:LiteralP|P)ath\s+)?$pathToken"
    )

    foreach ($pat in $writePatterns) {
        foreach ($m in [regex]::Matches($cmd, $pat)) {
            $tok = $m.Groups[1].Value.Trim('"').Trim("'")
            if ([string]::IsNullOrWhiteSpace($tok)) { continue }
            # Skip anything that doesn't look like a filesystem path
            if ($tok -match '^https?:' -or $tok -match '^http://127\.0\.0\.1' -or $tok -match '^localhost') { continue }
            if ($tok -match '^[\-\$]') { continue }   # flags or variables

            # Temp-dir carve-out (same rationale as for Edit/Write).
            if (Test-PathIsTempFile $tok) { continue }

            # Containment check
            if (-not (Test-PathInSandpit $tok)) {
                Reject "BLOCKED by guard.ps1: Bash write target '$tok' resolves outside the sandpit root '$sandpit_root'. Match: '$($m.Value)'"
            }

            # Per-job isolation
            $target_job = Get-PathJobSlug $tok
            if ($null -ne $target_job) {
                if ($null -eq $active) {
                    Reject "BLOCKED by guard.ps1: Bash write target '$tok' is in jobs/$target_job/ but no active job is pinned. Run /switch-job <slug> first."
                }
                if ($target_job -ne $active) {
                    Reject "BLOCKED by guard.ps1: Bash write target '$tok' is in jobs/$target_job/, but the active job is '$active'."
                }
            }
        }
    }

    exit 0
}

exit 0
