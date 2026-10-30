# Test Runs: Prompt Reviewer (SAP ABAP)

## Prompt 1: Constructors in OO ABAP

**Bad Prompt:**
Act as a senior SAP ABAP developer. I am learning Object-Oriented ABAP (OO ABAP) and want to understand constructors. Explain what a constructor is in OO ABAP, why it is needed, and how it works.



**Missing:** Example, Format, Constraints

**Hidden problem:** None in the original, but watch the rewrite: asking for a table, code, execution flow, output and a business example in only 200 words is a conflicting constraint.

**Better Prompt:**
Act as a senior SAP ABAP developer. I am learning Object-Oriented ABAP (OO ABAP) and want to understand constructors.
Explain instance constructors (CONSTRUCTOR) and static constructors
(CLASS\_CONSTRUCTOR): what they are, why they are needed, when each one runs,
and how they differ.
Structure your answer like this:

1. Simple definition of each (2-3 sentences).
2. Comparison table: trigger, how often it runs, parameters allowed, typical use.
3. One short ABAP code example showing both constructors in one class,
with the expected output.
4. Step-by-step execution flow for that example.
5. One real-world SAP business example (e.g. loading customizing data once).
6. Three common beginner mistakes.

Constraints: I am a beginner. Use simple English and explain every technical term. Use valid ABAP syntax for \[S/4HANA / ECC]. Keep the text short (max \~400 words, not counting code). No unnecessary theory.

## Prompt 2: Fetching sales data

**Bad Prompt:**
Write ABAP code to get sales data.



**Missing:** Role, Context, Input, Format, Constraints, Success criteria

**Hidden problem:** "Sales data" is undefined. The model will guess tables (VBAK, VBAP, VBRK?) and fields, and the code will probably not match what you need.

**Better Prompt:**

Act as a senior SAP ABAP developer.
Write an ABAP program that reads sales order data for a report.
System: \[S/4HANA 2023 / ECC 6.0].

Data needed:

* Header from VBAK: VBELN, ERDAT, KUNNR, NETWR
* Items from VBAP: POSNR, MATNR, KWMENG

Selection screen:

* Sales order number (SELECT-OPTIONS)
* Creation date (SELECT-OPTIONS)
* Sales organization (PARAMETERS, mandatory)

Requirements:

* Use one JOIN instead of nested SELECTs.
* Use new Open SQL syntax (@ host variables, inline declarations).
* Show a message if no data is found.

Return the complete code in one code block, then max 5 bullet points explaining the key parts.



## Prompt 3: Slow code

**Bad Prompt:**
Fix my code, it's slow.

```abap
SELECT \\\* FROM mara INTO TABLE lt\\\_mara.
LOOP AT lt\\\_mara INTO ls\\\_mara.
  SELECT SINGLE maktx FROM makt INTO lv\\\_maktx
    WHERE matnr = ls\\\_mara-matnr.
  WRITE: / ls\\\_mara-matnr, lv\\\_maktx.
ENDLOOP.
```

````

\*\*Missing:\*\* Role, Context, Constraints, Format, Success criteria

\*\*Hidden problem:\*\* The MAKT read has no language key (SPRAS), so it returns a random language's description. That is a correctness bug, not just a performance issue, and the prompt does not mention it.

\*\*Better Prompt:\*\*

Act as a senior SAP ABAP developer doing a performance review.

The code below is slow. MARA has about \\\[500,000] entries in our system (\\\[S/4HANA / ECC]).

Tasks:
1. Name every performance problem and every correctness bug.
2. Rewrite the code so it is fast and correct.
   Material descriptions must be in the logon language (sy-langu).
3. Keep the same output: material number and description per line.

Rules:
- Read only the fields that are needed (no SELECT \\\*).
- No SELECT inside a LOOP.
- Use new Open SQL syntax.

Format: a numbered list of problems (one line each), then the corrected code in one code block.

```abap
SELECT \\\* FROM mara INTO TABLE lt\\\_mara.
LOOP AT lt\\\_mara INTO ls\\\_mara.
  SELECT SINGLE maktx FROM makt INTO lv\\\_maktx
    WHERE matnr = ls\\\_mara-matnr.
  WRITE: / ls\\\_mara-matnr, lv\\\_maktx.
ENDLOOP.
```
````

\---

## Prompt 4: BAPIs

**Bad Prompt:**
Explain BAPIs.



**Missing:** Role, Context, Example, Format, Constraints

**Hidden problem:** No level or purpose given, so the answer could be a one-line definition or a long theory text about the Business Object Repository.

**Better Prompt:**



Act as a senior SAP ABAP developer teaching a junior colleague.

I know basic ABAP (reports, internal tables, function modules) but have never
used a BAPI. I need to create sales orders from an ABAP program.

Explain:

1. What a BAPI is and how it differs from a normal function module (3-4 sentences).
2. How to find the right BAPI (transaction BAPI, SE37).
3. Why BAPI\_TRANSACTION\_COMMIT is needed and what happens without it.
4. How to read the RETURN table for errors.

Include one short ABAP example that calls BAPI\_SALESORDER\_CREATEFROMDAT2 with minimal data, checks RETURN, and commits only on success.

Use simple English, max \~350 words plus the code. End with 3 common mistakes.



## Prompt 5: ALV report

**Bad Prompt:**

Create an ALV report.
**Missing:** Role, Context, Input, Format, Constraints, Success criteria

**Hidden problem:** ALV has several techniques (REUSE\_ALV\_GRID\_DISPLAY, CL\_SALV\_TABLE, CL\_GUI\_ALV\_GRID). Without saying which one and which data to show, the result is a random demo.

**Better Prompt:**



Act as a senior SAP ABAP developer.

Create an ALV report using CL\_SALV\_TABLE that shows open purchase orders.
System: \[S/4HANA / ECC 6.0].

Data:

* EKKO: EBELN, BUKRS, LIFNR, BEDAT
* EKPO: EBELP, MATNR, MENGE, NETPR

Selection screen: company code (mandatory), vendor and PO date (SELECT-OPTIONS).

ALV features:

* Optimized column width
* Standard toolbar functions (sort, filter, export)
* Zebra pattern
* Column headers in plain English

Rules: use a local class structure (selection, data read, display in separate methods), new Open SQL syntax, and handle the case of no data found.

Return the complete program in one code block, then a short explanation (max 5 bullet points).

