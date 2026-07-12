# M19 Operations Risk and Runbook Plan

Status: planning
Milestone: M19
Date: 2026-07-12

## Purpose

Define the minimum operational controls needed so the bounded Observatory evidence system is understandable and recoverable without pretending it is already a production service.

## Risk register

| Risk | Current exposure | Required control | Stop condition |
|---|---|---|---|
| Repository loss or corruption | GitHub remote exists, but independent restore proof is not yet established | encrypted repository archive plus disposable restore proof | hash, Git integrity, or commit mismatch |
| Secret committed to Git | `.gitignore` blocks common paths but cannot prevent all mistakes | tracked/staged secret-pattern inspection and owner review | likely credential or private key detected |
| Raw payload retained outside accepted posture | raw capture paths are ignored; M13 payload was purged | inventory ignored evidence roots and require explicit retention authority | unclassified raw/private material found |
| Purge claim without proof | accepted M13 purge proof exists for one bounded probe | require pre/post hash, containment, absence, actor, reason, and timestamp | payload still exists or path containment fails |
| Test evidence drift | result registers can become stale relative to HEAD | bind every proof to exact commit and command | proof commit differs from tested commit |
| Silent provider/parser drift | provider work is disarmed after M13 | preserve shape/hash/drift gates and block new execution | endpoint, shape, rights, price, or recipe change |
| Automatic recurrence accidentally introduced | M18 rejected recurrence for v1 | scan for scheduler/cron/task artifacts during review | recurring job artifact or provider loop appears |
| Destructive cleanup damages evidence | no general cleanup tooling admitted | dry inventory first; deletion requires exact owner authorization | target ambiguity or successor proof missing |
| Recovery depends on one machine | current local clone plus GitHub remote | independently encrypted archive stored separately | only one recoverable copy exists |

## Required operational runbooks

### 1. Repository state verification

Record:

```text
branch
HEAD SHA
commit subject
working tree status
remote tracking status
full-suite result where required
```

Never claim a state is backed up or proven without exact commit identity.

### 2. Secret exposure review

Review tracked and staged text for likely:

- API keys and tokens;
- private-key headers;
- connection strings with credentials;
- `.env`-style assignments;
- authentication cookies or bearer values;
- customer/private identifiers.

Do not print complete suspected secrets into proof records. Record path, category, and redacted finding only.

### 3. Raw/ignored evidence inventory

Inventory only the declared Observatory evidence roots and ignored capture paths.

Classify each item as:

```text
accepted_git_tracked_evidence
transient_allowed
purge_due
purged_with_proof
blocked_unclassified
```

Unknown material blocks cleanup and backup admission.

### 4. Retention cleanup proof

Any future authorized purge must prove:

- exact contained target;
- pre-purge existence, bytes, and hash where allowed;
- governing retention rule;
- actor and timestamp;
- post-purge absence;
- retained manifest/proof classification;
- no neighboring file deletion.

### 5. Backup creation

Follow `m19-backup-restore-policy-v0-1.md`. Backup only a clean, exact repository state. Never bundle ignored secrets or raw capture roots by convenience.

### 6. Restore proof

Restore into a disposable location, verify hashes and commit, run integrity checks and the full suite, and preserve only non-secret proof metadata.

### 7. Incident stop procedure

Stop work and preserve state when any of these appears:

- suspected secret exposure;
- unexplained raw/private data;
- hash mismatch;
- dirty or ambiguous repository state;
- failed restore or test suite;
- unexpected network/provider behavior;
- destructive cleanup uncertainty;
- recurrence or autonomous-spend artifact.

No automatic repair, deletion, provider retry, or credential rotation is authorized by this plan.

## Audit evidence ceiling

M19 operational evidence may retain:

- commit identifiers;
- hashes and byte counts of admitted backup artifacts;
- commands and pass/fail outcomes;
- redacted secret-finding categories;
- purge proof metadata;
- restore limitations and cleanup status.

It must not retain:

- credentials or decryption secrets;
- customer/private data;
- purged raw payload content;
- machine-wide inventory;
- unrelated repository content;
- strategy or recommendations.
