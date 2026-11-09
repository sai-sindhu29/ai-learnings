
import json
from pathlib import Path
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("purchase-order-server")

DATA_FILE = Path(__file__).parent / "purchase_orders.json"


def load_purchase_orders():
    with DATA_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


@mcp.tool()
def search_purchase_orders(po_number: str) -> list:
    """Search Purchase Orders by PO number."""

    search_value = po_number.strip().lower()

    if not search_value:
        return []

    purchase_orders = load_purchase_orders()

    return [
        po for po in purchase_orders
        if search_value in po["po_number"].lower()
    ]


@mcp.tool()
def filter_purchase_orders(
    vendor: str = "",
    status: str = ""
) -> list:
    """Filter Purchase Orders by vendor and status."""

    purchase_orders = load_purchase_orders()

    results = purchase_orders

    if vendor.strip():
        results = [
            po for po in results
            if po["vendor"].lower() == vendor.strip().lower()
        ]

    if status.strip():
        results = [
            po for po in results
            if po["status"].lower() == status.strip().lower()
        ]

    return results


if __name__ == "__main__":
    mcp.run()

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("purchase-order-server")

# Temporary sample data.
# We will replace this with your actual PO data.
purchase_orders = [
    {
        "po_number": "450001",
        "vendor": "ABC",
        "status": "Open"
    },
    {
        "po_number": "450002",
        "vendor": "XYZ",
        "status": "Closed"
    },
    {
        "po_number": "450003",
        "vendor": "ABC",
        "status": "Open"
    }
]


@mcp.tool()
def search_purchase_orders(po_number: str) -> list:
    """Search purchase orders using PO number."""

    search_value = po_number.strip()

    return [
        po for po in purchase_orders
        if search_value.lower() in po["po_number"].lower()
    ]


@mcp.tool()
def filter_purchase_orders(
    vendor: str = "",
    status: str = ""
) -> list:
    """Filter purchase orders by vendor and status."""

    results = purchase_orders

    if vendor.strip():
        results = [
            po for po in results
            if po["vendor"].lower() == vendor.strip().lower()
        ]

    if status.strip():
        results = [
            po for po in results
            if po["status"].lower() == status.strip().lower()
        ]

    return results


if __name__ == "__main__":
    mcp.run()
