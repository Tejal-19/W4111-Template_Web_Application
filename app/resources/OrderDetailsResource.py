from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field

from .AbstractBaseResource import AbstractBaseResource
from ..services.MySQLDataService import MySQLDataService


# ---------------------------------------------------------------------------
# Pydantic models  (mirror classicmodels `orderdetails` table columns)
# ---------------------------------------------------------------------------

class OrderDetail(BaseModel):
    orderNumber:     Optional[int]   = None
    productCode:     str             = ""
    quantityOrdered: int             = 0
    priceEach:       float           = 0.0
    orderLineNumber: int             = 0


class OrderDetailCollection(BaseModel):
    items: list[OrderDetail] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Composite-PK helper
# ---------------------------------------------------------------------------

def _composite_pk(order_number: str, product_code: str) -> dict:
    """Build the composite PK dict expected by MySQLDataService."""
    return {"orderNumber": order_number, "productCode": product_code}


# ---------------------------------------------------------------------------
# Resource
# ---------------------------------------------------------------------------

class OrderDetailsResource(AbstractBaseResource):
    """
    Resource for the `orderdetails` table in classicmodels.

    orderdetails has a composite primary key (orderNumber, productCode).
    MySQLDataService supports this when primary_key is a list of column names.
    The resource methods that operate on a single row accept both parts
    explicitly so routes can use path parameters /orders/{orderNumber}/orderdetails/{productCode}.
    """

    def __init__(self, config: dict | None = None) -> None:
        cfg = dict(config or {})
        super().__init__(cfg)
        self._service = MySQLDataService({
            **cfg,
            "table":       "orderdetails",
            "primary_key": ["orderNumber", "productCode"],   # composite PK
        })

    # ------------------------------------------------------------------
    # AbstractBaseResource implementation
    # ------------------------------------------------------------------

    def get(self, template: dict) -> OrderDetailCollection:
        """List/search — template may include orderNumber, productCode, etc."""
        rows = self._service.retrieveByTemplate(template)
        return OrderDetailCollection(
            items=[OrderDetail.model_validate(r) for r in rows]
        )

    def get_by_id(self, primary_key: str | dict) -> OrderDetail:
        """
        primary_key should be a dict {"orderNumber": …, "productCode": …}.
        Accepts a plain string only for interface compliance (not typical).
        """
        row = self._service.retrieveByPrimaryKey(primary_key)
        if not row:
            raise ValueError(f"No order detail with key {primary_key!r}")
        return OrderDetail.model_validate(row)

    def get_by_order(self, order_number: str) -> OrderDetailCollection:
        """Convenience: all detail lines for a given order."""
        return self.get({"orderNumber": order_number})

    def get_by_order_and_product(
        self, order_number: str, product_code: str
    ) -> OrderDetail:
        pk = _composite_pk(order_number, product_code)
        return self.get_by_id(pk)

    def post(self, new_data: OrderDetail) -> str:
        data = new_data.model_dump(exclude_none=False)
        return self._service.create(data)

    def put(
        self,
        order_number: str,
        product_code: str,
        new_data: OrderDetail,
    ) -> int:
        pk = _composite_pk(order_number, product_code)
        data = new_data.model_dump(exclude_none=False)
        data["orderNumber"] = int(order_number)
        data["productCode"] = product_code
        return self._service.updateByPrimaryKey(pk, data)

    def delete(self, order_number: str, product_code: str) -> int:  # type: ignore[override]
        pk = _composite_pk(order_number, product_code)
        return self._service.deleteByPrimaryKey(pk)