#!/usr/bin/env python3
"""Task 3 evaluation: rule-based invoice validator vs. 20 labelled invoices.

Inputs (read only):
  evals/data/labelled_invoices.json
  ../github-day-8/requisition-agent/requisitions.json
  ../github-day-8/requisition-agent/suppliers.csv

Outputs (written to evals/results/task3/):
  predictions.json          predicted label + per-rule results, per invoice
  expected_labels.json      expected label copied from the dataset, per invoice
  correctness.json          per-invoice correctness, accuracy, confusion matrix
  execution_time.json       wall-clock timings measured in this run
  model_cost.json           model cost status (no model is invoked, so unavailable)

Rules applied (all must pass for CLEAN; any failure gives EXCEPTION):
  1. pr_exists                     PR id exists in requisitions.json
  2. supplier_identity             invoice supplier == supplier on that PR
  3. supplier_active               invoice supplier has status "good" in suppliers.csv
  4. amount_numeric_positive       amount is a JSON number and > 0
  5. amount_below_approval_threshold  amount <= Rs 25 lakh (2,500,000)
"""

import csv
import hashlib
import json
import platform
import sys
import time
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path

EVALS_DIR = Path(__file__).resolve().parent
PROJECT_DIR = EVALS_DIR.parent
DATASET = EVALS_DIR / "data" / "labelled_invoices.json"
REF_DIR = PROJECT_DIR.parent / "github-day-8" / "requisition-agent"
REQUISITIONS = REF_DIR / "requisitions.json"
SUPPLIERS = REF_DIR / "suppliers.csv"
RESULTS_DIR = EVALS_DIR / "results" / "task3"

APPROVAL_THRESHOLD = Decimal("2500000")  # Rs 25 lakh; amounts above need manager approval
ACTIVE_STATUS = "good"

RULES = [
    "pr_exists",
    "supplier_identity",
    "supplier_active",
    "amount_numeric_positive",
    "amount_below_approval_threshold",
]


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def norm(name):
    return str(name).strip().lower() if name is not None else ""


def to_decimal(value):
    # Only real JSON numbers count; strings such as "450000" and booleans are rejected.
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    try:
        result = Decimal(str(value))
    except InvalidOperation:
        return None
    return result if result.is_finite() else None


def load_reference():
    requisitions_raw = json.loads(REQUISITIONS.read_text(encoding="utf-8"))
    if not isinstance(requisitions_raw, list):
        raise ValueError("requisitions.json must contain a JSON array")
    requisitions = {r["id"]: r for r in requisitions_raw}

    with SUPPLIERS.open(encoding="utf-8", newline="") as f:
        statuses = {
            norm(row["supplier"]): norm(row["status"])
            for row in csv.DictReader(f)
        }
    return requisitions, statuses


def evaluate(invoice, requisitions, statuses):
    """Apply the five rules to one invoice. Returns (predicted_label, rule_results)."""
    requisition = requisitions.get(invoice.get("pr_id"))
    invoice_supplier = norm(invoice.get("supplier"))
    amount = to_decimal(invoice.get("amount"))

    checks = {
        "pr_exists": requisition is not None,
        "supplier_identity": (
            requisition is not None
            and invoice_supplier != ""
            and invoice_supplier == norm(requisition.get("supplier"))
        ),
        "supplier_active": statuses.get(invoice_supplier) == ACTIVE_STATUS,
        "amount_numeric_positive": amount is not None and amount > 0,
        "amount_below_approval_threshold": (
            amount is not None and amount <= APPROVAL_THRESHOLD
        ),
    }

    label = "CLEAN" if all(checks[r] for r in RULES) else "EXCEPTION"
    return label, checks


def write_json(name, payload):
    path = RESULTS_DIR / name
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return path


def ms(ns):
    return round(ns / 1_000_000, 6)


def main():
    dataset_hash_before = sha256(DATASET)

    invoices = json.loads(DATASET.read_text(encoding="utf-8"))
    if not isinstance(invoices, list) or len(invoices) != 20:
        raise SystemExit(f"Expected 20 labelled invoices, found {len(invoices)}")
    for inv in invoices:
        if inv.get("expected_label") not in ("CLEAN", "EXCEPTION"):
            raise SystemExit(f"Bad expected_label in {inv.get('invoice_id')}")

    run_start = time.perf_counter_ns()
    ref_start = time.perf_counter_ns()
    requisitions, statuses = load_reference()
    reference_load_ns = time.perf_counter_ns() - ref_start

    predictions, per_invoice_ns = [], {}
    for inv in invoices:
        t0 = time.perf_counter_ns()
        label, checks = evaluate(inv, requisitions, statuses)
        per_invoice_ns[inv["invoice_id"]] = time.perf_counter_ns() - t0
        predictions.append({
            "invoice_id": inv["invoice_id"],
            "predicted_label": label,
            "rule_results": checks,
        })
    total_run_ns = time.perf_counter_ns() - run_start

    expected = [
        {"invoice_id": inv["invoice_id"], "expected_label": inv["expected_label"]}
        for inv in invoices
    ]

    # Confusion matrix with EXCEPTION as the positive class.
    tp = fp = tn = fn = 0
    rows = []
    for exp, pred in zip(expected, predictions):
        correct = exp["expected_label"] == pred["predicted_label"]
        e_pos = exp["expected_label"] == "EXCEPTION"
        p_pos = pred["predicted_label"] == "EXCEPTION"
        if e_pos and p_pos:
            tp += 1
        elif p_pos:
            fp += 1
        elif e_pos:
            fn += 1
        else:
            tn += 1
        rows.append({
            "invoice_id": exp["invoice_id"],
            "expected_label": exp["expected_label"],
            "predicted_label": pred["predicted_label"],
            "correct": correct,
        })

    total = len(rows)
    correct_count = sum(r["correct"] for r in rows)
    mismatches = [r["invoice_id"] for r in rows if not r["correct"]]

    def ratio(n, d):
        return round(n / d, 4) if d else None

    dataset_hash_after = sha256(DATASET)
    if dataset_hash_before != dataset_hash_after:
        raise SystemExit("ERROR: labelled dataset changed during the run")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).isoformat()

    write_json("predictions.json", predictions)
    write_json("expected_labels.json", expected)
    write_json("correctness.json", {
        "dataset": str(DATASET.relative_to(PROJECT_DIR)),
        "dataset_sha256_before_run": dataset_hash_before,
        "dataset_sha256_after_run": dataset_hash_after,
        "dataset_unchanged": True,
        "total_invoices": total,
        "correct": correct_count,
        "incorrect": total - correct_count,
        "accuracy": ratio(correct_count, total),
        "exception_class": {
            "precision": ratio(tp, tp + fp),
            "recall": ratio(tp, tp + fn),
        },
        "confusion_matrix": {
            "true_exception": tp,
            "false_exception": fp,
            "true_clean": tn,
            "false_clean": fn,
        },
        "mismatched_invoice_ids": mismatches,
        "per_invoice": rows,
    })
    write_json("execution_time.json", {
        "measured": True,
        "method": "time.perf_counter_ns around the rule evaluation in this Python process",
        "scope": "Rule-based validation only; no model is invoked",
        "timestamp_utc": timestamp,
        "total_run_ms": ms(total_run_ns),
        "reference_load_ms": ms(reference_load_ns),
        "per_invoice_ms": {k: ms(v) for k, v in per_invoice_ns.items()},
        "mean_per_invoice_ms": round(
            ms(sum(per_invoice_ns.values()) / len(per_invoice_ns)), 6
        ),
        "python_version": platform.python_version(),
        "platform": platform.platform(),
    })
    write_json("model_cost.json", {
        "measured": False,
        "status": "not_applicable",
        "model_invoked": False,
        "input_tokens": None,
        "output_tokens": None,
        "cost_usd": None,
        "reason": (
            "The validator is deterministic Python code. No LLM call is made, "
            "so there are no tokens or model charges to measure. null means "
            "unavailable, not zero."
        ),
        "timestamp_utc": timestamp,
    })

    print(f"Invoices evaluated: {total}")
    print(f"Correct: {correct_count}/{total} (accuracy {ratio(correct_count, total)})")
    print(f"EXCEPTION precision: {ratio(tp, tp + fp)}  recall: {ratio(tp, tp + fn)}")
    print(f"Confusion: TP={tp} FP={fp} TN={tn} FN={fn}")
    print(f"Mismatched: {', '.join(mismatches) if mismatches else 'none'}")
    print(f"Total run: {ms(total_run_ns)} ms")
    print(f"Dataset unchanged: {dataset_hash_before == dataset_hash_after}")
    print(f"Results written to: {RESULTS_DIR.relative_to(PROJECT_DIR)}")


if __name__ == "__main__":
    sys.exit(main())
