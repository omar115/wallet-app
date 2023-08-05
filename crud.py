from enum import Enum
from sqlalchemy.orm import Session
from datetime import datetime
import models


class WalletStatus(Enum):
    ENABLED = "enabled"
    DISABLED = "disabled"


class TransactionType(Enum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"


class TransactionStatus(Enum):
    SUCCESS = "success"


def create_wallet(db: Session, customer_xid: str, token: str):
    db_wallet = models.Wallet(customer_xid=customer_xid, token=token)
    _commit_and_refresh(db, db_wallet)
    return db_wallet


def get_wallet_by_token(db: Session, token: str):
    return db.query(models.Wallet).filter(models.Wallet.token == token).one_or_none()


def get_enable_wallet(db: Session, wallet: models.Wallet):
    if wallet.status == "enabled":
        raise ValueError("Wallet is already enabled")

    wallet.status = WalletStatus.ENABLED.value
    wallet.enabled_at = datetime.now()
    db.commit()
    db.refresh(wallet)
    return wallet


def add_deposit(db: Session, wallet: models.Wallet, amount: float, reference_id: str) -> models.Transaction:
    transaction = _handle_transaction(db, wallet, amount, reference_id, TransactionType.DEPOSIT)
    wallet.balance += amount
    db.commit()
    db.refresh(transaction)
    return transaction


def make_withdrawal(db: Session, wallet: models.Wallet, amount: float, reference_id: str) -> models.Transaction:
    if wallet.balance < amount:
        raise ValueError("Insufficient balance")
    transaction = _handle_transaction(db, wallet, -amount, reference_id, TransactionType.WITHDRAWAL)
    wallet.balance -= amount
    db.commit()
    db.refresh(transaction)
    return transaction


def disable_wallet(db: Session, wallet: models.Wallet):
    if wallet.status == "disabled":
        raise ValueError("Wallet is already disabled")

    wallet.status = WalletStatus.DISABLED.value
    wallet.disabled_at = datetime.now()
    db.commit()
    db.refresh(wallet)
    return wallet


def _commit_and_refresh(db: Session, instance):
    db.add(instance)
    db.commit()
    db.refresh(instance)


def _handle_transaction(db: Session, wallet: models.Wallet, amount: float, reference_id: str,
                        transaction_type: TransactionType):
    existing_transaction = db.query(models.Transaction).filter(
        models.Transaction.reference_id == reference_id).one_or_none()
    if existing_transaction:
        raise ValueError("Reference ID already exists")

    transaction = models.Transaction(
        status=TransactionStatus.SUCCESS.value,
        transacted_at=datetime.now(),
        type=transaction_type.value,
        amount=amount,
        reference_id=reference_id,
        wallet_id=wallet.id
    )
    db.add(transaction)
    return transaction
