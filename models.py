from sqlalchemy import Column, String, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
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
    disabled_at = Column(DateTime, nullable=True)
    transactions = relationship("Transaction", back_populates="wallet")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()), index=True)
    status = Column(String)
    transacted_at = Column(DateTime)
    type = Column(String)
    amount = Column(Float)
    reference_id = Column(String, default=lambda: str(uuid4()), index=True)
    wallet_id = Column(String, ForeignKey('wallets.id'))
    wallet = relationship("Wallet", back_populates="transactions")

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
