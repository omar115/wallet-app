import datetime
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient

from commons import format_balance
from main import app

client = TestClient(app)


def test_initialize_account_success():
    customer_xid = "ea0212d3-abd6-406f-8c67-868e814a2435"

    response = client.post("/api/v1/init", data={"customer_xid": customer_xid})

    assert response.status_code == 201
    assert response.json()["status"] == "success"
    assert "token" in response.json()["data"]
    assert response.json()["data"]["customer_xid"] == customer_xid


def test_initialize_account_missing_customer_xid():
    response = client.post("/api/v1/init")

    assert response.status_code == 400
    print(response.json())
    assert response.json()['detail']["status"] == "fail"
    assert response.json()["detail"]["data"]["error"]["customer_xid"] == ["Missing data for required field."]


def test_enable_wallet():
    """
    Test the enable_wallet endpoint.

    This test mocks the fetching of a wallet by its token and enabling the wallet
    to avoid real database interactions. It verifies that a disabled wallet can be
    successfully enabled via the API endpoint.
    """
    mock_wallet = Mock()
    mock_wallet.id = "1f486c05-31ce-4142-aecd-1909575f8506"
    mock_wallet.customer_xid = "ea0212d3-abd6-406f-8c67-868e814a2435"
    mock_wallet.status = "disabled"
    mock_wallet.enabled_at = None
    mock_wallet.balance = 1000

    with patch('main.get_wallet_by_token', return_value=mock_wallet), \
            patch('main.get_enable_wallet', return_value=mock_wallet):
        token = "3e3ccc8859751abcbf85b2645e681d79e4b9a4fa"
        headers = {"Authorization": f"Token {token}"}

        response = client.post("/api/v1/wallet", headers=headers)

        print(response.json())
        assert response.status_code == 201
        assert response.json()["status"] == "success"


def test_get_wallet_balance():
    """
    Test the get_wallet_balance endpoint.

    This test mocks the fetching of a wallet by its token to avoid real database interactions.
    It verifies that the endpoint correctly returns the wallet details for a given token.
    """

    # Create a mock wallet object.
    mock_wallet = Mock()
    mock_wallet.id = "1f486c05-31ce-4142-aecd-1909575f8506"
    mock_wallet.customer_xid = "ea0212d3-abd6-406f-8c67-868e814a2435"
    mock_wallet.status = "enabled"
    mock_wallet.enabled_at = datetime.datetime.now()
    mock_wallet.balance = 1000

    with patch('main.get_wallet_by_token', return_value=mock_wallet), \
            patch('main.check_wallet_status') as mock_check_status:
        # Make sure the wallet status check doesn't raise any exception.
        mock_check_status.return_value = None

        token = "3e3ccc8859751abcbf85b2645e681d79e4b9a4fa"
        headers = {"Authorization": f"Token {token}"}

        response = client.get("/api/v1/wallet", headers=headers)

        assert response.status_code == 200
        assert response.json()["status"] == "success"
        assert response.json()["data"]["wallet"]["id"] == mock_wallet.id
        assert response.json()["data"]["wallet"]["owned_by"] == mock_wallet.customer_xid
        assert response.json()["data"]["wallet"]["status"] == mock_wallet.status


def test_get_wallet_transactions():
    """
    Test the get_wallet_transactions endpoint.

    This test mocks the fetching of a wallet and its associated transactions to avoid real database interactions.
    It verifies that the endpoint correctly returns the list of transactions for a wallet identified by a token.
    """

    # Mocked transactions for the wallet.
    mock_transaction1 = Mock()
    mock_transaction1.id = "txn_001"
    mock_transaction1.status = "completed"
    mock_transaction1.transacted_at = datetime.datetime.now()
    mock_transaction1.type = "debit"
    mock_transaction1.amount = 500
    mock_transaction1.reference_id = "ref_001"

    mock_transaction2 = Mock()
    mock_transaction2.id = "txn_002"
    mock_transaction2.status = "completed"
    mock_transaction2.transacted_at = datetime.datetime.now()
    mock_transaction2.type = "credit"
    mock_transaction2.amount = 250
    mock_transaction2.reference_id = "ref_002"

    # Mock wallet object with transactions.
    mock_wallet = Mock()
    mock_wallet.transactions = [mock_transaction1, mock_transaction2]

    # Mock functions.
    with patch('main.get_wallet_by_token', return_value=mock_wallet), \
            patch('main.check_wallet_status') as mock_check_status:

        # Ensure the wallet status check doesn't raise any exception.
        mock_check_status.return_value = None

        token = "3e3ccc8859751abcbf85b2645e681d79e4b9a4fa"
        headers = {"Authorization": f"Token {token}"}

        response = client.get("/api/v1/wallet/transactions", headers=headers)

        # Assertions.
        assert response.status_code == 200
        assert response.json()["status"] == "success"
        transactions = response.json()["data"]["transactions"]
        assert len(transactions) == 2  # 2 transactions in our mock wallet.

        # Check if the transactions in the response match our mocked data.
        for transaction in transactions:
            if transaction["id"] == "txn_001":
                assert transaction["amount"] == format_balance(mock_transaction1.amount)
            elif transaction["id"] == "txn_002":
                assert transaction["amount"] == format_balance(mock_transaction2.amount)


def test_add_money_to_wallet():
    """
    Test the add_money_to_wallet endpoint.

    This test mocks the fetching of a wallet and the process of adding a deposit to avoid real database interactions.
    It verifies that the endpoint correctly adds a deposit to the wallet identified by a token.
    """

    # Mock a transaction/deposit for the wallet.
    mock_transaction = Mock()
    mock_transaction.id = "txn_003"
    mock_transaction.status = "completed"
    mock_transaction.transacted_at = datetime.datetime.now()
    mock_transaction.amount = 150.5
    mock_transaction.reference_id = "ref_003"

    # Mock wallet object.
    mock_wallet = Mock()
    mock_wallet.customer_xid = "ea0212d3-abd6-406f-8c67-868e814a2435"

    # Mock functions.
    with patch('main.get_wallet_by_token', return_value=mock_wallet), \
            patch('main.check_wallet_status') as mock_check_status, \
            patch('main.add_deposit', return_value=mock_transaction):
        # Ensure the wallet status check doesn't raise any exception.
        mock_check_status.return_value = None

        token = "3e3ccc8859751abcbf85b2645e681d79e4b9a4fa"
        headers = {"Authorization": f"Token {token}"}
        data = {"amount": 150.5, "reference_id": "ref_003"}

        response = client.post("/api/v1/wallet/deposits", data=data, headers=headers)

        # Assertions.
        assert response.status_code == 201
        assert response.json()["status"] == "success"

        deposit = response.json()["data"]["deposit"]
        assert deposit["id"] == "txn_003"
        assert deposit["amount"] == format_balance(mock_transaction.amount)
        assert deposit["reference_id"] == "ref_003"


def test_make_a_withdrawal():
    """
    Test the make_a_withdrawal endpoint.

    This test mocks the fetching of a wallet and the process of making a withdrawal to avoid real database interactions.
    It verifies that the endpoint correctly processes a withdrawal from the wallet identified by a token.
    """

    # Mock a withdrawal transaction for the wallet.
    mock_transaction = Mock()
    mock_transaction.id = "txn_004"
    mock_transaction.status = "completed"
    mock_transaction.transacted_at = datetime.datetime.now()
    mock_transaction.amount = 100.5
    mock_transaction.reference_id = "ref_004"

    # Mock wallet object.
    mock_wallet = Mock()
    mock_wallet.customer_xid = "ea0212d3-abd6-406f-8c67-868e814a2435"

    # Mock functions.
    with patch('main.get_wallet_by_token', return_value=mock_wallet), \
            patch('main.check_wallet_status') as mock_check_status, \
            patch('main.make_withdrawal', return_value=mock_transaction):
        # Ensure the wallet status check doesn't raise any exception.
        mock_check_status.return_value = None

        token = "3e3ccc8859751abcbf85b2645e681d79e4b9a4fa"
        headers = {"Authorization": f"Token {token}"}
        data = {"amount": 100.5, "reference_id": "ref_004"}

        response = client.post("/api/v1/wallet/withdrawals", data=data, headers=headers)

        # Assertions.
        assert response.status_code == 201
        assert response.json()["status"] == "success"

        withdrawal = response.json()["data"]["withdrawal"]
        assert withdrawal["id"] == "txn_004"
        assert withdrawal["amount"] == format_balance(mock_transaction.amount)
        assert withdrawal["reference_id"] == "ref_004"


def generate_mock_wallet(status="enabled"):
    mock_wallet = Mock()
    mock_wallet.id = "1f486c05-31ce-4142-aecd-1909575f8506"
    mock_wallet.customer_xid = "ea0212d3-abd6-406f-8c67-868e814a2435"
    mock_wallet.status = status
    mock_wallet.enabled_at = datetime.datetime.now() if status == "enabled" else None
    mock_wallet.disabled_at = datetime.datetime.now() if status == "disabled" else None
    mock_wallet.balance = 1000
    return mock_wallet


def format_balance(amount):
    return int(amount)


def test_disable_user_wallet():
    """
    Test the disable_user_wallet endpoint.

    This test mocks the fetching of a wallet and the process of disabling a wallet to avoid real database interactions.
    It verifies that the endpoint correctly processes the request to disable a wallet identified by a token.
    """

    # Use the utility function to generate a mock wallet with 'enabled' status.
    mock_wallet = generate_mock_wallet()

    # Mock functions.
    with patch('main.get_wallet_by_token', return_value=mock_wallet), \
            patch('main.check_wallet_status') as mock_check_status, \
            patch('main.disable_wallet', return_value=mock_wallet):
        # Ensure the wallet status check doesn't raise any exception.
        mock_check_status.return_value = None

        token = "3e3ccc8859751abcbf85b2645e681d79e4b9a4fa"
        headers = {"Authorization": f"Token {token}"}
        data = {"is_disabled": True}

        response = client.patch("/api/v1/wallet", data=data, headers=headers)

        # Assertions.
        assert response.status_code == 200
        assert response.json()["status"] == "success"

        wallet = response.json()["data"]["wallet"]
        assert wallet["id"] == mock_wallet.id
        assert wallet["balance"] == format_balance(mock_wallet.balance)
        assert wallet["status"] == mock_wallet.status
