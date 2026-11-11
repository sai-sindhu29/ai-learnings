#!/usr/bin/env python3
"""Invoice validation MCP server (Capstone 2 - Invoice Validation).

Exposes one MCP tool, ``validate_invoices``, which reads the sample records in
``requisition-agent/requisitions.json`` and the supplier master in
``requisition-agent/suppliers.csv``, applies the transparent validation rules
below, and writes four output files into this folder (github-day-8/):

    clean_invoices.json, exception_list.json, validation_summary.json

Data assumption: the source holds purchase requisitions, not invoices. Each
requisition is used as a sample invoice-validation record.

Nothing is posted to SAP. No purchase orders or invoices are created. The
source files are only read, never written.

Usage:
    python3 invoice_validator.py            # run as MCP server over stdio (Claude Code launches this)
    python3 invoice_validator.py --cli      # run the validation directly, no MCP client needed
"""

from __future__ import annotations

import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

# All paths are derived from this file's location. The tool never accepts a
# path argument, so it cannot read or write anywhere else.
BASE_DIR = Path(__file__).resolve().parent
SOURCE_DIR = BASE_DIR / "requisition-agent"
REQUISITIONS_FILE = SOURCE_DIR / "requisitions.json"
SUPPLIERS_FILE = SOURCE_DIR / "suppliers.csv"

CLEAN_FILE = BASE_DIR / "clean_invoices.json"
EXCEPTION_FILE = BASE_DIR / "exception_list.json"
SUMMARY_FILE = BASE_DIR / "validation_summary.json"

REQUIRED_FIELDS = ("id", "supplier", "amount")
REQUIRED_SUPPLIER_STATUS = "good"
# The source has no invoice identifier field. If a future source adds one
# named "invoice_id", the duplicate check runs automatically.
INVOICE_ID_FIELD = "invoice_id"

mcp = FastMCP("invoice-validator")


def _log(message: str) -> None:
    # stdout carries MCP JSON-RPC traffic in server mode, so log to stderr.
    print(message, file=sys.stderr)


def load_requisitions() -> list[dict[str, Any]]:
    with REQUISITIONS_FILE.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, list):
        raise ValueError(f"{REQUISITIONS_FILE.name} must contain a JSON array")
    return data


def load_suppliers() -> dict[str, str]:
    """Return {normalised supplier name: status} from suppliers.csv."""
    suppliers: dict[str, str] = {}
    with SUPPLIERS_FILE.open("r", encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            name = (row.get("supplier") or "").strip().lower()
            if name:
                suppliers[name] = (row.get("status") or "").strip()
    return suppliers


def _is_blank(value: Any) -> bool:
    return value is None or (isinstance(value, str) and not value.strip())


def _check_record(record: dict[str, Any], suppliers: dict[str, str]) -> list[str]:
    """Return the list of exception reasons for one record (empty = clean)."""
    reasons: list[str] = []

    # Rule 1: required fields present.
    missing = [f for f in REQUIRED_FIELDS if f not in record or _is_blank(record[f])]
    for field_name in missing:
        reasons.append(f"missing required field: {field_name}")

    # Rule 2: supplier exists in suppliers.csv (case-insensitive, trimmed).
    supplier_key = None
    if "supplier" not in missing:
        supplier_key = str(record["supplier"]).strip().lower()
        if supplier_key not in suppliers:
            reasons.append(
                f"supplier '{record['supplier']}' not found in suppliers.csv"
            )

    # Rule 3: supplier status must be good.
    if supplier_key is not None and supplier_key in suppliers:
        status = suppliers[supplier_key]
        if status.lower() != REQUIRED_SUPPLIER_STATUS:
            reasons.append(
                f"supplier status is '{status}' (required: '{REQUIRED_SUPPLIER_STATUS}')"
            )

    # Rule 4: amount must be a number greater than zero.
    if "amount" not in missing:
        raw = record["amount"]
        amount = None
        if isinstance(raw, bool):
            amount = None
        elif isinstance(raw, (int, float)):
            amount = float(raw)
        else:
            try:
                amount = float(str(raw).strip())
            except ValueError:
                amount = None
        if amount is None:
            reasons.append(f"amount is not numeric: {raw!r}")
        elif amount <= 0:
            reasons.append(f"amount must be greater than zero (got {raw})")

    return reasons


def _duplicate_invoice_ids(records: list[dict[str, Any]]) -> tuple[str, dict[str, int]]:
    """Return (status text, {invoice_id: count}) for duplicates above one."""
    present = [r for r in records if INVOICE_ID_FIELD in r and not _is_blank(r[INVOICE_ID_FIELD])]
    if not present:
        return ("NOT_APPLICABLE: source records have no invoice identifier field", {})
    counts: dict[str, int] = {}
    for r in present:
        key = str(r[INVOICE_ID_FIELD]).strip()
        counts[key] = counts.get(key, 0) + 1
    return ("APPLIED", {k: v for k, v in counts.items() if v > 1})


def run_validation(write_outputs: bool = True) -> dict[str, Any]:
    """Validate every requisition and (optionally) write the output files."""
    requisitions = load_requisitions()
    suppliers = load_suppliers()
    dup_status, duplicates = _duplicate_invoice_ids(requisitions)

    results: list[dict[str, Any]] = []
    for record in requisitions:
        reasons = _check_record(record, suppliers)
        # Duplicate reason added per record when the check applies.
        if INVOICE_ID_FIELD in record and str(record.get(INVOICE_ID_FIELD, "")).strip() in duplicates:
            reasons.append(
                f"duplicate invoice_id '{record[INVOICE_ID_FIELD]}' "
                f"(occurs {duplicates[str(record[INVOICE_ID_FIELD]).strip()]} times)"
            )
        status = "EXCEPTION" if reasons else "CLEAN"
        results.append({
            "record": record,
            "status": status,
            "reasons": reasons,
        })

    clean = [r["record"] for r in results if r["status"] == "CLEAN"]
    exceptions = [
        {
            "id": r["record"].get("id"),
            "supplier": r["record"].get("supplier"),
            "amount": r["record"].get("amount"),
            "status": "EXCEPTION",
            "reasons": r["reasons"],
        }
        for r in results if r["status"] == "EXCEPTION"
    ]

    generated_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    summary = {
        "task": "Capstone 2 - Invoice Validation",
        "generated_at_utc": generated_at,
        "data_assumption": (
            "The source contains purchase requisitions, not actual invoices. "
            "Each requisition is used as a sample invoice-validation record."
        ),
        "source_files": {
            "requisitions": str(REQUISITIONS_FILE.relative_to(BASE_DIR)),
            "suppliers": str(SUPPLIERS_FILE.relative_to(BASE_DIR)),
        },
        "rules": [
            "R1 required fields present: id, supplier, amount",
            "R2 supplier exists in suppliers.csv",
            f"R3 supplier status == '{REQUIRED_SUPPLIER_STATUS}'",
            "R4 amount is numeric and > 0",
            "R5 duplicate invoice_id (only when an invoice identifier field exists)",
        ],
        "duplicate_invoice_check": dup_status,
        "total_records": len(results),
        "clean_count": len(clean),
        "exception_count": len(exceptions),
        "clean_ids": [r["record"].get("id") for r in results if r["status"] == "CLEAN"],
        "exception_ids": [e["id"] for e in exceptions],
        "results": [
            {"id": r["record"].get("id"), "status": r["status"], "reasons": r["reasons"]}
            for r in results
        ],
        "sap_posting": "none - no SAP invoices or purchase orders were created",
    }

    if write_outputs:
        CLEAN_FILE.write_text(json.dumps(clean, indent=2) + "\n", encoding="utf-8")
        EXCEPTION_FILE.write_text(json.dumps(exceptions, indent=2) + "\n", encoding="utf-8")
        SUMMARY_FILE.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        summary["output_files"] = [
            CLEAN_FILE.name, EXCEPTION_FILE.name, SUMMARY_FILE.name,
        ]

    return summary


@mcp.tool()
def validate_invoices() -> dict:
    """Validate the five sample invoice records (requisition-agent/requisitions.json)
    against supplier master data (requisition-agent/suppliers.csv).

    Rules: required fields present; supplier exists; supplier status is 'good';
    amount > 0; duplicate invoice_id check when an identifier field exists.
    Each record is classified CLEAN or EXCEPTION with reasons. Writes
    clean_invoices.json, exception_list.json and validation_summary.json into
    the github-day-8 folder. Does not post anything to SAP.
    """
    _log("validate_invoices: running")
    summary = run_validation(write_outputs=True)
    _log(
        f"validate_invoices: {summary['clean_count']} clean, "
        f"{summary['exception_count']} exception"
    )
    return summary


def main() -> None:
    if "--cli" in sys.argv:
        summary = run_validation(write_outputs=True)
        print(json.dumps(summary, indent=2))
        return
    mcp.run()


if __name__ == "__main__":
    main()
