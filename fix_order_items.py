import mysql.connector
from faker import Faker
import random

fake = Faker()

def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",               
        password="12345678",  
        database="ecommerce_db"
    )

conn = connect_db()
cursor = conn.cursor()

print("🔧 Fixing order items...")

# Get all order IDs and seller_product IDs
cursor.execute("SELECT order_id FROM orders")
order_ids = [row[0] for row in cursor.fetchall()]

cursor.execute("SELECT seller_product_id FROM seller_products")
seller_product_ids = [row[0] for row in cursor.fetchall()]

if not order_ids or not seller_product_ids:
    print("❌ No orders or seller products found!")
    conn.close()
    exit()

print(f"Found {len(order_ids)} orders and {len(seller_product_ids)} seller products")

# Insert 2000 order items
order_items_count = 0
for i in range(2000):
    try:
        qty = random.randint(1, 5)
        sp_id = random.choice(seller_product_ids)
        cursor.execute(
            "SELECT price FROM seller_products WHERE seller_product_id = %s",
            (sp_id,),
        )
        price = cursor.fetchone()[0]
        line_total = round(price * qty, 2)
        cursor.execute(
            "INSERT INTO order_items (order_id, seller_product_id, quantity, unit_price, line_total) VALUES (%s, %s, %s, %s, %s)",
            (random.choice(order_ids),
             sp_id,
             qty,
             price,
             line_total)
        )
        order_items_count += 1
        if (i + 1) % 200 == 0:
            print(f"   ✓ {i + 1} order items inserted")
    except Exception as e:
        print(f"Error: {e}")
        continue

conn.commit()
print(f"\n✅ Successfully inserted {order_items_count} order items!")
conn.close()
