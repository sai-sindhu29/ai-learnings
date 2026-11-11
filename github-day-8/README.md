# Capstone 2 – Invoice Validation (MCP tool `validate_invoices`)

## Project objective

Build a working MCP tool, `validate_invoices`, that reads the five sample records in
`requisition-agent/requisitions.json`, checks them against supplier master data in
`requisition-agent/suppliers.csv`, and classifies each record as **CLEAN** or **EXCEPTION**
with a clear reason for every exception.

**Data assumption (important):** the source contains *purchase requisitions*, not actual
invoices. For this learning capstone each requisition is used as a sample invoice-validation
record. The source records are not changed and no real SAP invoice or purchase order is
created or posted.

## MCP architecture

```
Claude Code (MCP client)
   │  stdio, JSON-RPC (MCP protocol)
   ▼
invoice_validator.py  ── FastMCP server "invoice-validator" (Python MCP SDK 1.x)
   │  tool: validate_invoices()
   ├── reads  requisition-agent/requisitions.json   (read-only)
   ├── reads  requisition-agent/suppliers.csv       (read-only)
   └── writes clean_invoices.json, exception_list.json, validation_summary.json
              (only inside github-day-8/)
```

- **Server:** `invoice_validator.py`, built with `mcp.server.fastmcp.FastMCP`.
- **Transport:** stdio. Claude Code starts the server process itself.
- **Registration:** `.mcp.json` in this folder (project scope), created with `claude mcp add`.
- **Paths:** derived from the script's own location. The tool takes no path arguments, so it
  cannot read or write outside this folder.
- **Logging:** written to stderr only, because stdout carries the MCP protocol.

## Validation rules

| ID | Rule | Failure reason text |
|----|------|---------------------|
| R1 | Required fields present and non-blank: `id`, `supplier`, `amount` | `missing required field: <name>` |
| R2 | Supplier exists in `suppliers.csv` (trimmed, case-insensitive match on `supplier`) | `supplier '<name>' not found in suppliers.csv` |
| R3 | Supplier `status` in `suppliers.csv` is `good` | `supplier status is '<status>' (required: 'good')` |
| R4 | `amount` is numeric and greater than zero | `amount must be greater than zero (got <n>)` / `amount is not numeric: <v>` |
| R5 | Duplicate `invoice_id` check. **Applies only when the source has an invoice identifier field.** | `duplicate invoice_id '<id>' (occurs <n> times)` |

- A record with **zero** failed rules → `CLEAN`.
- A record with **one or more** failed rules → `EXCEPTION`. Every failed rule is listed.
- **R5 is not applicable to this source.** The requisitions have no invoice identifier
  (`invoice_id`), so the check was not run. The summary reports
  `NOT_APPLICABLE: source records have no invoice identifier field`. No invoice field was
  invented. If a future source adds `invoice_id`, the check runs automatically.

## Tool description

**Name:** `validate_invoices`
**Arguments:** none
**Returns:** a JSON object with `total_records`, `clean_count`, `exception_count`, `clean_ids`,
`exception_ids`, `duplicate_invoice_check`, per-record `results` (id, status, reasons), and
`output_files`.
**Side effects:** writes the three output JSON files into `github-day-8/`. Nothing is posted
to SAP.

## Execution steps

Run these from the `github-day-8/` folder.

1. **Install the MCP SDK** (version 1.x; the 2.x line renamed `FastMCP` and breaks this code):
   ```bash
   pip install "mcp[cli]<2"
   ```
2. **Run the validation directly** (no MCP client needed):
   ```bash
   python3 invoice_validator.py --cli
   ```
3. **Register the MCP server** (already done; `.mcp.json` is in this folder):
   ```bash
   claude mcp add --scope project invoice-validator -- python3 /home/user/claude-projects/github-day-8/invoice_validator.py
   ```
4. **Approve and connect in Claude Code.** Launch Claude Code from this folder:
   ```bash
   cd /home/user/claude-projects/github-day-8 && claude
   ```
   Project-scope servers need one-time approval. Accept the `invoice-validator` prompt, or run
   `/mcp` and enable it. Then ask Claude: *"Call the validate_invoices tool."*
5. **Run the end-to-end MCP test** (launches the server over stdio, lists tools, calls the tool):
   ```bash
   python3 /tmp/mcp_e2e/mcp_e2e_test.py
   ```
   The test file lives outside this folder so that only task outputs stay in `github-day-8/`.
6. **Check outputs:** `clean_invoices.json`, `exception_list.json`, `validation_summary.json`.

## Results for all five records

| ID | Supplier | Amount | Supplier status | Result | Reasons |
|----|----------|-------:|-----------------|--------|---------|
| PR1 | Sharma Steels | 450,000 | good | **CLEAN** | – |
| PR2 | Vizag Paints | 120,000 | good | **CLEAN** | – |
| PR3 | Guntur Cables | 98,000 | good | **CLEAN** | – |
| PR4 | New Vendor Co | 5,600,000 | new | **EXCEPTION** | supplier status is 'new' (required: 'good') |
| PR5 | Sharma Steels | 3,200,000 | good | **CLEAN** | – |

**Totals:** 5 records · 4 CLEAN (PR1, PR2, PR3, PR5) · 1 EXCEPTION (PR4)

## Exception reasons

- **PR4 (New Vendor Co, 5,600,000):** supplier status is `new`, not `good`. The supplier exists
  in `suppliers.csv`, and the amount is valid. Only R3 fails. The item needs supplier
  onboarding or approval before it can be treated as clean.

## Output files

| File | Content |
|------|---------|
| `clean_invoices.json` | The 4 CLEAN records, with their original fields unchanged |
| `exception_list.json` | The 1 EXCEPTION record with its reasons |
| `validation_summary.json` | Rules, totals, ID lists, R5 status, assumption, and per-record results |

## End-to-end test evidence

**Test 1 – direct run (`python3 invoice_validator.py --cli`):**
```
clean_count: 4    exception_count: 1
clean_ids: [PR1, PR2, PR3, PR5]    exception_ids: [PR4]
duplicate_invoice_check: NOT_APPLICABLE: source records have no invoice identifier field
```

**Test 2 – MCP protocol test (`/tmp/mcp_e2e/mcp_e2e_test.py`):**
```
server: invoice-validator 1.30.0
tools discovered: ['validate_invoices']
tool call: OK
total_records 5 | clean_count 4 | exception_count 1 | clean_ids [PR1,PR2,PR3,PR5]
exception_ids [PR4] | output_files [clean_invoices.json, exception_list.json, validation_summary.json]
```
The test exits with code 0. The server was launched by the MCP client over stdio, the tool
was discovered with `list_tools`, and it was invoked with `call_tool`. The output files were
then checked on disk.

**Test 3 – source files unchanged:** `requisition-agent/` still has its original modification
times (08:01–08:03). It was only read.

**Test 4 – Claude Code connection:** `claude mcp list` reports
`invoice-validator … Pending approval`. This is expected for a new project-scope server. It
connects after you approve it in an interactive `claude` session (step 4). That approval has
to be done by hand. The protocol-level test in Test 2 is the evidence that the server itself
works.

## Notes

- The `.mcp.json` path is absolute. Move the folder and re-run `claude mcp add` if needed.
- Empty placeholder files `clean_invoices.json`, `exception_list.json`, `invoice_validator.py`,
  `README.md`, and `validation_summary.json` also exist in the parent folder
  (`claude-projects/`). They are not part of this task's output and were not touched. They
  can be deleted if they are not needed.
- Existing ABAP documentation in this folder (`abap_review_notes.md`, `abap_unit_tests.md`,
  `designs.md`, `obsolete_statements.md`) is preserved.
