import cds from '@sap/cds'

// Returns today's date as text, like "2026-11-03"
function todayText() {
  const d = new Date()
  const mm = String(d.getMonth() + 1).padStart(2, '0')
  const dd = String(d.getDate()).padStart(2, '0')
  return `${d.getFullYear()}-${mm}-${dd}`
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

    // Rule 2: a PO is late if it is past due and not fully delivered
    this.after('READ', PurchaseOrders, (results) => {
      const rows = Array.isArray(results) ? results : [results]
      const today = todayText()

      for (const row of rows) {
        if (!row || row.dueDate === undefined || row.deliveredQty === undefined) continue
        row.isLate = row.dueDate < today && row.deliveredQty < row.orderedQty
      }
    })

    return super.init()
  }
}
