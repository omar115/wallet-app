from fastapi import FastAPI, Depends, HTTPException, status, Form, Header
from sqlalchemy.orm import Session
from typing import Optional
import secrets
from pydantic import BaseModel

import crud
import models
from database import SessionLocal, engine
from schemas import *
from fastapi.responses import JSONResponse

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class WalletData(WalletBase):
    token: str


class WalletResponse(BaseModel):
    data: WalletData
    status: str


@app.post("/api/v1/init", status_code=status.HTTP_201_CREATED)
async def initialize_account(customer_xid: str = Form(None), db: Session = Depends(get_db)):
    if customer_xid is None:
        content = {
            "data": {
                "error": {
                    "customer_xid": [
                        "Missing data for required field."
                    ]
                }
            },
            "status": "fail"
        }
        raise HTTPException(status_code=400, detail=content)

    token = secrets.token_hex(20)
    wallet = crud.create_wallet(db=db, customer_xid=customer_xid, token=token)

    content = {
        "data": {
            "token": token,
            "customer_xid": wallet.customer_xid,
        },
        "status": "success"
    }

    return JSONResponse(status_code=status.HTTP_201_CREATED, content=content)


@app.post("/api/v1/wallet", status_code=status.HTTP_201_CREATED)
async def enable_wallet(db: Session = Depends(get_db), authorization: Optional[str] = Header(None)):
    if authorization is None or not authorization.startswith('Token '):
        raise HTTPException(status_code=400, detail="Token Header not found")
    token = authorization.split(" ")[1].strip()
    print(token)
    try:
        wallet = crud.get_wallet_by_token(db=db, token=token)
        if wallet is None:
            raise HTTPException(status_code=404, detail="Wallet not found")

        if wallet.status == 'enabled':
            content = {
                "status": "fail",
                "data": {
                    "error": "Already enabled"
                }
            }
            raise HTTPException(status_code=400, detail=content)

        wallet = crud.enable_wallet(db=db, wallet=wallet)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    content = {
        "status": "success",
        "data": {
            "wallet": {
                "id": wallet.id,
                "owned_by": wallet.customer_xid,
                "status": wallet.status,
                "enabled_at": wallet.enabled_at.isoformat() if wallet.enabled_at else None,
                "balance": wallet.balance
            }
        }
    }

    return JSONResponse(status_code=status.HTTP_201_CREATED, content=content)


@app.get("/api/v1/wallet", status_code=status.HTTP_200_OK)
async def get_wallet_balance(db: Session = Depends(get_db), authorization: Optional[str] = Header(None)):
    if authorization is None or not authorization.startswith('Token '):
        raise HTTPException(status_code=400, detail="Token Header not found")
    token = authorization.split(" ")[1].strip()

    wallet = crud.get_wallet_by_token(db=db, token=token)

    if wallet is None:
        raise HTTPException(status_code=404, detail="Wallet not found")

    if wallet.status != 'enabled':
        content = {
            "status": "fail",
            "data": {
                "error": "Wallet disabled"
            }
        }
        raise HTTPException(status_code=400, detail=content)

    content = {
        "status": "success",
        "data": {
            "wallet": {
                "id": wallet.id,
                "owned_by": wallet.customer_xid,
                "status": wallet.status,
                "enabled_at": wallet.enabled_at.isoformat() if wallet.enabled_at else None,
                "balance": wallet.balance
            }
        }
    }

    return JSONResponse(status_code=status.HTTP_200_OK, content=content)


@app.get("/api/v1/wallet/transactions", status_code=status.HTTP_200_OK)
async def get_wallet_transactions(db: Session = Depends(get_db), authorization: Optional[str] = Header(None)):
    if authorization is None or not authorization.startswith('Token '):
        raise HTTPException(status_code=400, detail="Token Header not found")
    token = authorization.split(" ")[1].strip()

    wallet = crud.get_wallet_by_token(db=db, token=token)

    if wallet is None:
        raise HTTPException(status_code=404, detail="Wallet not found")

    if wallet.status != 'enabled':
        content = {
            "status": "fail",
            "data": {
                "error": "Wallet disabled"
            }
        }
        raise HTTPException(status_code=400, detail=content)

    transactions = wallet.transactions

    transactions_response = [
        {
            "id": transaction.id,
            "status": transaction.status,
            "transacted_at": transaction.transacted_at.isoformat() if transaction.transacted_at else None,
            "type": transaction.type,
            "amount": transaction.amount,
            "reference_id": transaction.reference_id
        }
        for transaction in transactions
    ]

    content = {
        "status": "success",
        "data": {
            "transactions": transactions_response
        }
    }

    return JSONResponse(status_code=status.HTTP_200_OK, content=content)


@app.post("/api/v1/wallet/deposits", status_code=status.HTTP_201_CREATED)
async def add_money_to_wallet(amount: float = Form(...), reference_id: str = Form(...), db: Session = Depends(get_db),
                              authorization: Optional[str] = Header(None)):
    if authorization is None or not authorization.startswith('Token '):
        raise HTTPException(status_code=400, detail="Token Header not found")
    token = authorization.split(" ")[1].strip()

    wallet = crud.get_wallet_by_token(db=db, token=token)
    if wallet is None:
        raise HTTPException(status_code=404, detail="Wallet not found")

    # Ensure wallet is enabled before deposit
    if wallet.status != 'enabled':
        content = {
            "status": "fail",
            "data": {
                "error": "Wallet is not enabled"
            }
        }
        raise HTTPException(status_code=400, detail=content)

    try:
        transaction = crud.add_deposit(
            db=db,
            wallet=wallet,
            amount=amount,
            reference_id=reference_id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    content = {
        "status": "success",
        "data": {
            "deposit": {
                "id": transaction.id,
                "deposited_by": wallet.customer_xid,
                "status": transaction.status,
                "deposited_at": transaction.transacted_at.isoformat(),
                "amount": transaction.amount,
                "reference_id": transaction.reference_id
            }
        }
    }

    return JSONResponse(status_code=status.HTTP_201_CREATED, content=content)


@app.post("/api/v1/wallet/withdrawals", status_code=status.HTTP_201_CREATED)
async def make_a_withdrawal(amount: float = Form(...), reference_id: str = Form(...), db: Session = Depends(get_db),
                            authorization: Optional[str] = Header(None)):
    if authorization is None or not authorization.startswith('Token '):
        raise HTTPException(status_code=400, detail="Token Header not found")

    token = authorization.split(" ")[1].strip()

    wallet = crud.get_wallet_by_token(db=db, token=token)
    if wallet is None:
        raise HTTPException(status_code=404, detail="Wallet not found")

    if wallet.status != 'enabled':
        content = {
            "status": "fail",
            "data": {
                "error": "Wallet is not enabled"
            }
        }
        raise HTTPException(status_code=400, detail=content)

    try:
        transaction = crud.make_withdrawal(db=db, wallet=wallet, amount=amount, reference_id=reference_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    content = {
        "status": "success",
        "data": {
            "withdrawal": {
                "id": transaction.id,
                "withdrawn_by": wallet.customer_xid,
                "status": transaction.status,
                "withdrawn_at": transaction.transacted_at.isoformat(),
                "amount": abs(transaction.amount),
                "reference_id": transaction.reference_id
            }
        }
    }

    return content


@app.patch("/api/v1/wallet", status_code=status.HTTP_200_OK)
async def disable_user_wallet(is_disabled: bool = Form(...), db: Session = Depends(get_db),
                              authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith('Token '):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token Header not found")

    token = authorization.split(" ")[1].strip()

    wallet = crud.get_wallet_by_token(db=db, token=token)
    if not wallet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wallet not found")

    if is_disabled:
        wallet = crud.disable_wallet(db=db, wallet=wallet)

    content = {
        "status": "success",
        "data": {
            "wallet": {
                "id": wallet.id,
                "owned_by": wallet.customer_xid,
                "status": wallet.status,
                "disabled_at": wallet.disabled_at.isoformat() if wallet.disabled_at else None,
                "balance": wallet.balance
            }
        }
    }
    return content
