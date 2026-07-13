# Tests

Status: M12 local test notes
Authority: none — execution notes only
Purpose: document how to run the local C2 first-slice tests without implying provider, DB, API/MCP, dashboard, or customer-data authorization

---

## Current Test Surface

The current executable test surface is limited to:

```text
C2 Controlled Public Manual Observation Package
```

The tests are fixture-based and local-only.

They must not call providers, use customer data, connect to a database, expose API/MCP tools, create dashboards, scrape marketplaces, or store strategy/recommendations.

---

## Run Command

From the repository root:

```powershell
python -m unittest discover -s tests
```

If using a virtual environment later, activate it first and run the same command.

---

## Current Note

Run tests through Codex's native local terminal. The `ob-dev-mcp` server is not the project test runner, and the old `ob-dev` Git/test tool path is retired from new work.

If the repository does not yet have a local virtual environment, use an explicitly selected Python 3.11+ interpreter. Do not claim a test or hammer result from configuration alone.

The authority-sync check is:

```powershell
python tools/check_authority_sync.py
```

Do not mark hammers as passed until the correct proof class has actually executed and its result is recorded.
