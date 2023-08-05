from fastapi import HTTPException


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
