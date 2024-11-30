# services/reviews.py
from flask import Blueprint, request, jsonify
from database import db, Customer, InventoryItem, Review
from werkzeug.exceptions import NotFound

reviews_bp = Blueprint('reviews', __name__)


@reviews_bp.route('/submit_review', methods=['POST'])
def submit_review():
    """
    Allows a customer to submit a review for a product.

    Returns:
        Response: A JSON response with the review submission result.
    """
    data = request.json
    username = data.get("username")
    good_name = data.get("product_name")
    rating = data.get("rating")
    comment = data.get("comment", "")

    customer = Customer.query.filter_by(username=username).first()
    if not customer:
        return jsonify({"error": "Customer not found."}), 404

    item = InventoryItem.query.filter_by(name=good_name).first()
    if not item:
        return jsonify({"error": "Product not found."}), 404

    if rating < 1 or rating > 5:
        return jsonify({"error": "Rating must be between 1 and 5."}), 400

    review = Review(
        customer_username=username,
        product_name=good_name,
        rating=rating,
        comment=comment
    )

    db.session.add(review)
    db.session.commit()
    return jsonify({"message": "Review submitted successfully."}), 201

@reviews_bp.route('/update_review/<int:review_id>', methods=['PUT'])
def update_review(review_id):
    """
    Allows a customer to update their existing review.

    Args:
        review_id (int): The ID of the review to update.

    Returns:
        Response: A JSON response with the updated review result.
    """
    data = request.json
    review = Review.query.get(review_id)
    if not review:
        return jsonify({"error": "Review not found."}), 404

    if "rating" in data:
        rating = data["rating"]
        if rating < 1 or rating > 5:
            return jsonify({"error": "Rating must be between 1 and 5."}), 400
        review.rating = rating
    
    if "comment" in data:
        review.comment = data["comment"]
    
    db.session.commit()
    return jsonify({"message": "Review updated successfully."}), 200

@reviews_bp.route('/delete_review/<int:review_id>', methods=['DELETE'])
def delete_review(review_id):
    """
    Allows a customer or administrator to delete a review.

    Args:
        review_id (int): The ID of the review to delete.

    Returns:
        Response: A JSON response with the deletion result.
    """
    review = Review.query.get(review_id)
    if not review:
        return jsonify({"error": "Review not found."}), 404

    db.session.delete(review)
    db.session.commit()
    return jsonify({"message": "Review deleted successfully."}), 200

@reviews_bp.route('/get_product_reviews/<name>', methods=['GET'])
def get_product_reviews(name):
    """
    Retrieves all reviews for a specific product.

    Args:
        name (str): The name of the product to get reviews for.

    Returns:
        Response: A JSON response containing the list of reviews.
    """
    item = InventoryItem.query.filter_by(name=name).first()
    if not item:
        return jsonify({"error": "Product not found."}), 404

    reviews = Review.query.filter_by(product_name=name).all()
    return jsonify([{
        "username": review.customer_username,
        "rating": review.rating,
        "comment": review.comment
    } for review in reviews]), 200

@reviews_bp.route('/get_customer_reviews/<username>', methods=['GET'])
def get_customer_reviews(username):
    """
    Retrieves all reviews made by a specific customer.

    Args:
        username (str): The username of the customer.

    Returns:
        Response: A JSON response containing the list of reviews.
    """
    customer = Customer.query.filter_by(username=username).first()
    if not customer:
        return jsonify({"error": "Customer not found."}), 404

    reviews = Review.query.filter_by(customer_username=username).all()
    return jsonify([{
        "product_name": review.product_name,
        "rating": review.rating,
        "comment": review.comment
    } for review in reviews]), 200
