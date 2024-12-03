from flask import Blueprint, request, jsonify, Flask
from database.database import db, InventoryItem
from sqlalchemy.sql import text
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

inventory_bp = Blueprint('inventory', __name__)

@inventory_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check for the Inventory service.
    """
    try:
        db.session.execute(text('SELECT 1'))
        db_status = "Healthy"
    except Exception as e:
        db_status = f"Unhealthy - {str(e)}"

    return jsonify({
        "service": "Inventory Service",
        "status": "Healthy",
        "database": db_status
    }), 200


def validate_inventory_data(data):
    """
    Validates the inventory data for adding or updating items.

    Args:
        data (dict): A dictionary containing inventory item information.

    Returns:
        list: A list of validation error messages. Returns an empty list if data is valid.
    """
    errors = []
    if not data.get('name') or len(data['name']) < 3:
        errors.append("Item name must be at least 3 characters long.")
    if not data.get('category') or data['category'].lower() not in ['food', 'clothes', 'accessories', 'electronics']:
        errors.append("Category must be one of 'food', 'clothes', 'accessories', or 'electronics' (case-insensitive).")
    if not isinstance(data.get('price'), (int, float)) or data['price'] <= 0:
        errors.append("Price must be a positive number.")
    if not isinstance(data.get('stock'), int) or data['stock'] < 0:
        errors.append("Stock must be a non-negative integer.")
    return errors

@inventory_bp.route('/add_item', methods=['POST'])
def add_item():
    """
    Adds a new item to the inventory.

    Returns:
        Response: A JSON response with a success message or validation errors.
    """
    data = request.json
    errors = validate_inventory_data(data)
    if errors:
        return jsonify({"errors": errors}), 400

    if InventoryItem.query.filter_by(name=data['name']).first():
        return jsonify({"error": "Item already exists."}), 400

    item = InventoryItem(
        name=data['name'],
        category=data['category'].capitalize(),
        price=data['price'],
        description=data.get('description', ''),
        stock=data['stock']
    )
    db.session.add(item)
    db.session.commit()
    return jsonify({"message": f"Item '{data['name']}' added successfully."}), 201

@inventory_bp.route('/update_item/<name>', methods=['PUT'])
def update_item(name):
    """
    Updates an existing inventory item.

    Args:
        name (str): The name of the item to update.

    Returns:
        Response: A JSON response with a success message or validation errors.
    """
    item = InventoryItem.query.filter_by(name=name).first()
    if not item:
        return jsonify({"error": "Item not found."}), 404

    data = request.json
    data['name'] = name
    print(data)
    errors = validate_inventory_data(data)
    if errors:
        return jsonify({"errors": errors}), 400

    # Update fields
    for key, value in data.items():
        setattr(item, key, value)
    db.session.commit()
    return jsonify({"message": f"Item '{name}' updated successfully."}), 200


@inventory_bp.route('/deduct_stock/<name>', methods=['POST'])
def deduct_stock(name):
    """
    Deducts a specified quantity from the stock of an inventory item.

    Args:
        name (str): The name of the item to update.
        quantity (int): The quantity to deduct from the stock.

    Returns:
        Response: A JSON response with a success message or validation error.
    """
    # Find the item by name
    item = InventoryItem.query.filter_by(name=name).first()
    if not item:
        return jsonify({"error": "Item not found."}), 404

    # Parse and validate input data
    data = request.json
    if "quantity" not in data or not isinstance(data['quantity'], int) or data['quantity'] <= 0:
        return jsonify({"error": "Invalid quantity. Quantity must be a positive integer."}), 400

    quantity = data['quantity']

    # Check if the deduction is possible
    if item.stock < quantity:
        return jsonify({"error": f"Insufficient stock. Available stock is {item.stock}."}), 400

    # Deduct the quantity from stock
    item.stock -= quantity
    db.session.commit()
    return jsonify({"message": f"{quantity} units deducted from stock for item '{name}'. Remaining stock: {item.stock}."}), 200



#extra features not required in the project's pdf
@inventory_bp.route('/get_items', methods=['GET'])
def get_items():
    """
    Retrieves all items in the inventory.

    Returns:
        Response: A JSON response containing a list of all items.
    """
    items = InventoryItem.query.all()
    return jsonify([{
        "name": item.name,
        "category": item.category,
        "price": item.price,
        "description": item.description,
        "stock": item.stock
    } for item in items]), 200

@inventory_bp.route('/get_item/<name>', methods=['GET'])
def get_item(name):
    """
    Retrieves an inventory item by its name.

    Args:
        name (str): The name of the item to retrieve.

    Returns:
        Response: A JSON response containing the item details or an error message.
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

@inventory_bp.route('/delete_item/<name>', methods=['DELETE'])
def delete_item(name):
    """
    Deletes an inventory item by its name.

    Args:
        name (str): The name of the item to delete.

    Returns:
        Response: A JSON response with a success or error message.
    """
    item = InventoryItem.query.filter_by(name=name).first()
    if not item:
        return jsonify({"error": "Item not found."}), 404

    db.session.delete(item)
    db.session.commit()
    return jsonify({"message": f"Item '{name}' deleted successfully."}), 200


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:12345@mysql_container:3306/ecommerce'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["25 per minute"] 
)

limiter.limit("20 per minute")(inventory_bp)  # Limit inventory routes to 20 requests per minute

app.register_blueprint(inventory_bp, url_prefix='/inventory')


# Main entry point
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5000, debug=True)
