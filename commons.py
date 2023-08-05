from fastapi import HTTPException, Header
from typing import Optional


def check_wallet_status(wallet):
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


def format_balance(balance):
    return int(balance)


def datetime_conversion(dt):
    return dt.isoformat() if dt else None


def extract_token(authorization: Optional[str] = Header(None)) -> str:
    if not authorization or not authorization.startswith('Token '):
        raise HTTPException(status_code=400, detail="Token Header not found")
    return authorization.split(" ")[1].strip()
