import sqlite3
from datetime import datetime, timedelta
import random

def setup_ecommerce_database(db_name="ecommerce_demand.db"):
    # Connect to SQLite database (creates it if it doesn't exist)
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # 1. Create Products Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Products (
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT,
            category TEXT,
            unit_price REAL,
            supplier_lead_time_days INTEGER
        )
    ''')

    # 2. Create Transactions Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Transactions (
            transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATETIME,
            customer_id INTEGER,
            product_id INTEGER,
            quantity_sold INTEGER,
            total_revenue REAL,
            FOREIGN KEY (product_id) REFERENCES Products (product_id)
        )
    ''')

    # 3. Create Inventory Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Inventory (
            inventory_id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            stock_on_hand INTEGER,
            safety_stock_threshold INTEGER,
            last_restock_date DATETIME,
            FOREIGN KEY (product_id) REFERENCES Products (product_id)
        )
    ''')

    # Insert Sample Products
    products = [
        ("Wireless Mouse", "Electronics", 25.00, 5),
        ("Mechanical Keyboard", "Electronics", 75.00, 7),
        ("Running Shoes", "Apparel", 60.00, 10),
        ("Cotton T-Shirt", "Apparel", 15.00, 4),
        ("Coffee Maker", "Home", 45.00, 6)
    ]
    cursor.executemany("INSERT OR IGNORE INTO Products (product_name, category, unit_price, supplier_lead_time_days) VALUES (?, ?, ?, ?)", products)

    # Insert Sample Inventory
    inventory = [
        (1, 150, 30, "2026-10-01"),
        (2, 45, 15, "2026-09-15"),
        (3, 80, 20, "2026-10-10"),
        (4, 300, 50, "2026-10-05"),
        (5, 25, 10, "2026-09-20")
    ]
    cursor.executemany("INSERT OR IGNORE INTO Inventory (product_id, stock_on_hand, safety_stock_threshold, last_restock_date) VALUES (?, ?, ?, ?)", inventory)

    # Insert Sample Transactions (Simulating 60 days of sales)
    base_date = datetime.now() - timedelta(days=60)
    for i in range(1, 200):
        t_date = (base_date + timedelta(days=random.randint(0, 59), hours=random.randint(8, 20))).strftime("%Y-%m-%d %H:%M:%S")
        cust_id = random.randint(1001, 1050)
        prod_id = random.randint(1, 5)
        qty = random.randint(1, 4)
        
        # Get product price to calculate revenue (mocking lookup)
        prices = {1: 25.00, 2: 75.00, 3: 60.00, 4: 15.00, 5: 45.00}
        revenue = round(qty * prices[prod_id], 2)

        cursor.execute('''
            INSERT INTO Transactions (date, customer_id, product_id, quantity_sold, total_revenue)
            VALUES (?, ?, ?, ?, ?)
        ''', (t_date, cust_id, prod_id, qty, revenue))

    conn.commit()
    conn.close()
    print("Database `ecommerce_demand.db` created and populated successfully!")

if __name__ == "__main__":
    setup_ecommerce_database()