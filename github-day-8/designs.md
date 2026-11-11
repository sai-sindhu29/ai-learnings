1st Agent 

 AGENT NAME: O2C Credit Check Agent

GOAL (1 line): Automatically validate customer creditworthiness, calculate credit exposure, and approve, hold, or block sales orders based on company credit policies.

STARTS WHEN:
A new sales order is created in SAP/Oracle ERP.
An order is submitted for credit validation.
A sales order is modified and requires a fresh credit check.

SKILLS (3–5 small actions):
Customer Validation: Retrieve customer master data, account status, and approved credit limit.
Credit Exposure Calculation: Fetch outstanding AR, open orders, overdue invoices, and calculate total credit exposure.
Credit Risk Assessment: Check credit limit utilization, overdue payments, and customer risk flags.
Credit Decision: Apply business rules to approve, hold, or block the sales order.
ERP Update & Notification: Update order credit status and notify the sales/credit team.

AUTO WHEN:
Customer account is active and not blocked.
Required financial data is available and validated.
Projected credit exposure is within the approved credit limit.
No overdue or high-risk policy violations exist.
Credit policy conditions are satisfied.

🔴 HUMAN WHEN:
Credit limit is exceeded.
Customer has overdue invoices beyond the permitted threshold.
Customer account is blocked or flagged as high risk.
Financial data is missing, inconsistent, or outdated.
Credit limit exception or manual override is requested.
ESCALATE TO:
Credit Analyst – Initial investigation and validation.
Credit Manager – Credit limit exceptions and approval decisions.
Finance Controller – High-value or exceptional credit-risk cases.

LOG THESE:
Sales Order ID and Customer ID.
Customer credit limit.
Outstanding AR and overdue invoice amount.
Existing open order exposure.
New order value.
Total projected credit exposure.
Credit utilization percentage.
Credit decision: APPROVE / HOLD / BLOCK / HUMAN REVIEW.
Decision reason and policy rule triggered.
Human approver ID and approval timestamp.
ERP update status.
Agent execution ID and timestamp.

2nd AGENT NAME: Leave Request Management Agent

GOAL (1 line): Automate employee leave requests by validating leave balances, checking company leave policies, and approving or escalating requests to the appropriate manager.

STARTS WHEN:
Employee submits a leave request through HRMS, portal, or Teams.
Employee modifies an existing leave request.
Employee requests leave cancellation or withdrawal.

SKILLS (3–5 small actions):
Employee Validation: Retrieve employee ID, department, manager, employment status, and leave eligibility.
Leave Balance Check: Fetch available leave balance, leave type, and requested leave duration.
Policy Validation: Validate leave rules, notice period, holidays, weekends, and supporting documents.
Conflict Detection: Check team availability, overlapping leave requests, and staffing constraints.
Approval & Notification: Route requests to managers, update HRMS, and notify employees.

AUTO WHEN:
Employee is eligible for the requested leave type.
Sufficient leave balance is available.
Leave policy requirements are satisfied.
No overlapping or duplicate leave request exists.
The request falls within predefined auto-approval rules.

🔴 HUMAN WHEN:
Insufficient leave balance.
Emergency or exceptional leave is requested.
Medical or other supporting documentation requires HR verification.
Leave exceeds the configured auto-approval duration.
Critical team staffing or business continuity is affected.
Policy exceptions or special approvals are required.


ESCALATE TO:
Reporting Manager – Initial leave approval.
HR Team – Policy exceptions, leave balance discrepancies, and special cases.
HR Manager – Extended leave, exceptional cases, and policy overrides.
LOG THESE:
Employee ID and employee name.
Department and reporting manager.
Leave request ID.
Leave type (Casual, Sick, Earned, Annual, etc.).
Leave start date and end date.
Total requested leave days.
Available leave balance before and after approval.
Policy validation results.
Holiday and weekend calculations.
Team availability and conflict status.
Approval status: APPROVED / REJECTED / PENDING / CANCELLED.
Rejection reason or exception details.
Approver ID and approval timestamp.
HRMS update status.
Agent execution ID and timestamp.
