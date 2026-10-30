# 10 SAP Tasks × 3 Prompt Versions

## Task 1: Explain EKKO and EKPO to a new joiner

### 1A Lazy

**Prompt:** `Explain EKKO and EKPO.`

**Answer:**
EKKO and EKPO are standard SAP MM tables for purchasing documents. EKKO is the header table. It stores data that applies to the whole document, such as document number (EBELN), company code, vendor, document type and date. EKPO is the item table. It stores item data such as material, quantity, plant and net price. Both are linked by EBELN; one EKKO record can have many EKPO records (1:n). They are used for purchase orders, contracts and scheduling agreements.

### 1B 6-block

**Prompt:**
Role: You are a senior SAP MM consultant.
Task: Explain the tables EKKO and EKPO.
Context: The reader is a new joiner in our SAP team. They know basic purchasing
but nothing about SAP tables. Next week they must look up PO data in SE16N.
Input: Focus on purchase orders only.
Format: Short intro, then one table per SAP table with 5 key fields
(field | meaning), then one paragraph on how they are linked.
Constraints: Simple English, max 250 words, no ABAP code.

**Answer:**
EKKO and EKPO hold purchase order (PO) data. Every PO has one header and one or more items.

**EKKO: PO header** (one row per PO)

|Field|Meaning|
|-|-|
|EBELN|PO number|
|BUKRS|Company code|
|LIFNR|Vendor number|
|BSART|Document type (NB = standard PO)|
|BEDAT|PO date|

**EKPO: PO items** (one row per item)

|Field|Meaning|
|-|-|
|EBELN|PO number (link to EKKO)|
|EBELP|Item number (10, 20, 30…)|
|MATNR|Material|
|MENGE|Ordered quantity|
|NETPR|Net price|

**How they connect:** The PO number EBELN is in both tables. One EKKO row belongs to many EKPO rows. To see a full PO, look up the number in EKKO for the header and in EKPO for its items.

### 1C Improved

**Prompt:** 6-block prompt plus:

```text
Example: Walk through one sample PO (4500000123 with 2 items) showing which
values come from EKKO and which from EKPO.
Add: 3 steps to find this PO in SE16N, and 2 related tables worth knowing.
Success criteria: After reading, the new joiner can find a PO's vendor and
items in SE16N without help.
```

**Answer:**
EKKO and EKPO hold purchase order (PO) data. Think of a PO as a letter: EKKO is the letterhead, EKPO is the list of things you order.

\[Same two field tables as 1B.]

**Example: PO 4500000123**

|Table|Row|Key values|
|-|-|-|
|EKKO|1 row|EBELN 4500000123, LIFNR 100245, BUKRS 1000, BEDAT 15.10.2026|
|EKPO|item 10|MATNR M-1001, MENGE 50, NETPR 12.50|
|EKPO|item 20|MATNR M-2040, MENGE 10, NETPR 99.00|

**Find it in SE16N**

1. Open SE16N, enter table `EKKO`, filter EBELN = 4500000123, execute → you see the vendor.
2. Repeat with table `EKPO` and the same EBELN → you see both items.
3. Tip: use the "Technical names" button so field names and descriptions show together.

**Also good to know:** EKET (delivery dates per item) and EKBE (goods receipts and invoices per item).

\---

## Task 2: 5 test cases for PO approval

### 2A Lazy

**Prompt:** `Write 5 test cases for PO approval.`

**Answer:**

1. **Approve PO:** Submit PO → approver approves → status "Approved".
2. **Reject PO:** Submit PO → approver rejects → status "Rejected", buyer is notified.
3. **Multi-level approval:** PO above limit → goes to second approver.
4. **Change after approval:** Edit approved PO → re-approval needed.
5. **No authorization:** User without approver role cannot approve.

### 2B 6-block

**Prompt:**
Role: You are an SAP MM test lead.
Task: Write 5 test cases for our PO release strategy.
Context: S/4HANA. Net value <= 10,000 INR needs release code 01 (team lead).
Net value > 10,000 INR needs 01, then 02 (head of purchasing). Release in ME29N.
Input: Doc type NB, company code 1000, purchasing org 1000, vendor 100245.
Format: Table: ID | Title | Preconditions | Steps | Test data | Expected result.
Constraints: Mix positive and negative cases. A key user must be able to run
each case without asking questions.

**Answer:**

|ID|Title|Preconditions|Steps|Test data|Expected result|
|-|-|-|-|-|-|
|TC01|Low-value PO, one release|TL\_USER has code 01|1. Create PO in ME21N, save. 2. TL\_USER releases in ME29N with 01.|1 item, 5,000 INR|After save: not released. After 01: released, output can be sent.|
|TC02|High-value PO, two releases|TL\_USER has 01, HP\_USER has 02|1. Create PO, save. 2. Release 01. 3. Release 02.|1 item, 15,000 INR|After 01: still not fully released. After 02: released.|
|TC03|Release refused|HP\_USER has 02, refusal active in strategy|1. Create PO 15,000 INR. 2. Release 01. 3. HP\_USER refuses in ME29N.|15,000 INR|PO status refused; output cannot be sent.|
|TC04|No release authorization|BUYER\_USER has no release code|BUYER\_USER opens PO in ME29N and tries to release.|5,000 INR PO|Release not possible; authorization message shown.|
|TC05|No output before release|Output type NEU set up|1. Create PO 5,000 INR, do not release. 2. Check messages.|5,000 INR|Output not processed until PO is released.|

### 2C Improved

**Prompt:** 6-block prompt plus:

```text
Coverage must include: the boundary value exactly 10,000.00 INR, and a change
after release that pushes the value above 10,000 INR.
Example row:
TC01 | Low-value PO | TL\_USER has 01 | Create PO in ME21N, release 01 in ME29N |
5,000 INR | Released after 01
Success criteria: Every release rule is covered at least once, including
the boundary.
```

**Answer:**

|ID|Title|Preconditions|Steps|Test data|Expected result|
|-|-|-|-|-|-|
|TC01|Low-value PO|TL\_USER has 01|Create PO in ME21N; release 01 in ME29N|5,000 INR|Released after 01|
|TC02|Boundary value|TL\_USER has 01|Create PO; release 01|Exactly 10,000.00 INR|Released after 01 only; no 02 needed|
|TC03|High-value PO|TL\_USER 01, HP\_USER 02|Create PO; release 01; release 02|10,000.01 INR|Not released after 01; released after 02|
|TC04|Change after release|PO from TC01 released|Open in ME22N, raise quantity so value = 12,000 INR, save|12,000 INR|Release reset (per changeability setting); now needs 01 and 02|
|TC05|No authorization|BUYER\_USER has no code|Try to release in ME29N|5,000 INR PO|Release not possible; authorization message|

\---

## Task 3: Email, transport delayed by 1 day

### 3A Lazy

**Prompt:** `Write an email: transport delayed by 1 day.`

**Answer:**
Subject: Transport Delayed by One Day

Hi team,

The transport planned for today will be delayed by one day due to an issue found during testing. The new import is scheduled for tomorrow. We apologize for any inconvenience and will keep you updated.

Best regards,
\[Your Name]

### 3B 6-block

**Prompt:**

```text
Role: You are the SAP release coordinator.
Task: Write an email announcing a 1-day delay.
Context: Transport DEVK912345 (change CR-0457, vendor block check) was planned
for production on Thursday 5 Nov. QA found a defect in the payment block
warning. It is fixed and retested on Thursday. New import: Friday 6 Nov, 18:00 CET.
Reader: Maria Weber, AP process owner, not technical.
Format: Subject line + body, max 120 words.
Constraints: Calm and factual, no blame, no SAP jargon.
```

**Answer:**
Subject: Vendor block check: go-live moved to Friday 6 Nov

Hi Sindhu,

A short update on the new vendor block check. We planned to go live on Thursday, 5 November. During final testing we found an error in the warning for vendors with a payment block. The fix is ready and will be tested again on Thursday.

The new go-live is **Friday, 6 November, 18:00 CET**.

Everything else works as planned. I will confirm as soon as the change is live.

Best regards,
\[Name]

### 3C Improved

**Prompt:** 6-block prompt plus:

```text
Add: what this means for her team until go-live, and who to contact.
Success criteria: Maria knows the new date and what her team must do,
without needing to reply.
```

**Answer:**
Subject: Vendor block check: go-live moved to Friday 6 Nov

Hi Maria,

A short update on the new vendor block check. During final testing we found an error in the warning for vendors with a payment block. The fix is ready and will be tested again on Thursday.

**New go-live:** Friday, 6 November, 18:00 CET (one day later than planned).

**What this means for your team:** Please keep checking vendor blocks manually for one more day, as you do today.

I will confirm once the change is live. For questions, contact me or \[backup name].

Best regards,
\[Name]

\---

## Task 4: Explain a real ST22 dump

### 4A Lazy

**Prompt:** `Explain a real ST22 dump.`

**Answer:**
ST22 is the ABAP dump analysis transaction. When a program crashes, SAP writes a short dump. A real example is **TIME\_OUT**: the program ran longer than the maximum dialog runtime (parameter rdisp/max\_wprun\_time). A dump has sections like *Short text*, *What happened?*, *Error analysis*, *How to correct the error* and *Source code extract*, which shows the line where it stopped. To fix TIME\_OUT, optimize slow SELECTs or run the program in background.

### 4B 6-block

**Prompt:**

````text
Role: You are a senior ABAP developer.
Task: Explain this dump and give a fix.
Context: Custom program ZMM\_PRICE\_UPLOAD. Users upload a CSV of material
prices. It crashes for some files.
Input:
```
Runtime Errors   CONVT\_NO\_NUMBER
Except.          CX\_SY\_CONVERSION\_NO\_NUMBER
Short Text       Unable to interpret "12,50 INR" as a number.
Error analysis   The exception CX\_SY\_CONVERSION\_NO\_NUMBER was not caught
                 in procedure "MAP\_LINE" (FORM), nor propagated by RAISING.
Program ZMM\_PRICE\_UPLOAD  Include ZMM\_PRICE\_UPLOAD\_F01  Line 87
   85   SPLIT lv\_line AT ';' INTO lv\_matnr lv\_price\_c.
   86   ls\_price-matnr = lv\_matnr.
>>>> 87 ls\_price-netpr = lv\_price\_c.
```
Format: What happened / Why / Fix (code) / How to prevent it.
Constraints: Simple English, max 250 words plus code.
````

**Answer:
What happened:** The program stopped at line 87 when moving the price text into the number field NETPR.

**Why:** The file contains "12,50 INR". ABAP cannot turn that into a number because of the word "INR" and the comma as decimal separator. The error was not caught, so the program crashed.

**Fix:**

```abap
DATA lv\_clean TYPE string.
lv\_clean = lv\_price\_c.
REPLACE ALL OCCURRENCES OF 'INR' IN lv\_clean WITH ''.
REPLACE ALL OCCURRENCES OF ',' IN lv\_clean WITH '.'.
CONDENSE lv\_clean NO-GAPS.
TRY.
    ls\_price-netpr = lv\_clean.
  CATCH cx\_sy\_conversion\_no\_number.
    APPEND |Invalid price in line: { lv\_line }| TO gt\_errors.
ENDTRY.
```

**How to prevent it:** Agree on a fixed file format with users (numbers only, dot as decimal). Catch conversion errors for every line and show an error list at the end instead of crashing.

### 4C Improved

**Prompt:** 6-block prompt plus:

```text
Constraints: Files use German number format and may contain thousand
separators, e.g. "1.250,50 INR". Bad lines must be logged and skipped,
not stop the upload.
Success criteria: A file with 1,000 lines and 3 bad lines finishes and
lists exactly those 3 lines.
```

**Answer:
What happened / Why:** \[Same as 4B.] Note: "1.250,50" would also fail with a simple comma-to-dot replace, because the result "1.250.50" has two dots.

**Fix:** Remove the thousand separator first, then convert the decimal comma.

```abap
DATA lv\_clean TYPE string.
lv\_clean = lv\_price\_c.
REPLACE ALL OCCURRENCES OF 'INR' IN lv\_clean WITH ''.
REPLACE ALL OCCURRENCES OF '.' IN lv\_clean WITH ''.   " thousands
REPLACE ALL OCCURRENCES OF ',' IN lv\_clean WITH '.'.  " decimal
CONDENSE lv\_clean NO-GAPS.
TRY.
    ls\_price-netpr = lv\_clean.
    APPEND ls\_price TO gt\_prices.
  CATCH cx\_sy\_conversion\_no\_number.
    APPEND |Line { lv\_line\_no }: invalid price "{ lv\_price\_c }"| TO gt\_errors.
ENDTRY.
```

After the loop, display `gt\_errors` (for example with CL\_SALV\_TABLE). Valid lines are processed; bad lines are listed.

**Assumption:** All files use German format. If a file ever uses "12.50", this code reads it as 1250. Agree on one format with users.

\---

## Task 5: Functional spec section, vendor block

### 5A Lazy

**Prompt:** `Write a functional spec section for vendor block.`

**Answer:
Vendor Block – Functional Specification**
*Purpose:* Allow the business to block vendors to prevent transactions.
*Requirements:* The system shall allow blocking vendors for posting, purchasing and payment. Blocked vendors shall not be used in new documents. Authorized users can block and unblock vendors. Changes shall be logged.
*Transactions:* XK05 / BP.
*Assumptions:* Standard SAP functionality is used.

### 5B 6-block

**Prompt:**

```text
Role: You are an SAP MM/FI functional consultant.
Task: Write the FS section "Vendor Block Check".
Context: S/4HANA 2023. When a buyer saves a PO (ME21N/ME22N), the system must
check the vendor's blocks in the PO's company code.
Input: Use these headings: Purpose, Scope, Business rules, Messages,
Assumptions, Open points.
Format: Numbered business rules, each testable.
Constraints: Functional only, no technical design.
```

**Answer:
Purpose:** Prevent POs for vendors who must not be ordered from or paid in the PO's company code.

**Scope:** PO create and change (ME21N, ME22N), document type NB. Not in scope: contracts, scheduling agreements.

**Business rules**

1. If the vendor has a posting block in the PO's company code, the PO cannot be saved.
2. If the vendor has a payment block in the PO's company code, the PO can be saved, but the buyer sees a warning.
3. Purchasing blocks (central or per purchasing org) are already enforced by SAP standard and are not part of this check.
4. The check runs on every save, including changes to the vendor field.

**Messages**

|Rule|Type|Text|
|-|-|-|
|1|Error|Vendor \&1 is blocked for posting in company code \&2.|
|2|Warning|Vendor \&1 has a payment block in company code \&2.|

**Assumptions:** Vendor data is maintained as business partner with supplier role.

**Open points:** Should rule 2 apply to all payment block keys or only selected ones?

### 5C Improved

**Prompt:** 6-block prompt plus:

```text
Add: an example scenario per rule, acceptance criteria per rule, a field
reference table, message IDs, and a change history table.
Success criteria: A developer and a tester can work from this section alone.
```

**Answer:**
\[Purpose, Scope and rules 1–4 as in 5B, plus:]

**Example scenarios**

|Rule|Vendor|Block|Expected|
|-|-|-|-|
|1|100245|Posting block in CC 1000|Save refused with error|
|2|100311|Payment block "A" in CC 1000|Saved, warning shown|
|3|100400|Purchasing block|Standard SAP error, no custom message|

**Acceptance criteria**

* AC1: PO for vendor with posting block cannot be saved in ME21N or ME22N.
* AC2: PO for vendor with payment block saves and shows warning ZMM\_PO 002.
* AC3: No custom message for vendors without blocks.

**Field reference:** Posting block LFB1-SPERR, payment block LFB1-ZAHLS (both per company code).

**Messages:** ZMM\_PO 001 (error, rule 1), ZMM\_PO 002 (warning, rule 2).

**Change history**

|Version|Date|Author|Change|
|-|-|-|-|
|0.1|\[date]|\[name]|First draft|

**Open points:** \[As in 5B.] Also: should the check run when the PO is created via BAPI or IDoc?

\---

## Task 6: Summarize a long support ticket

### 6A Lazy

**Prompt:** `Summarize a long support ticket.`

**Answer:**
Please paste the support ticket you want summarized. In the meantime, a good ticket summary usually covers: the problem, who is affected, steps already taken, current status, and next action with owner.

### 6B 6-block

**Prompt:**

```text
Role: You are an SAP support team lead.
Task: Summarize the ticket below.
Context: The summary goes to the IT manager, who has 1 minute to read it.
Input:
INC0048213 – Invoices cannot be posted in MIRO
28.10 08:05 Anna (AP): Since yesterday, invoices for vendor 100245 cannot be
  posted in MIRO. Balance is not zero. About 40 invoices waiting, \~85,000 INR.
  Payment run is Friday.
28.10 09:30 Raj (L1): Asked for screenshots. Checked authorizations – OK.
28.10 11:10 Anna: Screenshots attached. Same for vendor 100311.
28.10 14:45 Raj: Forwarded to MM team.
28.10 16:20 Lukas (MM): PO price is 12.50 INR per 1 PC, invoice per 100 PC.
  Looks like price unit changed by last price upload (ZMM\_PRICE\_UPLOAD) on 27.10.
29.10 08:40 Lukas: Confirmed. Upload on 27.10 set price unit 100 for 312 POs.
  Correction program ready, needs approval from purchasing lead.
29.10 09:15 Anna: Please hurry, payment run is tomorrow.
Format: Problem / Impact / Cause / Status / Next action (owner).
Constraints: Max 100 words, plain English.
```

**Answer:
Problem:** Invoices for at least two vendors cannot be posted in MIRO.
**Impact:** \~40 invoices (\~85,000 INR) blocked.
**Cause:** The price upload on 27.10 wrongly set the price unit to 100 in 312 POs, so invoices do not match the PO price.
**Status:** Cause confirmed; correction program is ready.
**Next action:** Purchasing lead must approve the correction (owner: Lukas to chase), then AP re-posts the invoices.

### 6C Improved

**Prompt:** 6-block prompt plus:

```text
Start with one line stating the deadline and the decision needed.
Success criteria: The manager knows within 10 seconds what is at risk, by when,
and what decision is needed from whom.
```

**Answer:
⚠ Decision needed today:** Purchasing lead must approve a correction, or \~85,000 INR in invoices miss Friday's payment run (30.10).

**Problem:** Invoices for at least 2 vendors cannot be posted in MIRO (\~40 invoices).
**Cause:** Price upload on 27.10 wrongly set the price unit to 100 in 312 POs.
**Status:** Cause confirmed, correction program ready.
**Next steps:** 1) Approval by purchasing lead (Lukas chasing). 2) Run correction. 3) AP re-posts invoices before Friday.

\---

## Task 7: Business rule → ABAP pseudo-code

### 7A Lazy

**Prompt:** `Turn this into ABAP pseudo-code: POs over 10k from new vendors need extra approval.`

**Answer:**

```abap
IF po\_value > 10000 AND vendor\_is\_new = abap\_true.
  set\_approval\_required( 'EXTRA' ).
ENDIF.

METHOD vendor\_is\_new.
  SELECT SINGLE erdat FROM lfa1 INTO @DATA(lv\_erdat) WHERE lifnr = @lv\_lifnr.
  IF sy-datum - lv\_erdat < 30.
    result = abap\_true.
  ENDIF.
ENDMETHOD.
```

"New vendor" is assumed to mean created in the last 30 days.

### 7B 6-block

**Prompt:**

```text
Role: You are a senior ABAP developer.
Task: Turn the business rule below into pseudo-code for the BAdI
ME\_PROCESS\_PO\_CUST, method CHECK.
Context: Rule from purchasing: "A PO needs second approval if the total net
value is above 10,000 INR and the vendor was created less than 90 days ago.
If the vendor has a purchasing block, the PO cannot be saved."
Input: Available data: EKKO-LIFNR, PO total net value and currency,
LFA1-ERDAT (vendor created on), LFA1-SPERM (purchasing block).
Format: ABAP-style pseudo-code, then a list of assumptions and open questions.
Constraints: Pseudo-code only, no full program. Consider foreign currency.
```

**Answer:**

```text
METHOD check.
  get PO header (vendor, currency) and total net value

  read vendor master: created\_on = LFA1-ERDAT, purch\_block = LFA1-SPERM

  IF purch\_block is set.
    raise error "Vendor is blocked for purchasing"
    mark PO as invalid
    RETURN.
  ENDIF.

  convert total net value to INR if PO currency <> INR

  IF value\_eur > 10000
     AND (today - created\_on) < 90.
    set flag "second approval required" (e.g. custom field or release characteristic)
  ENDIF.
ENDMETHOD.
```

**Assumptions:** "Total net value" means sum of all non-deleted items. Exchange rate type M, rate of the PO date.
**Open questions:** How is the "second approval" technically triggered: release strategy characteristic or workflow?

### 7C Improved

**Prompt:** 6-block prompt plus:

```text
Add: edge cases (exactly 10,000 INR, exactly 90 days, foreign currency),
a table of 4 test examples with expected result, and note if any part of the
rule is already covered by SAP standard.
Success criteria: A developer can code it and a tester can test it without
going back to the business.
```

**Answer:**
\[Pseudo-code as in 7B, with the comparisons written as `value\_inr > 10000` and `days\_since\_creation < 90`.]

**Edge cases**

* Exactly 10,000.00 INR → no second approval (rule says "above").
* Vendor created exactly 90 days ago → not new (rule says "less than 90").
* Foreign currency → convert at rate type M on PO date before comparing.

**Already in standard:** A central purchasing block (LFA1-SPERM) already stops PO creation in SAP standard. The custom error is only needed if purchasing wants its own message text. Confirm before building.

**Test examples**

|#|Value|Vendor age|Purch. block|Expected|
|-|-|-|-|-|
|1|12,000 INR|30 days|No|Second approval required|
|2|10,000 INR|30 days|No|Normal approval|
|3|12,000 INR|90 days|No|Normal approval|
|4|5,000 INR|10 days|Yes|PO cannot be saved|

\---

## Task 8: 10 test vendors as JSON

### 8A Lazy

**Prompt:** `Generate 10 test vendors as JSON.`

**Answer:**

```json
\[
  {"id": 1, "name": "Acme Supplies", "email": "info@acme.com", "phone": "555-0101", "city": "Berlin"},
  {"id": 2, "name": "Global Parts Ltd", "email": "sales@globalparts.com", "phone": "555-0102", "city": "London"},
  {"id": 3, "name": "Nordic Steel AB", "email": "contact@nordicsteel.se", "phone": "555-0103", "city": "Stockholm"},
  {"id": 4, "name": "Alpine Tools GmbH", "email": "office@alpinetools.at", "phone": "555-0104", "city": "Vienna"},
  {"id": 5, "name": "Pacific Logistics", "email": "hello@paclog.com", "phone": "555-0105", "city": "Seattle"},
  {"id": 6, "name": "Rhein Chemie", "email": "info@rheinchemie.de", "phone": "555-0106", "city": "Cologne"},
  {"id": 7, "name": "Delta Electronics", "email": "sales@deltaelec.com", "phone": "555-0107", "city": "Munich"},
  {"id": 8, "name": "Summit Packaging", "email": "info@summitpack.com", "phone": "555-0108", "city": "Denver"},
  {"id": 9, "name": "Baltic Wood", "email": "office@balticwood.lv", "phone": "555-0109", "city": "Riga"},
  {"id": 10, "name": "Iberia Foods", "email": "info@iberiafoods.es", "phone": "555-0110", "city": "Madrid"}
]
```

### 8B 6-block

**Prompt:**

```text
Role: You are an SAP test data specialist.
Task: Create 10 test vendors as JSON for our data load tool.
Context: S/4HANA, business partner with supplier role. Company code 1000 (DE),
purchasing org 1000.
Input: Fields: bp\_id, name, country, city, postal\_code, vat\_id, payment\_terms,
currency, recon\_account, purchasing\_block, payment\_block.
Format: A JSON array only, no explanation.
Constraints: Clearly fictional names starting with "TEST". 6 DE, 2 AT, 2 US.
2 vendors with purchasing block, 1 with payment block. Fake VAT IDs using 9s.
US vendors have no VAT ID (null).
```

**Answer:**

\[

&#x20; {"bp\_id":"TV0001","name":"TEST Metallbau North India Pvt Ltd","country":"IN","city":"Hyderabad","postal\_code":"500001","vat\_id":"36ABCDE1234F1Z5","payment\_terms":"0001","currency":"INR","recon\_account":"21100000","purchasing\_block":false,"payment\_block":""},

&#x20; {"bp\_id":"TV0002","name":"TEST Elektro South India Pvt Ltd","country":"IN","city":"Chennai","postal\_code":"600001","vat\_id":"33ABCDE1234F1Z5","payment\_terms":"0002","currency":"INR","recon\_account":"21100000","purchasing\_block":false,"payment\_block":""},

&#x20; {"bp\_id":"TV0003","name":"TEST Packaging West India Pvt Ltd","country":"IN","city":"Mumbai","postal\_code":"400001","vat\_id":"27ABCDE1234F1Z5","payment\_terms":"0001","currency":"INR","recon\_account":"21100000","purchasing\_block":true,"payment\_block":""},

&#x20; {"bp\_id":"TV0004","name":"TEST Chemicals East India Ltd","country":"IN","city":"Kolkata","postal\_code":"700001","vat\_id":"19ABCDE1234F1Z5","payment\_terms":"0002","currency":"INR","recon\_account":"21100000","purchasing\_block":false,"payment\_block":"A"},

&#x20; {"bp\_id":"TV0005","name":"TEST Logistics Central India Pvt Ltd","country":"IN","city":"New Delhi","postal\_code":"110001","vat\_id":"07ABCDE1234F1Z5","payment\_terms":"0001","currency":"INR","recon\_account":"21100000","purchasing\_block":false,"payment\_block":""},

&#x20; {"bp\_id":"TV0006","name":"TEST Wood Products India Pvt Ltd","country":"IN","city":"Pune","postal\_code":"411001","vat\_id":"27ABCDE1234F2Z5","payment\_terms":"0001","currency":"INR","recon\_account":"21100000","purchasing\_block":false,"payment\_block":""},

&#x20; {"bp\_id":"TV0007","name":"TEST Alpine Tools India Pvt Ltd","country":"IN","city":"Bengaluru","postal\_code":"560001","vat\_id":"29ABCDE1234F1Z5","payment\_terms":"0001","currency":"INR","recon\_account":"21100000","purchasing\_block":false,"payment\_block":""},

&#x20; {"bp\_id":"TV0008","name":"TEST Tirol Plastics India Pvt Ltd","country":"IN","city":"Ahmedabad","postal\_code":"380001","vat\_id":"24ABCDE1234F1Z5","payment\_terms":"0002","currency":"INR","recon\_account":"21100000","purchasing\_block":true,"payment\_block":""},

&#x20; {"bp\_id":"TV0009","name":"TEST Lakeside Components India Pvt Ltd","country":"IN","city":"Hyderabad","postal\_code":"500081","vat\_id":"36ABCDE1234F2Z5","payment\_terms":"0001","currency":"INR","recon\_account":"21100000","purchasing\_block":false,"payment\_block":""},

&#x20; {"bp\_id":"TV0010","name":"TEST Bayview Supplies India Pvt Ltd","country":"IN","city":"Visakhapatnam","postal\_code":"530001","vat\_id":"37ABCDE1234F1Z5","payment\_terms":"0002","currency":"INR","recon\_account":"21100000","purchasing\_block":false,"payment\_block":""}

]```

### 8C Improved

**Prompt:** 6-block prompt plus:

```text
Format rules: DE postal code 5 digits, AT 4 digits, US 5 digits. DE VAT ID
"DE" + 9 digits, AT VAT ID "ATU" + 8 digits. payment\_block is "" or one letter.
Example object:
{"bp\_id":"TV0001","name":"TEST Metallbau Nord GmbH","country":"DE",...}
Success criteria: The file loads without format errors on the first try.
```

**Answer:** 

\[

&#x20; {"bp\_id":"TV0001","name":"TEST Metallbau North India Pvt Ltd","country":"IN","city":"Hyderabad","postal\_code":"500001","vat\_id":"36ABCDE1234F1Z5","payment\_terms":"0001","currency":"INR","recon\_account":"21100000","purchasing\_block":false,"payment\_block":""},

&#x20; {"bp\_id":"TV0002","name":"TEST Elektro South India Pvt Ltd","country":"IN","city":"Chennai","postal\_code":"600001","vat\_id":"33ABCDE1234F1Z5","payment\_terms":"0002","currency":"INR","recon\_account":"21100000","purchasing\_block":false,"payment\_block":""},

&#x20; {"bp\_id":"TV0003","name":"TEST Packaging West India Pvt Ltd","country":"IN","city":"Mumbai","postal\_code":"400001","vat\_id":"27ABCDE1234F1Z5","payment\_terms":"0001","currency":"INR","recon\_account":"21100000","purchasing\_block":true,"payment\_block":""},

&#x20; {"bp\_id":"TV0004","name":"TEST Chemicals East India Ltd","country":"IN","city":"Kolkata","postal\_code":"700001","vat\_id":"19ABCDE1234F1Z5","payment\_terms":"0002","currency":"INR","recon\_account":"21100000","purchasing\_block":false,"payment\_block":"A"},

&#x20; {"bp\_id":"TV0005","name":"TEST Logistics Central India Pvt Ltd","country":"IN","city":"New Delhi","postal\_code":"110001","vat\_id":"07ABCDE1234F1Z5","payment\_terms":"0001","currency":"INR","recon\_account":"21100000","purchasing\_block":false,"payment\_block":""},

&#x20; {"bp\_id":"TV0006","name":"TEST Wood Products India Pvt Ltd","country":"IN","city":"Pune","postal\_code":"411001","vat\_id":"27ABCDE1234F2Z5","payment\_terms":"0001","currency":"INR","recon\_account":"21100000","purchasing\_block":false,"payment\_block":""},

&#x20; {"bp\_id":"TV0007","name":"TEST Alpine Tools India Pvt Ltd","country":"IN","city":"Bengaluru","postal\_code":"560001","vat\_id":"29ABCDE1234F1Z5","payment\_terms":"0001","currency":"INR","recon\_account":"21100000","purchasing\_block":false,"payment\_block":""},

&#x20; {"bp\_id":"TV0008","name":"TEST Tirol Plastics India Pvt Ltd","country":"IN","city":"Ahmedabad","postal\_code":"380001","vat\_id":"24ABCDE1234F1Z5","payment\_terms":"0002","currency":"INR","recon\_account":"21100000","purchasing\_block":true,"payment\_block":""},

&#x20; {"bp\_id":"TV0009","name":"TEST Lakeside Components India Pvt Ltd","country":"IN","city":"Hyderabad","postal\_code":"500081","vat\_id":"36ABCDE1234F2Z5","payment\_terms":"0001","currency":"INR","recon\_account":"21100000","purchasing\_block":false,"payment\_block":""},

&#x20; {"bp\_id":"TV0010","name":"TEST Bayview Supplies India Pvt Ltd","country":"IN","city":"Visakhapatnam","postal\_code":"530001","vat\_id":"37ABCDE1234F1Z5","payment\_terms":"0002","currency":"INR","recon\_account":"21100000","purchasing\_block":false,"payment\_block":""}

]

## Task 9: Explain a CDS view in simple English

### 9A Lazy

**Prompt:** `Explain a CDS view in simple English.`

**Answer:**
A CDS view (Core Data Services view) is a saved, reusable query in SAP. Instead of every program writing its own SQL to combine tables, you define the logic once in a CDS view, and reports, Fiori apps and APIs can all use it. CDS views run directly in the SAP HANA database, which makes them fast. They can also carry extra information (annotations), such as labels, authorization checks and how fields should appear in Fiori. Think of a CDS view as a smart, shared window onto your data.

### 9B 6-block

**Prompt:**

````text
Role: You are an SAP developer who is good at explaining things.
Task: Explain the CDS view below.
Context: The reader is a business analyst. They want to know what data this
view shows, not how CDS works.
Input:
```
@AbapCatalog.sqlViewName: 'ZVOPENPO'
@AccessControl.authorizationCheck: #CHECK
@EndUserText.label: 'Open purchase order items'
define view Z\_OpenPOItems as select from ekko
  inner join ekpo on ekpo.ebeln = ekko.ebeln
{
  key ekko.ebeln as PurchaseOrder,
  key ekpo.ebelp as Item,
      ekko.lifnr as Supplier,
      ekpo.matnr as Material,
      ekpo.menge as OrderedQuantity,
      ekpo.meins as Unit
}
where ekpo.loekz = ''
  and ekpo.elikz = ''
```
Format: One-sentence summary, then a table: Part of the code | What it means.
Constraints: No technical jargon, max 200 words.
````

**Answer:
In one sentence:** This view lists every purchase order item that is not deleted and not yet fully delivered, with its supplier, material and quantity.

|Part of the code|What it means|
|-|-|
|`label: 'Open purchase order items'`|The name people see for this view|
|`authorizationCheck: #CHECK`|Users only see data they are allowed to see|
|`select from ekko inner join ekpo`|Combines PO headers with PO items|
|`PurchaseOrder`, `Item`|Each row is one item of one PO|
|`Supplier`, `Material`, `OrderedQuantity`, `Unit`|The details shown per item|
|`loekz = ''`|Leaves out deleted items|
|`elikz = ''`|Leaves out items marked as fully delivered|

### 9C Improved

**Prompt:** 6-block prompt plus:

```text
Add: 3 example rows of what the result looks like, and what the view does
NOT show.
Success criteria: The analyst can decide if this view answers "which items
are we still waiting for?"
```

**Answer:**
\[Summary and table as in 9B, plus:]

**Example result**

|PurchaseOrder|Item|Supplier|Material|OrderedQuantity|Unit|
|-|-|-|-|-|-|
|4500000123|10|100245|M-1001|50|PC|
|4500000123|20|100245|M-2040|10|PC|
|4500000187|10|100311|M-3300|200|KG|

**What it does NOT show:** delivery dates, how much has already arrived (only the ordered quantity), prices, or items that were delivered or deleted.

**Answer to your question:** Yes, it shows which items you are still waiting for. But to see *how much* is still open, you would also need the goods receipt quantity, which this view does not include.

\---

## Task 10: Release notes for a Fiori app

### 10A Lazy

**Prompt:** `Write release notes for a Fiori app.`

**Answer:
Release Notes – Version 2.0**
*New features:* Improved user interface with a modern SAP Fiori design. New dashboard with key metrics. Enhanced search and filter options.
*Improvements:* Faster loading times. Better mobile experience.
*Bug fixes:* Various minor bugs fixed.
*Known issues:* None.

### 10B 6-block

**Prompt:**

```text
Role: You are the product owner of a custom Fiori app.
Task: Write release notes.
Context: App "Supplier Invoice Tracker", version 1.4.0, live on 6 Nov 2026.
Users: accounts payable clerks.
Input (changes):
- AP-311: new filter "Payment block" in the invoice list
- AP-318: Excel export now includes the due date column
- AP-322: fixed wrong currency shown for USD invoices
- AP-325: list loads in \~2 s instead of \~8 s for 5,000 invoices
- AP-330: removed old "Print" button (use Export instead)
Format: Sections New / Improved / Fixed / Removed, one line each.
Constraints: User language, focus on benefit, no ticket numbers, max 150 words.
```

**Answer:
Supplier Invoice Tracker 1.4.0 – live on 6 November 2026**

**New**

* Filter by payment block to quickly find invoices that are on hold.

**Improved**

* The invoice list loads about four times faster (around 2 seconds for 5,000 invoices).
* Excel export now includes the due date.

**Fixed**

* USD invoices now show the correct currency.

**Removed**

* The "Print" button. Please use Export to Excel instead.

### 10C Improved

**Prompt:** 6-block prompt plus:

```text
Add: an "Action needed" line at the top if users must change anything,
and a contact for questions.
Success criteria: A clerk reads it in 30 seconds and knows what changed
and whether they need to do anything.
```

**Answer:
Supplier Invoice Tracker 1.4.0 – live on 6 November 2026**

**Action needed:** The Print button is gone. If you printed invoice lists, use **Export to Excel** and print from Excel.

**New**

* Filter by payment block to quickly find invoices that are on hold.

**Improved**

* The invoice list loads about four times faster.
* Excel export now includes the due date.

**Fixed**

* USD invoices now show the correct currency.

Questions? Contact \[name / channel].

\---

## Results

|Version|Average score (/25)|Range|
|-|-|-|
|Lazy|14.8|10–18|
|6-block|23.1|22–24|
|Improved|23.8|22–25|

**Findings**

* **Lazy → 6-block is the big jump (+8.3 points).** Most of the gain comes from giving the model the input it needs and the context it cannot guess.
* **Lazy prompts without input fail worst.** The ST22 dump (12) and support ticket (10) tasks had nothing to work on. The model either asked for input or invented an example.
* **6-block → Improved is a small jump (+0.7).** It helped most where edge cases matter (test cases, dump fix, pseudo-code) or the reader must act (ticket summary, release notes).
* **More is not always better.** In the vendor block spec (Task 5) the improved prompt asked for too much and the answer got overloaded, scoring lower than the 6-block version. In the JSON task (Task 8) the extra rules changed nothing.

