import test from 'node:test';
import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

// This checkout contains an MCP server, not a CAP/OData or UI5 application.
// Run its real functions with the declared mcp dependency; do not mock them.
const server = fileURLToPath(new URL('../mcp-server/server.py', import.meta.url));
const python = process.env.PO_TEST_PYTHON || 'python3';
const bridge = `
import json, runpy, sys
module = runpy.run_path(sys.argv[1])
request = json.loads(sys.argv[2])
print(json.dumps(module[request["function"]](**request["arguments"])))
`;

function call(functionName, arguments_ = {}) {
  return JSON.parse(execFileSync(python, [
    '-c', bridge, server,
    JSON.stringify({ function: functionName, arguments: arguments_ }),
  ], { encoding: 'utf8' }));
}

// These are the existing server's records, including its actual field names.
const orders = [
  { po_number: '450001', vendor: 'ABC', status: 'Open' },
  { po_number: '450002', vendor: 'XYZ', status: 'Closed' },
  { po_number: '450003', vendor: 'ABC', status: 'Open' },
];

test('PO number search returns the matching complete record', () => {
  assert.deepEqual(call('search_purchase_orders', { po_number: '450001' }), [orders[0]]);
});

test('PO number search ignores leading and trailing spaces', () => {
  assert.deepEqual(call('search_purchase_orders', { po_number: '  450002  ' }), [orders[1]]);
});

for (const vendor of ['ABC', 'XYZ']) {
  test(`vendor filter returns only ${vendor} purchase orders`, () => {
    assert.deepEqual(call('filter_purchase_orders', { vendor }),
      orders.filter((order) => order.vendor === vendor));
  });
}

for (const status of ['Open', 'Closed']) {
  test(`status filter supports the existing ${status} status`, () => {
    assert.deepEqual(call('filter_purchase_orders', { status }),
      orders.filter((order) => order.status === status));
  });
}

test('vendor and status filters apply together using AND', () => {
  assert.deepEqual(call('filter_purchase_orders', { vendor: 'ABC', status: 'Open' }),
    [orders[0], orders[2]]);
  assert.deepEqual(call('filter_purchase_orders', { vendor: 'ABC', status: 'Closed' }), []);
});

test('combined PO number, vendor and status filters', {
  skip: 'No function or UI accepts all three filters; search and filtering are separate MCP tools.',
}, () => {});

test('Clear Filters resets UI selections and restores the original list', {
  skip: 'No UI5 application, selection controls, or Clear Filters handler exists in this checkout.',
}, () => {});

test('empty backend filter values return the complete list after a filtered call', () => {
  assert.deepEqual(call('filter_purchase_orders', { vendor: 'XYZ', status: 'Closed' }),
    [orders[1]]);
  assert.deepEqual(call('filter_purchase_orders', { vendor: '', status: '' }), orders);
});

test('search returns no records for an unmatched PO number', () => {
  // Derive an absent search value from actual PO numbers; no invented fixture record.
  const absentNumber = orders.map((order) => order.po_number).join('');
  assert.deepEqual(call('search_purchase_orders', { po_number: absentNumber }), []);
});

test('empty results display an appropriate empty-state message', {
  skip: 'The server returns arrays only; no UI or empty-state message is implemented.',
}, () => {});

test('existing unfiltered listing preserves every record, field, and order', () => {
  assert.deepEqual(call('filter_purchase_orders'), orders);
});

test('existing partial PO number search remains available', () => {
  assert.deepEqual(call('search_purchase_orders', { po_number: '45000' }), orders);
});
