from flask import Blueprint, request, jsonify
from flask import Flask
from database.database import db, Customer
from werkzeug.security import generate_password_hash, check_password_hash
import re
from sqlalchemy.sql import text
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

customers_bp = Blueprint('customers', __name__)

@customers_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check for the Customers service.

    Returns:
        Response: JSON with service and database status.
    """
    try:
        # Check database connectivity
        db.session.execute(text('SELECT 1'))
        db_status = "Healthy"
    except Exception as e:
        db_status = f"Unhealthy - {str(e)}"

    return jsonify({
        "service": "Customers Service",
        "status": "Healthy",
        "database": db_status
    }), 200


def validate_customer_data(data):
    """
    Validates the customer data for registration and updates.

    Args:
        data (dict): A dictionary containing customer information.

    Returns:
        list: A list of validation error messages. Returns an empty list if data is valid.
    """
    errors = []
    if not data.get('full_name') or len(data['full_name']) < 3:
        errors.append("Full name must be at least 3 characters long.")
    if not data.get('username') or not re.match(r'^[a-zA-Z0-9_.-]+$', data['username']):
        errors.append("Username must contain only letters, numbers, and '.', '_', '-'.")
    if not data.get('password') or len(data['password']) < 8:
        errors.append("Password must be at least 8 characters long.")
    if data.get('age') and (not isinstance(data['age'], int) or data['age'] < 0):
        errors.append("Age must be a non-negative integer.")

    # Normalize and validate gender
    gender = data.get('gender', '').lower()
    if gender and gender not in ['male', 'female', 'other']:
        errors.append("Gender must be 'Male', 'Female', or 'Other' (case-insensitive).")
    
    marital_status = data.get('marital_status', '').lower()
    if marital_status and marital_status not in ['single', 'married', 'divorced', 'widowed']:
        errors.append("Marital status must be one of 'Single', 'Married', 'Divorced', or 'Widowed' (case-insensitive).")
    
    return errors

def validate_username(username):
    """
    Validates the username format.

    Args:
        username (str): The username to validate.

    Returns:
        bool: True if the username is valid, False otherwise.
    """
    if not re.match(r'^[a-zA-Z0-9_.-]+$', username):
        return False
    return True


# Routes
@customers_bp.route('/register', methods=['POST'])
def register_customer():
    """
    Registers a new customer.

    Returns:
        Response: A JSON response with a success message or validation errors.
    """
    data = request.json
    errors = validate_customer_data(data)
    if errors:
        return jsonify({"errors": errors}), 400

    username = data.get('username')
    if Customer.query.filter_by(username=username).first():
        return jsonify({"error": "Username already exists"}), 400

    hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')
    customer = Customer(
        full_name=data.get("full_name"),
        username=username,
        password=hashed_password,
        age=data.get("age"),
        address=data.get("address"),
        gender=data.get("gender", '').capitalize(),
        marital_status=data.get("marital_status", '').capitalize()
    )
    db.session.add(customer)
    db.session.commit()
    return jsonify({"message": "Customer registered successfully"}), 201

@customers_bp.route('/customers', methods=['GET'])
def get_all_customers():
    """
    Retrieves all registered customers.

    Returns:
        Response: A JSON response containing a list of all customers.
    """
    customers = Customer.query.all()
    return jsonify([{
        "full_name": c.full_name,
        "username": c.username,
        "age": c.age,
        "address": c.address,
        "gender": c.gender,
        "marital_status": c.marital_status,
        "wallet": c.wallet
    } for c in customers]), 200

@customers_bp.route('/customer/<username>', methods=['GET'])
def get_customer(username):
    """
    Retrieves a customer by username.

    Args:
        username (str): The username of the customer.

    Returns:
        Response: A JSON response containing customer details or an error message.
    """
    if not validate_username(username):
        return jsonify({"error": "Invalid username format"}), 400

    customer = Customer.query.filter_by(username=username).first()
    if not customer:
        return jsonify({"error": "Customer not found"}), 404

    return jsonify({
        "full_name": customer.full_name,
        "username": customer.username,
        "age": customer.age,
        "address": customer.address,
        "gender": customer.gender,
        "marital_status": customer.marital_status,
        "wallet": customer.wallet
    }), 200

@customers_bp.route('/delete/<username>', methods=['DELETE'])
def delete_customer(username):
    """
    Deletes a customer by username.

    Args:
        username (str): The username of the customer to delete.

    Returns:
        Response: A JSON response with a success or error message.
    """
    if not validate_username(username):
        return jsonify({"error": "Invalid username format"}), 400

    customer = Customer.query.filter_by(username=username).first()
    if not customer:
        return jsonify({"error": "Customer not found"}), 404

    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message": "Customer deleted successfully"}), 200

@customers_bp.route('/update/<username>', methods=['PUT'])
def update_customer(username):
    """
    Updates customer details by username.

    Args:
        username (str): The username of the customer to update.

    Returns:
        Response: A JSON response with a success message or validation errors.
    """
    if not validate_username(username):
        return jsonify({"error": "Invalid username format"}), 400
    
    customer = Customer.query.filter_by(username=username).first()
    if not customer:
        return jsonify({"error": "Customer not found"}), 404

    data = request.json
    errors = validate_customer_data(data)
    if errors:
        return jsonify({"errors": errors}), 400

    # Update fields
    for key, value in data.items():
        if key == 'password':  # Re-hash password if updated
            value = generate_password_hash(value, method='pbkdf2:sha256')
        setattr(customer, key, value)
    db.session.commit()
    return jsonify({"message": "Customer updated successfully"}), 200

@customers_bp.route('/charge/<username>', methods=['POST'])
def charge_wallet(username):
    """
    Charges a customer's wallet.

    Args:
        username (str): The username of the customer.
        amount (float): The amount to add to the wallet.

    Returns:
        Response: A JSON response with a success message or validation error.
    """
    if not validate_username(username):
        return jsonify({"error": "Invalid username format"}), 400

    data = request.json
    if "amount" not in data:
        return jsonify({"error": "Amount is missing from the request payload."}), 400

    amount = data.get("amount")
    if not isinstance(amount, (int, float)) or amount <= 0:
        return jsonify({"error": "Invalid amount. Amount must be a positive number."}), 400

    customer = Customer.query.filter_by(username=username).first()
    if not customer:
        return jsonify({"error": "Customer not found"}), 404

    customer.wallet += amount
    db.session.commit()
    return jsonify({"message": f"${amount} added to wallet"}), 200

@customers_bp.route('/deduct/<username>', methods=['POST'])
def deduct_wallet(username):
    """
    Deducts an amount from a customer's wallet.

    Args:
        username (str): The username of the customer.
        amount (float): The amount to deduct from the wallet.

    Returns:
        Response: A JSON response with a success message or error.
    """
    if not validate_username(username):
        return jsonify({"error": "Invalid username format"}), 400

    data = request.json
    if "amount" not in data:
        return jsonify({"error": "Amount is missing from the request payload."}), 400

    amount = data.get("amount")
    if not isinstance(amount, (int, float)) or amount <= 0:
        return jsonify({"error": "Invalid amount. Amount must be a positive number."}), 400

    customer = Customer.query.filter_by(username=username).first()
    if not customer:
        return jsonify({"error": "Customer not found"}), 404

    if customer.wallet < amount:
        return jsonify({"error": "Insufficient funds"}), 400

    customer.wallet -= amount
    db.session.commit()
    return jsonify({"message": f"${amount} deducted from wallet"}), 200


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:12345@mysql_container:3306/ecommerce'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["20 per minute"]  # Apply 20 requests per minute for the entire service
)

limiter.limit("20 per minute")(customers_bp)  # Limit customer routes to 20 requests per minute

app.register_blueprint(customers_bp, url_prefix='/customers')


# Main entry point
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5000, debug=True)
