# Hardest Attack to Stop

The duplicate invoice attack was the hardest to stop because identifying duplicates requires comparing invoices with previously processed records.
A single invoice cannot be identified as a duplicate without maintaining historical invoice information.
The agent needs to track invoice IDs across multiple submissions.
Without persistent duplicate tracking, the same invoice could be accepted more than once.
This attack demonstrates why state management and a reliable audit trail are important for financial agents.
