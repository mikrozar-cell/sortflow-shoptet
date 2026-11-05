"""
Automated verification suite for SortFlow Pro for Shoptet (`sortflow_shoptet`).
"""

from __future__ import annotations

import hashlib
import hmac
from app.shoptet_service import (
    compute_shoptet_category_order,
    verify_shoptet_webhook_signature,
)


def run_shoptet_tests() -> None:
    sample_products = [
        {"product_guid": "shp-101", "title": "Produkt A", "stock_amount": 15},
        {"product_guid": "shp-102", "title": "Produkt B (Vyprodáno)", "stock_amount": 0},
        {"product_guid": "shp-103", "title": "Produkt C", "stock_amount": 25},
        {"product_guid": "shp-104", "title": "Produkt D (Připnutý)", "stock_amount": 10},
    ]

    stored_positions = {
        "shp-101": {"product_guid": "shp-101", "manual_position": 10, "saved_in_stock_position": 10, "is_pinned": False, "is_out_of_stock": False},
        "shp-102": {"product_guid": "shp-102", "manual_position": 20, "saved_in_stock_position": 20, "is_pinned": False, "is_out_of_stock": False},
        "shp-103": {"product_guid": "shp-103", "manual_position": 30, "saved_in_stock_position": 30, "is_pinned": False, "is_out_of_stock": False},
        "shp-104": {"product_guid": "shp-104", "manual_position": 40, "saved_in_stock_position": 40, "is_pinned": True, "is_out_of_stock": False},
    }

    # 1. Pinned goes #1, OOS goes to the bottom, Shoptet priorities assigned in 0..65535
    ordered, updated = compute_shoptet_category_order(
        shoptet_products=sample_products,
        stored_positions=stored_positions,
        auto_demote_oos=True,
        restore_on_restock=True,
        new_products_position="after_pinned",
    )
    assert ordered[0]["product_guid"] == "shp-104"  # Pinned #1
    assert ordered[-1]["product_guid"] == "shp-102"  # OOS demoted to bottom
    assert updated["shp-102"]["saved_in_stock_position"] == 20  # Restock Memory preserved!

    # 2. Restock Memory test: shp-102 is restocked (+20 ks) -> returns to its exact rank!
    sample_products[1]["stock_amount"] = 20
    ordered_restocked, _ = compute_shoptet_category_order(
        shoptet_products=sample_products,
        stored_positions=updated,
        auto_demote_oos=True,
        restore_on_restock=True,
        new_products_position="after_pinned",
    )
    assert ordered_restocked[0]["product_guid"] == "shp-104"  # Pinned #1
    assert ordered_restocked[1]["product_guid"] == "shp-101"  # #2
    assert ordered_restocked[2]["product_guid"] == "shp-102"  # Restored right before shp-103!

    # 3. Webhook signature verification
    secret = "shoptet_webhook_secret_123"
    body = b'{"event":"stock:movement","eshopId":45891}'
    valid_sig = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    assert verify_shoptet_webhook_signature(body, valid_sig, secret) is True
    assert verify_shoptet_webhook_signature(body, "invalid", secret) is False

    print("ALL SHOPTET TESTS PASSED 100%!")


if __name__ == "__main__":
    run_shoptet_tests()
