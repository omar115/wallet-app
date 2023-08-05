from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class WalletBase(BaseModel):
    """
    WalletBase class defines the schema of a wallet object
    """
    id: Optional[str]
    customer_xid: str
    status: Optional[str]
    enabled_at: Optional[datetime]
    disabled_at: Optional[datetime]
    balance: Optional[float]
    token: Optional[str]

    class Config:
        from_attributes = True


class TransactionBase(BaseModel):
    """
    TransactionBase class to define the schema of Transaction object
    """
    id: Optional[str]
    status: str
    transacted_at: datetime
    type: str
    amount: float
    reference_id: Optional[str]
    wallet_id: str

    class Config:
        from_attributes = True


class DepositRequest(BaseModel):
    amount: float
    reference_id: str


class DisableWalletRequest(BaseModel):
    is_disabled: bool


class WalletData(WalletBase):
    token: str


class WalletResponse(BaseModel):
    data: WalletData
    status: str
