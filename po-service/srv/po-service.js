import cds from '@sap/cds'

// Returns today's date as text, like "2026-11-03"
function todayText() {
  const d = new Date()
  const mm = String(d.getMonth() + 1).padStart(2, '0')
  const dd = String(d.getDate()).padStart(2, '0')
  return `${d.getFullYear()}-${mm}-${dd}`
}

// Derived PO status. Uses only existing fields; no new business statuses.
//   Delivered: deliveredQty >= orderedQty
//   Late:      dueDate < today and not delivered
//   Open:      everything else
const STATUSES = ['Late', 'Delivered', 'Open']

function statusOf(row, today) {
  if (row.deliveredQty >= row.orderedQty) return 'Delivered'
  return row.dueDate < today ? 'Late' : 'Open'
}

// Predicate tokens (CAP where-array form) for a status, and for its complement
function statusPredicate(status, today) {
  const due = { ref: ['dueDate'] }, delivered = { ref: ['deliveredQty'] }, ordered = { ref: ['orderedQty'] }, t = { val: today }
  if (status === 'Late') return [due, '<', t, 'and', delivered, '<', ordered]
  if (status === 'Delivered') return [delivered, '>=', ordered]
  return [delivered, '<', ordered, 'and', due, '>=', t] // Open
}

function statusComplement(status, today) {
  const due = { ref: ['dueDate'] }, delivered = { ref: ['deliveredQty'] }, ordered = { ref: ['orderedQty'] }, t = { val: today }
  if (status === 'Late') return [due, '>=', t, 'or', delivered, '>=', ordered]
  if (status === 'Delivered') return [delivered, '<', ordered]
  return [due, '<', t, 'or', delivered, '>=', ordered] // not Open
}

const isRef = (token, name) => token && typeof token === 'object' && token.ref && token.ref.length === 1 && token.ref[0] === name

// True if a where-array (including nested xpr groups and function args) references `name`
function hasRef(node, name) {
  if (Array.isArray(node)) return node.some((n) => hasRef(n, name))
  if (node && typeof node === 'object') {
    if (isRef(node, name)) return true
    return Object.values(node).some((v) => hasRef(v, name))
  }
  return false
}

// Replace `status <op> '<value>'` terms with equivalent predicates on stored columns.
// Throws an error object with HTTP 400 for unsupported use of status.
function rewriteStatusTerms(where, today) {
  const out = []
  for (let i = 0; i < where.length; i++) {
    const token = where[i]
    // Parenthesised group: CAP represents "( ... )" as { xpr: [...] }
    if (token && Array.isArray(token.xpr)) {
      out.push({ ...token, xpr: rewriteStatusTerms(token.xpr, today) })
      continue
    }
    if (isRef(token, 'status')) {
      const op = where[i + 1]
      const operand = where[i + 2]
      const negate = op === '!=' || op === '<>'
      if (!(op === '=' || op === '==' || negate) || !operand || typeof operand.val !== 'string') {
        throw Object.assign(new Error('status supports only "eq"/"ne" with a status value'), { code: 400 })
      }
      if (!STATUSES.includes(operand.val)) {
        throw Object.assign(new Error(`Invalid status "${operand.val}". Use one of: ${STATUSES.join(', ')}`), { code: 400 })
      }
      const pred = negate ? statusComplement(operand.val, today) : statusPredicate(operand.val, today)
      out.push('(', ...pred, ')')
      i += 2
      continue
    }
    // contains(poNumber, ' 4500 ') -> trim the search text (FR-01)
    if (token && token.func === 'contains' && isRef(token.args?.[0], 'poNumber') && typeof token.args[1]?.val === 'string') {
      out.push({ ...token, args: [token.args[0], { val: token.args[1].val.trim() }] })
      continue
    }
    out.push(token)
  }
  return out
}

export default class POService extends cds.ApplicationService {
  async init() {
    const { PurchaseOrders } = this.entities

    // Rule 1: a PO must have an amount above zero
    this.before('CREATE', PurchaseOrders, (req) => {
      if (req.data.amount !== undefined && req.data.amount <= 0) {
        req.reject(400, 'Amount must be greater than 0')
      }
    })

    // Filtering: rewrite status terms into stored-field predicates, trim PO search text
    this.before('READ', PurchaseOrders, (req) => {
      const select = req.query.SELECT
      if (!select) return

      if (select.orderBy?.some((o) => o.ref?.[0] === 'status')) {
        return req.reject(400, 'status cannot be used in $orderby')
      }
      if (!select.where) return

      try {
        select.where = rewriteStatusTerms(select.where, todayText())
      } catch (err) {
        if (err.code === 400) return req.reject(400, err.message)
        throw err
      }
      // Any status reference left over (e.g. inside an unsupported form) cannot reach SQL
      if (hasRef(select.where, 'status')) {
        return req.reject(400, 'status supports only "eq"/"ne" with a status value')
      }
    })

    // Rule 2: a PO is late if it is past due and not fully delivered
    // Derived status (Late | Delivered | Open) uses the same rule via statusOf()
    this.after('READ', PurchaseOrders, (results) => {
      const rows = Array.isArray(results) ? results : [results]
      const today = todayText()

      for (const row of rows) {
        if (!row || row.dueDate === undefined || row.deliveredQty === undefined) continue
        row.isLate = row.dueDate < today && row.deliveredQty < row.orderedQty
        if (row.orderedQty !== undefined) row.status = statusOf(row, today)
      }
    })

    return super.init()
  }
}
