from flask import Blueprint, request, jsonify, Flask
from database.database import db, Customer, InventoryItem, Review
from datetime import datetime
from sqlalchemy.sql import text
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity


reviews_bp = Blueprint('reviews', __name__)

@reviews_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check for the Reviews service.
    """
    try:
        db.session.execute(text('SELECT 1'))
        db_status = "Healthy"
    except Exception as e:
        db_status = f"Unhealthy - {str(e)}"

    return jsonify({
        "service": "Reviews Service",
        "status": "Healthy",
        "database": db_status
    }), 200

@reviews_bp.route('/submit', methods=['POST'])
@jwt_required()
def submit_review():
    """
    Allows customers to submit a review for a product.

    Request JSON:
        {
            "username": "<customer_username>",
            "item_name": "<item_name>",
            "rating": <rating>,
            "comment": "<comment>"
        }

    Returns:
        Response: A JSON response with a success message or error.
    """
    data = request.json
    username = data.get('username')
    item_name = data.get('item_name')
    rating = data.get('rating')
    comment = data.get('comment', '')

    if not username or not item_name or rating is None:
        return jsonify({"error": "Username, item_name, and rating are required."}), 400
    if not isinstance(rating, int) or rating < 1 or rating > 5:
        return jsonify({"error": "Rating must be an integer between 1 and 5."}), 400

    # Check if customer exists
    customer = Customer.query.filter_by(username=username).first()
    if not customer:
        return jsonify({"error": "Customer not found."}), 404

    # Check if item exists
    item = InventoryItem.query.filter_by(name=item_name).first()
    if not item:
        return jsonify({"error": "Item not found."}), 404

    # Create new review
    review = Review(
        customer_id=customer.id,
        item_id=item.id,
        rating=rating,
        comment=comment,
        status='pending',
        timestamp=datetime.utcnow()
    )
    db.session.add(review)
    db.session.commit()

    return jsonify({"message": "Review submitted successfully and is pending approval."}), 201

@reviews_bp.route('/update/<int:review_id>', methods=['PUT'])
@jwt_required()
def update_review(review_id):
    """
    Allows customers to update their existing review.

    Args:
        review_id (int): The ID of the review to update.

    Request JSON:
        {
            "username": "<customer_username>",
            "rating": <new_rating>,
            "comment": "<new_comment>"
        }

    Returns:
        Response: A JSON response with a success message or error.
    """
    data = request.json
    username = data.get('username')
    rating = data.get('rating')
    comment = data.get('comment')

    if not username:
        return jsonify({"error": "Username is required."}), 400

    # Check if review exists
    review = db.session.get(Review, review_id)
    if not review:
        return jsonify({"error": "Review not found."}), 404

    # Check if customer is the author of the review
    customer = Customer.query.filter_by(username=username).first()
    if not customer or customer.id != review.customer_id:
        return jsonify({"error": "You can only update your own reviews."}), 403

    # Update review
    if rating is not None:
        if not isinstance(rating, int) or rating < 1 or rating > 5:
            return jsonify({"error": "Rating must be an integer between 1 and 5."}), 400
        review.rating = rating
    if comment is not None:
        review.comment = comment

    review.timestamp = datetime.utcnow()
    review.status = 'pending'  # Reset status to pending after update
    db.session.commit()

    return jsonify({"message": "Review updated successfully and is pending approval."}), 200

@reviews_bp.route('/delete/<int:review_id>', methods=['DELETE'])
@jwt_required()
def delete_review(review_id):
    """
    Allows customers to delete their review.

    Args:
        review_id (int): The ID of the review to delete.

    Request JSON:
        {
            "username": "<customer_username>"
        }

    Returns:
        Response: A JSON response with a success message or error.
    """
    data = request.json
    username = data.get('username')

    if not username:
        return jsonify({"error": "Username is required."}), 400

    # Check if review exists
    review = db.session.get(Review, review_id)
    if not review:
        return jsonify({"error": "Review not found."}), 404

    # Check if customer is the author
    customer = Customer.query.filter_by(username=username).first()
    if not customer or customer.id != review.customer_id:
        return jsonify({"error": "You can only delete your own reviews."}), 403

    db.session.delete(review)
    db.session.commit()

    return jsonify({"message": "Review deleted successfully."}), 200

@reviews_bp.route('/product_reviews/<item_name>', methods=['GET'])
def get_product_reviews(item_name):
    """
    Retrieves all approved reviews for a specific product.

    Args:
        item_name (str): The name of the product.

    Returns:
        Response: A JSON response containing a list of reviews.
    """
    item = InventoryItem.query.filter_by(name=item_name).first()
    if not item:
        return jsonify({"error": "Item not found."}), 404

    reviews = Review.query.filter_by(item_id=item.id, status='approved').all()
    result = []
    for review in reviews:
        customer = db.session.get(Customer, review.customer_id)
        result.append({
            "username": customer.username,
            "rating": review.rating,
            "comment": review.comment,
            "timestamp": review.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        })
    return jsonify(result), 200

@reviews_bp.route('/customer_reviews/<username>', methods=['GET'])
def get_customer_reviews(username):
    """
    Retrieves all reviews submitted by a specific customer.

    Args:
        username (str): The username of the customer.

    Returns:
        Response: A JSON response containing a list of reviews.
    """
    customer = Customer.query.filter_by(username=username).first()
    if not customer:
        return jsonify({"error": "Customer not found."}), 404

    reviews = Review.query.filter_by(customer_id=customer.id).all()
    result = []
    for review in reviews:
        item = db.session.get(InventoryItem, review.item_id)
        result.append({
            "item_name": item.name,
            "rating": review.rating,
            "comment": review.comment,
            "status": review.status,
            "timestamp": review.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        })
    return jsonify(result), 200

@reviews_bp.route('/review/<int:review_id>', methods=['GET'])
def get_review_details(review_id):
    """
    Retrieves detailed information about a specific review.

    Args:
        review_id (int): The ID of the review.

    Returns:
        Response: A JSON response containing review details.
    """
    review = db.session.get(Review, review_id)
    if not review:
        return jsonify({"error": "Review not found."}), 404

    customer = db.session.get(Customer, review.customer_id)
    item = db.session.get(InventoryItem, review.item_id)

    return jsonify({
        "username": customer.username,
        "item_name": item.name,
        "rating": review.rating,
        "comment": review.comment,
        "status": review.status,
        "timestamp": review.timestamp.strftime('%Y-%m-%d %H:%M:%S')
    }), 200

@reviews_bp.route('/moderate/<int:review_id>', methods=['POST'])
def moderate_review(review_id):
    """
    Allows administrators to moderate a review by approving or deleting it.

    Args:
        review_id (int): The ID of the review to moderate.

    Request JSON:
        {
            "action": "<approve|delete>"
        }

    Returns:
        Response: A JSON response with a success message or error.
    """
    data = request.json
    action = data.get('action')

    if action not in ['approve',  'delete']:
        return jsonify({"error": "Invalid action. Must be 'approve' or 'delete'."}), 400

    review = db.session.get(Review, review_id)
    if not review:
        return jsonify({"error": "Review not found."}), 404

    if action == 'approve':
        review.status = 'approved'
    elif action == 'delete':
        db.session.delete(review)
        db.session.commit()
        return jsonify({"message": "Review deleted successfully."}), 200

    db.session.commit()
    return jsonify({"message": f"Review {action}d successfully."}), 200

@reviews_bp.route('/flag/<int:review_id>', methods=['POST'])
def flag_review(review_id):
    """
    Flags a review as inappropriate.

    Args:
        review_id (int): ID of the review to flag.

    Returns:
        Response: JSON message indicating success or failure.
    """
    review = Review.query.get(review_id)
    if not review:
        return jsonify({"error": "Review not found"}), 404

    review.status = 'flagged'
    db.session.commit()
    return jsonify({"message": f"Review {review_id} has been flagged for moderation."}), 200

@reviews_bp.route('/flagged', methods=['GET'])
def get_flagged_reviews():
    """
    Retrieves all flagged reviews for moderation.

    Returns:
        Response: JSON list of flagged reviews.
    """
    flagged_reviews = Review.query.filter_by(status="flagged").all()
    return jsonify([{
    "id": review.id,
    "customer_id": review.customer_id,
    "item_id": review.item_id,  # Changed from product_id to item_id
    "rating": review.rating,
    "comment": review.comment,  # Renamed from review_text to comment
    "status": review.status,
    "timestamp": review.timestamp.isoformat()  # Convert datetime to ISO format for JSON
    
    } for review in flagged_reviews]), 200




app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:12345@mysql_container:3306/ecommerce'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = "3f2eb67d8e9f8b0d27f5c2f92a7ab7d78bcf29d9b1a0d2b1c42f68ec72e8cd50"  

db.init_app(app)
jwt = JWTManager(app)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["20 per minute"]  # Apply 20 requests per minute for the entire service
)

limiter.limit("20 per minute")(reviews_bp)  # Limit review routes to 20 requests per minute

app.register_blueprint(reviews_bp, url_prefix='/reviews')


# Main entry point
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5000, debug=True)

