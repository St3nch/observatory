# M19 Backup and Restore Owner-Local Runbook

Status: authorized owner-local execution instructions
Authority: `decisions/2026-07-12-m19-bounded-backup-restore-proof-authorization.md`
Date: 2026-07-12

## Purpose

Execute one bounded repository-only Git bundle and disposable restore proof without cloud upload, credentials, automatic scheduling, database work, provider activity, or destructive cleanup.

## Fixed roots

```powershell
$SourceRepo = 'C:\dev\observatory'
$WorkRoot = 'C:\dev\observatory-backup-work'
$RestoreRoot = 'C:\dev\observatory-restore-proof'
```

## Runbook

Run in PowerShell 7 from a normal owner-controlled terminal.

```powershell
$ErrorActionPreference = 'Stop'

$SourceRepo = 'C:\dev\observatory'
$WorkRoot = 'C:\dev\observatory-backup-work'
$RestoreRoot = 'C:\dev\observatory-restore-proof'
$BundlePath = Join-Path $WorkRoot 'observatory.bundle'
$ManifestPath = Join-Path $WorkRoot 'm19-manifest.json'

function Assert-OutsideSourceRepo {
    param([string]$Candidate)
    $source = [System.IO.Path]::GetFullPath($SourceRepo).TrimEnd('\\')
    $target = [System.IO.Path]::GetFullPath($Candidate).TrimEnd('\\')
    if ($target.Equals($source, [System.StringComparison]::OrdinalIgnoreCase) -or
        $target.StartsWith($source + '\\', [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "blocked: target root overlaps source repository: $target"
    }
}

Assert-OutsideSourceRepo $WorkRoot
Assert-OutsideSourceRepo $RestoreRoot

Set-Location $SourceRepo

$status = git status --porcelain=v1
if ($LASTEXITCODE -ne 0) { throw 'blocked: git status failed' }
if ($status) { throw 'blocked: source working tree is dirty' }

$branch = (git branch --show-current).Trim()
$head = (git rev-parse HEAD).Trim()
$upstream = (git rev-parse --abbrev-ref --symbolic-full-name '@{u}').Trim()
$localHead = (git rev-parse HEAD).Trim()
$remoteHead = (git rev-parse '@{u}').Trim()
if ($localHead -ne $remoteHead) { throw 'blocked: source repository is not synced with upstream' }

if (Test-Path $WorkRoot) {
    $existing = Get-ChildItem -LiteralPath $WorkRoot -Force
    if ($existing) { throw 'blocked: work root contains pre-existing material' }
} else {
    New-Item -ItemType Directory -Path $WorkRoot | Out-Null
}

if (Test-Path $RestoreRoot) {
    $existing = Get-ChildItem -LiteralPath $RestoreRoot -Force
    if ($existing) { throw 'blocked: restore root contains pre-existing material' }
} else {
    New-Item -ItemType Directory -Path $RestoreRoot | Out-Null
}

git bundle create $BundlePath --all
if ($LASTEXITCODE -ne 0) { throw 'failed: git bundle creation failed' }

git bundle verify $BundlePath
if ($LASTEXITCODE -ne 0) { throw 'failed: git bundle verification failed' }

$bundleHash = (Get-FileHash -LiteralPath $BundlePath -Algorithm SHA256).Hash.ToLowerInvariant()
$bundleBytes = (Get-Item -LiteralPath $BundlePath).Length

$manifest = [ordered]@{
    proof_version = '1'
    source_repository_label = 'observatory'
    source_branch = $branch
    source_head = $head
    upstream = $upstream
    bundle_filename = 'observatory.bundle'
    bundle_sha256 = $bundleHash
    bundle_bytes = $bundleBytes
    encryption_status = 'blocked_pending_owner_tool_and_key_path'
    created_at = [DateTimeOffset]::UtcNow.ToString('o')
}
$manifest | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $ManifestPath -Encoding utf8NoBOM

$preRestoreHash = (Get-FileHash -LiteralPath $BundlePath -Algorithm SHA256).Hash.ToLowerInvariant()
if ($preRestoreHash -ne $bundleHash) { throw 'failed: bundle hash mismatch before restore' }

git clone $BundlePath $RestoreRoot
if ($LASTEXITCODE -ne 0) { throw 'failed: restore clone failed' }

Set-Location $RestoreRoot
$restoredHead = (git rev-parse HEAD).Trim()
if ($restoredHead -ne $head) { throw "failed: restored commit mismatch: $restoredHead" }

$restoredStatus = git status --porcelain=v1
if ($LASTEXITCODE -ne 0) { throw 'failed: restored git status failed' }
if ($restoredStatus) { throw 'failed: restored working tree is dirty' }

git fsck --full
if ($LASTEXITCODE -ne 0) { throw 'failed: git fsck failed' }

$prohibited = @('.env', 'secrets', 'captures', 'raw-captures', 'probe-evidence', '.venv', 'venv')
foreach ($name in $prohibited) {
    if (Test-Path (Join-Path $RestoreRoot $name)) {
        throw "failed: prohibited ignored path appeared in restore: $name"
    }
}

$env:PYTHONPATH = (Join-Path $RestoreRoot 'src')
python -m unittest discover -s tests
if ($LASTEXITCODE -ne 0) { throw 'failed: restored full test suite failed' }

[ordered]@{
    source_branch = $branch
    source_head = $head
    restored_head = $restoredHead
    bundle_sha256 = $bundleHash
    bundle_bytes = $bundleBytes
    encryption_status = 'blocked_pending_owner_tool_and_key_path'
    restore_integrity = 'passed'
    full_suite = 'passed'
    cleanup_status = 'not_authorized_artifacts_preserved'
} | ConvertTo-Json -Depth 5
```

## Required result handling

Paste the terminal output showing:

- branch and source HEAD;
- bundle verification result;
- bundle SHA-256 and byte count from `m19-manifest.json`;
- restored HEAD;
- `git fsck --full` result;
- full test count and result;
- final JSON summary.

Do not delete either local root after the proof. Cleanup remains separately gated.

## Honest classification

With the current authorization, the strongest possible successful result is:

```text
passed_repository_archive_and_restore_proof
encryption_status: blocked_pending_owner_tool_and_key_path
```

It is not an encrypted-backup proof.
