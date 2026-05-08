from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field

from .AbstractBaseResource import AbstractBaseResource
from ..services.MySQLDataService import MySQLDataService


# ---------------------------------------------------------------------------
# Pydantic models  (mirror classicmodels `customers` table columns)
# ---------------------------------------------------------------------------

class Customer(BaseModel):
    customerNumber:         Optional[int]   = None
    customerName:           str             = ""
    contactLastName:        str             = ""
    contactFirstName:       str             = ""
    phone:                  str             = ""
    addressLine1:           str             = ""
    addressLine2:           Optional[str]   = None
    city:                   str             = ""
    state:                  Optional[str]   = None
    postalCode:             Optional[str]   = None
    country:                str             = ""
    salesRepEmployeeNumber: Optional[int]   = None
    creditLimit:            Optional[float] = None


class CustomerCollection(BaseModel):
    items: list[Customer] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Resource
# ---------------------------------------------------------------------------

class CustomerResource(AbstractBaseResource):
    """
    Resource for the `customers` table in classicmodels.
    Mirrors HarryPotterResource: wires Pydantic models to MySQLDataService
    and implements get / get_by_id / post / put / delete.
    """

    def __init__(self, config: dict | None = None) -> None:
        cfg = dict(config or {})
        super().__init__(cfg)
        self._service = MySQLDataService({
            **cfg,
            "table":       "customers",
            "primary_key": "customerNumber",
        })

    # ------------------------------------------------------------------
    # AbstractBaseResource implementation
    # ------------------------------------------------------------------

    def get(self, template: dict) -> CustomerCollection:
        rows = self._service.retrieveByTemplate(template)
        return CustomerCollection(
            items=[Customer.model_validate(r) for r in rows]
        )

    def get_by_id(self, customer_number: str) -> Customer:
        row = self._service.retrieveByPrimaryKey(str(customer_number))
        if not row:
            raise ValueError(f"No customer with customerNumber {customer_number!r}")
        return Customer.model_validate(row)

    def post(self, new_data: Customer) -> str:
        data = new_data.model_dump(exclude_none=False)
        # Remove None PK so MySQL auto-assigns / caller supplies it
        if data.get("customerNumber") is None:
            data.pop("customerNumber", None)
        return self._service.create(data)

    def put(self, customer_number: str, new_data: Customer) -> int:
        data = new_data.model_dump(exclude_none=False)
        data["customerNumber"] = int(customer_number)
        return self._service.updateByPrimaryKey(str(customer_number), data)

    def delete(self, customer_number: str) -> int:
        return self._service.deleteByPrimaryKey(str(customer_number))