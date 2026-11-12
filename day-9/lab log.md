Day 9 – Lab Log: Secure Invoice Agent
1. Project Overview
Built a secure invoice validation agent that checks invoices against purchase requisitions and supplier reference data.

The agent validates invoices before they can proceed to posting.

2. Security Testing
Created and tested 10 attack invoices:

Prompt injection
Amount mismatch
Invalid PR
Duplicate invoice
Huge invoice amount
Invalid dates
Invalid GSTIN
Vendor mismatch
Empty invoice
Line-item total mismatch

All 10 attack tests passed using pytest.

The invoices were routed to the exception list with reasons, and no posting operations occurred.

3. Audit Log

1. Generated audit_log.json to record invoice decisions.
2. Generated exception_list.json to record rejected invoices and their reasons.
3. Verified that posting operations remained zero.
4. The duplicate invoice test also demonstrated that replayed invoices could be detected.

4. Model Evaluation

Evaluated Claude Haiku 5.5 and Claude Sonnet 5.5 using 20 labelled invoices.

Metric	Haiku 5.5	Sonnet 5.5
Accuracy	90%	90%
Correct predictions	18	18
Incorrect predictions	2	2
Execution time	0.00029 sec	0.00027 sec
Cost	Not measurable	Not measurable

Both models produced the same predictions.

The two incorrect predictions were INV007 and INV014, where invoice amounts did not match the expected PR amounts.

5. What Would Stop Me From Putting This Into Production?

I would not put this agent into production yet for the following reasons:

1. The evaluation accuracy is only 90%, so additional validation is required.
2. Invoice-to-PR amount matching needs to be implemented and tested properly.
3. Supplier reference data must be regularly updated and verified.
4. Duplicate detection needs reliable persistent storage across executions.
5. Production deployment needs authentication, access controls and secure audit-log storage.
6. Human approval should be required for high-value invoices.
7. More real-world and adversarial testing is needed before deployment.

6. Final Conclusion
This project helped me understand how to build and test a secure invoice validation agent.

I implemented validation rules in code, tested 10 attack scenarios, generated exception and audit logs, and evaluated two Claude models using 20 labelled invoices.
The system is a working prototype, but it requires further accuracy improvements, security testing and production safeguards before real financial transactions can be processed.