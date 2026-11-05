
# Specification: SAP Invoice vs Purchase Order Validation

## 1. Objective

Build an application that validates supplier invoices against existing Purchase Order (PO) records.

## 2. Business Problem

Suppliers send invoices for goods and services ordered by a company.

The application should compare invoice information with PO records and identify discrepancies before invoice processing.

## 3. Functional Requirements

1. Read supplier invoice information.
2. Extract the PO number.
3. Identify the supplier.
4. Compare the invoice supplier with the PO supplier.
5. Compare invoice quantity with PO quantity.
6. Compare invoice unit price with PO unit price.
7. Validate the invoice total amount.
8. Identify missing or invalid information.
9. Display validation results and discrepancies.

## 4. Validation Rules

| Field | Validation |
|---|---|
| PO Number | Must exist in the PO list |
| Supplier | Must match the PO supplier |
| Quantity | Must match the PO quantity |
| Unit Price | Must match the PO unit price |
| Total Amount | Must match the expected total |

## 5. Expected Output

The application should display:

- Invoice number
- PO number
- Supplier name
- Invoice amount
- PO amount
- Validation status
- List of discrepancies

## 6. Test Scenarios

1. Invoice matching the PO.
2. Invoice with an incorrect PO number.
3. Invoice with a different supplier.
4. Invoice with incorrect quantity.
5. Invoice with incorrect unit price.
6. Invoice with incorrect total amount.
7. Invoice with missing information.

## 7. Constraints

- Use existing project dependencies.
- Do not install npm packages without approval.
- Preserve existing project functionality.
- Use sample invoices and PO data for testing.
