# ABAP Statement Review: Obsolete and Modernizable Statements

**Source reviewed:** `github-day-0/po_open_list` (report `zms_po_open_list`, 25 lines)
**Reviewer role:** Senior ABAP code reviewer (static review)
**Original file:** not modified

---

## 0. Target release: unknown (limitation)

The target SAP NetWeaver / S/4HANA release is **not stated**. This matters because "obsolete" depends on the release:

- Modern Open SQL (`@` escapes, inline `DATA(...)`) needs roughly **ABAP 7.40 SP05 or later**. Most systems today are well past that.
- Some recommendations (for example, released CDS views) apply only to **S/4HANA** or systems that support them.

**Assumption used below:** the system is at least ABAP 7.50, and possibly S/4HANA. Items that depend on the release are marked as such. Please confirm your release (SE37 → `SAP_BASIS` / System → Status, or ask Basis) so the classifications can be finalized.

---

## 1. Summary

| Result | Count |
|---|---|
| Truly obsolete statements (must change) | **0** |
| Valid but not recommended style | 2 |
| Valid, could be modernized | 4 |
| Strategic (release-dependent) | 1 |

**Overall verdict:** The code is already written in a modern style. It uses inline declarations, `@` host-variable escapes, explicit column lists, and `CL_SALV_TABLE`. It contains **no deprecated or removed statements**. The improvements below are about style, safety, and future upgrade-readiness.

---

## 2. Statements checked and found NOT obsolete

These are commonly flagged as old. Your code does not use them, or uses them correctly.

| Statement / pattern | Found in code? | Status |
|---|---|---|
| `SELECT ... ENDSELECT` loop | No | Not used. Good. |
| `SELECT SINGLE` with `ENDSELECT` | No | Not used. |
| `TABLES:` work areas | No | Not used. |
| `OCCURS` internal tables | No | Not used. |
| `WITH HEADER LINE` | No | Not used. |
| `MOVE` / `COMPUTE` | No | Not used. |
| `CONCATENATE` | No | Not used. |
| `FORM` / `PERFORM` routines | No | Not used. |
| `CALL FUNCTION 'REUSE_ALV_GRID_DISPLAY'` (old ALV) | No | Not used. Code uses `CL_SALV_TABLE`. Good. |
| `WRITE` list output | No | Not used. |
| `SELECT *` | No | Not used. Column list is explicit. Good. |
| `DESCRIBE TABLE` | No | Not used. |
| `REPORT` keyword | Yes (line 1) | **Valid.** Still the correct keyword for executable programs. |
| `START-OF-SELECTION` event | Yes (line 9) | **Valid.** See section 3, item B. |
| `SELECT-OPTIONS` | Yes (lines 6–7) | **Valid.** No newer replacement for selection-screen input. |
| `DATA:` chained declaration | Yes (lines 3–4) | **Valid.** |
| `INTO TABLE @DATA(...)` | Yes (line 20) | **Already modern.** |
| `cl_salv_table=>factory` | Yes (line 21) | **Already modern.** |

---

## 3. Findings

### A. Valid, but not recommended: helper `DATA` variables used only for typing

**Original statement (lines 3–4 and 6–7):**
```abap
DATA: lv_lifnr TYPE ekko-lifnr,
      lv_bedat TYPE ekko-bedat.

SELECT-OPTIONS: s_lifnr FOR lv_lifnr,
                s_bedat FOR lv_bedat.
```

**Why it is not recommended:** The two variables are never used as values. They exist only to give the selection fields a type. This adds two declarations and an indirection that a reader has to follow. The `FOR <database-field>` form is shorter and clearer.

**Modern alternative:** Reference the database field directly in `SELECT-OPTIONS`.

**Before:**
```abap
DATA: lv_lifnr TYPE ekko-lifnr,
      lv_bedat TYPE ekko-bedat.

SELECT-OPTIONS: s_lifnr FOR lv_lifnr,
                s_bedat FOR lv_bedat.
```

**After:**
```abap
SELECT-OPTIONS: s_lifnr FOR ekko-lifnr,
                s_bedat FOR ekko-bedat.
```

**Recommendation and priority:** **Low.** Clean-up only. Safe to change. No behavior change.

---

### B. Valid, but not recommended for new code: event-based report structure

**Original statement (line 9):**
```abap
START-OF-SELECTION.
  " ... all logic here ...
```

**Why it is not recommended:** This is still valid and common. It is classic procedural reporting. Since the logic is only a few lines, there is no real problem. For larger reports, class-based structure is easier to test (see the ABAP Unit review).

**Modern alternative:** A local class with a `run` method, called from `START-OF-SELECTION`.

**Before:**
```abap
START-OF-SELECTION.
  SELECT ... INTO TABLE @DATA(lt_po) ...
  cl_salv_table=>factory( ... ).
  lo_alv->display( ).
```

**After:**
```abap
CLASS lcl_po_list DEFINITION.
  PUBLIC SECTION.
    CLASS-METHODS run.
ENDCLASS.

CLASS lcl_po_list IMPLEMENTATION.
  METHOD run.
    SELECT ... INTO TABLE @DATA(lt_po) ...
    cl_salv_table=>factory( ... ).
    lo_alv->display( ).
  ENDMETHOD.
ENDCLASS.

START-OF-SELECTION.
  lcl_po_list=>run( ).
```

**Recommendation and priority:** **Low.** Optional. Do this when you add tests or more logic.

---

### C. Strategic (release-dependent): direct table access vs. released CDS views

**Original statement (lines 10–20):**
```abap
SELECT a~ebeln, a~lifnr, a~bedat, b~ebelp, b~matnr, b~menge
  FROM ekko AS a
  INNER JOIN ekpo AS b ON b~ebeln = a~ebeln
  WHERE a~lifnr IN @s_lifnr
  AND a~bedat IN @s_bedat
  INTO TABLE @DATA(lt_po).
```

**Why it is not recommended (on S/4HANA):** Reading the underlying tables `EKKO` and `EKPO` directly is still allowed. However, SAP recommends **released APIs and CDS views** for new development. Those are stable across upgrades. Direct table reads can break when table structures change, and on S/4HANA some purchasing data is provided through the released interfaces. This is an **architecture** point, not a syntax problem.

**Modern alternative (S/4HANA, verify in your system):** A released purchasing CDS view such as `I_PurchaseOrderItemAPI01`, read with ABAP SQL.

**Before:**
```abap
SELECT a~ebeln, a~lifnr, b~ebelp, b~matnr, b~menge
  FROM ekko AS a
  INNER JOIN ekpo AS b ON b~ebeln = a~ebeln
  WHERE a~lifnr IN @s_lifnr
  INTO TABLE @DATA(lt_po).
```

**After (illustrative, check view name and fields in ADT/SE80 first):**
```abap
SELECT PurchaseOrder, Supplier, PurchaseOrderItem, Material, OrderQuantity
  FROM i_purchaseorderitemapi01
  WHERE Supplier IN @s_lifnr
  INTO TABLE @DATA(lt_po).
```

**Recommendation and priority:** **Medium.** Check first whether the system is S/4HANA and whether a released view exists for your needs. Do not change the data source without testing, since the field names and semantics differ.

---

### D. Valid, could be modernized: error handling around ALV

**Original statement (lines 21–24):**
```abap
cl_salv_table=>factory(
  IMPORTING r_salv_table = DATA(lo_alv)
  CHANGING t_table = lt_po ).
lo_alv->display( ).
```

**Why it could be improved:** The statement is modern, but it has no exception handling. `cl_salv_table=>factory` can raise `cx_salv_msg`. Without a handler, the user sees a short dump.

**Modern alternative:** Wrap the calls in `TRY ... CATCH`.

**Before:**
```abap
cl_salv_table=>factory(
  IMPORTING r_salv_table = DATA(lo_alv)
  CHANGING t_table = lt_po ).
lo_alv->display( ).
```

**After:**
```abap
TRY.
    cl_salv_table=>factory(
      IMPORTING r_salv_table = DATA(lo_alv)
      CHANGING  t_table      = lt_po ).
    lo_alv->display( ).
  CATCH cx_salv_msg INTO DATA(lx_salv).
    MESSAGE lx_salv->get_text( ) TYPE 'E'.
ENDTRY.
```

**Recommendation and priority:** **Medium.** Improves robustness. Low effort.

---

### E. Valid, could be modernized: result checking

**Original:** No check on whether `lt_po` is empty. The user gets an empty ALV grid.

**Modern alternative:** `IS INITIAL` check, with a message.

**Before:**
```abap
" (no check) -> empty ALV is displayed
```

**After:**
```abap
IF lt_po IS INITIAL.
  MESSAGE 'No PO items found for the selection.' TYPE 'S' DISPLAY LIKE 'W'.
  RETURN.
ENDIF.
```

**Recommendation and priority:** **Low.** Usability.

---

### F. Valid, could be modernized: sorting and row limits in the query

**Original (lines 10–20):** No `ORDER BY`. No row limit (`UP TO n ROWS`).

**Why it matters:** Without a limit, a broad selection can read very large data sets. The modern Open SQL options control this in the database, not in ABAP. `ORDER BY` gives a stable, predictable order.

**Before:**
```abap
  WHERE a~lifnr IN @s_lifnr
  AND a~bedat IN @s_bedat
  INTO TABLE @DATA(lt_po).
```

**After:**
```abap
  WHERE a~lifnr IN @s_lifnr
  AND a~bedat IN @s_bedat
  ORDER BY a~ebeln, b~ebelp
  INTO TABLE @DATA(lt_po)
  UP TO 5000 ROWS.
```

**Recommendation and priority:** **Medium.** Performance and predictability. Confirm the row limit with the business.

---

### G. Valid, could be modernized: ALV column settings

**Original:** Default column widths. No optimization.

**Modern alternative:** Use the ALV column and function objects.

**Before:**
```abap
lo_alv->display( ).
```

**After:**
```abap
lo_alv->get_columns( )->set_optimize( abap_true ).
lo_alv->get_functions( )->set_all( abap_true ).
lo_alv->display( ).
```

**Recommendation and priority:** **Low.** Usability.

---

## 4. Prioritized action list

| Priority | Item | Section | Effort |
|---|---|---|---|
| 1 (Medium) | Add `TRY / CATCH cx_salv_msg` around ALV | 3D | Low |
| 2 (Medium) | Add `ORDER BY` and `UP TO n ROWS` | 3F | Low |
| 3 (Medium, check release) | Evaluate released CDS view for S/4HANA | 3C | Medium–High |
| 4 (Low) | Replace helper `DATA` with `FOR ekko-...` | 3A | Very low |
| 5 (Low) | Empty-result check with message | 3E | Very low |
| 6 (Low) | ALV column optimization | 3G | Very low |
| 7 (Optional) | Class-based structure | 3B | Medium |

---

## 5. Notes and limits

- **Static review only.** The code was not compiled, not run, and not checked with the ABAP syntax checker or the ATC (ABAP Test Cockpit) on a real system. Running ATC with the "Simplification Database" and "Modernization" checks would confirm this review.
- **Release dependency:** The `@` escapes and inline declarations assume ABAP 7.40 SP05 or later. If the system is older, the code would not compile, and this review would need to be redone.
- **Released view names** in section 3C are examples. Confirm them in the system before use.
- **Naming and business logic** (what "open" means) are outside the scope of this review. See the earlier review notes in `abap_review_notes.md`.
