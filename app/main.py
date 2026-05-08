from __future__ import annotations

import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()  # loads .env into os.environ

from .resources.CustomerResource import Customer, CustomerCollection, CustomerResource
from .resources.OrderResource import Order, OrderCollection, OrderResource
from .resources.OrderDetailsResource import OrderDetail, OrderDetailCollection, OrderDetailsResource

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

app = FastAPI(
    title=os.getenv("APP_NAME", "Starter FastAPI App"),
    version="0.1.0",
)

# Singleton resource instances
customer_resource      = CustomerResource()
order_resource         = OrderResource()
order_details_resource = OrderDetailsResource()


# ---------------------------------------------------------------------------
# Utility / health routes  (keep starter routes unchanged)
# ---------------------------------------------------------------------------

class EchoRequest(BaseModel):
    message: str


@app.get("/", tags=["root"])
def read_root() -> dict:
    return {"message": "Hello from FastAPI"}


@app.get("/health", tags=["health"])
def health() -> dict:
    return {"status": "ok"}


@app.post("/echo", tags=["echo"])
def echo(payload: EchoRequest) -> EchoRequest:
    return payload


# ---------------------------------------------------------------------------
# Task 5 — Customer routes
# ---------------------------------------------------------------------------

@app.get("/customers", tags=["customers"])
def get_customers(
    customerName:           str | None = None,
    contactLastName:        str | None = None,
    contactFirstName:       str | None = None,
    city:                   str | None = None,
    country:                str | None = None,
    salesRepEmployeeNumber: int | None = None,
) -> CustomerCollection:
    template: dict = {}
    if customerName           is not None: template["customerName"]           = customerName
    if contactLastName        is not None: template["contactLastName"]        = contactLastName
    if contactFirstName       is not None: template["contactFirstName"]       = contactFirstName
    if city                   is not None: template["city"]                   = city
    if country                is not None: template["country"]                = country
    if salesRepEmployeeNumber is not None: template["salesRepEmployeeNumber"] = salesRepEmployeeNumber
    return customer_resource.get(template)


@app.post("/customers", tags=["customers"])
def create_customer(new_data: Customer) -> str:
    return str(customer_resource.post(new_data))


@app.get("/customers/{customerNumber}", tags=["customers"])
def get_customer_by_id(customerNumber: int) -> Customer:
    try:
        return customer_resource.get_by_id(str(customerNumber))
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.put("/customers/{customerNumber}", tags=["customers"])
def update_customer(customerNumber: int, new_data: Customer) -> dict:
    try:
        updated = customer_resource.put(str(customerNumber), new_data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if updated == 0:
        raise HTTPException(status_code=404, detail=f"Customer {customerNumber} not found")
    return {"updated": updated}


@app.delete("/customers/{customerNumber}", tags=["customers"])
def delete_customer(customerNumber: int) -> dict:
    deleted = customer_resource.delete(str(customerNumber))
    if deleted == 0:
        raise HTTPException(status_code=404, detail=f"Customer {customerNumber} not found")
    return {"deleted": deleted}


# ---------------------------------------------------------------------------
# Task 5 — Order routes
# ---------------------------------------------------------------------------

@app.get("/orders", tags=["orders"])
def get_orders(
    status:         str | None = None,
    customerNumber: int | None = None,
) -> OrderCollection:
    template: dict = {}
    if status         is not None: template["status"]         = status
    if customerNumber is not None: template["customerNumber"] = customerNumber
    return order_resource.get(template)


@app.post("/orders", tags=["orders"])
def create_order(new_data: Order) -> str:
    return str(order_resource.post(new_data))


@app.get("/orders/{orderNumber}", tags=["orders"])
def get_order_by_id(orderNumber: int) -> Order:
    try:
        return order_resource.get_by_id(str(orderNumber))
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.put("/orders/{orderNumber}", tags=["orders"])
def update_order(orderNumber: int, new_data: Order) -> dict:
    try:
        updated = order_resource.put(str(orderNumber), new_data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if updated == 0:
        raise HTTPException(status_code=404, detail=f"Order {orderNumber} not found")
    return {"updated": updated}


@app.delete("/orders/{orderNumber}", tags=["orders"])
def delete_order(orderNumber: int) -> dict:
    deleted = order_resource.delete(str(orderNumber))
    if deleted == 0:
        raise HTTPException(status_code=404, detail=f"Order {orderNumber} not found")
    return {"deleted": deleted}


# ---------------------------------------------------------------------------
# Task 5 — OrderDetails routes
#
# Collection  GET  /orders/{orderNumber}/orderdetails
#             POST /orderdetails
# Single row  GET/PUT/DELETE /orders/{orderNumber}/orderdetails/{productCode}
# ---------------------------------------------------------------------------

@app.get("/orderdetails", tags=["orderdetails"])
def get_all_order_details(
    orderNumber:  int | None = None,
    productCode:  str | None = None,
) -> OrderDetailCollection:
    template: dict = {}
    if orderNumber is not None: template["orderNumber"] = orderNumber
    if productCode is not None: template["productCode"] = productCode
    return order_details_resource.get(template)


@app.post("/orderdetails", tags=["orderdetails"])
def create_order_detail(new_data: OrderDetail) -> str:
    return str(order_details_resource.post(new_data))


@app.get("/orders/{orderNumber}/orderdetails", tags=["orderdetails"])
def get_order_details_for_order(orderNumber: int) -> OrderDetailCollection:
    return order_details_resource.get_by_order(str(orderNumber))


@app.get("/orders/{orderNumber}/orderdetails/{productCode}", tags=["orderdetails"])
def get_order_detail(orderNumber: int, productCode: str) -> OrderDetail:
    try:
        return order_details_resource.get_by_order_and_product(str(orderNumber), productCode)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.put("/orders/{orderNumber}/orderdetails/{productCode}", tags=["orderdetails"])
def update_order_detail(orderNumber: int, productCode: str, new_data: OrderDetail) -> dict:
    try:
        updated = order_details_resource.put(str(orderNumber), productCode, new_data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if updated == 0:
        raise HTTPException(
            status_code=404,
            detail=f"OrderDetail ({orderNumber}, {productCode}) not found",
        )
    return {"updated": updated}


@app.delete("/orders/{orderNumber}/orderdetails/{productCode}", tags=["orderdetails"])
def delete_order_detail(orderNumber: int, productCode: str) -> dict:
    deleted = order_details_resource.delete(str(orderNumber), productCode)
    if deleted == 0:
        raise HTTPException(
            status_code=404,
            detail=f"OrderDetail ({orderNumber}, {productCode}) not found",
        )
    return {"deleted": deleted}


# ---------------------------------------------------------------------------
# Entrypoint — python -m app.main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        reload=True,
    )

