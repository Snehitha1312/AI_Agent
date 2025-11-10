# schemas.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class LineItem(BaseModel):
    lineItemId: str
    name: Optional[str] = None
    itemId: Optional[str] = None
    itemCode: Optional[str] = None
    price: Optional[int] = None  # cents
    unitQty: Optional[float] = None
    unitName: Optional[str] = None
    createdTime: Optional[datetime] = None
    printed: Optional[int] = None
    refunded: Optional[int] = None

class Order(BaseModel):
    merchantId: Optional[str] = None
    orderId: str
    orderNumber: Optional[str] = None
    createdTime: datetime
    modifiedTime: Optional[datetime] = None
    state: Optional[str] = None  # "locked" or "open"
    currency: Optional[str] = "USD"
    total: Optional[int] = 0     # cents
    taxRemoved: Optional[int] = 0
    tipAmount: Optional[int] = None
    employeeId: Optional[str] = None
    deviceId: Optional[str] = None
    customerId: Optional[str] = None
    note: Optional[str] = None
    loyaltyNumber: Optional[str] = None
    rewardsCode: Optional[str] = None
    rewardsExpires: Optional[datetime] = None
    lineItems: List[LineItem] = Field(default_factory=list)
    discounts: Optional[list] = None
