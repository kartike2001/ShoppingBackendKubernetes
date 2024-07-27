import psycopg2
import helpers

# This class contains all the methods that interact with the database
class dbmethods:
    def __init__(self):
        self.connection = psycopg2.connect(
            database="shopping_cart", user="root", password="password", host="postgres", port="5432")
        self.cur = self.connection.cursor()
        self.cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255),
                email VARCHAR(255),
                password VARCHAR(255),
                authToken VARCHAR(255)
            )
        ''')
        self.cur.execute('''
            CREATE TABLE IF NOT EXISTS cart (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                itemName VARCHAR(255),
                itemPrice NUMERIC(10, 2),
                itemQuantity INTEGER,
                bought BOOLEAN
            )
        ''')
        self.cur.execute('''
            CREATE TABLE IF NOT EXISTS order_sessions (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                orderDate TIMESTAMP
            )
        ''')
        self.cur.execute('''
            CREATE TABLE IF NOT EXISTS order_history (
                id SERIAL PRIMARY KEY,
                session_id INTEGER REFERENCES order_sessions(id),
                itemName VARCHAR(255),
                itemPrice NUMERIC(10, 2),
                itemQuantity INTEGER
            )
        ''')
        self.connection.commit()

    # Create a new user
    def create_user(self, name, email, hashedPass, authToken):
        self.cur.execute(
            "INSERT INTO users (name, email, password, authToken) VALUES (%s, %s, %s, %s)",
            (name, email, hashedPass, authToken))
        self.connection.commit()

    # Get user by email
    def get_user_by_email(self, email):
        self.cur.execute(
            "SELECT * FROM users WHERE email = %s", (email,))
        return self.cur.fetchone()

    # Verify login
    def verify_login(self, email):
        self.cur.execute(
            "SELECT * FROM users WHERE email = %s", (email,))
        return self.cur.fetchall()

    # Verify auth token
    def verify_auth(self, authToken):
        self.cur.execute(
            "SELECT * FROM users WHERE authToken = %s", (authToken,))
        return self.cur.fetchall()

    # Update auth token
    def update_auth_token(self, user_id, authToken):
        self.cur.execute(
            "UPDATE users SET authToken = %s WHERE id = %s", (authToken, user_id))
        self.connection.commit()

    # Add item to cart
    def add_to_cart(self, user_id, itemName, itemPrice, itemQuantity):
        self.cur.execute(
            "INSERT INTO cart (user_id, itemName, itemPrice, itemQuantity, bought) VALUES (%s, %s, %s, %s, %s)",
            (user_id, itemName, itemPrice, itemQuantity, False))
        self.connection.commit()

    # Get a single item
    def get_cart_item(self, user_id, itemName, itemPrice):
        self.cur.execute(
            """
            SELECT * FROM cart
            WHERE user_id = %s AND itemName = %s AND itemPrice = %s AND bought = False
            """,
            (user_id, itemName, itemPrice))
        return self.cur.fetchall()

    # View cart
    def view_cart(self, user_id):
        self.cur.execute(
            "SELECT name FROM users WHERE id = %s", (user_id,))
        user = self.cur.fetchone()

        self.cur.execute(
            """
            SELECT id, itemName, itemPrice, itemQuantity, 
                   SUM(itemPrice * itemQuantity) OVER (PARTITION BY user_id) as total
            FROM cart 
            WHERE user_id = %s AND bought = False
            """,
            (user_id,))

        rows = self.cur.fetchall()

        if rows:
            total = float(rows[0][4])
        else:
            total = 0.0

        items = [{"id": row[0], "itemName": row[1], "itemPrice": float(row[2]), "itemQuantity": row[3]} for row in rows]

        return {"userName": user[0], "userID": user_id, "items": items, "total": total}

    # Remove from cart
    def remove_from_cart(self, cart_id):
        self.cur.execute(
            "DELETE FROM cart WHERE id = %s", (cart_id,))
        self.connection.commit()

    # Update cart quantity
    def update_cart_quantity(self, cart_id, itemQuantity):
        self.cur.execute(
            "UPDATE cart SET itemQuantity = %s WHERE id = %s",
            (itemQuantity, cart_id)
        )
        self.connection.commit()

    # Checkout entire cart
    def checkout_entire_cart(self, user_id):
        self.cur.execute(
            "SELECT * FROM cart WHERE user_id = %s AND bought = False", (user_id,))
        items = self.cur.fetchall()
        self.cur.execute(
            "INSERT INTO order_sessions (user_id, orderDate) VALUES (%s, NOW()) RETURNING id", (user_id,))
        session_id = self.cur.fetchone()[0]
        for item in items:
            self.cur.execute(
                "INSERT INTO order_history (session_id, itemName, itemPrice, itemQuantity) VALUES (%s, %s, %s, %s)",
                (session_id, item[2], item[3], item[4]))
        self.cur.execute(
            "UPDATE cart SET bought = True WHERE user_id = %s AND bought = False", (user_id,))
        self.connection.commit()

    # Get order history
    def get_order_history(self, user_id):
        self.cur.execute(
            "SELECT name FROM users WHERE id = %s", (user_id,))
        user = self.cur.fetchone()
        self.cur.execute(
            """
            SELECT os.id, os.orderDate, oh.itemName, oh.itemPrice, oh.itemQuantity
            FROM order_sessions os JOIN order_history oh ON os.id = oh.session_id 
            WHERE os.user_id = %s ORDER BY os.orderDate DESC
            """,
            (user_id,))
        history = self.cur.fetchall()
        sessions = {}
        for record in history:
            session_id = record[0]
            if session_id not in sessions:
                sessions[session_id] = {
                    "orderDate": record[1].strftime('%Y-%m-%d %H:%M:%S'),
                    "items": []
                }
            sessions[session_id]["items"].append({
                "itemName": record[2],
                "itemPrice": float(record[3]),
                "itemQuantity": record[4]
            })
        return {"userName": user[0], "userID": user_id, "sessions": sessions}

    def close_connection(self):
        self.connection.close()
