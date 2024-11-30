from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    age = db.Column(db.Integer, nullable=True)
    address = db.Column(db.String(200), nullable=True)
    gender = db.Column(db.String(10), nullable=True)
    marital_status = db.Column(db.String(20), nullable=True)
    wallet = db.Column(db.Float, default=0.0)

class InventoryItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200), nullable=True)
    stock = db.Column(db.Integer, nullable=False)

class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_username = db.Column(db.String(50), db.ForeignKey('customer.username'), nullable=False)
    item_name = db.Column(db.String(100), db.ForeignKey('inventory_item.name'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)

    customer = db.relationship("Customer", back_populates="sales")
    item = db.relationship("InventoryItem", back_populates="sales")

Customer.sales = db.relationship("Sale", back_populates="customer")
InventoryItem.sales = db.relationship("Sale", back_populates="item")

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_username = db.Column(db.String(50), db.ForeignKey('customer.username'), nullable=False)
    product_name = db.Column(db.String(100), db.ForeignKey('inventory_item.name'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.String(255))

    customer = db.relationship("Customer", back_populates="reviews")
    product = db.relationship("InventoryItem", back_populates="reviews")

Customer.reviews = db.relationship("Review", back_populates="customer")
InventoryItem.reviews = db.relationship("Review", back_populates="product")