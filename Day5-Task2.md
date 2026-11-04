# **Python Code:**

import json



\# File path to your purchase order dataset

JSON\_PATH = "pos.json"



def load\_pos() -> list:

&#x20;   """Helper function to load records from pos.json."""

&#x20;   try:

&#x20;       with open(JSON\_PATH, "r") as f:

&#x20;           return json.load(f)

&#x20;   except FileNotFoundError:

&#x20;       print(f"\[Error] '{JSON\_PATH}' not found in the current directory.")

&#x20;       return \[]



\# --- 1. Tool Definitions (The Kitchen) ---



def get\_po\_status(po\_number: str) -> dict:

&#x20;   """Acts as a high-level summary check for a PO."""

&#x20;   data = load\_pos()

&#x20;   matching\_rows = \[row for row in data if str(row.get("Pur.Doc.")) == str(po\_number)]

&#x20;   

&#x20;   if not matching\_rows:

&#x20;       return {"error": f"Purchase Order {po\_number} not found."}

&#x20;   

&#x20;   supplier = matching\_rows\[0].get("Supplier")

&#x20;   doc\_date = matching\_rows\[0].get("Doc. Date")

&#x20;   total\_items = len(matching\_rows)

&#x20;   total\_qty = sum(row.get("Order Quantity", 0) for row in matching\_rows)

&#x20;   

&#x20;   return {

&#x20;       "po\_number": str(po\_number),

&#x20;       "supplier": supplier,

&#x20;       "doc\_date": doc\_date,

&#x20;       "total\_items": total\_items,

&#x20;       "total\_ordered\_qty": total\_qty,

&#x20;       "status": "active"

&#x20;   }



def get\_po\_supplier(po\_number: str) -> dict:

&#x20;   """Acts as a lookup to verify vendor/supplier accountability."""

&#x20;   data = load\_pos()

&#x20;   matching\_rows = \[row for row in data if str(row.get("Pur.Doc.")) == str(po\_number)]

&#x20;   

&#x20;   if not matching\_rows:

&#x20;       return {"error": f"Purchase Order {po\_number} not found."}

&#x20;       

&#x20;   return {

&#x20;       "po\_number": str(po\_number),

&#x20;       "supplier": matching\_rows\[0].get("Supplier")

&#x20;   }



def list\_po\_items(po\_number: str) -> dict:

&#x20;   """Acts as a line-item breakdown (materials and quantities)."""

&#x20;   data = load\_pos()

&#x20;   matching\_rows = \[row for row in data if str(row.get("Pur.Doc.")) == str(po\_number)]

&#x20;   

&#x20;   if not matching\_rows:

&#x20;       return {"error": f"Purchase Order {po\_number} not found."}

&#x20;       

&#x20;   items = \[

&#x20;       {

&#x20;           "item": row.get("Item"),

&#x20;           "material": row.get("Material"),

&#x20;           "order\_quantity": row.get("Order Quantity")

&#x20;       }

&#x20;       for row in matching\_rows

&#x20;   ]

&#x20;   

&#x20;   return {

&#x20;       "po\_number": str(po\_number),

&#x20;       "items": items

&#x20;   }



def get\_pos\_by\_supplier(supplier\_id: str) -> dict:

&#x20;   """Acts as a portfolio search to filter all orders belonging to a specific vendor."""

&#x20;   data = load\_pos()

&#x20;   matching\_rows = \[row for row in data if str(row.get("Supplier", "")).lower() == supplier\_id.lower()]

&#x20;   

&#x20;   if not matching\_rows:

&#x20;       return {"error": f"No Purchase Orders found for supplier {supplier\_id}."}

&#x20;       

&#x20;   unique\_pos = list(set(str(row\["Pur.Doc."]) for row in matching\_rows))

&#x20;   

&#x20;   return {

&#x20;       "supplier": supplier\_id,

&#x20;       "purchase\_orders": unique\_pos,

&#x20;       "total\_pos": len(unique\_pos)

&#x20;   }





\# --- 2. Dynamic Agent Router (Checks pos.json directly) ---

def run\_agent\_query(user\_query: str):

&#x20;   data = load\_pos()

&#x20;   if not data:

&#x20;       return



&#x20;   query\_lower = user\_query.lower()

&#x20;   

&#x20;   # Extract all valid PO numbers present in pos.json

&#x20;   all\_po\_numbers = set(str(row\["Pur.Doc."]) for row in data)

&#x20;   

&#x20;   # Extract all valid suppliers present in pos.json

&#x20;   all\_suppliers = set(str(row\["Supplier"]) for row in data)



&#x20;   # Find if any valid PO number is mentioned in the user query

&#x20;   found\_po = None

&#x20;   for word in user\_query.split():

&#x20;       clean\_word = "".join(c for c in word if c.isalnum())

&#x20;       if clean\_word in all\_po\_numbers:

&#x20;           found\_po = clean\_word

&#x20;           break



&#x20;   # Find if any valid supplier is mentioned in the user query

&#x20;   found\_supplier = None

&#x20;   for sup in all\_suppliers:

&#x20;       if sup.lower() in query\_lower:

&#x20;           found\_supplier = sup

&#x20;           break



&#x20;   # Intent Routing based on extracted entities \& keywords

&#x20;   if "supplier" in query\_lower and ("list" in query\_lower or "all" in query\_lower or "from" in query\_lower or "vendor" in query\_lower) and found\_supplier:

&#x20;       print(f"\\n\[AI Agent] Intent: Get POs by Supplier -> Calling `get\_pos\_by\_supplier('{found\_supplier}')`")

&#x20;       result = get\_pos\_by\_supplier(found\_supplier)

&#x20;       print(json.dumps(result, indent=2))



&#x20;   elif "item" in query\_lower or "material" in query\_lower or "breakdown" in query\_lower:

&#x20;       if not found\_po:

&#x20;           print(f"\\n\[AI Agent] I couldn't find a valid PO number in your query. Please include a PO from pos.json.")

&#x20;           return

&#x20;       print(f"\\n\[AI Agent] Intent: List PO Items -> Calling `list\_po\_items('{found\_po}')`")

&#x20;       result = list\_po\_items(found\_po)

&#x20;       print(json.dumps(result, indent=2))



&#x20;   elif "vendor" in query\_lower or "who" in query\_lower:

&#x20;       if not found\_po:

&#x20;           print(f"\\n\[AI Agent] I couldn't find a valid PO number in your query. Please include a PO from pos.json.")

&#x20;           return

&#x20;       print(f"\\n\[AI Agent] Intent: Get PO Supplier -> Calling `get\_po\_supplier('{found\_po}')`")

&#x20;       result = get\_po\_supplier(found\_po)

&#x20;       print(json.dumps(result, indent=2))



&#x20;   else:

&#x20;       # Default / Status Check

&#x20;       if not found\_po:

&#x20;           print(f"\\n\[AI Agent] I couldn't match a PO number or supplier from your question in `pos.json`.")

&#x20;           print("Try asking like: 'What is the status of PO 4500000004?'")

&#x20;           return

&#x20;       print(f"\\n\[AI Agent] Intent: Check PO Status -> Calling `get\_po\_status('{found\_po}')`")

&#x20;       result = get\_po\_status(found\_po)

&#x20;       print(json.dumps(result, indent=2))





\# --- 3. Interactive Agent Loop ---

if \_\_name\_\_ == "\_\_main\_\_":

&#x20;   print("==================================================")

&#x20;   print("   SAP PURCHASE ORDER AI AGENT (DYNAMIC)          ")

&#x20;   print("==================================================")

&#x20;   print("Type your questions below (type 'exit' to quit).\\n")

&#x20;   

&#x20;   while True:

&#x20;       try:

&#x20;           user\_input = input("You: ").strip()

&#x20;           if not user\_input:

&#x20;               continue

&#x20;           if user\_input.lower() in \["exit", "quit", "q"]:

&#x20;               print("\\n\[AI Agent] Goodbye!")

&#x20;               break

&#x20;           

&#x20;           run\_agent\_query(user\_input)

&#x20;           print("-" \* 50)

&#x20;       except KeyboardInterrupt:

&#x20;           print("\\n\[AI Agent] Exiting...")

&#x20;           break



## **Response**

===================================

&#x20;      LATE PO AI AGENT

===================================



========== STEP 1 ==========



\[TOOL CALLED] find\_late\_pos

\[INPUT] {}



LATE PURCHASE ORDERS:

\[

&#x20; {

&#x20;   "poNumber": "4500011",

&#x20;   "vendor\_ID": "V001",

&#x20;   "dueDate": "2026-10-20",

&#x20;   "orderedQty": 100,

&#x20;   "deliveredQty": 60,

&#x20;   "pendingQty": 40,

&#x20;   "amount": 420000,

&#x20;   "daysOverdue": 31

&#x20; },

&#x20; {

&#x20;   "poNumber": "4500012",

&#x20;   "vendor\_ID": "V001",

&#x20;   "dueDate": "2026-10-20",

&#x20;   "orderedQty": 100,

&#x20;   "deliveredQty": 60,

&#x20;   "pendingQty": 40,

&#x20;   "amount": 420000,

&#x20;   "daysOverdue": 31

&#x20; },

&#x20; {

&#x20;   "poNumber": "4500014",

&#x20;   "vendor\_ID": "V003",

&#x20;   "dueDate": "2026-10-20",

&#x20;   "orderedQty": 50,

&#x20;   "deliveredQty": 0,

&#x20;   "pendingQty": 50,

&#x20;   "amount": 130000,

&#x20;   "daysOverdue": 31

&#x20; },

&#x20; {

&#x20;   "poNumber": "4500015",

&#x20;   "vendor\_ID": "V002",

&#x20;   "dueDate": "2026-09-15",

&#x20;   "orderedQty": 80,

&#x20;   "deliveredQty": 30,

&#x20;   "pendingQty": 50,

&#x20;   "amount": 148000,

&#x20;   "daysOverdue": 66

&#x20; },

&#x20; {

&#x20;   "poNumber": "4500016",

&#x20;   "vendor\_ID": "V001",

&#x20;   "dueDate": "2026-10-25",

&#x20;   "orderedQty": 120,

&#x20;   "deliveredQty": 70,

&#x20;   "pendingQty": 50,

&#x20;   "amount": 372000,

&#x20;   "daysOverdue": 26

&#x20; }

]



========== STEP 2 ==========



\[TOOL CALLED] get\_vendor\_details

\[INPUT] {'po\_id': '4500011'}

PO processed: 4500011

Vendor: V001



========== STEP 3 ==========



\[TOOL CALLED] get\_vendor\_details

\[INPUT] {'po\_id': '4500012'}

PO processed: 4500012

Vendor: V001



========== STEP 4 ==========



\[TOOL CALLED] get\_vendor\_details

\[INPUT] {'po\_id': '4500014'}

PO processed: 4500014

Vendor: V003



========== STEP 5 ==========



\[TOOL CALLED] get\_vendor\_details

\[INPUT] {'po\_id': '4500015'}

PO processed: 4500015

Vendor: V002



========== STEP 6 ==========



\[TOOL CALLED] get\_vendor\_details

\[INPUT] {'po\_id': '4500016'}

PO processed: 4500016

Vendor: V001



========== STEP 7 ==========

All late POs processed.

Continuing demonstration loop.



========== STEP 8 ==========

All late POs processed.

Continuing demonstration loop.



========== STEP 9 ==========

All late POs processed.

Continuing demonstration loop.



========== STEP 10 ==========

All late POs processed.

Continuing demonstration loop.



===================================

&#x20;STEP 10 COMPLETED

&#x20;GENERATING VENDOR EMAIL DRAFTS

===================================



Preparing email for vendor: V001

Missing email for V001. Creating a draft without a recipient.



EMAIL DRAFT CREATED FOR V001

Subject: Urgent: Follow-up on 3 Overdue Purchase Orders - V001

Saved: email\_drafts\\V001\_email.json



Preparing email for vendor: V003

Missing email for V003. Creating a draft without a recipient.



EMAIL DRAFT CREATED FOR V003

Subject: Urgent: Follow-up on 1 Overdue Purchase Orders - V003

Saved: email\_drafts\\V003\_email.json



Preparing email for vendor: V002

Missing email for V002. Creating a draft without a recipient.



EMAIL DRAFT CREATED FOR V002

Subject: Urgent: Follow-up on 1 Overdue Purchase Orders - V002

Saved: email\_drafts\\V002\_email.json



===================================

&#x20;         FINAL RESULT

===================================

Total late POs: 5

Processed POs: 5

Total vendors: 3

Email drafts created: 3



VENDOR-WISE SUMMARY:

V001 -> 3 late POs

V003 -> 1 late POs

V002 -> 1 late POs



Draft folder: email\_drafts

All drafts saved. No emails sent.

