import pytest
from app import app
from database.database import db, Customer

@pytest.fixture
def client():
    """
    Test client for Flask app.
    """
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///:memory:"  # Use in-memory DB for testing
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    with app.test_client() as client:
        with app.app_context():
            db.create_all()  # Create tables for testing
        yield client
        with app.app_context():
            db.drop_all()  # Clean up after tests


def test_register_customer(client):
    """
    Test customer registration.
    """
    response = client.post('/customers/register', json={
        "full_name": "John Doe",
        "username": "johndoe",
        "password": "securepassword",
        "age": 30,
        "gender": "Male",
        "marital_status": "Single"
    })
    assert response.status_code == 201
    assert response.get_json()["message"] == "Customer registered successfully"


def test_register_existing_customer(client):
    """
    Test registering a customer with an existing username.
    """
    client.post('/customers/register', json={
        "full_name": "John Doe",
        "username": "johndoe",
        "password": "securepassword",
        "age": 30,
        "gender": "Male",
        "marital_status": "Single"
    })
    response = client.post('/customers/register', json={
        "full_name": "Jane Smith",
        "username": "johndoe",  # Same username
        "password": "securepassword123",
        "age": 25,
        "gender": "Female",
        "marital_status": "Married"
    })
    assert response.status_code == 400
    assert response.get_json()["error"] == "Username already exists"


def test_get_all_customers(client):
    """
    Test retrieving all registered customers.
    """
    client.post('/customers/register', json={
        "full_name": "John Doe",
        "username": "johndoe",
        "password": "securepassword",
        "age": 30,
        "gender": "Male",
        "marital_status": "Single"
    })
    response = client.get('/customers/customers')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1
    assert data[0]["username"] == "johndoe"


def test_get_customer(client):
    """
    Test retrieving a single customer by username.
    """
    client.post('/customers/register', json={
        "full_name": "John Doe",
        "username": "johndoe",
        "password": "securepassword",
        "age": 30,
        "gender": "Male",
        "marital_status": "Single"
    })
    response = client.get('/customers/customer/johndoe')
    assert response.status_code == 200
    data = response.get_json()
    assert data["username"] == "johndoe"


def test_delete_customer(client):
    """
    Test deleting a customer.
    """
    client.post('/customers/register', json={
        "full_name": "John Doe",
        "username": "johndoe",
        "password": "securepassword",
        "age": 30,
        "gender": "Male",
        "marital_status": "Single"
    })
    response = client.delete('/customers/delete/johndoe')
    assert response.status_code == 200
    assert response.get_json()["message"] == "Customer deleted successfully"


def test_charge_wallet(client):
    """
    Test charging a customer's wallet.
    """
    client.post('/customers/register', json={
        "full_name": "John Doe",
        "username": "johndoe",
        "password": "securepassword",
        "age": 30,
        "gender": "Male",
        "marital_status": "Single"
    })
    response = client.post('/customers/charge/johndoe', json={"amount": 50})
    assert response.status_code == 200
    assert response.get_json()["message"] == "$50 added to wallet"


def test_deduct_wallet(client):
    """
    Test deducting from a customer's wallet.
    """
    client.post('/customers/register', json={
        "full_name": "John Doe",
        "username": "johndoe",
        "password": "securepassword",
        "age": 30,
        "gender": "Male",
        "marital_status": "Single"
    })
    client.post('/customers/charge/johndoe', json={"amount": 100})
    response = client.post('/customers/deduct/johndoe', json={"amount": 30})
    assert response.status_code == 200
    assert response.get_json()["message"] == "$30 deducted from wallet"

    # Insufficient funds
    response = client.post('/customers/deduct/johndoe', json={"amount": 200})
    assert response.status_code == 400
    assert response.get_json()["error"] == "Insufficient funds"


def test_register_customer_missing_fields(client):
    """
    Test customer registration with missing required fields.
    """
    response = client.post('/customers/register', json={
        "username": "johndoe",  # Missing full_name, password, etc.
        "age": 30,
        "gender": "Male",
        "marital_status": "Single"
    })
    assert response.status_code == 400
    errors = response.get_json()["errors"]
    assert "Full name must be at least 3 characters long." in errors
    assert "Password must be at least 8 characters long." in errors


def test_register_customer_invalid_username(client):
    """
    Test customer registration with an invalid username.
    """
    response = client.post('/customers/register', json={
        "full_name": "John Doe",
        "username": "invalid username!",  # Invalid characters
        "password": "securepassword",
        "age": 30,
        "gender": "Male",
        "marital_status": "Single"
    })
    assert response.status_code == 400
    assert "Username must contain only letters, numbers, and '.', '_', '-'." in response.get_json()["errors"]


def test_register_customer_invalid_gender(client):
    """
    Test customer registration with an invalid gender.
    """
    response = client.post('/customers/register', json={
        "full_name": "John Doe",
        "username": "johndoe",
        "password": "securepassword",
        "age": 30,
        "gender": "InvalidGender",  # Not in ['Male', 'Female', 'Other']
        "marital_status": "Single"
    })
    assert response.status_code == 400
    assert "Gender must be 'Male', 'Female', or 'Other' (case-insensitive)." in response.get_json()["errors"]


def test_register_customer_invalid_age(client):
    """
    Test customer registration with an invalid age.
    """
    response = client.post('/customers/register', json={
        "full_name": "John Doe",
        "username": "johndoe",
        "password": "securepassword",
        "age": -5,  # Negative age
        "gender": "Male",
        "marital_status": "Single"
    })
    assert response.status_code == 400
    assert "Age must be a non-negative integer." in response.get_json()["errors"]


def test_register_customer_invalid_marital_status(client):
    """
    Test customer registration with an invalid marital status.
    """
    response = client.post('/customers/register', json={
        "full_name": "John Doe",
        "username": "johndoe",
        "password": "securepassword",
        "age": 30,
        "gender": "Male",
        "marital_status": "Complicated"  # Not in ['Single', 'Married', 'Divorced', 'Widowed']
    })
    assert response.status_code == 400
    assert "Marital status must be one of 'Single', 'Married', 'Divorced', or 'Widowed' (case-insensitive)." in response.get_json()["errors"]
