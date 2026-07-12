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

The ChatGPT `ob-dev` connector expects a fixed interpreter at:

```text
C:\dev\observatory\.venv\Scripts\python.exe
```

At the time this file was added, that interpreter did not exist, so connector-side execution was not available.

Do not mark hammers as passed until tests are actually executed and the result is recorded.
