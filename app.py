from flask import Flask
from database import db
from services.customers import customers_bp
from services.inventory import inventory_bp
from services.sales import sales_bp
from services.reviews import reviews_bp

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:12345@localhost:3306/ecommerce_saade_souaiby'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

app.register_blueprint(customers_bp, url_prefix='/customers')
app.register_blueprint(inventory_bp, url_prefix='/inventory')
app.register_blueprint(sales_bp, url_prefix='/sales')
app.register_blueprint(reviews_bp, url_prefix='/reviews')

# Main entry point
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
