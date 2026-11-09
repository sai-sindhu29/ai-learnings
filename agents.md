1.  Project Overview

Main Objective:

Search purchase orders using PO numbers.
Filter purchase orders by vendor.
Filter purchase orders by status.
Retrieve purchase order information through an MCP server.

2. Technology Used
Python – MCP server implementation.
JavaScript – Automated testing using Node.js.
JSON – Purchase order data storage.
Git – Version control.

3. AI Agent Comparison: Claude Code vs Codex

Both Claude Code and Codex were given the same Day 6 Purchase Order feature requirements.

Claude Code Approach

-> Created integration tests for the existing CAP/OData application.
-> Started the CAP server as a child process.
-> Used an in-memory SQLite database for testing.
-> Tested the actual OData endpoints.
-> Checked PO search, vendor filtering, status filtering, combined filters, and existing application functionality.
-> Used the original CSV file to calculate expected test results.

Codex Approach

-> Identified that the current checkout contains a Python MCP server rather than a CAP/OData or UI5 application.
-> Used the existing Python MCP server functions directly.
-> Created JavaScript tests using Node.js built-in test tools.
-> Used Python's runpy to load and execute the actual Python functions.
-> Tested PO number search, vendor filtering, status filtering, and combined vendor/status filtering.
-> Skipped three tests because the required combined-filter function or UI functionality does not exist.

4. Comparison and Findings

Area	            Claude Code                 	Codex
Testing approach	CAP/OData integration testing	MCP function testing
Language        	JavaScript                  	JavaScript
Backend         	CAP server                  	Python MCP server
Database/data   	CSV and in-memory SQLite    	JSON file
Execution       	Starts a server	Calls           Python functions
Test framework  	Node.js test                	Node.js test
Main focus      	Application features        	Existing MCP tools

5. Instructions for Future AI Agents

-> Understand the existing project structure before making changes.
-> Do not assume that a CAP application or UI5 interface exists.
-> Preserve existing MCP tool functionality.
-> Use the actual purchase order JSON data.
-> Do not introduce unnecessary dependencies.
-> Write automated tests for new functionality.
-> Do not modify existing functionality without a clear requirement.
-> Run all relevant tests before completing changes.
-> Explain any skipped tests and why they were skipped.

6. Final Observation

Claude Code approached the task as a CAP/OData application testing problem, whereas Codex adapted its approach to the actual Python MCP server available in the checkout.

Codex's approach was more suitable for the current Day 7 MCP project because it tested the actual Python functions and existing JSON data.

The comparison highlighted the importance of checking the project structure before implementing a feature.
