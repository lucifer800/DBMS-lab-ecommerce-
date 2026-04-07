import mysql.connector
from mysql.connector import Error
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

def add_product():
    conn = connect_db()
    cursor = conn.cursor()
    name = input("Enter product name: ")
    sku = input("Enter SKU code: ")
    category_id = input("Enter category ID: ")
    desc = input("Enter description: ")
    query = "INSERT INTO products (sku, name, description, category_id) VALUES (%s, %s, %s, %s)"
    cursor.execute(query, (sku, name, desc, category_id))
    conn.commit()
    print("Product added successfully!")
    conn.close()

def view_products():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT product_id, name, category_id, created_at FROM products")
    for row in cursor.fetchall():
        print(row)
    conn.close()

def update_product():
    conn = connect_db()
    cursor = conn.cursor()
    pid = input("Enter product ID to update: ")
    new_name = input("Enter new product name: ")
    query = "UPDATE products SET name = %s WHERE product_id = %s"
    cursor.execute(query, (new_name, pid))
    conn.commit()
    print("Product updated successfully!")
    conn.close()

def delete_product():
    conn = connect_db()
    cursor = conn.cursor()
    pid = input("Enter product ID to delete: ")
    query = "DELETE FROM products WHERE product_id = %s"
    cursor.execute(query, (pid,))
    conn.commit()
    print("Product deleted successfully!")
    conn.close()

def most_selling_products():
    conn = connect_db()
    cursor = conn.cursor()
    query = """
        SELECT p.name, SUM(oi.quantity) AS sold
        FROM order_items oi
        JOIN seller_products sp ON oi.seller_product_id = sp.seller_product_id
        JOIN products p ON sp.product_id = p.product_id
        GROUP BY p.product_id
        ORDER BY sold DESC
        LIMIT 10;
    """
    cursor.execute(query)
    print("\n🏆 Top Selling Products:")
    for name, sold in cursor.fetchall():
        print(f"{name}: {sold} sold")
    conn.close()

def most_frequent_customers():
    conn = connect_db()
    cursor = conn.cursor()
    query = """
        SELECT c.first_name, COUNT(o.order_id) AS total_orders
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
        GROUP BY c.customer_id
        ORDER BY total_orders DESC
        LIMIT 10;
    """
    cursor.execute(query)
    print("\n👥 Most Frequent Customers:")
    for name, total in cursor.fetchall():
        print(f"{name}: {total} orders")
    conn.close()

def track_inventory():
    conn = connect_db()
    cursor = conn.cursor()
    query = """
        SELECT s.name AS seller, p.name AS product, sp.stock
        FROM seller_products sp
        JOIN sellers s ON sp.seller_id = s.seller_id
        JOIN products p ON sp.product_id = p.product_id
        ORDER BY sp.stock ASC;
    """
    cursor.execute(query)
    print("\n📦 Inventory Status:")
    for seller, product, stock in cursor.fetchall():
        print(f"Seller: {seller} | Product: {product} | Stock: {stock}")
    conn.close()

def process_orders():
    conn = connect_db()
    cursor = conn.cursor()
    print("\nPending / Processing Orders:")
    cursor.execute("SELECT order_id, status, total_amount FROM orders WHERE status IN ('pending','processing');")
    rows = cursor.fetchall()
    if not rows:
        print("No pending orders.")
    else:
        for oid, status, total in rows:
            print(f"Order {oid} | Status: {status} | Total: {total}")
            update = input("Mark this order as 'shipped' or 'cancelled'? (s/c/skip): ").lower()
            if update == 's':
                cursor.execute("UPDATE orders SET status='shipped' WHERE order_id=%s", (oid,))
            elif update == 'c':
                cursor.execute("UPDATE orders SET status='cancelled' WHERE order_id=%s", (oid,))
        conn.commit()
        print("Order statuses updated.")
    conn.close()

def payment_status():
    conn = connect_db()
    cursor = conn.cursor()
    query = """
        SELECT p.payment_id, o.order_id, p.method, p.status, p.amount
        FROM payments p
        JOIN orders o ON p.order_id = o.order_id
        ORDER BY p.created_at DESC;
    """
    cursor.execute(query)
    print("\n Payment Status:")
    for pid, oid, method, status, amt in cursor.fetchall():
        print(f"Payment ID: {pid} | Order: {oid} | Method: {method} | Status: {status} | Amount: {amt}")
    conn.close()

def menu():
    while True:
        print("\n========== E-COMMERCE MANAGEMENT ==========")
        print("1. Add Product")
        print("2. View Products")
        print("3. Update Product")
        print("4. Delete Product")
        print("5. Most Selling Products")
        print("6. Most Frequent Customers")
        print("7. Track Inventory")
        print("8. Process Orders")
        print("9. View Payment Status")
        print("10. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            add_product()
        elif choice == '2':
            view_products()
        elif choice == '3':
            update_product()
        elif choice == '4':
            delete_product()
        elif choice == '5':
            most_selling_products()
        elif choice == '6':
            most_frequent_customers()
        elif choice == '7':
            track_inventory()
        elif choice == '8':
            process_orders()
        elif choice == '9':
            payment_status()
        elif choice == '10':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Try again!")

if __name__ == "__main__":
    try:
        menu()
    except Error as e:
        print("Database Error:", e)
