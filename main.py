from fastapi import FastAPI, Depends, HTTPException, status, Form, Header
from sqlalchemy.orm import Session
from typing import Optional
import secrets
from pydantic import BaseModel

import crud
import models
import schemas
from database import SessionLocal, engine
from fastapi.responses import JSONResponse

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class WalletData(schemas.WalletBase):
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
