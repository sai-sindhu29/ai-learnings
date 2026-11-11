# ABAP Unit Test Plan and Code: `zms_po_open_list`

**Source analyzed:** `github-day-0/po_open_list` (report `zms_po_open_list`, 25 lines)
**Output:** `github-day-8/abap_unit_tests.md`
**Original source file:** not modified

---

## 0. Limitations (read first)

| Item | Status |
|---|---|
| Target SAP release | **Unknown.** Code assumes ABAP 7.50 or later (inline declarations, `@` escapes, `WITH EMPTY KEY`, `RANGE OF` types). Confirm your release before use. |
| Run on a real SAP system | **No.** No SAP system was available. The tests have **not been executed** with ABAP Unit. |
| Syntax check | Done with **abaplint** (open-source ABAP parser, v2.120.101, configured for `v755`). It checks the report and test classes, but **it does not know SAP standard objects**. So calls to `CL_ABAP_UNIT_ASSERT`, `CL_OSQL_TEST_ENVIRONMENT`, `CL_SALV_TABLE`, and DDIC types (`EKKO`, `EKPO`) were **not** verified. A real SAP syntax check is still required. |
| Database tests | Rely on `CL_OSQL_TEST_ENVIRONMENT` (Open SQL test doubles). Behavior of joins on doubled tables should be confirmed on your release. |

---

## 1. What is testable in the original program

The original program is a **flat report**:
- It has no methods, no functions, and no classes.
- Its logic is one `SELECT` with a join and `WHERE` filters, followed by an ALV display.
- ABAP Unit can only test **callable units**. The flat code cannot be called from a test.

| Part of original code | Testable? | Reason |
|---|---|---|
| `SELECT-OPTIONS` (selection screen) | No | UI. Tested manually. |
| `SELECT ... INNER JOIN ... WHERE ...` (lines 10–20) | **Yes, after a small refactor** | This is the business logic: which PO items are returned for the vendor and date ranges. |
| `cl_salv_table=>factory` / `display` (lines 21–24) | No (in unit tests) | Displays a full-screen ALV. Tested manually. |

**The business logic to test is the selection:**
1. Vendor range (`s_lifnr`) filters `EKKO-LIFNR`.
2. Date range (`s_bedat`) filters `EKKO-BEDAT`.
3. An inner join returns **one row per PO item** and **excludes** POs without items, and items without a PO header.

---

## 2. Refactoring: what changed and why

The SELECT must move into a **method** so a test can call it. Everything else stays the same.

| Change | Type | Why |
|---|---|---|
| The `SELECT` moved, unchanged, into `lcl_po_repository=>get_po_items`. The column list, join, and `WHERE` are identical. | Structure only | ABAP Unit needs a callable unit. Business logic is unchanged. |
| The vendor and date filters are now **parameters** (`it_lifnr`, `it_bedat`) instead of read from `s_lifnr` / `s_bedat` directly. The program passes `s_lifnr[]` and `s_bedat[]` in. | Structure only | Lets the test supply its own filter values. Same values reach the same `WHERE` clause. |
| `DATA: lv_lifnr ..., lv_bedat ...` removed. `SELECT-OPTIONS` now use `FOR ekko-lifnr` / `FOR ekko-bedat`. | Code cleanup | These two variables were only used for typing. Same field types, same selection screen. |
| Result table type is declared as `tt_po_item` in the class instead of inline `DATA(lt_po)`. | Structure only | The method needs a named return type. The rows and columns are the same. |
| `START-OF-SELECTION` now calls the repository, then displays the ALV as before. | Structure only | Keeps the program's behavior. |

**Business logic NOT changed.** The program still:
- returns all PO items matching the ranges,
- does **not** filter for open items,
- does **not** limit the number of rows,
- does **not** add `ORDER BY`.

**Why those four are not changed here:** each one would change which rows the program returns. The task says not to change business logic without explanation. The tests document the **current** behavior. The improvements from the earlier review (open-item filter, row limit, ordering) are shown in section 6 as illustrative examples only.

---

## 3. Executable code (refactored program with ABAP Unit tests)

**Status: executable ABAP, syntax-checked with abaplint only.** Copy this whole block into a new report in SE38 / ADT. Run the tests with **Ctrl+Shift+F10** (SE38) or **Run As → ABAP Unit Test** (ADT).

The test classes use `FOR TESTING`, `RISK LEVEL HARMLESS`, `DURATION SHORT`, and `CL_ABAP_UNIT_ASSERT`.

```abap
REPORT zms_po_open_list.

*----------------------------------------------------------------------*
* Selection screen (same fields as the original)
*----------------------------------------------------------------------*
SELECT-OPTIONS: s_lifnr FOR ekko-lifnr,
                s_bedat FOR ekko-bedat.

*----------------------------------------------------------------------*
* Data access: the original SELECT, moved unchanged into a method
*----------------------------------------------------------------------*
CLASS lcl_po_repository DEFINITION.
  PUBLIC SECTION.
    TYPES:
      BEGIN OF ty_po_item,
        ebeln TYPE ekko-ebeln,
        lifnr TYPE ekko-lifnr,
        bedat TYPE ekko-bedat,
        ebelp TYPE ekpo-ebelp,
        matnr TYPE ekpo-matnr,
        menge TYPE ekpo-menge,
      END OF ty_po_item,
      tt_po_item TYPE STANDARD TABLE OF ty_po_item WITH EMPTY KEY,
      tr_lifnr   TYPE RANGE OF ekko-lifnr,
      tr_bedat   TYPE RANGE OF ekko-bedat.

    METHODS get_po_items
      IMPORTING it_lifnr        TYPE tr_lifnr
                it_bedat        TYPE tr_bedat
      RETURNING VALUE(rt_items) TYPE tt_po_item.
ENDCLASS.

CLASS lcl_po_repository IMPLEMENTATION.
  METHOD get_po_items.
    SELECT a~ebeln,
           a~lifnr,
           a~bedat,
           b~ebelp,
           b~matnr,
           b~menge
      FROM ekko AS a
      INNER JOIN ekpo AS b ON b~ebeln = a~ebeln
      WHERE a~lifnr IN @it_lifnr
        AND a~bedat IN @it_bedat
      INTO TABLE @rt_items.
  ENDMETHOD.
ENDCLASS.

*----------------------------------------------------------------------*
* Main flow
*----------------------------------------------------------------------*
START-OF-SELECTION.
  DATA(lo_repo) = NEW lcl_po_repository( ).
  DATA(lt_po)   = lo_repo->get_po_items(
                    it_lifnr = s_lifnr[]
                    it_bedat = s_bedat[] ).

  cl_salv_table=>factory(
    IMPORTING r_salv_table = DATA(lo_alv)
    CHANGING  t_table      = lt_po ).
  lo_alv->display( ).

*======================================================================*
* ABAP Unit tests
*======================================================================*
CLASS ltc_po_repository DEFINITION FINAL FOR TESTING
  RISK LEVEL HARMLESS
  DURATION SHORT.

  PRIVATE SECTION.
    TYPES:
      tt_ekko TYPE STANDARD TABLE OF ekko WITH EMPTY KEY,
      tt_ekpo TYPE STANDARD TABLE OF ekpo WITH EMPTY KEY.

    CLASS-DATA go_env TYPE REF TO if_osql_test_environment.
    DATA mo_repo TYPE REF TO lcl_po_repository.

    CLASS-METHODS class_setup.
    CLASS-METHODS class_teardown.
    METHODS setup.

    METHODS given_data
      IMPORTING it_ekko TYPE tt_ekko
                it_ekpo TYPE tt_ekpo.
    METHODS given_standard_fixture.

    " Positive
    METHODS p01_one_row_per_item FOR TESTING.
    METHODS p02_maps_fields_correctly FOR TESTING.
    METHODS p03_multi_vendor_date_filter FOR TESTING.
    METHODS p04_empty_date_no_filter FOR TESTING.

    " Negative
    METHODS n01_vendor_not_in_range FOR TESTING.
    METHODS n02_excluded_vendor_absent FOR TESTING.
    METHODS n03_empty_db_returns_nothing FOR TESTING.
    METHODS n04_header_no_items_excluded FOR TESTING.
    METHODS n05_item_no_header_excluded FOR TESTING.

    " Boundary
    METHODS b01_date_equal_to_low_bound FOR TESTING.
    METHODS b02_date_equal_to_high_bound FOR TESTING.
    METHODS b03_day_after_high_bound FOR TESTING.
    METHODS b04_day_before_low_bound FOR TESTING.
    METHODS b05_year_edge_date_included FOR TESTING.
    METHODS b06_zero_quantity_is_returned FOR TESTING.
ENDCLASS.

CLASS ltc_po_repository IMPLEMENTATION.

  METHOD class_setup.
    go_env = cl_osql_test_environment=>create(
               i_dependencies = VALUE #( ( 'EKKO' ) ( 'EKPO' ) ) ).
  ENDMETHOD.

  METHOD class_teardown.
    go_env->destroy( ).
  ENDMETHOD.

  METHOD setup.
    go_env->clear_doubles( ).
    mo_repo = NEW lcl_po_repository( ).
  ENDMETHOD.

  METHOD given_data.
    go_env->insert_test_data( it_ekko ).
    go_env->insert_test_data( it_ekpo ).
  ENDMETHOD.

  METHOD given_standard_fixture.
    given_data(
      it_ekko = VALUE #(
        ( ebeln = '4500000001' lifnr = '0000100001' bedat = '20260115' )
        ( ebeln = '4500000002' lifnr = '0000100002' bedat = '20260201' )
        ( ebeln = '4500000003' lifnr = '0000100001' bedat = '20251231' )
        ( ebeln = '4500000004' lifnr = '0000100001' bedat = '20260131' ) )  " header, no items
      it_ekpo = VALUE #(
        ( ebeln = '4500000001' ebelp = '00010' matnr = 'MAT-A' menge = '5' )
        ( ebeln = '4500000001' ebelp = '00020' matnr = 'MAT-B' menge = '10' )
        ( ebeln = '4500000002' ebelp = '00010' matnr = 'MAT-C' menge = '0' )
        ( ebeln = '4500000003' ebelp = '00010' matnr = 'MAT-D' menge = '3' )
        ( ebeln = '4500000009' ebelp = '00010' matnr = 'MAT-X' menge = '1' ) ) ). " item, no header
  ENDMETHOD.

  "--- Positive -----------------------------------------------------------

  METHOD p01_one_row_per_item.
    given_standard_fixture( ).

    DATA(lt_result) = mo_repo->get_po_items(
      it_lifnr = VALUE #( ( sign = 'I' option = 'EQ' low = '0000100001' ) )
      it_bedat = VALUE #( ( sign = 'I' option = 'BT' low = '20260101' high = '20261231' ) ) ).

    cl_abap_unit_assert=>assert_equals(
      act = lines( lt_result )
      exp = 2
      msg = 'Vendor 0000100001 in 2026 must return 2 items of PO 4500000001' ).
  ENDMETHOD.

  METHOD p02_maps_fields_correctly.
    given_standard_fixture( ).

    DATA(lt_result) = mo_repo->get_po_items(
      it_lifnr = VALUE #( ( sign = 'I' option = 'EQ' low = '0000100001' ) )
      it_bedat = VALUE #( ( sign = 'I' option = 'BT' low = '20260101' high = '20261231' ) ) ).

    READ TABLE lt_result INTO DATA(ls_item) WITH KEY ebelp = '00020'.
    cl_abap_unit_assert=>assert_subrc(
      exp = 0
      act = sy-subrc
      msg = 'Item 00020 must be returned' ).

    cl_abap_unit_assert=>assert_equals(
      act = ls_item-ebeln
      exp = '4500000001'
      msg = 'PO number mapped incorrectly' ).
    cl_abap_unit_assert=>assert_equals(
      act = ls_item-lifnr
      exp = '0000100001'
      msg = 'Vendor mapped incorrectly' ).
    cl_abap_unit_assert=>assert_equals(
      act = ls_item-matnr
      exp = 'MAT-B'
      msg = 'Material mapped incorrectly' ).
    cl_abap_unit_assert=>assert_equals(
      act = ls_item-menge
      exp = 10
      msg = 'Quantity mapped incorrectly' ).
  ENDMETHOD.

  METHOD p03_multi_vendor_date_filter.
    given_standard_fixture( ).

    DATA(lt_result) = mo_repo->get_po_items(
      it_lifnr = VALUE #( ( sign = 'I' option = 'EQ' low = '0000100001' )
                          ( sign = 'I' option = 'EQ' low = '0000100002' ) )
      it_bedat = VALUE #( ( sign = 'I' option = 'BT' low = '20260101' high = '20261231' ) ) ).

    " PO 1 (2 items) + PO 2 (1 item). PO 3 is outside the date range.
    cl_abap_unit_assert=>assert_equals(
      act = lines( lt_result )
      exp = 3
      msg = 'Two vendors in 2026 must return 3 items' ).
  ENDMETHOD.

  METHOD p04_empty_date_no_filter.
    given_standard_fixture( ).

    DATA(lt_result) = mo_repo->get_po_items(
      it_lifnr = VALUE #( ( sign = 'I' option = 'EQ' low = '0000100001' )
                          ( sign = 'I' option = 'EQ' low = '0000100002' ) )
      it_bedat = VALUE #( ) ).

    " PO 1 (2) + PO 2 (1) + PO 3 (1). PO 4 has no items, so it is excluded.
    cl_abap_unit_assert=>assert_equals(
      act = lines( lt_result )
      exp = 4
      msg = 'Empty date range must not filter by date' ).
  ENDMETHOD.

  "--- Negative -----------------------------------------------------------

  METHOD n01_vendor_not_in_range.
    given_standard_fixture( ).

    DATA(lt_result) = mo_repo->get_po_items(
      it_lifnr = VALUE #( ( sign = 'I' option = 'EQ' low = '0000999999' ) )
      it_bedat = VALUE #( ) ).

    cl_abap_unit_assert=>assert_initial(
      act = lt_result
      msg = 'Unknown vendor must return no items' ).
  ENDMETHOD.

  METHOD n02_excluded_vendor_absent.
    given_standard_fixture( ).

    " Exclude vendor 0000100001, keep everything else
    DATA(lt_result) = mo_repo->get_po_items(
      it_lifnr = VALUE #( ( sign = 'E' option = 'EQ' low = '0000100001' ) )
      it_bedat = VALUE #( ) ).

    cl_abap_unit_assert=>assert_equals(
      act = lines( lt_result )
      exp = 1
      msg = 'Only vendor 0000100002 (1 item) must remain' ).

    READ TABLE lt_result INDEX 1 INTO DATA(ls_item).
    cl_abap_unit_assert=>assert_equals(
      act = ls_item-lifnr
      exp = '0000100002'
      msg = 'Excluded vendor must not appear in the result' ).
  ENDMETHOD.

  METHOD n03_empty_db_returns_nothing.
    " No data inserted: setup() has already cleared the doubles
    DATA(lt_result) = mo_repo->get_po_items(
      it_lifnr = VALUE #( )
      it_bedat = VALUE #( ) ).

    cl_abap_unit_assert=>assert_initial(
      act = lt_result
      msg = 'Empty database must return no items' ).
  ENDMETHOD.

  METHOD n04_header_no_items_excluded.
    given_data(
      it_ekko = VALUE #( ( ebeln = '4500000004' lifnr = '0000100001' bedat = '20260131' ) )
      it_ekpo = VALUE #( ) ).

    DATA(lt_result) = mo_repo->get_po_items(
      it_lifnr = VALUE #( ( sign = 'I' option = 'EQ' low = '0000100001' ) )
      it_bedat = VALUE #( ) ).

    cl_abap_unit_assert=>assert_initial(
      act = lt_result
      msg = 'PO header with no items must not be returned (inner join)' ).
  ENDMETHOD.

  METHOD n05_item_no_header_excluded.
    given_data(
      it_ekko = VALUE #( )
      it_ekpo = VALUE #( ( ebeln = '4500000009' ebelp = '00010' matnr = 'MAT-X' menge = '1' ) ) ).

    DATA(lt_result) = mo_repo->get_po_items(
      it_lifnr = VALUE #( )
      it_bedat = VALUE #( ) ).

    cl_abap_unit_assert=>assert_initial(
      act = lt_result
      msg = 'Item without a PO header must not be returned (inner join)' ).
  ENDMETHOD.

  "--- Boundary -----------------------------------------------------------

  METHOD b01_date_equal_to_low_bound.
    given_standard_fixture( ).

    " PO 1 is dated 20260115 = low bound
    DATA(lt_result) = mo_repo->get_po_items(
      it_lifnr = VALUE #( ( sign = 'I' option = 'EQ' low = '0000100001' ) )
      it_bedat = VALUE #( ( sign = 'I' option = 'BT' low = '20260115' high = '20261231' ) ) ).

    cl_abap_unit_assert=>assert_equals(
      act = lines( lt_result )
      exp = 2
      msg = 'Date equal to low bound must be included' ).
  ENDMETHOD.

  METHOD b02_date_equal_to_high_bound.
    given_standard_fixture( ).

    " PO 1 is dated 20260115 = high bound
    DATA(lt_result) = mo_repo->get_po_items(
      it_lifnr = VALUE #( ( sign = 'I' option = 'EQ' low = '0000100001' ) )
      it_bedat = VALUE #( ( sign = 'I' option = 'BT' low = '20260101' high = '20260115' ) ) ).

    cl_abap_unit_assert=>assert_equals(
      act = lines( lt_result )
      exp = 2
      msg = 'Date equal to high bound must be included' ).
  ENDMETHOD.

  METHOD b03_day_after_high_bound.
    given_standard_fixture( ).

    " PO 1 is dated 20260115, the range ends 20260114
    DATA(lt_result) = mo_repo->get_po_items(
      it_lifnr = VALUE #( ( sign = 'I' option = 'EQ' low = '0000100001' ) )
      it_bedat = VALUE #( ( sign = 'I' option = 'BT' low = '20260101' high = '20260114' ) ) ).

    cl_abap_unit_assert=>assert_initial(
      act = lt_result
      msg = 'Date one day after high bound must be excluded' ).
  ENDMETHOD.

  METHOD b04_day_before_low_bound.
    given_standard_fixture( ).

    " PO 1 is dated 20260115, the range starts 20260116
    DATA(lt_result) = mo_repo->get_po_items(
      it_lifnr = VALUE #( ( sign = 'I' option = 'EQ' low = '0000100001' ) )
      it_bedat = VALUE #( ( sign = 'I' option = 'BT' low = '20260116' high = '20261231' ) ) ).

    cl_abap_unit_assert=>assert_initial(
      act = lt_result
      msg = 'Date one day before low bound must be excluded' ).
  ENDMETHOD.

  METHOD b05_year_edge_date_included.
    given_standard_fixture( ).

    " PO 3 is dated 20251231 (last day of 2025)
    DATA(lt_result) = mo_repo->get_po_items(
      it_lifnr = VALUE #( ( sign = 'I' option = 'EQ' low = '0000100001' ) )
      it_bedat = VALUE #( ( sign = 'I' option = 'BT' low = '20251231' high = '20251231' ) ) ).

    cl_abap_unit_assert=>assert_equals(
      act = lines( lt_result )
      exp = 1
      msg = 'Last day of 2025 must be included' ).
  ENDMETHOD.

  METHOD b06_zero_quantity_is_returned.
    given_standard_fixture( ).

    " PO 2 item has menge = 0. The original code has no quantity filter.
    DATA(lt_result) = mo_repo->get_po_items(
      it_lifnr = VALUE #( ( sign = 'I' option = 'EQ' low = '0000100002' ) )
      it_bedat = VALUE #( ) ).

    cl_abap_unit_assert=>assert_equals(
      act = lines( lt_result )
      exp = 1
      msg = 'Zero-quantity item must still be returned' ).

    READ TABLE lt_result INDEX 1 INTO DATA(ls_item).
    cl_abap_unit_assert=>assert_equals(
      act = ls_item-menge
      exp = 0
      msg = 'Quantity must be 0' ).
  ENDMETHOD.

ENDCLASS.
```

---

## 4. Test fixture

The `given_standard_fixture` method inserts this data into the Open SQL test doubles before each test that needs it.

**EKKO (PO headers)**

| EBELN | LIFNR | BEDAT | Purpose |
|---|---|---|---|
| 4500000001 | 0000100001 | 20260115 | Standard PO, 2 items |
| 4500000002 | 0000100002 | 20260201 | Second vendor, 1 item with quantity 0 |
| 4500000003 | 0000100001 | 20251231 | Last day of 2025, 1 item |
| 4500000004 | 0000100001 | 20260131 | Header with **no items** |

**EKPO (PO items)**

| EBELN | EBELP | MATNR | MENGE | Purpose |
|---|---|---|---|---|
| 4500000001 | 00010 | MAT-A | 5 | |
| 4500000001 | 00020 | MAT-B | 10 | Used in field-mapping test |
| 4500000002 | 00010 | MAT-C | 0 | Zero quantity boundary |
| 4500000003 | 00010 | MAT-D | 3 | |
| 4500000009 | 00010 | MAT-X | 1 | Item with **no header** |

---

## 5. Test cases

Each row explains the scenario, the input, the expected result, and the assertion used.

### 5.1 Positive scenarios

| ID | Test method | Scenario | Input | Expected result | Assertion |
|---|---|---|---|---|---|
| P01 | `p01_one_row_per_item` | Vendor and 2026 date range return one row per item | Vendor `0000100001`, dates `20260101`–`20261231` | **2 rows** (both items of PO 4500000001). PO 3 is outside the date range. PO 4 has no items. | `assert_equals` on `lines( )` |
| P02 | `p02_maps_fields_correctly` | Each output field has the right value | Same as P01, read row with `EBELP = 00020` | PO `4500000001`, vendor `0000100001`, material `MAT-B`, quantity `10` | `assert_subrc`, then `assert_equals` on each field |
| P03 | `p03_multi_vendor_date_filter` | Two vendors with a date filter | Vendors `0000100001` and `0000100002`, dates in 2026 | **3 rows**: PO 1 (2 items) and PO 2 (1 item). PO 3 is outside the date range. | `assert_equals` on `lines( )` |
| P04 | `p04_empty_date_no_filter` | An empty date range means "no date filter" | Two vendors, empty date range | **4 rows**: PO 1 (2), PO 2 (1), PO 3 (1). PO 4 still excluded (no items). | `assert_equals` on `lines( )` |

### 5.2 Negative scenarios

| ID | Test method | Scenario | Input | Expected result | Assertion |
|---|---|---|---|---|---|
| N01 | `n01_vendor_not_in_range` | Vendor with no POs | Vendor `0000999999` | **No rows** | `assert_initial` |
| N02 | `n02_excluded_vendor_absent` | Exclusion range (`SIGN = 'E'`) removes a vendor | Exclude `0000100001`, no date filter | **1 row**, vendor `0000100002` only | `assert_equals` on count, then on vendor |
| N03 | `n03_empty_db_returns_nothing` | No data in the database | No data inserted | **No rows** | `assert_initial` |
| N04 | `n04_header_no_items_excluded` | PO header with no items is not returned (inner join) | Only PO 4 inserted, no items | **No rows** | `assert_initial` |
| N05 | `n05_item_no_header_excluded` | Item with no PO header is not returned (inner join) | Only item for PO 4500000009 inserted, no header | **No rows** | `assert_initial` |

### 5.3 Boundary scenarios

| ID | Test method | Scenario | Input | Expected result | Assertion |
|---|---|---|---|---|---|
| B01 | `b01_date_equal_to_low_bound` | Date equals the low bound | Range starts `20260115` (PO 1 date) | **Included**: 2 rows | `assert_equals` on count |
| B02 | `b02_date_equal_to_high_bound` | Date equals the high bound | Range ends `20260115` | **Included**: 2 rows | `assert_equals` on count |
| B03 | `b03_day_after_high_bound` | One day after the high bound | Range ends `20260114` | **Excluded**: no rows | `assert_initial` |
| B04 | `b04_day_before_low_bound` | One day before the low bound | Range starts `20260116` | **Excluded**: no rows | `assert_initial` |
| B05 | `b05_year_edge_date_included` | Last day of the year | Range `20251231`–`20251231` | **Included**: 1 row (PO 3) | `assert_equals` on count |
| B06 | `b06_zero_quantity_is_returned` | Quantity 0 is not filtered out | Vendor `0000100002`, no date filter | **1 row**, quantity `0` | `assert_equals` on count and quantity |

**Why the boundary tests matter:** `IN` with `BT` is inclusive at both ends. B01 and B02 confirm that. B03 and B04 confirm that the day just outside is excluded. If someone later changed the filter to `>` or `<`, these tests would fail.

---

## 6. Illustrative examples (NOT executable, NOT in the test class)

These show ideas from the earlier reviews. They are **not** part of the code above, because they would change the program's current behavior.

### 6.1 Test for an "open items only" filter (new business rule)

**Status: illustrative.** This requires a decision from the business about what "open" means. It is not in the original program.

```abap
" ILLUSTRATIVE ONLY - requires adding the filter to get_po_items first
METHOD p05_open_items_only.
  given_data(
    it_ekko = VALUE #( ( ebeln = '4500000005' lifnr = '0000100001' bedat = '20260115' ) )
    it_ekpo = VALUE #( ( ebeln = '4500000005' ebelp = '00010' matnr = 'MAT-E' menge = '4' elikz = 'X' )   " delivery completed
                       ( ebeln = '4500000005' ebelp = '00020' matnr = 'MAT-F' menge = '2' elikz = ' ' ) ) ).

  DATA(lt_result) = mo_repo->get_po_items(
    it_lifnr = VALUE #( ( sign = 'I' option = 'EQ' low = '0000100001' ) )
    it_bedat = VALUE #( ) ).

  " Expect only the open item 00020
  cl_abap_unit_assert=>assert_equals( act = lines( lt_result ) exp = 1 ).
ENDMETHOD.
```

Note: the `elikz` field is not in `ty_po_item`, so the structure would also need updating.

### 6.2 Test for a row limit (new behavior)

**Status: illustrative.** Needs `UP TO n ROWS` added to the SELECT first. Then insert more rows than the limit and assert that the result has at most `n` rows.

### 6.3 Test seam with an interface (if `CL_OSQL_TEST_ENVIRONMENT` is not available)

**Status: illustrative.** Use this only if your release does not support the Open SQL test environment.

```abap
" ILLUSTRATIVE ONLY
INTERFACE lif_po_source.
  TYPES tt_items TYPE STANDARD TABLE OF lcl_po_repository=>ty_po_item WITH EMPTY KEY.
  METHODS read IMPORTING it_lifnr TYPE lcl_po_repository=>tr_lifnr
                         it_bedat TYPE lcl_po_repository=>tr_bedat
               RETURNING VALUE(rt_items) TYPE tt_items.
ENDINTERFACE.
```

A test double class would implement `lif_po_source` and return fixed rows. The repository would then take the source through its constructor. This also tests the logic without a database, but it does not test the SQL itself.

---

## 7. How to run and maintain the tests

1. **Run:** In SE38 or ADT, run the report's ABAP Unit tests (Ctrl+Shift+F10 in SE38, or **Run As → ABAP Unit Test** in ADT).
2. **Expected result:** all 15 test methods should pass (P01–P04, N01–N05, B01–B06). This has not been run yet.
3. **Manual tests (not covered by ABAP Unit):**
   - Run the report on the selection screen and check the ALV appears with the expected columns.
   - Run with empty selection fields and confirm the ALV still appears (current behavior).
   - Confirm the ALV "Back" and "Exit" buttons end the program.
4. **Maintenance:** If the SELECT changes (for example, adding `ORDER BY` or an open-item filter), update the matching tests in the same change.
5. **Naming:** ABAP Unit method names are limited to 30 characters. All names above respect this.

---

## 8. Summary

| Metric | Value |
|---|---|
| Test methods | 15 (4 positive, 5 negative, 6 boundary) |
| Setup and teardown | `class_setup` / `class_teardown` (test environment), `setup` (clear doubles, new repository) |
| Business logic changed | **None** (structure refactored only) |
| Executed on SAP | **No** |
| Syntax checked | abaplint only (SAP objects not verified) |
| Target release | Unknown, assumed 7.50+ |

**Next steps:**
1. Confirm the SAP release.
2. Paste the code into a development system and run ABAP Unit.
3. Run the ATC checks (see the earlier `obsolete_statements.md`).
4. Decide on the "open items" business rule, then add tests from section 6.1.
