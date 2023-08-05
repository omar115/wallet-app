from unittest import mock
from datetime import datetime
from sqlalchemy.orm import Session
import crud
import models


def get_mock_wallet():
    return models.Wallet(
        customer_xid="test_customer_xid",
        token="test_token",
        balance=1000
    )


def get_mock_transaction():
    return models.Transaction(
        id="test_id",
        status="success",
        transacted_at=datetime.now(),
        type="deposit",
        amount=100,
        reference_id="test_ref_id",
        wallet_id="test_wallet_id"
    )


def test_create_wallet():
    with mock.patch.object(Session, 'add', return_value=None) as mock_add, \
            mock.patch.object(Session, 'commit', return_value=None) as mock_commit, \
            mock.patch.object(Session, 'refresh', return_value=None) as mock_refresh:
        db = Session()
        wallet = crud.create_wallet(db, "test_customer_xid", "test_token")

        assert wallet.customer_xid == "test_customer_xid"
        assert wallet.token == "test_token"


def test_get_wallet_by_token():
    with mock.patch.object(Session, 'query', return_value=mock.MagicMock(filter=mock.MagicMock(
            return_value=mock.MagicMock(one_or_none=mock.MagicMock(return_value=get_mock_wallet()))))):
        db = Session()
        wallet = crud.get_wallet_by_token(db, "test_token")

        assert wallet.token == "test_token"


def test_get_enable_wallet():
    with mock.patch.object(Session, 'commit', return_value=None) as mock_commit, \
            mock.patch.object(Session, 'refresh', return_value=None) as mock_refresh:
        db = Session()
        wallet = get_mock_wallet()
        wallet.status = "disabled"
        enabled_wallet = crud.get_enable_wallet(db, wallet)

        assert enabled_wallet.status == "enabled"
