import pytest
from app import app
from database import db, Sale, Customer, InventoryItem

@pytest.fixture
def client():
    """
    Test client for Flask app.
    """
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///:memory:"  # Use in-memory DB for testing
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    with app.test_client() as client:
        with app.app_context():  # Ensure the context is pushed
            db.create_all()  # Create tables for testing
        yield client
        with app.app_context():
            db.drop_all()  # Clean up after tests



def test_create_sale(client):
    """
    Test creating a new sale.
    """
    # First, add a customer and an inventory item to the database
    customer = Customer(full_name="John Doe", username="johndoe", password="securepassword", age=30, gender="Male", marital_status="Single")
    db.session.add(customer)
    db.session.commit()

    item = InventoryItem(name="Laptop", category="electronics", price=1200.99, description="High-performance laptop", stock=50)
    db.session.add(item)
    db.session.commit()

    response = client.post('/sales/create', json={
        "customer_username": "johndoe",
        "item_name": "Laptop",
        "quantity": 2,
        "total_amount": 2401.98
    })
    assert response.status_code == 201
    assert response.get_json()["message"] == "Sale recorded successfully."


def test_create_sale_with_insufficient_stock(client):
    """
    Test creating a sale when there is insufficient stock for the requested quantity.
    """
    # First, add a customer and an inventory item to the database
    customer = Customer(full_name="John Doe", username="johndoe", password="securepassword", age=30, gender="Male", marital_status="Single")
    db.session.add(customer)
    db.session.commit()

    item = InventoryItem(name="Laptop", category="electronics", price=1200.99, description="High-performance laptop", stock=5)
    db.session.add(item)
    db.session.commit()

    # Try creating a sale for more quantity than available
    response = client.post('/sales/create', json={
        "customer_username": "johndoe",
        "item_name": "Laptop",
        "quantity": 10,  # More than the available stock
        "total_amount": 12009.80
    })
    assert response.status_code == 400
    assert response.get_json()["error"] == "Insufficient stock."


def test_create_sale_invalid_customer(client):
    """
    Test creating a sale with a non-existent customer.
    """
    # First, add an inventory item to the database
    item = InventoryItem(name="Laptop", category="electronics", price=1200.99, description="High-performance laptop", stock=50)
    db.session.add(item)
    db.session.commit()

    # Try creating a sale with a non-existent customer
    response = client.post('/sales/create', json={
        "customer_username": "nonexistent_user",  # Invalid username
        "item_name": "Laptop",
        "quantity": 2,
        "total_amount": 2401.98
    })
    assert response.status_code == 404
    assert response.get_json()["error"] == "Customer not found."


def test_create_sale_invalid_item(client):
    """
    Test creating a sale with a non-existent inventory item.
    """
    # First, add a customer to the database
    customer = Customer(full_name="John Doe", username="johndoe", password="securepassword", age=30, gender="Male", marital_status="Single")
    db.session.add(customer)
    db.session.commit()

    # Try creating a sale with a non-existent item
    response = client.post('/sales/create', json={
        "customer_username": "johndoe",
        "item_name": "Nonexistent Item",  # Invalid item name
        "quantity": 2,
        "total_amount": 2401.98
    })
    assert response.status_code == 404
    assert response.get_json()["error"] == "Item not found."


def test_get_sales(client):
    """
    Test retrieving all sales.
    """
    # Add a customer and an inventory item
    customer = Customer(full_name="John Doe", username="johndoe", password="securepassword", age=30, gender="Male", marital_status="Single")
    db.session.add(customer)
    db.session.commit()

    item = InventoryItem(name="Laptop", category="electronics", price=1200.99, description="High-performance laptop", stock=50)
    db.session.add(item)
    db.session.commit()

    # Create a sale
    client.post('/sales/create', json={
        "customer_username": "johndoe",
        "item_name": "Laptop",
        "quantity": 2,
        "total_amount": 2401.98
    })

    response = client.get('/sales')
    assert response.status_code == 200
    sales = response.get_json()
    assert len(sales) == 1
    assert sales[0]["customer_username"] == "johndoe"
    assert sales[0]["item_name"] == "Laptop"
    assert sales[0]["quantity"] == 2


def test_get_sale(client):
    """
    Test retrieving a single sale by its ID.
    """
    # Add a customer and an inventory item
    customer = Customer(full_name="John Doe", username="johndoe", password="securepassword", age=30, gender="Male", marital_status="Single")
    db.session.add(customer)
    db.session.commit()

    item = InventoryItem(name="Laptop", category="electronics", price=1200.99, description="High-performance laptop", stock=50)
    db.session.add(item)
    db.session.commit()

    # Create a sale
    sale_response = client.post('/sales/create', json={
        "customer_username": "johndoe",
        "item_name": "Laptop",
        "quantity": 2,
        "total_amount": 2401.98
    })
    sale_id = sale_response.get_json()["sale_id"]

    response = client.get(f'/sales/{sale_id}')
    assert response.status_code == 200
    sale = response.get_json()
    assert sale["sale_id"] == sale_id
    assert sale["customer_username"] == "johndoe"
    assert sale["item_name"] == "Laptop"


def test_delete_sale(client):
    """
    Test deleting a sale.
    """
    # Add a customer and an inventory item
    customer = Customer(full_name="John Doe", username="johndoe", password="securepassword", age=30, gender="Male", marital_status="Single")
    db.session.add(customer)
    db.session.commit()

    item = InventoryItem(name="Laptop", category="electronics", price=1200.99, description="High-performance laptop", stock=50)
    db.session.add(item)
    db.session.commit()

    # Create a sale
    sale_response = client.post('/sales/create', json={
        "customer_username": "johndoe",
        "item_name": "Laptop",
        "quantity": 2,
        "total_amount": 2401.98
    })
    sale_id = sale_response.get_json()["sale_id"]

    # Delete the sale
    response = client.delete(f'/sales/{sale_id}')
    assert response.status_code == 200
    assert response.get_json()["message"] == "Sale deleted successfully."


def test_delete_nonexistent_sale(client):
    """
    Test deleting a non-existent sale.
    """
    response = client.delete('/sales/999')  # Non-existent sale ID
    assert response.status_code == 404
    assert response.get_json()["error"] == "Sale not found."
