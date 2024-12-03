import pytest
from app import app
from database.database import db, Customer, InventoryItem

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
            db.create_all()
            # Setup initial data for tests
            # Create a test customer
            customer = Customer(
                full_name="John Doe",
                username="johndoe",
                password="hashed_password",  # Assuming password hashing is handled
                age=30,
                gender="Male",
                marital_status="Single",
                wallet=100.00  # Initial wallet balance
            )
            db.session.add(customer)
            # Create test inventory items
            item1 = InventoryItem(
                name="Laptop",
                category="Electronics",
                price=999.99,
                description="A high-end laptop",
                stock=10
            )
            item2 = InventoryItem(
                name="Headphones",
                category="Accessories",
                price=199.99,
                description="Noise-cancelling headphones",
                stock=5
            )
            db.session.add_all([item1, item2])
            db.session.commit()
        yield client
        with app.app_context():
            db.drop_all()

def test_display_available_goods(client):
    """
    Test displaying all available goods.
    """
    response = client.get('/sales/display_goods')
    assert response.status_code == 200
    goods = response.get_json()
    assert isinstance(goods, list)
    assert len(goods) == 2
    assert goods[0]["name"] == "Laptop"
    assert goods[1]["name"] == "Headphones"

def test_get_good_details(client):
    """
    Test retrieving details of a specific good.
    """
    response = client.get('/sales/goods/Laptop')
    assert response.status_code == 200
    item = response.get_json()
    assert item["name"] == "Laptop"
    assert item["price"] == 999.99
    assert item["stock"] == 10

    # Test non-existing item
    response = client.get('/sales/goods/Smartphone')
    assert response.status_code == 404
    assert response.get_json()["error"] == "Item not found."

def test_make_purchase(client):
    """
    Test making a successful purchase.
    """
    # Charge the customer's wallet to ensure sufficient funds
    client.post('/customers/charge/johndoe', json={"amount": 1000})
    response = client.post('/sales/purchase', json={
        "username": "johndoe",
        "item_name": "Laptop",
        "quantity": 1
    })
    assert response.status_code == 200
    assert "Purchase successful." in response.get_json()["message"]

    # Verify that the customer's wallet balance decreased
    response = client.get('/customers/customer/johndoe')
    customer = response.get_json()
    expected_balance = 100.00 + 1000 - 999.99  # Initial + charged - price
    assert abs(customer["wallet"] - expected_balance) < 1E-6

    # Verify that the item's stock decreased
    response = client.get('/inventory/get_item/Laptop')
    item = response.get_json()
    assert item["stock"] == 9  # Stock reduced by 1

def test_make_purchase_insufficient_funds(client):
    """
    Test making a purchase with insufficient funds.
    """
    response = client.post('/sales/purchase', json={
        "username": "johndoe",
        "item_name": "Laptop",
        "quantity": 1
    })
    assert response.status_code == 400
    assert response.get_json()["error"] == "Insufficient funds in wallet."

def test_make_purchase_insufficient_stock(client):
    """
    Test making a purchase when there is insufficient stock.
    """
    # Charge the customer's wallet sufficiently
    client.post('/customers/charge/johndoe', json={"amount": 10000})
    response = client.post('/sales/purchase', json={
        "username": "johndoe",
        "item_name": "Headphones",
        "quantity": 10  # Exceeds available stock
    })
    assert response.status_code == 400
    assert response.get_json()["error"] == "Insufficient stock. Available stock: 5."

def test_make_purchase_nonexistent_item(client):
    """
    Test making a purchase of a nonexistent item.
    """
    response = client.post('/sales/purchase', json={
        "username": "johndoe",
        "item_name": "Smartphone",
        "quantity": 1
    })
    assert response.status_code == 404
    assert response.get_json()["error"] == "Item not found."

def test_make_purchase_nonexistent_customer(client):
    """
    Test making a purchase with a nonexistent customer.
    """
    response = client.post('/sales/purchase', json={
        "username": "janedoe",
        "item_name": "Laptop",
        "quantity": 1
    })
    assert response.status_code == 404
    assert response.get_json()["error"] == "Customer not found."

def test_get_purchase_history(client):
    """
    Test retrieving a customer's purchase history.
    """
    # Make some purchases
    client.post('/customers/charge/johndoe', json={"amount": 2000})
    client.post('/sales/purchase', json={
        "username": "johndoe",
        "item_name": "Laptop",
        "quantity": 1
    })
    client.post('/sales/purchase', json={
        "username": "johndoe",
        "item_name": "Headphones",
        "quantity": 2
    })

    response = client.get('/sales/purchase_history/johndoe')
    assert response.status_code == 200
    history = response.get_json()
    assert len(history) == 2
    assert history[0]["item_name"] == "Laptop"
    assert history[0]["quantity"] == 1
    assert history[1]["item_name"] == "Headphones"
    assert history[1]["quantity"] == 2

def test_get_purchase_history_no_purchases(client):
    """
    Test retrieving purchase history for a customer with no purchases.
    """
    response = client.get('/sales/purchase_history/johndoe')
    assert response.status_code == 200
    history = response.get_json()
    assert history == []

def test_get_purchase_history_nonexistent_customer(client):
    """
    Test retrieving purchase history for a nonexistent customer.
    """
    response = client.get('/sales/purchase_history/janedoe')
    assert response.status_code == 404
    assert response.get_json()["error"] == "Customer not found."
