import pytest
from app import app
from database.database import db, InventoryItem

@pytest.fixture
def client(): #temporary test env. to test our requests without actually running the server
    """
    Test client for Flask app.
    """
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///:memory:"  # Use in-memory DB for testing
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    with app.test_client() as client:
        with app.app_context():
            db.create_all()  
        yield client
        with app.app_context():
            db.drop_all()  # Clean up after tests


def test_add_item(client):
    """
    Test adding a new inventory item.
    """
    response = client.post('/inventory/add_item', json={
        "name": "Laptop",
        "category": "electronics",
        "price": 1200.99,
        "description": "High-performance laptop",
        "stock": 50
    })
    assert response.status_code == 201
    assert response.get_json()["message"] == "Item 'Laptop' added successfully."


def test_add_existing_item(client):
    """
    Test adding an existing inventory item.
    """
    client.post('/inventory/add_item', json={
        "name": "Laptop",
        "category": "electronics",
        "price": 1200.99,
        "description": "High-performance laptop",
        "stock": 50
    })
    response = client.post('/inventory/add_item', json={
        "name": "Laptop",  # has same name
        "category": "electronics",
        "price": 999.99,
        "description": "Another laptop",
        "stock": 30
    })
    assert response.status_code == 400
    assert response.get_json()["error"] == "Item already exists."


def test_add_item_invalid_data(client):
    """
    Test adding an item with invalid data.
    """
    response = client.post('/inventory/add_item', json={
        "name": "L",  # too short
        "category": "invalid_category",  # Invalid category
        "price": -10,  # has negative price
        "stock": -5  # has negative stock
    })
    assert response.status_code == 400
    errors = response.get_json()["errors"]
    assert "Item name must be at least 3 characters long." in errors
    assert "Category must be one of 'food', 'clothes', 'accessories', or 'electronics' (case-insensitive)." in errors
    assert "Price must be a positive number." in errors
    assert "Stock must be a non-negative integer." in errors


def test_update_item(client):
    """
    Test updating an existing inventory item.
    """
    client.post('/inventory/add_item', json={
        "name": "Laptop",
        "category": "electronics",
        "price": 1200.99,
        "description": "High-performance laptop",
        "stock": 50
    })
    response = client.put('/inventory/update_item/Laptop', json={
        "name": "Laptop",
        "category": "electronics",
        "price": 999.99,  # Updated price
        "description": "Updated laptop description",
        "stock": 30  # Updated stock
    })
    assert response.status_code == 200
    assert response.get_json()["message"] == "Item 'Laptop' updated successfully."


def test_deduct_stock(client):
    """
    Test deducting stock from an inventory item.
    """
    client.post('/inventory/add_item', json={
        "name": "Laptop",
        "category": "electronics",
        "price": 1200.99,
        "description": "High-performance laptop",
        "stock": 50
    })
    response = client.post('/inventory/deduct_stock/Laptop', json={"quantity": 10})
    assert response.status_code == 200
    assert response.get_json()["message"] == "10 units deducted from stock for item 'Laptop'. Remaining stock: 40."

    # try to deduct more than available stock
    response = client.post('/inventory/deduct_stock/Laptop', json={"quantity": 100})
    assert response.status_code == 400
    assert response.get_json()["error"] == "Insufficient stock. Available stock is 40."


def test_get_items(client):
    """
    Test retrieving all inventory items.
    """
    client.post('/inventory/add_item', json={
        "name": "Laptop",
        "category": "electronics",
        "price": 1200.99,
        "description": "High-performance laptop",
        "stock": 50
    })
    client.post('/inventory/add_item', json={
        "name": "Phone",
        "category": "electronics",
        "price": 799.99,
        "description": "Latest smartphone",
        "stock": 100
    })
    response = client.get('/inventory/get_items')
    assert response.status_code == 200
    items = response.get_json()
    assert len(items) == 2
    assert items[0]["name"] == "Laptop"
    assert items[1]["name"] == "Phone"


def test_get_item(client):
    """
    Test retrieving a single inventory item by name.
    """
    client.post('/inventory/add_item', json={
        "name": "Laptop",
        "category": "electronics",
        "price": 1200.99,
        "description": "High-performance laptop",
        "stock": 50
    })
    response = client.get('/inventory/get_item/Laptop')
    assert response.status_code == 200
    item = response.get_json()
    assert item["name"] == "Laptop"
    assert item["stock"] == 50


def test_delete_item(client):
    """
    Test deleting an inventory item.
    """
    client.post('/inventory/add_item', json={
        "name": "Laptop",
        "category": "electronics",
        "price": 1200.99,
        "description": "High-performance laptop",
        "stock": 50
    })
    response = client.delete('/inventory/delete_item/Laptop')
    assert response.status_code == 200
    assert response.get_json()["message"] == "Item 'Laptop' deleted successfully."

    # Try deleting a non existing item
    response = client.delete('/inventory/delete_item/Laptop')
    assert response.status_code == 404
    assert response.get_json()["error"] == "Item not found."
