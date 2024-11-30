import pytest
from app import app
from database import db, Customer, InventoryItem, Review

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
                password="hashed_password",
                age=30,
                gender="Male",
                marital_status="Single",
                wallet=100.00
            )
            db.session.add(customer)
            # Create another customer
            customer2 = Customer(
                full_name="Jane Smith",
                username="janesmith",
                password="hashed_password",
                age=28,
                gender="Female",
                marital_status="Married",
                wallet=200.00
            )
            db.session.add(customer2)
            # Create test inventory items
            item = InventoryItem(
                name="Laptop",
                category="Electronics",
                price=999.99,
                description="A high-end laptop",
                stock=10
            )
            db.session.add(item)
            db.session.commit()
        yield client
        with app.app_context():
            db.drop_all()

def test_submit_review(client):
    """
    Test submitting a new review.
    """
    response = client.post('/reviews/submit', json={
        "username": "johndoe",
        "item_name": "Laptop",
        "rating": 5,
        "comment": "Excellent product!"
    })
    assert response.status_code == 201
    assert response.get_json()["message"] == "Review submitted successfully and is pending approval."

def test_submit_review_invalid_rating(client):
    """
    Test submitting a review with an invalid rating.
    """
    response = client.post('/reviews/submit', json={
        "username": "johndoe",
        "item_name": "Laptop",
        "rating": 6,  # Invalid rating
        "comment": "Great!"
    })
    assert response.status_code == 400
    assert response.get_json()["error"] == "Rating must be an integer between 1 and 5."

def test_submit_review_nonexistent_customer(client):
    """
    Test submitting a review with a nonexistent customer.
    """
    response = client.post('/reviews/submit', json={
        "username": "nonexistent",
        "item_name": "Laptop",
        "rating": 5,
        "comment": "Great!"
    })
    assert response.status_code == 404
    assert response.get_json()["error"] == "Customer not found."

def test_submit_review_nonexistent_item(client):
    """
    Test submitting a review for a nonexistent item.
    """
    response = client.post('/reviews/submit', json={
        "username": "johndoe",
        "item_name": "Smartphone",
        "rating": 4,
        "comment": "Good!"
    })
    assert response.status_code == 404
    assert response.get_json()["error"] == "Item not found."

def test_update_review(client):
    """
    Test updating an existing review.
    """
    # Submit a review first
    client.post('/reviews/submit', json={
        "username": "johndoe",
        "item_name": "Laptop",
        "rating": 5,
        "comment": "Excellent product!"
    })
    # Retrieve the review ID
    with app.app_context():
        review = Review.query.filter_by(customer_id=1).first()
        review_id = review.id

    # Update the review
    response = client.put(f'/reviews/update/{review_id}', json={
        "username": "johndoe",
        "rating": 4,
        "comment": "Updated comment."
    })
    assert response.status_code == 200
    assert response.get_json()["message"] == "Review updated successfully and is pending approval."

def test_update_review_not_author(client):
    """
    Test updating a review by someone who is not the author.
    """
    # Submit a review with johndoe
    client.post('/reviews/submit', json={
        "username": "johndoe",
        "item_name": "Laptop",
        "rating": 5,
        "comment": "Excellent product!"
    })
    # Retrieve the review ID
    with app.app_context():
        review = Review.query.filter_by(customer_id=1).first()
        review_id = review.id

    # Attempt to update the review with janesmith
    response = client.put(f'/reviews/update/{review_id}', json={
        "username": "janesmith",
        "rating": 3,
        "comment": "I didn't write this."
    })
    assert response.status_code == 403
    assert response.get_json()["error"] == "You can only update your own reviews."

def test_delete_review(client):
    """
    Test deleting a review.
    """
    # Submit a review
    client.post('/reviews/submit', json={
        "username": "johndoe",
        "item_name": "Laptop",
        "rating": 5,
        "comment": "Excellent product!"
    })
    # Retrieve the review ID
    with app.app_context():
        review = Review.query.filter_by(customer_id=1).first()
        review_id = review.id

    # Delete the review
    response = client.delete(f'/reviews/delete/{review_id}', json={
        "username": "johndoe"
    })
    assert response.status_code == 200
    assert response.get_json()["message"] == "Review deleted successfully."

def test_delete_review_not_author(client):
    """
    Test deleting a review by someone who is not the author.
    """
    # Submit a review with johndoe
    client.post('/reviews/submit', json={
        "username": "johndoe",
        "item_name": "Laptop",
        "rating": 5,
        "comment": "Excellent product!"
    })
    # Retrieve the review ID
    with app.app_context():
        review = Review.query.filter_by(customer_id=1).first()
        review_id = review.id

    # Attempt to delete the review with janesmith
    response = client.delete(f'/reviews/delete/{review_id}', json={
        "username": "janesmith"
    })
    assert response.status_code == 403
    assert response.get_json()["error"] == "You can only delete your own reviews."

def test_get_product_reviews(client):
    """
    Test retrieving all approved reviews for a product.
    """
    # Submit a review and approve it
    client.post('/reviews/submit', json={
        "username": "johndoe",
        "item_name": "Laptop",
        "rating": 5,
        "comment": "Excellent product!"
    })
    with app.app_context():
        review = Review.query.filter_by(customer_id=1).first()
        review.status = 'approved'
        db.session.commit()

    response = client.get('/reviews/product_reviews/Laptop')
    assert response.status_code == 200
    reviews = response.get_json()
    assert len(reviews) == 1
    assert reviews[0]["username"] == "johndoe"
    assert reviews[0]["rating"] == 5

def test_get_customer_reviews(client):
    """
    Test retrieving all reviews submitted by a customer.
    """
    # Submit two reviews with johndoe
    client.post('/reviews/submit', json={
        "username": "johndoe",
        "item_name": "Laptop",
        "rating": 5,
        "comment": "Excellent product!"
    })
    # Add another item
    client.post('/inventory/add_item', json={
        "name": "Mouse",
        "category": "Accessories",
        "price": 49.99,
        "description": "Wireless mouse",
        "stock": 20
    })
    client.post('/reviews/submit', json={
        "username": "johndoe",
        "item_name": "Mouse",
        "rating": 4,
        "comment": "Good mouse."
    })

    response = client.get('/reviews/customer_reviews/johndoe')
    assert response.status_code == 200
    reviews = response.get_json()
    assert len(reviews) == 2
    assert reviews[0]["item_name"] == "Laptop"
    assert reviews[1]["item_name"] == "Mouse"

def test_get_review_details(client):
    """
    Test retrieving details of a specific review.
    """
    # Submit a review
    client.post('/reviews/submit', json={
        "username": "johndoe",
        "item_name": "Laptop",
        "rating": 5,
        "comment": "Excellent product!"
    })
    with app.app_context():
        review = Review.query.first()
        review_id = review.id

    response = client.get(f'/reviews/review/{review_id}')
    assert response.status_code == 200
    review_data = response.get_json()
    assert review_data["username"] == "johndoe"
    assert review_data["item_name"] == "Laptop"
    assert review_data["rating"] == 5

def test_moderate_review_approve(client):
    """
    Test approving a review as an admin.
    """
    # Submit a review
    client.post('/reviews/submit', json={
        "username": "janesmith",
        "item_name": "Laptop",
        "rating": 4,
        "comment": "Very good!"
    })
    with app.app_context():
        review = Review.query.first()
        review_id = review.id

    # Moderate the review
    response = client.post(f'/reviews/moderate/{review_id}', json={
        "action": "approve"
    })
    assert response.status_code == 200
    assert response.get_json()["message"] == "Review approved successfully."

    # Check that the status is updated
    with app.app_context():
        review = db.session.get(Review, review_id)
        assert review.status == 'approved'

def test_moderate_review_flag(client):
    """
    Test flagging a review as an admin.
    """
    # Submit a review
    client.post('/reviews/submit', json={
        "username": "janesmith",
        "item_name": "Laptop",
        "rating": 1,
        "comment": "Terrible!"
    })
    with app.app_context():
        review = Review.query.first()
        review_id = review.id

    # Moderate the review
    response = client.post(f'/reviews/moderate/{review_id}', json={
        "action": "flag"
    })
    assert response.status_code == 200
    assert response.get_json()["message"] == "Review flagd successfully."

    # Check that the status is updated
    with app.app_context():
        review = db.session.get(Review, review_id)
        assert review.status == 'flagged'

def test_moderate_review_delete(client):
    """
    Test deleting a review as an admin.
    """
    # Submit a review
    client.post('/reviews/submit', json={
        "username": "janesmith",
        "item_name": "Laptop",
        "rating": 2,
        "comment": "Not good."
    })
    with app.app_context():
        review = Review.query.first()
        review_id = review.id

    # Moderate the review
    response = client.post(f'/reviews/moderate/{review_id}', json={
        "action": "delete"
    })
    assert response.status_code == 200
    assert response.get_json()["message"] == "Review deleted successfully."

    # Check that the review is deleted
    with app.app_context():
        review = db.session.get(Review, review_id)
        assert review is None

def test_moderate_review_invalid_action(client):
    """
    Test moderating a review with an invalid action.
    """
    # Submit a review
    client.post('/reviews/submit', json={
        "username": "janesmith",
        "item_name": "Laptop",
        "rating": 3,
        "comment": "Average."
    })
    with app.app_context():
        review = Review.query.first()
        review_id = review.id

    # Attempt to moderate with an invalid action
    response = client.post(f'/reviews/moderate/{review_id}', json={
        "action": "invalid_action"
    })
    assert response.status_code == 400
    assert response.get_json()["error"] == "Invalid action. Must be 'approve', 'flag', or 'delete'."
