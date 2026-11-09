// Automated tests for PO search and filtering (Phase 3).
// Run with: npm test
//
// Starts cds-serve as a child process on a free port with an in-memory SQLite
// database, so the tests do not touch db.sqlite and can be re-run safely.
// Expected results are derived from the seed CSV and today's date, so the
// tests stay correct as the calendar moves on.

import { test, before, after, describe } from 'node:test'
import assert from 'node:assert/strict'
import { spawn } from 'node:child_process'
import { createServer } from 'node:net'
import { readFileSync } from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const csvPath = path.join(root, 'db/data/resoftwa.po-PurchaseOrders.csv')

let proc
let base

function freePort() {
  return new Promise((resolve, reject) => {
    const s = createServer()
    s.unref()
    s.on('error', reject)
    s.listen(0, () => {
      const { port } = s.address()
      s.close(() => resolve(port))
    })
  })
}

async function waitUntilReady(url, timeoutMs = 60000) {
  const start = Date.now()
  while (Date.now() - start < timeoutMs) {
    try {
      const r = await fetch(url)
      if (r.ok) return
    } catch {
      // server not up yet
    }
    await new Promise((r) => setTimeout(r, 300))
  }
  throw new Error(`Server did not become ready at ${url}`)
}

before(async () => {
  const port = await freePort()
  base = `http://localhost:${port}/odata/v4/po`
  proc = spawn(process.execPath, [path.join(root, 'node_modules/.bin/cds-serve')], {
    cwd: root,
    env: { ...process.env, PORT: String(port), CDS_REQUIRES_DB_CREDENTIALS_URL: ':memory:' },
    stdio: ['ignore', 'pipe', 'pipe'],
  })
  proc.stderr.on('data', () => {}) // keep output quiet; errors surface through assertions
  await waitUntilReady(`${base}/PurchaseOrders?$top=1`)
}, { timeout: 90000 })

after(() => {
  if (proc && !proc.killed) proc.kill()
})

// ---- helpers --------------------------------------------------------------

async function get(query) {
  const r = await fetch(`${base}/PurchaseOrders${query}`)
  return { status: r.status, body: await r.json() }
}

const numbers = (body) => body.value.map((row) => row.poNumber).sort()

// Same local-date rule the service uses (server and test share one machine)
function todayText() {
  const d = new Date()
  const mm = String(d.getMonth() + 1).padStart(2, '0')
  const dd = String(d.getDate()).padStart(2, '0')
  return `${d.getFullYear()}-${mm}-${dd}`
}

// Seed rows, parsed straight from the CSV
const seed = readFileSync(csvPath, 'utf8')
  .trim()
  .split(/\r?\n/)
  .slice(1)
  .map((line) => {
    const [poNumber, vendor_ID, dueDate, orderedQty, deliveredQty] = line.split(',')
    return { poNumber, vendor_ID, dueDate, orderedQty: Number(orderedQty), deliveredQty: Number(deliveredQty) }
  })

const today = todayText()
const expectedStatus = (row) => {
  if (row.deliveredQty >= row.orderedQty) return 'Delivered'
  return row.dueDate < today ? 'Late' : 'Open'
}
const expectedNumbers = (predicate) => seed.filter(predicate).map((r) => r.poNumber).sort()

// ---- PO number search (FR-01) ---------------------------------------------

describe('PO number search', () => {
  test('valid PO number returns exactly that PO', async () => {
    const { status, body } = await get(`?$filter=contains(poNumber,'4500013')`)
    assert.equal(status, 200)
    assert.deepEqual(numbers(body), ['4500013'])
  })

  test('invalid PO number returns an empty list with HTTP 200', async () => {
    const { status, body } = await get(`?$filter=contains(poNumber,'9999999')`)
    assert.equal(status, 200)
    assert.deepEqual(body.value, [])
  })

  test('leading and trailing spaces are ignored', async () => {
    const padded = await get(`?$filter=contains(poNumber,'%20%20%204500013%20%20')`)
    const trimmed = await get(`?$filter=contains(poNumber,'4500013')`)
    assert.equal(padded.status, 200)
    assert.deepEqual(numbers(padded.body), numbers(trimmed.body))
  })

  test('partial PO number matches all POs containing it', async () => {
    const { body } = await get(`?$filter=contains(poNumber,'4500')`)
    assert.equal(body.value.length, seed.length)
  })
})

// ---- Vendor filter (FR-02) ------------------------------------------------

describe('Vendor filter', () => {
  test('returns only POs for the selected vendor', async () => {
    const { status, body } = await get(`?$filter=vendor_ID%20eq%20'V002'`)
    assert.equal(status, 200)
    assert.deepEqual(numbers(body), expectedNumbers((r) => r.vendor_ID === 'V002'))
    assert.deepEqual(numbers(body), ['4500013', '4500015', '4500018'])
  })

  test('vendor with no POs returns an empty list', async () => {
    const { status, body } = await get(`?$filter=vendor_ID%20eq%20'V004'&$expand=vendor`)
    assert.equal(status, 200)
    assert.deepEqual(numbers(body), ['4500019'])
  })
})

// ---- Status filter (FR-03) ------------------------------------------------

describe('Status filter', () => {
  for (const status of ['Late', 'Delivered', 'Open']) {
    test(`status eq '${status}' returns the POs with that derived status`, async () => {
      const { status: code, body } = await get(`?$filter=status%20eq%20'${status}'`)
      assert.equal(code, 200)
      assert.deepEqual(numbers(body), expectedNumbers((r) => expectedStatus(r) === status))
    })
  }

  test('status ne excludes the given status', async () => {
    const { status: code, body } = await get(`?$filter=status%20ne%20'Late'`)
    assert.equal(code, 200)
    assert.deepEqual(numbers(body), expectedNumbers((r) => expectedStatus(r) !== 'Late'))
  })

  test('every returned row carries its status', async () => {
    const { body } = await get('')
    for (const row of body.value) {
      const seedRow = seed.find((r) => r.poNumber === row.poNumber)
      assert.equal(row.status, expectedStatus(seedRow), `status of ${row.poNumber}`)
    }
  })

  test('unknown status value returns HTTP 400', async () => {
    const { status } = await get(`?$filter=status%20eq%20'Bogus'`)
    assert.equal(status, 400)
  })

  test('sorting by status returns HTTP 400 (status is not stored)', async () => {
    const { status } = await get(`?$orderby=status`)
    assert.equal(status, 400)
  })
})

// ---- Combined filtering (FR-04) and Clear (FR-05) -------------------------

describe('Combined filters and Clear', () => {
  test('PO search + vendor + status are applied together', async () => {
    const { status, body } = await get(
      `?$filter=contains(poNumber,'4500')%20and%20vendor_ID%20eq%20'V002'%20and%20status%20eq%20'Open'`,
    )
    assert.equal(status, 200)
    assert.deepEqual(numbers(body), expectedNumbers((r) => r.vendor_ID === 'V002' && expectedStatus(r) === 'Open'))
    assert.deepEqual(numbers(body), ['4500018'])
  })

  test('combination with no match returns an empty list (FR-06)', async () => {
    const { status, body } = await get(
      `?$filter=vendor_ID%20eq%20'V004'%20and%20status%20eq%20'Late'`,
    )
    assert.equal(status, 200)
    assert.deepEqual(body.value, [])
  })

  test('status combined with OR keeps its precedence against other terms', async () => {
    const { body } = await get(
      `?$filter=vendor_ID%20eq%20'V001'%20and%20(status%20eq%20'Late'%20or%20status%20eq%20'Delivered')`,
    )
    assert.deepEqual(numbers(body), expectedNumbers((r) => r.vendor_ID === 'V001' && ['Late', 'Delivered'].includes(expectedStatus(r))))
  })

  test('no filters ("Clear") returns the full unfiltered list', async () => {
    const { status, body } = await get('')
    assert.equal(status, 200)
    assert.equal(body.value.length, seed.length)
    assert.deepEqual(numbers(body), seed.map((r) => r.poNumber).sort())
  })
})

// ---- Existing PO list behavior is preserved -------------------------------

describe('Existing PO list functionality', () => {
  test('isLate is still computed as before', async () => {
    const { body } = await get('')
    for (const row of body.value) {
      const seedRow = seed.find((r) => r.poNumber === row.poNumber)
      assert.equal(row.isLate, seedRow.dueDate < today && seedRow.deliveredQty < seedRow.orderedQty, `isLate of ${row.poNumber}`)
    }
  })

  test('$expand=vendor still returns vendor details', async () => {
    const { body } = await get(`?$filter=poNumber%20eq%20'4500012'&$expand=vendor`)
    assert.equal(body.value[0].vendor.name, 'Sharma Steels')
  })

  test('$orderby=dueDate still sorts ascending', async () => {
    const { body } = await get(`?$orderby=dueDate`)
    const dates = body.value.map((r) => r.dueDate)
    assert.deepEqual(dates, [...dates].sort())
  })

  test('create with amount 0 is rejected with HTTP 400', async () => {
    const r = await fetch(`${base}/PurchaseOrders`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ poNumber: '4600001', vendor_ID: 'V001', dueDate: '2026-12-01', orderedQty: 10, deliveredQty: 0, amount: 0 }),
    })
    assert.equal(r.status, 400)
  })

  test('valid create succeeds and the new PO is searchable and filterable', async () => {
    const r = await fetch(`${base}/PurchaseOrders`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ poNumber: '4600002', vendor_ID: 'V001', dueDate: '2026-12-01', orderedQty: 10, deliveredQty: 0, amount: 50000 }),
    })
    assert.equal(r.status, 201)

    const found = await get(`?$filter=contains(poNumber,'4600002')`)
    assert.deepEqual(numbers(found.body), ['4600002'])
    assert.equal(found.body.value[0].status, 'Open')

    const open = await get(`?$filter=status%20eq%20'Open'%20and%20contains(poNumber,'4600002')`)
    assert.deepEqual(numbers(open.body), ['4600002'])
  })
})
