### Python Script

import json, re, sys

from datetime import datetime



REQUIRED = \["invoice\_no", "invoice\_date", "customer\_name", "gstin"]

DATE\_FIELDS = \["invoice\_date"]

GSTIN\_FIELDS = \["gstin"]

DATE\_FORMATS = \["%Y-%m-%d", "%d.%m.%Y", "%d-%m-%Y", "%d/%m/%Y"]

CHECK\_CHECKSUM = True  # set False to check format only

GSTIN\_RE = re.compile(r"^\\d{2}\[A-Z]{5}\\d{4}\[A-Z]\[1-9A-Z]Z\[0-9A-Z]$")

CHARS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"



def valid\_date(value):

&#x20;   for fmt in DATE\_FORMATS:

&#x20;       try:

&#x20;           datetime.strptime(str(value).strip(), fmt)

&#x20;           return True

&#x20;       except ValueError:

&#x20;           pass

&#x20;   return False



def gstin\_problem(value):

&#x20;   g = str(value).strip().upper()

&#x20;   if len(g) != 15:

&#x20;       return f"has {len(g)} characters, expected 15"

&#x20;   if not GSTIN\_RE.match(g):

&#x20;       return "does not match the GSTIN format"

&#x20;   if CHECK\_CHECKSUM:

&#x20;       total = 0

&#x20;       for i, ch in enumerate(g\[:14]):

&#x20;           v = CHARS.index(ch) \* (1 if i % 2 == 0 else 2)

&#x20;           total += v // 36 + v % 36

&#x20;       if CHARS\[(36 - total % 36) % 36] != g\[14]:

&#x20;           return "has an invalid check digit"

&#x20;   return None



def check(rec, label):

&#x20;   errs = \[f"{label}: missing '{f}'" for f in REQUIRED if rec.get(f) in (None, "")]

&#x20;   for f in DATE\_FIELDS:

&#x20;       if rec.get(f) and not valid\_date(rec\[f]):

&#x20;           errs.append(f"{label}: '{f}' = {rec\[f]!r} is not a valid date")

&#x20;   for f in GSTIN\_FIELDS:

&#x20;       problem = rec.get(f) and gstin\_problem(rec\[f])

&#x20;       if problem:

&#x20;           errs.append(f"{label}: '{f}' = {rec\[f]!r} {problem}")

&#x20;   return errs



data = json.load(open(sys.argv\[1], encoding="utf-8"))

records = data if isinstance(data, list) else \[data]

errors = \[e for i, r in enumerate(records, 1) for e in check(r, f"Record {i}")]

print("\\n".join(errors) if errors else f"OK: {len(records)} record(s) valid")

sys.exit(1 if errors else 0)





#### 3 Broken  JSON Files

##### 1st Broken JSON :

The customer\_name field is missing.

{

&#x20;   "invoice\_no": "INV001",

&#x20;   "invoice\_date": "2026-10-25",

&#x20;   "gstin": "27ABCDE1234F1Z5"

}





Expected output:

Record 1: missing 'customer\_name'



##### 2nd Broken JSON:

The invoice date 2026-15-40 is invalid.

{

&#x20;   "invoice\_no": "INV002",

&#x20;   "invoice\_date": "2026-15-40",

&#x20;   "customer\_name": "ABC Technologies",

&#x20;   "gstin": "27ABCDE1234F1Z5"

}





Expected output:

Record 1: 'invoice\_date' = '2026-15-40' is not a valid date



##### 3rd Broken JSON:

The GSTIN contains only 14 characters instead of 15.

{

&#x20;   "invoice\_no": "INV003",

&#x20;   "invoice\_date": "2026-10-28",

&#x20;   "customer\_name": "XYZ Solutions",

&#x20;   "gstin": "27ABCDE1234F1Z"

}





Expected output:

Record 1: 'gstin' = '27ABCDE1234F1Z' has 14 characters, expected 15





