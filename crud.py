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
    print('crudy ', token)
    x = db.query(models.Wallet).filter(models.Wallet.token == token).one_or_none()
    print('x status ', x)
    return db.query(models.Wallet).filter(models.Wallet.token == token).one_or_none()


def enable_wallet(db: Session, wallet: models.Wallet):
    if wallet.status == "enabled":
        raise ValueError("Wallet is already enabled")

    wallet.status = "enabled"
    wallet.enabled_at = datetime.now()
    db.commit()
    db.refresh(wallet)
    return wallet
