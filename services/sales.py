# services/sales.py
from flask import Blueprint, request, jsonify
from database import db, Customer, InventoryItem
from sqlalchemy.exc import IntegrityError

sales_bp = Blueprint('sales', __name__)

def validate_purchase_data(customer, good_name, quantity):
    """
    Validates the purchase data including checking if the good is available 
    and if the customer has sufficient funds.

    Args:
        customer (Customer): The customer making the purchase.
        good_name (str): The name of the good to be purchased.
        quantity (int): The quantity to be purchased.

    Returns:
        dict: A dictionary containing success or error messages.
    """
    item = InventoryItem.query.filter_by(name=good_name).first()
    if not item:
        return {"error": "Item not found."}

    if item.stock < quantity:
        return {"error": f"Insufficient stock. Available stock is {item.stock}."}

    total_price = item.price * quantity
    if customer.wallet < total_price:
        return {"error": "Insufficient funds."}

    return {"success": True, "total_price": total_price, "item": item}

@sales_bp.route('/display_goods', methods=['GET'])
def display_goods():
    """
    Displays all available goods with their name and price.

    Returns:
        Response: A JSON response containing a list of goods.
    """
    items = InventoryItem.query.all()
    return jsonify([{
        "name": item.name,
        "price": item.price
    } for item in items]), 200

@sales_bp.route('/get_goods_details/<name>', methods=['GET'])
def get_goods_details(name):
    """
    Retrieves detailed information about a specific good.

    Args:
        name (str): The name of the good to retrieve.

    Returns:
        Response: A JSON response containing item details.
    """
    item = InventoryItem.query.filter_by(name=name).first()
    if not item:
        return jsonify({"error": "Item not found."}), 404

    return jsonify({
        "name": item.name,
        "category": item.category,
        "price": item.price,
        "description": item.description,
        "stock": item.stock
    }), 200

@sales_bp.route('/sale', methods=['POST'])
def make_sale():
    """
    Processes a sale, deducting the amount from the customer's wallet and reducing stock.

    Returns:
        Response: A JSON response with the result of the sale.
    """
    data = request.json
    username = data.get("username")
    good_name = data.get("good_name")
    quantity = data.get("quantity", 1)

    customer = Customer.query.filter_by(username=username).first()
    if not customer:
        return jsonify({"error": "Customer not found."}), 404

    # Validate the purchase
    validation = validate_purchase_data(customer, good_name, quantity)
    if "error" in validation:
        return jsonify(validation), 400

    # Process the purchase
    total_price = validation["total_price"]
    item = validation["item"]

    customer.wallet -= total_price
    item.stock -= quantity

    # Save purchase history (not implemented in database yet)
    # Assume you have a PurchaseHistory table for this

    db.session.commit()
    return jsonify({
        "message": f"Sale successful. {quantity} {good_name} purchased for ${total_price}.",
        "new_wallet_balance": customer.wallet,
        "remaining_stock": item.stock
    }), 200
