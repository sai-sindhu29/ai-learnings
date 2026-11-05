# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

- Install: `npm install`
- Start the server: `npm start` (runs `cds-serve`, port 4004). The `cds` CLI is not in `node_modules/.bin`, so `cds watch` (used by the VS Code task and `readme.md`) needs the global `@sap/cds-dk` package.
- Service root: `http://localhost:4004/odata/v4/po` (entities `Vendors`, `PurchaseOrders`)
- Tests: there is no test runner and no `test` script. `test/po.http` is a manual REST Client file (VS Code `humao.rest-client`). Start the server first, then run the requests one at a time. Request 5 should return 400. Request 6 should return 201, but it reuses `poNumber` 4500020 from request 5, so it only works once; after a successful run, change the number or delete the row before running it again. Request 2 hardcodes the date `2026-11-03`, so update it if you need the "late" check to match today.
- Lint: `eslint.config.mjs` imports `@sap/cds/eslint.config.mjs`, but `eslint` is not in `package.json` or `node_modules/.bin`, and there is no lint script. Linting does not run as-is.

## Architecture

This is a SAP CAP (Node.js) service with three layers, each in its own folder:

- **Domain model**: `db/schema.cds` (namespace `resoftwa.po`) defines `Vendors` and `PurchaseOrders`. `PurchaseOrders.vendor` is an association, so the foreign key column is `vendor_ID`. The `isLate` field is `virtual`, so it is not stored.
- **Seed data**: `db/data/*.csv` (`resoftwa.po-Vendors.csv`, `resoftwa.po-PurchaseOrders.csv`). CAP loads these by file name, and the CSV headers must match the entity and column names.
- **Service**: `srv/po-service.cds` exposes both entities as projections at `/odata/v4/po`. CAP binds the handler `srv/po-service.js` by matching file name, so the two files must stay paired.

Business logic lives only in `srv/po-service.js`, in `init()`:

- **Create validation**: `before('CREATE')` rejects a PO with `amount <= 0` (400). It runs on CREATE only, so an UPDATE can still set a non-positive amount.
- **Late flag**: `after('READ')` computes `isLate` in memory as `dueDate < today && deliveredQty < orderedQty`. Because it is never stored, `isLate` cannot be used in `$filter` or `$orderby`. Filter on `dueDate` and `deliveredQty` directly, as `po.http` request 2 does. It is only computed when the result row contains both `dueDate` and `deliveredQty`. Dates are compared as strings in `YYYY-MM-DD` form, using the server's local date.

`app/` is empty (no UI yet).

## Repository notes

- The git repository root is the parent folder `/home/user/projects`, not `po-service`, so git paths are prefixed with `po-service/`. `git status` there also lists unrelated sibling folders.
- `test/ZMS_PO_OPEN_LIST.abap` is an untracked on-premise SAP ABAP report (`zms_po_open_list`), not part of the Node service. Ignore it unless the task is about the ABAP side.
