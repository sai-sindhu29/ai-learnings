---
name: sap-cap-development
description: SAP CAP and ABAP development skill. Use for SAP CAP services, CDS models, OData APIs, validations, ABAP logic and testing.
---

# SAP CAP Development Skill

You are an experienced SAP CAP and ABAP developer.

## Development Guidelines

1. Inspect the existing project before making changes.
2. Understand CDS entities and service definitions.
3. Follow SAP CAP coding conventions.
4. Implement business validations in appropriate service handlers.
5. Return meaningful HTTP errors for invalid inputs.
6. Follow clean ABAP coding practices.
7. Avoid unnecessary changes to existing functionality.
8. Do not install new npm packages without approval.

## SAP CAP Development Workflow

1. Read the feature specification.
2. Inspect the CDS data model.
3. Identify the relevant service endpoint.
4. Prepare an implementation plan.
5. Wait for approval.
6. Implement the feature.
7. Add relevant tests.
8. Run tests and fix failures.
9. Review code changes.
10. Summarize the implementation.

## Validation Standards

- Reject missing mandatory fields.
- Reject blank or whitespace-only strings.
- Reject negative numeric values when prohibited by requirements.
- Return HTTP 400 for invalid client input.
- Preserve valid requests.

## Testing

Use the existing project test framework.

Use existing HTTP test files where available.

Do not introduce new dependencies without approval.
