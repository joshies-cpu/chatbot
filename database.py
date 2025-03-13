import sqlite3

# Database initialization
def init_db():
    conn = sqlite3.connect("chatbot.db")
    cursor = conn.cursor()

    # Create a table for user carts with a primary key
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cart (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            product_name TEXT
        )
    ''')

    # Create a table for user preferences
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_preferences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            category TEXT,
            brand TEXT,
            min_price FLOAT,
            max_price FLOAT
        )
    ''')

    # Create a table for purchase history
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS purchase_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            product_name TEXT,
            purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create a table for order details (NEW for order tracking support)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS order_details (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER,
            user_id TEXT,
            product_name TEXT,
            status TEXT,
            delivery_date TEXT
        )
    ''')

    conn.commit()
    conn.close()


# Add an item to the user's cart
def add_to_cart(user_id, product_name):
    try:
        with sqlite3.connect("chatbot.db") as conn:
            cursor = conn.cursor()
            
            # Check if item is already in cart
            cursor.execute("SELECT COUNT(*) FROM cart WHERE user_id = ? AND product_name = ?", (user_id, product_name))
            if cursor.fetchone()[0] == 0:
                cursor.execute("INSERT INTO cart (user_id, product_name) VALUES (?, ?)", (user_id, product_name))
                conn.commit()
    except Exception as e:
        print(f"Error adding item to cart: {e}")

# Remove an item from the user's cart
def remove_from_cart(user_id, product_name):
    try:
        with sqlite3.connect("chatbot.db") as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM cart WHERE user_id = ? AND product_name = ?", (user_id, product_name))
            conn.commit()
    except Exception as e:
        print(f"Error removing item from cart: {e}")

# View the items in the user's cart
def view_cart(user_id):
    try:
        with sqlite3.connect("chatbot.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT product_name FROM cart WHERE user_id = ?", (user_id,))
            return [row[0] for row in cursor.fetchall()]
    except Exception as e:
        print(f"Error viewing cart: {e}")
        return []

# Clear the user's cart
def clear_cart(user_id):
    try:
        with sqlite3.connect("chatbot.db") as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM cart WHERE user_id = ?", (user_id,))
            conn.commit()
    except Exception as e:
        print(f"Error clearing cart: {e}")

# Add user preferences
def add_user_preference(user_id, category=None, brand=None, min_price=None, max_price=None):
    try:
        with sqlite3.connect("chatbot.db") as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO user_preferences (user_id, category, brand, min_price, max_price)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, category, brand, min_price, max_price))
            conn.commit()
    except Exception as e:
        print(f"Error adding user preferences: {e}")

# Get user preferences
def get_user_preferences(user_id):
    try:
        with sqlite3.connect("chatbot.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT category, brand, min_price, max_price FROM user_preferences WHERE user_id = ?", (user_id,))
            return cursor.fetchall()
    except Exception as e:
        print(f"Error retrieving user preferences: {e}")
        return []

# Add purchase history
def add_purchase(user_id, product_name):
    try:
        with sqlite3.connect("chatbot.db") as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO purchase_history (user_id, product_name)
                VALUES (?, ?)
            """, (user_id, product_name))
            conn.commit()
    except Exception as e:
        print(f"Error adding purchase history: {e}")

# Get purchase history
def get_purchase_history(user_id):
    try:
        with sqlite3.connect("chatbot.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT product_name FROM purchase_history WHERE user_id = ?", (user_id,))
            return [row[0] for row in cursor.fetchall()]
    except Exception as e:
        print(f"Error retrieving purchase history: {e}")
        return []

# Add order details (NEW for improved order tracking)
def add_order_details(order_id, user_id, product_name, status, delivery_date):
    try:
        with sqlite3.connect("chatbot.db") as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO order_details (order_id, user_id, product_name, status, delivery_date)
                VALUES (?, ?, ?, ?, ?)
            """, (order_id, user_id, product_name, status, delivery_date))
            conn.commit()
    except Exception as e:
        print(f"Error adding order details: {e}")

# Get order details (NEW for improved order tracking)
def get_order_details(order_id):
    try:
        with sqlite3.connect("chatbot.db") as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT product_name, status, delivery_date 
                FROM order_details 
                WHERE order_id = ?
            """, (order_id,))
            return cursor.fetchone()
    except Exception as e:
        print(f"Error retrieving order details: {e}")
        return None

# Initialize the database when this file is executed
if __name__ == "__main__":
    init_db()
