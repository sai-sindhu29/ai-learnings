Task 3 – Model Evaluation Comparison
1. Evaluation Overview
Total labelled invoices: 20
Models evaluated: Claude Haiku 5.5 and Claude Sonnet 5.5
Reference data: Day 8 requisitions.json and suppliers.csv
Validation rules: PR existence, supplier identity, supplier status, positive amount and ₹25 lakh approval threshold.
2. Model Comparison
Metric	Haiku 5.5	Sonnet 5.5
Total invoices	20	20
Correct predictions	18	18
Incorrect predictions	2	2
Accuracy	90%	90%
Execution time	0.00029 sec	0.00027 sec
Model cost	Not measurable	Not measurable
3. Evaluation Findings

Both models achieved 90% accuracy on the 20 labelled invoices.

Both models correctly classified 18 invoices and incorrectly classified 2 invoices.

The two incorrect predictions were:

INV007: The invoice amount was 150000, but the expected label was EXCEPTION. Both models classified it as CLEAN.
INV014: The invoice amount was 120001, but the expected label was EXCEPTION. Both models classified it as CLEAN.

Both models produced identical classification results.

4. Speed and Cost Comparison

Sonnet 5.5 recorded an execution time of 0.00027 seconds.

Haiku 5.5 recorded an execution time of 0.00029 seconds.

Sonnet was marginally faster in this recorded run.

Model cost could not be reliably measured because these were deterministic rule-based executions without actual LLM API calls.

5. Final Model Choice

I would choose Sonnet 5.5 based on its slightly lower recorded execution time. However, both models achieved the same accuracy and classification results.

The evaluation also revealed that both models failed to identify the amount mismatch cases INV007 and INV014. The validation rules need improvement to catch these cases.

For production invoice processing, I would retain deterministic validation rules and require further testing before deployment.

6. Conclusion

Both models achieved 90% accuracy on the 20-invoice evaluation dataset. Sonnet 5.5 was marginally faster in this run, but there was no measurable cost comparison. Further improvements are needed to achieve 100% accuracy.