import json
import csv
import os

# Load requisitions
with open("requisitions.json") as f:
    requisitions = json.load(f)

# Load suppliers
suppliers = {}

with open("suppliers.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        suppliers[row["supplier"]] = row["status"].lower()

po_created = []
manager_approval = []
decision_logs = []

# Tool 1: Check supplier
def check_supplier(supplier):
    return suppliers.get(supplier, "unknown")

# Tool 2: Create PO (simulation only)
def create_po(req, reason):
    po = {
        "requisition_id": req["id"],
        "supplier": req["supplier"],
        "amount": req["amount"],
        "status": "PO_CREATED",
        "reason": reason
    }
    po_created.append(po)

# Tool 3: Route to manager
def route_to_manager(req, reason):
    manager_approval.append({
        "requisition_id": req["id"],
        "supplier": req["supplier"],
        "amount": req["amount"],
        "status": "PENDING_MANAGER_APPROVAL",
        "reason": reason
    })

# Process requisitions
for req in requisitions:
    status = check_supplier(req["supplier"])

    if req["amount"] > 2500000:
        reason = "Amount exceeds ₹25 lakh approval threshold"
        route_to_manager(req, reason)

    elif status != "good":
        reason = f"Supplier status is '{status}', manager approval required"
        route_to_manager(req, reason)

    else:
        reason = "Supplier is approved and amount is within threshold"
        create_po(req, reason)

    decision_logs.append({
        "requisition_id": req["id"],
        "supplier_status": status,
        "amount": req["amount"],
        "decision_reason": reason
    })

# Save outputs
with open("po_created.json", "w") as f:
    json.dump(po_created, f, indent=4)

with open("manager_approval.json", "w") as f:
    json.dump(manager_approval, f, indent=4)

with open("decision_logs.json", "w") as f:
    json.dump(decision_logs, f, indent=4)

print("Processing completed!")
print("Automatic POs:", len(po_created))
print("Manager approvals:", len(manager_approval))
