from sqlalchemy.orm import Session
from datetime import datetime
import models


def create_wallet(db: Session, customer_xid: str, token: str):
    db_wallet = models.Wallet(customer_xid=customer_xid, token=token)
    db.add(db_wallet)
    db.commit()
    db.refresh(db_wallet)
    return db_wallet


def get_wallet_by_token(db: Session, token: str):
    return db.query(models.Wallet).filter(models.Wallet.token == token).one_or_none()


def enable_wallet(db: Session, wallet: models.Wallet):
    if wallet.status == "enabled":
        raise ValueError("Wallet is already enabled")

    wallet.status = "enabled"
    wallet.enabled_at = datetime.now()
    db.commit()
    db.refresh(wallet)
    return wallet


def add_deposit(db: Session, wallet: models.Wallet, amount: float, reference_id: str) -> models.Transaction:
    existing_transaction = db.query(models.Transaction).filter(
        models.Transaction.reference_id == reference_id).one_or_none()
    if existing_transaction:
        raise ValueError("Reference ID already exists")

    transaction = models.Transaction(
        status="success",
        transacted_at=datetime.now(),
        type="deposit",
        amount=amount,
        reference_id=reference_id,
        wallet_id=wallet.id
    )
    db.add(transaction)

    wallet.balance += amount
    db.commit()
    db.refresh(transaction)

    return transaction


def make_withdrawal(db: Session, wallet: models.Wallet, amount: float, reference_id: str) -> models.Transaction:
    existing_transaction = db.query(models.Transaction).filter(
        models.Transaction.reference_id == reference_id).one_or_none()
    if existing_transaction:
        raise ValueError("Reference ID already exists")

    if wallet.balance < amount:
        raise ValueError("Insufficient balance")

    # Create a new withdrawal transaction
    transaction = models.Transaction(
        status="success",
        transacted_at=datetime.now(),
        type="withdrawal",
        amount=-amount,
        reference_id=reference_id,
        wallet_id=wallet.id
    )
    db.add(transaction)

    wallet.balance -= amount
    db.commit()
    db.refresh(transaction)

    return transaction


def disable_wallet(db: Session, wallet: models.Wallet):
    if wallet.status == "disabled":
        raise ValueError("Wallet is already disabled")

    wallet.status = "disabled"
    wallet.disabled_at = datetime.now()
    db.commit()
    db.refresh(wallet)
    return wallet
