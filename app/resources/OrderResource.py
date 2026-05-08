from __future__ import annotations

import datetime
from typing import Optional, Union
from pydantic import BaseModel, Field

from .AbstractBaseResource import AbstractBaseResource
from ..services.MySQLDataService import MySQLDataService


class Order(BaseModel):
    orderNumber:    Optional[int]                       = None
    orderDate:      Optional[Union[datetime.date, str]] = None
    requiredDate:   Optional[Union[datetime.date, str]] = None
    shippedDate:    Optional[Union[datetime.date, str]] = None
    status:         str                                 = ""
    comments:       Optional[str]                       = None
    customerNumber: int                                 = 0

    model_config = {"json_encoders": {datetime.date: lambda v: v.isoformat()}}


class OrderCollection(BaseModel):
    items: list[Order] = Field(default_factory=list)


class OrderResource(AbstractBaseResource):

    def __init__(self, config: dict | None = None) -> None:
        cfg = dict(config or {})
        super().__init__(cfg)
        self._service = MySQLDataService({
            **cfg,
            "table":       "orders",
            "primary_key": "orderNumber",
        })

    def get(self, template: dict) -> OrderCollection:
        rows = self._service.retrieveByTemplate(template)
        return OrderCollection(items=[Order.model_validate(r) for r in rows])

    def get_by_id(self, order_number: str) -> Order:
        row = self._service.retrieveByPrimaryKey(str(order_number))
        if not row:
            raise ValueError(f"No order with orderNumber {order_number!r}")
        return Order.model_validate(row)

    def post(self, new_data: Order) -> str:
        data = new_data.model_dump(exclude_none=False)
        if data.get("orderNumber") is None:
            data.pop("orderNumber", None)
        return self._service.create(data)

    def put(self, order_number: str, new_data: Order) -> int:
        data = new_data.model_dump(exclude_none=False)
        data["orderNumber"] = int(order_number)
        return self._service.updateByPrimaryKey(str(order_number), data)

    def delete(self, order_number: str) -> int:
        return self._service.deleteByPrimaryKey(str(order_number))
