from flask import Blueprint, request, jsonify, Flask
from database.database import db, Customer, InventoryItem, Sale
from datetime import datetime

sales_bp = Blueprint('sales', __name__)

@sales_bp.route('/display_goods', methods=['GET'])
def display_available_goods():
    """
    Displays all available goods with their name and price.

    Returns:
        Response: A JSON response containing a list of goods with name and price.
    """
    items = InventoryItem.query.filter(InventoryItem.stock > 0).all()
    goods = [{"name": item.name, "price": item.price} for item in items]
    return jsonify(goods), 200

@sales_bp.route('/goods/<name>', methods=['GET'])
def get_good_details(name):
    """
    Retrieves full information related to a specific good.

    Args:
        name (str): The name of the good.

    Returns:
        Response: A JSON response containing good details or an error message.
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

@sales_bp.route('/purchase', methods=['POST'])
def make_purchase():
    """
    Processes a purchase made by a customer.

    Request JSON:
        {
            "username": "<customer_username>",
            "item_name": "<item_name>",
            "quantity": <quantity>
        }

    Returns:
        Response: A JSON response with a success message or error.
    """
    data = request.json
    username = data.get('username')
    item_name = data.get('item_name')
    quantity = data.get('quantity', 1)

    if not username or not item_name:
        return jsonify({"error": "Username and item_name are required."}), 400
    if not isinstance(quantity, int) or quantity <= 0:
        return jsonify({"error": "Quantity must be a positive integer."}), 400

    # Check if customer exists
    customer = Customer.query.filter_by(username=username).first()
    if not customer:
        return jsonify({"error": "Customer not found."}), 404

    # Check if item exists
    item = InventoryItem.query.filter_by(name=item_name).first()
    if not item:
        return jsonify({"error": "Item not found."}), 404

    # Check if item is in stock
    if item.stock < quantity:
        return jsonify({"error": f"Insufficient stock. Available stock: {item.stock}."}), 400

    # Calculate total price
    total_price = item.price * quantity

    # Check if customer has enough money
    if customer.wallet < total_price:
        return jsonify({"error": "Insufficient funds in wallet."}), 400

    # Deduct money from customer wallet
    customer.wallet -= total_price

    # Decrease stock
    item.stock -= quantity

    # Record the sale
    sale = Sale(
        customer_id=customer.id,
        item_id=item.id,
        quantity=quantity,
        price=item.price,
        total_price=total_price,
        timestamp=datetime.utcnow()
    )
    db.session.add(sale)
    db.session.commit()

    return jsonify({"message": f"Purchase successful. {quantity} x {item_name} bought for ${total_price}."}), 200

@sales_bp.route('/purchase_history/<username>', methods=['GET'])
def get_purchase_history(username):
    """
    Retrieves the purchase history of a customer.

    Args:
        username (str): The username of the customer.

    Returns:
        Response: A JSON response containing the purchase history or an error message.
    """
    customer = Customer.query.filter_by(username=username).first()
    if not customer:
        return jsonify({"error": "Customer not found."}), 404

    purchases = Sale.query.filter_by(customer_id=customer.id).all()
    history = []
    for sale in purchases:
        item = db.session.get(InventoryItem, sale.item_id)
        history.append({
            "item_name": item.name,
            "quantity": sale.quantity,
            "price": sale.price,
            "total_price": sale.total_price,
            "timestamp": sale.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        })
    return jsonify(history), 200

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:12345@mysql_container:3306/ecommerce'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

app.register_blueprint(sales_bp, url_prefix='/sales')


# Main entry point
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5000, debug=True)

