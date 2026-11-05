"""
Shoptet API Client + Deterministic Category Priority Sorting Engine.
Official Shoptet Endpoints used:
  - GET   /api/categories
  - GET   /api/categories/{categoryGuid}
  - PATCH /api/categories/{categoryGuid} (sets catalogueSorting = 'category-priority')
  - GET   /api/categories/{categoryGuid}/productsPriority
  - PATCH /api/categories/{categoryGuid}/productsPriority (batches up to 300 products, priority 0..65535)
  - GET   /api/products
  - POST  /api/webhooks (stock:movement, product:create, product:update, addon:uninstall)
"""

from __future__ import annotations

import copy
import hashlib
import hmac
from typing import Any, Dict, List, Optional, Tuple

import httpx

SHOPTET_API_BASE = "https://api.myshoptet.com"


def compute_shoptet_category_order(
    shoptet_products: List[Dict[str, Any]],
    stored_positions: Dict[str, Dict[str, Any]],
    auto_demote_oos: bool = True,
    restore_on_restock: bool = True,
    new_products_position: str = "after_pinned",
) -> Tuple[List[Dict[str, Any]], Dict[str, Dict[str, Any]]]:
    """
    Deterministic sorting engine for Shoptet categories:
      Tier 0: Pinned & In-Stock products (Připnuté produkty skladem)
      Tier 1: New Arrivals (Novinky dle nastavení 'after_pinned' / 'top')
      Tier 2: Regular In-Stock products (Skladem — s obnovením pozice po naskladnění!)
      Tier 3: Out-of-Stock products (Vyprodané produkty na konci kategorie)
    """
    enriched: List[Dict[str, Any]] = []
    updated_positions: Dict[str, Dict[str, Any]] = {}

    for idx, raw in enumerate(shoptet_products):
        prod = copy.deepcopy(raw)
        guid = str(prod["product_guid"])
        stock = int(prod.get("stock_amount", 0))
        is_in_stock = stock > 0
        prod["is_in_stock"] = is_in_stock

        st = stored_positions.get(guid)
        is_new_product = st is None

        if st is not None:
            is_pinned = bool(st.get("is_pinned", False))
            manual_pos = int(st.get("manual_position", (idx + 1) * 10))
            saved_mem = st.get("saved_in_stock_position")
            was_oos = bool(st.get("is_out_of_stock", False))

            if not is_in_stock:
                if not was_oos or saved_mem is None:
                    saved_mem = manual_pos
                is_oos_flag = True
            else:
                if was_oos and restore_on_restock and saved_mem is not None:
                    manual_pos = int(saved_mem)
                saved_mem = manual_pos
                is_oos_flag = False
        else:
            is_pinned = False
            manual_pos = (idx + 1) * 10
            saved_mem = manual_pos
            is_oos_flag = not is_in_stock

        updated_positions[guid] = {
            "product_guid": guid,
            "manual_position": manual_pos,
            "saved_in_stock_position": saved_mem,
            "is_pinned": is_pinned,
            "is_out_of_stock": is_oos_flag,
        }

        prod["is_pinned"] = is_pinned
        prod["manual_position"] = manual_pos
        prod["saved_in_stock_position"] = saved_mem
        prod["is_new_product"] = is_new_product
        prod["shoptet_priority"] = manual_pos
        enriched.append(prod)

    def sort_key(item: Dict[str, Any]) -> Tuple[int, int, str]:
        in_stock = item["is_in_stock"]
        pinned = item["is_pinned"]
        is_new = item["is_new_product"]
        pos = item["manual_position"]

        if auto_demote_oos and not in_stock:
            return (3, pos, item["product_guid"])

        if pinned:
            return (0, pos, item["product_guid"])

        if is_new:
            if new_products_position == "top":
                return (-1, pos, item["product_guid"])
            if new_products_position == "after_pinned":
                return (1, pos, item["product_guid"])
            if new_products_position == "bottom":
                return (2, 999999 + pos, item["product_guid"])

        return (2, pos, item["product_guid"])

    sorted_list = sorted(enriched, key=sort_key)

    for rank_idx, item in enumerate(sorted_list):
        rank_num = rank_idx + 1
        # Shoptet priority range is 0..65535 (ascending order when catalogueSorting='category-priority')
        priority_val = min(65535, rank_num * 10)
        item["effective_rank"] = rank_num
        item["shoptet_priority"] = priority_val
        guid = item["product_guid"]
        if item["is_in_stock"]:
            updated_positions[guid]["manual_position"] = priority_val
            updated_positions[guid]["saved_in_stock_position"] = priority_val

    return sorted_list, updated_positions


class ShoptetApiClient:
    """
    Asynchronous client for Shoptet Public Addon API (`https://api.myshoptet.com`).
    """

    def __init__(self, access_token: str) -> None:
        self.access_token = access_token
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/vnd.shoptet.v1.0+json",
        }

    async def get_categories(self) -> List[Dict[str, Any]]:
        url = f"{SHOPTET_API_BASE}/api/categories"
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.get(url, headers=self.headers)
            resp.raise_for_status()
            body = resp.json()
            return body.get("data", {}).get("categories", [])

    async def ensure_category_priority_sorting(self, category_guid: str) -> bool:
        """
        Ensures category uses `category-priority` sorting in Shoptet storefront.
        """
        url = f"{SHOPTET_API_BASE}/api/categories/{category_guid}"
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.get(url, headers=self.headers)
            resp.raise_for_status()
            cat_data = resp.json().get("data", {})
            if cat_data.get("catalogueSorting") == "category-priority":
                return False

            patch_resp = await client.patch(
                url,
                headers=self.headers,
                json={"data": {"catalogueSorting": "category-priority"}},
            )
            patch_resp.raise_for_status()
            return True

    async def get_category_products_priority(self, category_guid: str) -> List[Dict[str, Any]]:
        """
        Fetches product priorities in a category via `GET /api/categories/{categoryGuid}/productsPriority`.
        """
        url = f"{SHOPTET_API_BASE}/api/categories/{category_guid}/productsPriority?itemsPerPage=1000"
        async with httpx.AsyncClient(timeout=25.0) as client:
            resp = await client.get(url, headers=self.headers)
            resp.raise_for_status()
            return resp.json().get("data", {}).get("productsPriority", [])

    async def update_category_products_priority(
        self, category_guid: str, ordered_products: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Updates product priorities in batches of up to 300 items per Shoptet API specification:
        `PATCH /api/categories/{categoryGuid}/productsPriority`
        Priority values: 0..65535.
        """
        url = f"{SHOPTET_API_BASE}/api/categories/{category_guid}/productsPriority"
        batch_size = 300
        updated_total = 0

        async with httpx.AsyncClient(timeout=30.0) as client:
            for start in range(0, len(ordered_products), batch_size):
                chunk = ordered_products[start : start + batch_size]
                payload_items = [
                    {
                        "productGuid": item["product_guid"],
                        "priority": max(0, min(65535, int(item.get("shoptet_priority", (idx + 1) * 10)))),
                    }
                    for idx, item in enumerate(chunk, start=start)
                ]
                resp = await client.patch(url, headers=self.headers, json={"data": payload_items})
                resp.raise_for_status()
                updated_total += len(payload_items)

        return {"synced": True, "updated_count": updated_total}


def verify_shoptet_webhook_signature(raw_body: bytes, signature_header: str, webhook_secret: str) -> bool:
    """
    Verifies `Shoptet-Webhook-Signature` HMAC-SHA1 / HMAC-SHA256 header.
    """
    if not signature_header:
        return False
    digest_sha256 = hmac.new(webhook_secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()
    digest_sha1 = hmac.new(webhook_secret.encode("utf-8"), raw_body, hashlib.sha1).hexdigest()
    return hmac.compare_digest(digest_sha256, signature_header) or hmac.compare_digest(digest_sha1, signature_header)
