using { resoftwa.po as db } from '../db/schema';

// Service that exposes vendors and purchase orders
// Available at /odata/v4/po
service POService @(path: '/odata/v4/po') {
  entity Vendors        as projection on db.Vendors;
  entity PurchaseOrders as projection on db.PurchaseOrders;
}
