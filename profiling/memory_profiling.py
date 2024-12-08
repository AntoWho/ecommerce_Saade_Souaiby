from memory_profiler import profile
import requests

# Define base URLs based on your Docker Compose setup
CUSTOMER_URL = "http://localhost:5001/customers"
INVENTORY_URL = "http://localhost:5002/inventory"
SALES_URL = "http://localhost:5003/sales"
REVIEWS_URL = "http://localhost:5004/reviews"

# Define variables
username = "john.doe"
name = "Laptop"
review_id = "1"

@profile
def register_customer():
    url = f"{CUSTOMER_URL}/register"
    payload = {
        "full_name": "John Doe",
        "username": username,
        "password": "securePass123",
        "age": 30,
        "address": "123 Main St, City, Country",
        "gender": "Male",
        "marital_status": "Single"
    }
    response = requests.post(url, json=payload)
    print(f"Register Customer: {response.status_code} - {response.json()}")

@profile
def get_all_customers():
    url = f"{CUSTOMER_URL}/customers"
    response = requests.get(url)
    print(f"Get All Customers: {response.status_code} - {response.json()}")

@profile
def get_customer_by_username():
    url = f"{CUSTOMER_URL}/customer/{username}"
    response = requests.get(url)
    print(f"Get Customer by Username: {response.status_code} - {response.json()}")

@profile
def update_customer():
    url = f"{CUSTOMER_URL}/update/{username}"
    payload = {
        "full_name": "John Updated",
        "password": "newSecurePass123",
        "age": 31,
        "username": username
    }
    response = requests.put(url, json=payload)
    print(f"Update Customer: {response.status_code} - {response.json()}")

@profile
def delete_customer():
    url = f"{CUSTOMER_URL}/delete/{username}"
    response = requests.delete(url)
    try:
        json_response = response.json()
    except ValueError:  # This occurs if response is not JSON
        json_response = None
    print(f"Delete Customer: {response.status_code} - {json_response}")

@profile
def charge_wallet():
    url = f"{CUSTOMER_URL}/charge/{username}"
    payload = {"amount": 50.0}
    response = requests.post(url, json=payload)
    print(f"Charge Wallet: {response.status_code} - {response.json()}")

@profile
def deduct_wallet():
    url = f"{CUSTOMER_URL}/deduct/{username}"
    payload = {"amount": 30.0}
    response = requests.post(url, json=payload)
    print(f"Deduct Wallet: {response.status_code} - {response.json()}")

@profile
def health_check_customers():
    url = f"{CUSTOMER_URL}/health"
    response = requests.get(url)
    print(f"Health Check (Customers): {response.status_code} - {response.json()}")

@profile
def add_inventory_item():
    url = f"{INVENTORY_URL}/add_item"
    payload = {
        "name": name,
        "category": "Electronics",
        "price": 1200.99,
        "description": "A high-end gaming laptop.",
        "stock": 10
    }
    response = requests.post(url, json=payload)
    print(f"Add Inventory Item: {response.status_code} - {response.json()}")

@profile
def update_inventory_item():
    url = f"{INVENTORY_URL}/update_item/{name}"
    payload = {
        "price": 11.50,
        "stock": 15,
        "category": "Electronics"
    }
    response = requests.put(url, json=payload)
    print(f"Update Inventory Item: {response.status_code} - {response.json()}")

@profile
def deduct_stock():
    url = f"{INVENTORY_URL}/deduct_stock/{name}"
    payload = {"quantity": 2}
    response = requests.post(url, json=payload)
    print(f"Deduct Stock: {response.status_code} - {response.json()}")

@profile
def get_all_items():
    url = f"{INVENTORY_URL}/get_items"
    response = requests.get(url)
    print(f"Get All Items: {response.status_code} - {response.json()}")

@profile
def get_item_by_name():
    url = f"{INVENTORY_URL}/get_item/{name}"
    response = requests.get(url)
    print(f"Get Item by Name: {response.status_code} - {response.json()}")

@profile
def delete_item():
    url = f"{INVENTORY_URL}/delete_item/{name}"
    response = requests.delete(url)
    try:
        json_response = response.json()
    except ValueError:  # Handles empty or non-JSON responses
        json_response = None
    print(f"Delete Item: {response.status_code} - {json_response}")

@profile
def health_check_inventory():
    url = f"{INVENTORY_URL}/health"
    response = requests.get(url)
    print(f"Health Check (Inventory): {response.status_code} - {response.json()}")

@profile
def display_available_goods():
    url = f"{SALES_URL}/display_goods"
    response = requests.get(url)
    print(f"Display Available Goods: {response.status_code} - {response.json()}")

@profile
def get_good_details():
    url = f"{SALES_URL}/goods/{name}"
    response = requests.get(url)
    print(f"Get Good Details: {response.status_code} - {response.json()}")

@profile
def make_purchase():
    url = f"{SALES_URL}/purchase"
    payload = {
        "username": username,
        "item_name": name,
        "quantity": 1
    }
    response = requests.post(url, json=payload)
    print(f"Make Purchase: {response.status_code} - {response.json()}")

@profile
def get_purchase_history():
    url = f"{SALES_URL}/purchase_history/{username}"
    response = requests.get(url)
    print(f"Get Purchase History: {response.status_code} - {response.json()}")

@profile
def submit_review():
    url = f"{REVIEWS_URL}/submit"
    payload = {
        "username": username,
        "item_name": name,
        "rating": 5,
        "comment": "Excellent performance!"
    }
    response = requests.post(url, json=payload)
    print(f"Submit Review: {response.status_code} - {response.json()}")

@profile
def update_review():
    url = f"{REVIEWS_URL}/update/{review_id}"
    payload = {
        "username": username,
        "rating": 4,
        "comment": "Updated: Very good, but battery life could improve."
    }
    response = requests.put(url, json=payload)
    print(f"Update Review: {response.status_code} - {response.json()}")

@profile
def delete_review():
    url = f"{REVIEWS_URL}/delete/{review_id}"
    payload = {"username": username}
    response = requests.delete(url, json=payload)
    print(f"Delete Review: {response.status_code} - {response.json()}")

@profile
def moderate_review():
    url = f"{REVIEWS_URL}/moderate/{review_id}"
    payload = {"action": "approve"}
    response = requests.post(url, json=payload)
    print(f"Moderate Review: {response.status_code} - {response.json()}")

@profile
def get_product_reviews():
    url = f"{REVIEWS_URL}/product_reviews/{name}"
    response = requests.get(url)
    print(f"Get Product Reviews: {response.status_code} - {response.json()}")

@profile
def get_customer_reviews():
    url = f"{REVIEWS_URL}/customer_reviews/{username}"
    response = requests.get(url)
    print(f"Get Customer Reviews: {response.status_code} - {response.json()}")

@profile
def get_review_details():
    url = f"{REVIEWS_URL}/review/{review_id}"
    response = requests.get(url)
    print(f"Get Review Details: {response.status_code} - {response.json()}")

@profile
def flag_review():
    url = f"{REVIEWS_URL}/flag/{review_id}"
    response = requests.post(url)
    print(f"Flag Review: {response.status_code} - {response.json()}")

@profile
def get_flagged_reviews():
    url = f"{REVIEWS_URL}/flagged"
    response = requests.get(url)
    print(f"Get Flagged Reviews: {response.status_code} - {response.json()}")

@profile
def health_check_sales():
    url = f"{SALES_URL}/health"
    response = requests.get(url)
    print(f"Health Check (Sales): {response.status_code} - {response.json()}")

@profile
def health_check_reviews():
    url = f"{REVIEWS_URL}/health"
    response = requests.get(url)
    print(f"Health Check (Reviews): {response.status_code} - {response.json()}")

@profile
def run_all_requests():
    # Health Checks
    health_check_customers()
    health_check_inventory()
    health_check_sales()
    health_check_reviews()

    # Customers API
    register_customer()
    get_all_customers()
    get_customer_by_username()
    update_customer()
    charge_wallet()
    deduct_wallet()
    delete_customer()

    # Inventory API
    add_inventory_item()
    update_inventory_item()
    deduct_stock()
    get_all_items()
    get_item_by_name()
    delete_item()

    # Sales API
    display_available_goods()
    get_good_details()
    make_purchase()
    get_purchase_history()

    # Reviews API
    submit_review()
    update_review()
    delete_review()
    moderate_review()
    get_product_reviews()
    get_customer_reviews()
    get_review_details()
    flag_review()
    get_flagged_reviews()

if __name__ == "__main__":
    run_all_requests()