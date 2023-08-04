from sqlalchemy import Column, String, DateTime, Float
from database import Base
from uuid import uuid4


class Wallet(Base):
    __tablename__ = "wallets"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()), index=True)
    customer_xid = Column(String, index=True)
    status = Column(String, default="disabled")
    enabled_at = Column(DateTime, nullable=True)
    balance = Column(Float, default=0)
    token = Column(String, unique=True)
