from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class WalletBase(BaseModel):
    id: Optional[str]
    customer_xid: str
    status: Optional[str]
    enabled_at: Optional[datetime]
    balance: Optional[float]
    token: Optional[str]

    class Config:
        from_attributes = True
