from flask import Flask
from database.database import db
from services.customers.customers import customers_bp
from services.inventory.inventory import inventory_bp
from services.sales.sales import sales_bp
from services.reviews.reviews import reviews_bp
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:12345@localhost:3306/ecommerce_saade_souaiby'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

limiter = Limiter(
    get_remote_address,  # Use the client's IP address for rate-limiting
    app=app,
    default_limits=["200 per day", "50 per hour"]  # Default rate limits
)
# Apply rate limiting to blueprints
limiter.limit("20 per minute")(customers_bp)  # Limit customer routes to 10 requests per minute
limiter.limit("20 per minute")(inventory_bp)  # Limit inventory routes to 20 requests per minute
limiter.limit("25 per minute")(reviews_bp)  # Limit review routes to 15 requests per minute
limiter.limit("30 per minute")(sales_bp)  # Limit sales routes to 25 requests per minute

app.register_blueprint(customers_bp, url_prefix='/customers')
app.register_blueprint(inventory_bp, url_prefix='/inventory')
app.register_blueprint(sales_bp, url_prefix='/sales')
app.register_blueprint(reviews_bp, url_prefix='/reviews')

# Main entry point
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
