# ABAP Code Review Notes: `zms_po_open_list`

**Source reviewed:** `github-day-0/po_open_list` (25 lines, a single ABAP report file)
**Reviewer role:** Senior ABAP developer (static code review)
**Note:** The source was read only. No SAP system was available, so the code was not syntax-checked or run. Findings are based on reading the code.

---

## 1. What the program does

It is a simple **selection report** that lists **purchase order (PO) line items** from the SAP tables `EKKO` (PO header) and `EKPO` (PO item).

The user enters:
- a **vendor range** (`s_lifnr`)
- a **PO date range** (`s_bedat`)

The program then reads all matching PO items and shows them in an **ALV grid** (the standard SAP list viewer built with `CL_SALV_TABLE`).

**In plain words:** "Show me all PO lines for these vendors, created in these dates."

> The name says "open list", but the code does **not** filter for open POs. See Section 7.

---

## 2. Section-by-section walkthrough

| Lines | Section | What it does |
|---|---|---|
| 1 | `REPORT zms_po_open_list.` | Declares the program. Every executable ABAP report needs this. |
| 3–4 | `DATA:` | Declares two helper variables, `lv_lifnr` and `lv_bedat`. They exist only to give the selection fields a data type. |
| 6–7 | `SELECT-OPTIONS:` | Creates two input fields on the selection screen. Each one is a range (low/high values, plus include/exclude). |
| 9 | `START-OF-SELECTION.` | The main logic starts here. It runs after the user presses Execute. |
| 10–20 | `SELECT ... INTO TABLE @DATA(lt_po)` | Reads the database. Joins header and items and fills an internal table. |
| 21–23 | `cl_salv_table=>factory(...)` | Creates the ALV object and passes it the internal table. |
| 24 | `lo_alv->display( ).` | Shows the ALV grid on screen. |

---

## 3. Variables, internal tables, work areas, and database operations

### 3.1 Variables

| Name | Type | Purpose |
|---|---|---|
| `lv_lifnr` | `EKKO-LIFNR` (vendor number) | Used only to type `s_lifnr`. Never used as a value. |
| `lv_bedat` | `EKKO-BEDAT` (PO date) | Used only to type `s_bedat`. Never used as a value. |
| `s_lifnr` | Select-option (range of vendor numbers) | Filter input from the user. |
| `s_bedat` | Select-option (range of dates) | Filter input from the user. |
| `lt_po` | Internal table (inline, `DATA(...)`) | Holds the query result. Its structure is built from the SELECT column list. |
| `lo_alv` | Object reference (`CL_SALV_TABLE`) | The ALV object. Created inline in the `IMPORTING` clause. |

### 3.2 Internal table `lt_po`

- Created **inline** by `INTO TABLE @DATA(lt_po)`. No separate `TYPES` or `DATA` statement is needed.
- Each row has six fields, in this order: `ebeln`, `lifnr`, `bedat`, `ebelp`, `matnr`, `menge`.
- It is a **standard table**, with one row per PO item.
- The PO header fields (`ebeln`, `lifnr`, `bedat`) repeat on every item row of the same PO. This is normal for a flat item list.

### 3.3 Work areas

- **None declared.** `INTO TABLE` fills the table directly, so no work area (`wa_...`) is used.
- Good for performance here: no row-by-row loop.

### 3.4 Database operations

| Item | Detail |
|---|---|
| Statement | One `SELECT` (Open SQL) |
| Tables | `EKKO AS a` (header), `EKPO AS b` (items) |
| Join | `INNER JOIN` on `b~ebeln = a~ebeln`. Only POs that have at least one item are returned. |
| Columns | 6 columns, listed explicitly (no `SELECT *`, which is good) |
| Filters | `a~lifnr IN @s_lifnr` and `a~bedat IN @s_bedat` |
| Row limit | **None** (no `UP TO n ROWS`) |
| Ordering | **None** (no `ORDER BY`) |
| Client handling | Automatic. Open SQL adds the client (`MANDT`) filter for you. |
| Syntax | `@` host-variable escapes and `@DATA()` inline declarations. This needs ABAP 7.40 SP05 or higher (7.50+ is common today). |

---

## 4. Complete execution flow

```
1. Program is started (SE38 / SA38 / transaction).
2. Selection screen is shown:
      - Vendor (s_lifnr) and PO date (s_bedat) fields
      - Both are empty by default = "no filter"
3. User presses Execute (F8).
4. START-OF-SELECTION runs.
5. SELECT joins EKKO and EKPO:
      - Applies the vendor and date ranges
      - Returns every matching item row
      - Fills lt_po
6. cl_salv_table=>factory() creates the ALV object from lt_po.
7. lo_alv->display() shows the ALV grid.
8. The user works in the grid (sort, filter, export).
9. Back / Exit ends the program.
```

**Key point:** the whole process is **one database read**, then **one display**. There is no loop, no update, and no write to the database. The program is **read-only**.

---

## 5. Strengths

- Small, simple, and easy to follow.
- Explicit column list in the `SELECT` (no `SELECT *`).
- Uses `@` escapes and inline declarations (modern Open SQL style).
- Uses `IN` ranges, so the user can enter many values, not just one.
- Uses ALV (`CL_SALV_TABLE`), which gives sorting, filtering, and export for free.
- No loops over database rows. Set-based processing is the right pattern.

---

## 6. Potential performance issues

Ranked from highest to lowest impact:

### 6.1 HIGH: No row limit and no mandatory selection

- If the user presses **Execute with empty selection fields**, the query has no `WHERE` filter on vendor or date.
- On a live system, `EKKO` and `EKPO` can hold **millions of rows**.
- All rows go into memory (`lt_po`), then into the ALV. This can cause:
  - Long runtimes
  - High memory use on the application server
  - A dump (`TSV_TNEW_PAGE_ALLOC_FAILED` or a time-out)
  - A slow or unusable ALV grid

**Fix options:**
- Make at least one selection field mandatory (`OBLIGATORY` on the `SELECT-OPTIONS` line), or add a default date range.
- Add a row limit, for example `UP TO 5000 ROWS`, and warn the user when it is reached.
- Check the result count before showing the ALV.

### 6.2 MEDIUM: Index use is not verified

- The `WHERE` clause filters on `EKKO-LIFNR` and `EKKO-BEDAT`.
- Whether these filters are fast depends on the **secondary indexes** that exist on `EKKO` in your system.
- **Action:** Check the table indexes in SE11 (Indexes button) and run the statement through the **SQL trace (ST05)** or the **Explain SQL** in ST05. Confirm the database uses an index and does not scan the full table.

### 6.3 MEDIUM: Join on large tables

- An inner join between `EKKO` and `EKPO` is normal. It is efficient when the header filter is selective.
- If the header filter is weak (for example, a very wide date range), the join reads a large share of both tables.
- **Fix:** Keep the header filter selective (see 6.1).

### 6.4 LOW: No `ORDER BY`

- The data comes back in no defined order.
- The ALV can sort it later, so this is only a problem if the order matters before display.
- Add `ORDER BY a~ebeln, b~ebelp` if a stable, readable order is needed.

### 6.5 LOW: Extra variables

- `lv_lifnr` and `lv_bedat` are only used for typing.
- They cost almost nothing, but they add clutter.
- **Simpler option:** `SELECT-OPTIONS: s_lifnr FOR ekko-lifnr, s_bedat FOR ekko-bedat.`

---

## 7. Functional and robustness issues (beyond performance)

These are not performance problems, but a senior reviewer would raise them.

### 7.1 HIGH: The "open" list does not filter for open POs

- The program name is `po_open_list`, but there is **no open-status filter**.
- It returns **all** PO items in the date and vendor range, including items that are:
  - Fully delivered (`EKPO-ELIKZ = 'X'`)
  - Deleted (`EKPO-LOEKZ` is not blank)
  - Closed or invoiced
- **Fix:** Add conditions that match your definition of "open". For example:
  ```abap
  AND b~loekz = @space
  AND b~elikz = @space
  ```
  Confirm the business rule with the functional team first. "Open" can mean different things, such as "not delivered", "not invoiced", or "quantity remaining > 0".

### 7.2 MEDIUM: Missing authorization check

- The program reads purchasing data but does **not** call `AUTHORITY-CHECK`.
- Standard SAP does not check authorization for custom reports on its own. Users with report access may see data they should not.
- **Fix:** Add an `AUTHORITY-CHECK` against the purchasing authorization objects used in your system (for example, `M_BEST_BSA` or `M_BEST_WRK`, check with your security team). Also check the vendor and company code fields if your roles use them.

### 7.3 MEDIUM: No error handling around ALV

- `cl_salv_table=>factory` can raise `cx_salv_msg`. The code does not catch it.
- `lo_alv->display( )` can also raise an exception.
- If something fails, the user sees a short dump instead of a clear message.
- **Fix:**
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

### 7.4 LOW: No "no data" message

- If the query returns nothing, the program shows an **empty ALV grid** with no explanation.
- **Fix:** After the `SELECT`, check `IF lt_po IS INITIAL.` and show a message such as "No purchase order items found for the selection."

### 7.5 LOW: No ALV usability settings

- Columns are not optimized, and there are no column titles or ALV functions set.
- **Fix (optional):**
  ```abap
  lo_alv->get_columns( )->set_optimize( abap_true ).
  lo_alv->get_functions( )->set_all( abap_true ).
  ```

### 7.6 LOW: Program title and text symbols

- No program title is set. The report shows no title on the selection screen.
- **Fix:** Maintain the title and text symbols (for example, "Open PO Items") in the text elements.

### 7.7 LOW: Naming and documentation

- No comment block explains the purpose, author, date, or change history.
- Add a short header comment. Most SAP teams require one.

---

## 8. Suggested improved version (for reference only)

This is an illustration of the points above. **Your original file has not been changed.** Test any version in a development system before use.

```abap
REPORT zms_po_open_list.

*----------------------------------------------------------------------*
* Purpose: List open PO items by vendor and PO date
*----------------------------------------------------------------------*
SELECT-OPTIONS: s_lifnr FOR ekko-lifnr,
                s_bedat FOR ekko-bedat OBLIGATORY.   " Mandatory date range

START-OF-SELECTION.

  SELECT a~ebeln,
         a~lifnr,
         a~bedat,
         b~ebelp,
         b~matnr,
         b~menge
    FROM ekko AS a
    INNER JOIN ekpo AS b ON b~ebeln = a~ebeln
    WHERE a~lifnr IN @s_lifnr
      AND a~bedat IN @s_bedat
      AND b~loekz = @space          " Not deleted
      AND b~elikz = @space          " Delivery not completed (adjust to your definition)
    ORDER BY a~ebeln, b~ebelp
    INTO TABLE @DATA(lt_po)
    UP TO 5000 ROWS.

  IF lt_po IS INITIAL.
    MESSAGE 'No open PO items found for the selection.' TYPE 'S' DISPLAY LIKE 'W'.
    RETURN.
  ENDIF.

  TRY.
      cl_salv_table=>factory(
        IMPORTING r_salv_table = DATA(lo_alv)
        CHANGING  t_table      = lt_po ).
      lo_alv->get_columns( )->set_optimize( abap_true ).
      lo_alv->display( ).
    CATCH cx_salv_msg INTO DATA(lx_salv).
      MESSAGE lx_salv->get_text( ) TYPE 'E'.
  ENDTRY.
```

> Notes on this version:
> - `OBLIGATORY` on the date range prevents a full-table read.
> - `UP TO 5000 ROWS` is a safety limit. Adjust the number to your needs.
> - The `loekz` and `elikz` filters are assumptions about "open". Confirm them with the business.
> - An `AUTHORITY-CHECK` is still needed (see 7.2).

---

## 9. Summary of findings

| # | Severity | Area | Finding |
|---|---|---|---|
| 1 | High | Performance | No row limit and no mandatory selection. An empty selection reads all POs. |
| 2 | High | Functional | "Open" list does not filter for open items. |
| 3 | Medium | Performance | Index use on `EKKO` (`LIFNR`, `BEDAT`) is not verified. |
| 4 | Medium | Security | No `AUTHORITY-CHECK`. |
| 5 | Medium | Robustness | No `TRY/CATCH` around the ALV calls. |
| 6 | Low | Performance | No `ORDER BY`. |
| 7 | Low | Usability | No "no data" message. |
| 8 | Low | Usability | No ALV column optimization or functions. |
| 9 | Low | Code quality | Helper `DATA` declarations could be replaced with `FOR ekko-...`. |
| 10 | Low | Documentation | No header comment, title, or text symbols. |

**Overall:** The program is short, clean, and uses good modern Open SQL and ALV practice. Its main risks are **no data limit** and **a name that promises "open" items without filtering for them**. Fix those two first.

---

## 10. Review limits

- Static review only. Not compiled, not run, not tested against SAP data.
- Index names, authorization object names, and status-field meanings depend on your SAP release and customizing. Confirm them in your system.
- The "open" definition is a business decision. Check it with the functional owner.
