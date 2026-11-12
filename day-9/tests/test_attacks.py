from pathlib import Path

from secure_invoice_validator import validate_file

ATTACKS = Path(__file__).resolve().parents[1] / "attack_invoices"


def check_attack(filename, seen=None):
    result = validate_file(ATTACKS / filename, seen)
    assert result["status"] == "EXCEPTION", result
    assert result["posting"] == "NOT_POSTED"
    assert result["reasons"], result
    return result


def test_01_prompt_injection():
    result = check_attack("attack_01_prompt_injection.json")
    assert any("instruction-like" in r for r in result["reasons"])


def test_02_amount_mismatch():
    result = check_attack("attack_02_amount_mismatch.json")
    assert any("PO amount" in r for r in result["reasons"])


def test_03_invalid_pr():
    result = check_attack("attack_03_invalid_pr.json")
    assert any("does not exist" in r for r in result["reasons"])


def test_04_duplicate_invoice():
    seen = set()
    first = validate_file(ATTACKS / "attack_04_duplicate.json", seen)
    second = check_attack("attack_04_duplicate.json", seen)
    assert first["status"] == "CLEAN"
    assert any("Duplicate invoice ID" in r for r in second["reasons"])


def test_05_huge_amount():
    result = check_attack("attack_05_huge_amount.json")
    assert any("₹25 lakh" in r for r in result["reasons"])


def test_06_invalid_dates():
    result = check_attack("attack_06_invalid_dates.json")
    assert any("Due date" in r for r in result["reasons"])


def test_07_invalid_gstin():
    result = check_attack("attack_07_invalid_gstin.json")
    assert any("GSTIN" in r for r in result["reasons"])


def test_08_vendor_mismatch():
    result = check_attack("attack_08_vendor_mismatch.json")
    assert any("vendor" in r.lower() for r in result["reasons"])


def test_09_empty_invoice():
    result = check_attack("attack_09_empty_invoice.json")
    assert any("empty" in r.lower() for r in result["reasons"])


def test_10_total_mismatch():
    result = check_attack("attack_10_total_mismatch.json")
    assert any("line-item sum" in r for r in result["reasons"])
