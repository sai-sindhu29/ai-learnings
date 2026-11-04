namespace resoftwa.po;

// Vendors who supply goods
entity Vendors {
  key ID     : String(10);
  name       : String(80);
  rating     : String(10); // good | new | poor
}

// Purchase orders sent to vendors
entity PurchaseOrders {
  key poNumber     : String(10);
  vendor           : Association to Vendors;
  dueDate          : Date;
  orderedQty       : Integer;
  deliveredQty     : Integer;
  amount           : Decimal(15,2);
  virtual isLate   : Boolean; // computed in srv/po-service.js, not stored
}
