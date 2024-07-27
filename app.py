import logging
from flask import Flask, request, jsonify, make_response, render_template, send_from_directory
from flask_cors import CORS
import bcrypt
from dbmethods import dbmethods
import helpers
import hashlib

# Create the Flask app
app = Flask(__name__)
CORS(app, supports_credentials=True)

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/cart')
def cart():
    return render_template('cart.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/orderHistoryPage')
def order_history_page():
    return render_template('order_history.html')

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

# Create a new user endpoint
@app.route('/users/create', methods=['POST'])
def create_user():
    try:
        userInformation = request.json
        name = helpers.sanitize_input(userInformation["name"])
        email = helpers.sanitize_input(userInformation["email"])
        plainTextPassword = helpers.sanitize_input(userInformation["password"])
        salt = bcrypt.gensalt()
        hashedPassword = bcrypt.hashpw(plainTextPassword.encode('utf-8'), salt)
        db = dbmethods()
        existing_user = db.get_user_by_email(email)

        if existing_user:
            db.close_connection()
            content = {"message": "User already exists"}
            response = make_response(jsonify(content))
            return response, 409

        db.create_user(name, email, hashedPassword.decode(), None)
        db.close_connection()
        content = {"message": "User created successfully"}
        response = make_response(jsonify(content))
        return response, 201
    except Exception as e:
        logger.error("Error creating user: %s", e)
        return jsonify({"message": "Internal Server Error"}), 500

# Verify user endpoint
@app.route('/users/verify', methods=['POST'])
def verify_user():
    try:
        userInformation = request.json
        email = helpers.sanitize_input(userInformation['email'])
        plainTextPassword = helpers.sanitize_input(userInformation['password'])
        db = dbmethods()
        user = db.verify_login(email)
        if user and bcrypt.checkpw(plainTextPassword.encode('utf-8'), user[0][3].encode('utf-8')):
            authToken = helpers.generate_token()
            db.update_auth_token(user[0][0], hashlib.sha256(authToken.encode("utf-8")).hexdigest())
            db.close_connection()
            content = {"message": "User verified successfully", "name": user[0][1], "user_id": user[0][0],
                       "email": user[0][2], "authToken": authToken}
            response = make_response(jsonify(content))
            response.set_cookie(key="authToken", value=authToken, httponly=True, max_age=3600)
            return response, 200
        else:
            db.close_connection()
            return jsonify({"message": "User verification failed"}), 401
    except Exception as e:
        logger.error("Error verifying user: %s", e)
        return jsonify({"message": "Internal Server Error"}), 500

# Add Item to cart endpoint
@app.route('/cart/items', methods=['POST'])
def add_to_cart():
    try:
        authToken = request.cookies.get('authToken')
        if authToken:
            db = dbmethods()
            user = db.verify_auth(hashlib.sha256(authToken.encode("utf-8")).hexdigest())
            if user:
                cartInformation = request.json
                itemName = helpers.sanitize_input(cartInformation["itemName"])
                itemPrice = helpers.sanitize_input(float(cartInformation["itemPrice"]))
                itemQuantity = helpers.sanitize_input(int(cartInformation["itemQuantity"]))

                if itemPrice < 0:
                    return jsonify({"message": "Price must be non-negative"}), 400

                if itemQuantity <= 0:
                    return jsonify({"message": "Quantity must not be 0 or non-negative"}), 400

                existing_item = db.get_cart_item(user[0][0], itemName, itemPrice)

                if existing_item:
                    new_quantity = existing_item[0][4] + itemQuantity
                    db.update_cart_quantity(existing_item[0][0], new_quantity)
                    message = "Quantity updated"
                else:
                    db.add_to_cart(user[0][0], itemName, itemPrice, itemQuantity)
                    message = f"Added {itemName} to the cart!"

                db.close_connection()
                return jsonify({"message": message}), 200
            else:
                db.close_connection()
                return jsonify({"message": "User verification failed"}), 401
        else:
            return jsonify({"message": "Authentication required"}), 401
    except Exception as e:
        logger.error("Error adding to cart: %s", e)
        return jsonify({"message": "Internal Server Error"}), 500

# Update cart quantity endpoint
@app.route('/cart/items', methods=['PUT'])
def update_cart_quantity():
    try:
        authToken = request.cookies.get('authToken')
        if authToken:
            db = dbmethods()
            user = db.verify_auth(hashlib.sha256(authToken.encode("utf-8")).hexdigest())
            if user:
                cart_id = helpers.sanitize_input(request.json['cart_id'])
                itemQuantity = helpers.sanitize_input(int(request.json['itemQuantity']))

                if itemQuantity < 0:
                    return jsonify({"message": "You can't set quantity negative"}), 400
                elif itemQuantity == 0:
                    db.remove_from_cart(cart_id)
                    db.close_connection()
                    return jsonify({"message": "Item removed from cart"}), 200
                else:
                    db.update_cart_quantity(cart_id, itemQuantity)
                    db.close_connection()
                    return jsonify({"message": "Cart item quantity updated"}), 200
            else:
                db.close_connection()
                return jsonify({"message": "User verification failed"}), 401
        else:
            return jsonify({"message": "Authentication required"}), 401
    except Exception as e:
        logger.error("Error updating cart quantity: %s", e)
        return jsonify({"message": "Internal Server Error"}), 500

# Remove from cart endpoint
@app.route('/cart/items', methods=['DELETE'])
def remove_from_cart():
    try:
        authToken = request.cookies.get('authToken')
        if authToken:
            db = dbmethods()
            user = db.verify_auth(hashlib.sha256(authToken.encode("utf-8")).hexdigest())
            if user:
                cart_id = helpers.sanitize_input(request.json['cart_id'])
                db.remove_from_cart(cart_id)
                db.close_connection()
                return jsonify({"message": "Item removed from cart"}), 200
            else:
                db.close_connection()
                return jsonify({"message": "User verification failed"}), 401
        else:
            return jsonify({"message": "Authentication required"}), 401
    except Exception as e:
        logger.error("Error removing from cart: %s", e)
        return jsonify({"message": "Internal Server Error"}), 500

# View Cart endpoint
@app.route('/cart/items', methods=['GET'])
def view_cart():
    try:
        authToken = request.cookies.get('authToken')
        if authToken:
            db = dbmethods()
            user = db.verify_auth(hashlib.sha256(authToken.encode("utf-8")).hexdigest())
            if user:
                cart = db.view_cart(user[0][0])
                db.close_connection()
                return jsonify(cart), 200
            else:
                db.close_connection()
                return jsonify({"message": "User verification failed"}), 401
        else:
            return jsonify({"message": "Authentication required"}), 401
    except Exception as e:
        logger.error("Error viewing cart: %s", e)
        return jsonify({"message": "Internal Server Error"}), 500

# Checkout cart endpoint
@app.route('/cart/checkout', methods=['POST'])
def checkout_cart():
    try:
        authToken = request.cookies.get('authToken')
        if authToken:
            db = dbmethods()
            user = db.verify_auth(hashlib.sha256(authToken.encode("utf-8")).hexdigest())
            if user:
                db.checkout_entire_cart(user[0][0])
                db.close_connection()
                return jsonify({"message": "Cart checked out successfully"}), 200
            else:
                db.close_connection()
                return jsonify({"message": "User verification failed"}), 401
        else:
            return jsonify({"message": "Authentication required"}), 401
    except Exception as e:
        logger.error("Error checking out cart: %s", e)
        return jsonify({"message": "Internal Server Error"}), 500

# Get user order history endpoint
@app.route('/users/orderHistory', methods=['GET'])
def order_history():
    try:
        authToken = request.cookies.get('authToken')
        if authToken:
            db = dbmethods()
            user = db.verify_auth(hashlib.sha256(authToken.encode("utf-8")).hexdigest())
            if user:
                history = db.get_order_history(user[0][0])
                db.close_connection()
                return jsonify(history), 200
            else:
                db.close_connection()
                return jsonify({"message": "User verification failed"}), 401
        else:
            return jsonify({"message": "Authentication required"}), 401
    except Exception as e:
        logger.error("Error retrieving order history: %s", e)
        return jsonify({"message": "Internal Server Error"}), 500

# Logout endpoint
@app.route('/users/logout', methods=['POST'])
def logout():
    try:
        authToken = request.cookies.get('authToken')
        if authToken:
            db = dbmethods()
            user = db.verify_auth(hashlib.sha256(authToken.encode("utf-8")).hexdigest())
            if user:
                db.update_auth_token(user[0][0], None)
                db.close_connection()
                response = make_response(jsonify({"message": "User logged out successfully"}))
                response.set_cookie(key='authToken', value='', expires=0)
                return response, 200
            else:
                db.close_connection()
                return jsonify({"message": "User verification failed"}), 401
        else:
            return jsonify({"message": "Not logged in"}), 400
    except Exception as e:
        logger.error("Error logging out: %s", e)
        return jsonify({"message": "Internal Server Error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)