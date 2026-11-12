
cat > secure_invoice_validator.py <<'PY'
import csv
import json
import re
from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path

BASE = Path(__file__).resolve().parent
SOURCE = BASE.parent / "github-day-8" / "requisition-agent"

ATTACK_DIR = BASE / "attack_invoices"
AUDIT_FILE = BASE / "audit_log.json"
EXCEPTION_FILE = BASE / "exception_list.json"

MAX_AMOUNT = Decimal("2500000")

GSTIN_PATTERN = re.compile(
    r"[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][1-9A-Z]Z[0-9A-Z]"
)

INJECTION_PATTERN = re.compile(
    r"ignore\s+all\s+rules|approve\s+me|"
    r"bypass\s+(?:all\s+)?(?:rules|validation)|"
    r"ignore\s+previous\s+instructions",
    re.IGNORECASE,
)


def load_reference_data():
    requisitions = json.loads(
        (SOURCE / "requisitions.json").read_text(encoding="utf-8")
    )

    with (SOURCE / "suppliers.csv").open(
        encoding="utf-8", newline=""
    ) as f:
        suppliers = {
            row["supplier"].strip().lower():
            row["status"].strip().lower()
            for row in csv.DictReader(f)
        }

    if not isinstance(requisitions, list):
        raise ValueError("Requisitions file must contain a JSON array")

    return {r["id"]: r for r in requisitions}, suppliers


def to_decimal(value):
    if isinstance(value, bool) or value is None:
        return None

    try:
        result = Decimal(str(value))
        return result if result.is_finite() else None
    except (InvalidOperation, ValueError, TypeError):
        return None


def contains_injection(value):
    if isinstance(value, str):
        return bool(INJECTION_PATTERN.search(value))

    if isinstance(value, dict):
        return any(contains_injection(v) for v in value.values())

    if isinstance(value, list):
        return any(contains_injection(v) for v in value)

    return False


def validate_invoice(data, requisitions, suppliers, seen_ids=None):
    reasons = []
    seen_ids = seen_ids if seen_ids is not None else set()


    # Attack 1: Prompt injection.
    if contains_injection(data):
        reasons.append("Suspicious instruction-like text in invoice")

    # Required fields.
    for field in ("id", "supplier", "amount"):
        if field not in data or data[field] is None or (
            isinstance(data[field], str) and not data[field].strip()
        ):
            reasons.append(f"Missing required field: {field}")

    pr_id = data.get("id")
    amount = to_decimal(data.get("amount"))

    # Attack 3: PR must exist.
    if not isinstance(pr_id, str) or pr_id not in requisitions:
        reasons.append(f"PR '{pr_id}' does not exist")
        reference = None
    else:
        reference = requisitions[pr_id]

    # Attack 2: Compare invoice amount with PO/requisition amount.
    if amount is not None and reference is not None:
        expected_amount = to_decimal(reference.get("amount"))

        if expected_amount is not None and amount != expected_amount:
            reasons.append("Invoice amount does not match PO amount")

    # Attack 4: Duplicate invoice ID.
    invoice_id = data.get("invoice_id")

    if invoice_id is not None and str(invoice_id).strip():
        invoice_id = str(invoice_id).strip()

        if invoice_id in seen_ids:
            reasons.append(f"Duplicate invoice ID: {invoice_id}")
        else:
            seen_ids.add(invoice_id)

    # Attack 5: Amount validation and approval threshold.
    if amount is None:
        reasons.append("Amount must be numeric")
    elif amount <= 0:
        reasons.append("Amount must be greater than zero")
    elif amount > MAX_AMOUNT:
        reasons.append(
            "Amount exceeds ₹25 lakh; manager approval required"
        )

    # Attack 6: Date validation.
    invoice_date = data.get("invoice_date")
    due_date = data.get("due_date")

    if invoice_date or due_date:
        try:
            if not invoice_date or not due_date:
                raise ValueError("Both dates are required")

            inv_date = date.fromisoformat(invoice_date)
            due = date.fromisoformat(due_date)

            if due < inv_date:
                reasons.append("Due date is before invoice date")

        except (ValueError, TypeError):
            reasons.append("Invoice date or due date is invalid")

    # Attack 7: GSTIN validation.
    gstin = data.get("gstin")

    if gstin is not None and (
        not isinstance(gstin, str)
        or not GSTIN_PATTERN.fullmatch(gstin)
    ):
        reasons.append("GSTIN format is invalid")

    # Attack 8: Vendor must match the PR and supplier master.
    if reference is not None:
        expected_vendor = reference["supplier"].strip().lower()
        actual_vendor = str(data.get("supplier", "")).strip().lower()

        if actual_vendor != expected_vendor:
            reasons.append("Invoice vendor does not match PR vendor")

        if data.get("po_supplier") and (
            str(data["po_supplier"]).strip().lower()
            != expected_vendor
        ):
            reasons.append("PO vendor does not match PR vendor")

        status = suppliers.get(expected_vendor, "unknown")

        if status != "good":
            reasons.append(
                f"Supplier status is '{status}'; human approval required"
            )
    # Attack 9: Empty or invalid invoice.
    if not isinstance(data, dict) or not data:
        return ["Invoice is empty or invalid"]

    # Attack 10: Line-item total validation.
    if "line_items" in data:
        items = data["line_items"]
        declared_total = to_decimal(data.get("total"))

        if not isinstance(items, list) or not items:
            reasons.append("Invalid or empty line-item list")
        else:
            item_amounts = [
                to_decimal(item.get("amount"))
                if isinstance(item, dict) else None
                for item in items
            ]

            if any(value is None for value in item_amounts):
                reasons.append("Invalid line-item structure")
            elif declared_total is None:
                reasons.append("Declared total is missing or invalid")
            elif sum(item_amounts, Decimal("0")) != declared_total:
                reasons.append(
                    "Declared total does not match line-item sum"
                )

    # Remove duplicate messages while preserving order.
    return list(dict.fromkeys(reasons))


def validate_file(path, seen_ids=None):
    path = Path(path)

    try:
        raw = path.read_text(encoding="utf-8")
        data = json.loads(raw) if raw.strip() else None
    except (json.JSONDecodeError, UnicodeDecodeError, OSError):
        data = None

    requisitions, suppliers = load_reference_data()

    reasons = validate_invoice(
        data, requisitions, suppliers, seen_ids
    )

    return {
        "file": path.name,
        "status": "EXCEPTION" if reasons else "CLEAN",
        "reasons": reasons,
        "posting": "NOT_POSTED",
    }


def main():
    seen_ids = set()
    audit = []

    for path in sorted(ATTACK_DIR.glob("*.json")):
        result = validate_file(path, seen_ids)
        audit.append(result)

        print(
            result["file"], "=>", result["status"],
            "|", "; ".join(result["reasons"])
        )

        # Replay Attack 4 to verify duplicate detection.
        if path.name == "attack_04_duplicate.json":
            duplicate = validate_file(path, seen_ids)
            duplicate["file"] = path.name + " (replayed)"
            audit.append(duplicate)

            print(
                "Duplicate replay =>", duplicate["status"],
                "|", "; ".join(duplicate["reasons"])
            )

    timestamp = datetime.now(timezone.utc).isoformat()

    AUDIT_FILE.write_text(
        json.dumps({
            "generated_at_utc": timestamp,
            "total_entries": len(audit),
            "posting_operations": 0,
            "results": audit,
        }, indent=2) + "\n",
        encoding="utf-8"
    )

    exceptions = [
        entry for entry in audit
        if entry["status"] == "EXCEPTION"
    ]

    EXCEPTION_FILE.write_text(
        json.dumps(exceptions, indent=2) + "\n",
        encoding="utf-8"
    )

    print("\nAudit log saved.")
    print("Total audit entries:", len(audit))
    print("Exception entries:", len(exceptions))
    print("Posting operations: 0")


if __name__ == "__main__":
    main()
PY
