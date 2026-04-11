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

def insert_all_data():
    conn = connect_db()
    cursor = conn.cursor()
    
    print("🚀 Starting to insert sample data...")
    
    try:
        # 1. Insert Categories
        print("📁 Inserting categories...")
        categories = ['Electronics', 'Clothing', 'Books', 'Home & Kitchen', 'Sports', 
                      'Toys', 'Beauty', 'Automotive', 'Jewelry', 'Health']
        category_ids = []
        for cat in categories:
            try:
                cursor.execute("INSERT INTO categories (name) VALUES (%s)", (cat,))
                category_ids.append(cursor.lastrowid)
            except mysql.connector.IntegrityError:
                # Category already exists, fetch its ID
                cursor.execute("SELECT category_id FROM categories WHERE name = %s", (cat,))
                result = cursor.fetchone()
                if result:
                    category_ids.append(result[0])
        
        print(f"   ✓ Categories ready: {len(category_ids)}")
        
        # 2. Fetch existing products or insert new ones (up to 1000 total)
        print("📦 Checking existing products...")
        cursor.execute("SELECT product_id FROM products")
        product_ids = [row[0] for row in cursor.fetchall()]
        existing_count = len(product_ids)
        
        if existing_count >= 1000:
            print(f"   ℹ️  Already have {existing_count} products. Skipping product insertion.")
        else:
            needed = 1000 - existing_count
            print(f"   Found {existing_count} existing products. Inserting {needed} more...")
            inserted = 0
            attempts = 0
            while inserted < needed and attempts < needed * 2:
                try:
                    cursor.execute(
                        "INSERT INTO products (sku, name, description, category_id) VALUES (%s, %s, %s, %s)",
                        (fake.unique.bothify(text='SKU-####-????'), 
                         fake.catch_phrase(), 
                         fake.text(max_nb_chars=200),
                         random.choice(category_ids))
                    )
                    product_ids.append(cursor.lastrowid)
                    inserted += 1
                    if inserted % 100 == 0:
                        print(f"   ✓ {existing_count + inserted} total products")
                except (mysql.connector.IntegrityError, mysql.connector.Error):
                    pass
                attempts += 1
            print(f"   ✓ Total products now: {len(product_ids)}")
        
        # 3. Fetch existing customers or insert new ones (up to 1500 total)
        print("👤 Checking existing customers...")
        cursor.execute("SELECT customer_id FROM customers")
        customer_ids = [row[0] for row in cursor.fetchall()]
        existing_count = len(customer_ids)
        
        if existing_count >= 1500:
            print(f"   ℹ️  Already have {existing_count} customers. Skipping customer insertion.")
        else:
            needed = 1500 - existing_count
            print(f"   Found {existing_count} existing customers. Inserting {needed} more...")
            inserted = 0
            attempts = 0
            while inserted < needed and attempts < needed * 2:
                try:
                    cursor.execute(
                        "INSERT INTO customers (email, password, first_name, last_name, phone) VALUES (%s, %s, %s, %s, %s)",
                        (fake.unique.email(),
                         fake.password(length=12),
                         fake.first_name(), 
                         fake.last_name(),
                         fake.phone_number())
                    )
                    customer_ids.append(cursor.lastrowid)
                    inserted += 1
                    if inserted % 200 == 0:
                        print(f"   ✓ {existing_count + inserted} total customers")
                except (mysql.connector.IntegrityError, mysql.connector.Error):
                    pass
                attempts += 1
            print(f"   ✓ Total customers now: {len(customer_ids)}")
        
        # 4. Fetch existing sellers or insert new ones (up to 200 total)
        print("🏪 Checking existing sellers...")
        cursor.execute("SELECT seller_id FROM sellers")
        seller_ids = [row[0] for row in cursor.fetchall()]
        existing_count = len(seller_ids)
        
        if existing_count >= 200:
            print(f"   ℹ️  Already have {existing_count} sellers. Skipping seller insertion.")
        else:
            needed = 200 - existing_count
            print(f"   Found {existing_count} existing sellers. Inserting {needed} more...")
            inserted = 0
            attempts = 0
            while inserted < needed and attempts < needed * 2:
                try:
                    cursor.execute(
                        "INSERT INTO sellers (email, name, phone) VALUES (%s, %s, %s)",
                        (fake.unique.company_email(),
                         fake.company(), 
                         fake.phone_number())
                    )
                    seller_ids.append(cursor.lastrowid)
                    inserted += 1
                    if inserted % 50 == 0:
                        print(f"   ✓ {existing_count + inserted} total sellers")
                except (mysql.connector.IntegrityError, mysql.connector.Error) as e:
                    pass
                attempts += 1
            print(f"   ✓ Total sellers now: {len(seller_ids)}")
        
        # Ensure we have minimum data to continue
        if not product_ids or not customer_ids or not seller_ids:
            print("❌ Error: Not enough base data (products, customers, or sellers). Please check your database.")
            conn.close()
            return
        
        # 5. Insert Seller Products (1500 seller-product mappings)
        print("🔗 Inserting seller-product mappings...")
        seller_product_ids = []
        for i in range(1500):
            try:
                cursor.execute(
                    "INSERT INTO seller_products (seller_id, product_id, price, stock) VALUES (%s, %s, %s, %s)",
                    (random.choice(seller_ids),
                     random.choice(product_ids),
                     round(random.uniform(5.0, 500.0), 2),
                     random.randint(0, 1000))
                )
                seller_product_ids.append(cursor.lastrowid)
                if (i + 1) % 200 == 0:
                    print(f"   ✓ {i + 1} seller-products inserted")
            except (mysql.connector.IntegrityError, mysql.connector.Error):
                continue
        print(f"   ✓ Total seller-products: {len(seller_product_ids)}")
        
        if not seller_product_ids:
            print("❌ Error: No seller products created. Cannot proceed with orders.")
            conn.close()
            return
        
        # 6. Insert Orders (1000 orders)
        print("🛒 Inserting 1000 orders...")
        order_ids = []
        statuses = ['pending', 'processing', 'shipped', 'delivered', 'cancelled']
        for i in range(1000):
            try:
                total = round(random.uniform(10.0, 1000.0), 2)
                cursor.execute(
                    "INSERT INTO orders (customer_id, status, total_amount) VALUES (%s, %s, %s)",
                    (random.choice(customer_ids),
                     random.choice(statuses),
                     total)
                )
                order_ids.append(cursor.lastrowid)
                if (i + 1) % 100 == 0:
                    print(f"   ✓ {i + 1} orders inserted")
            except mysql.connector.Error:
                continue
        print(f"   ✓ Total orders: {len(order_ids)}")
        
        if not order_ids:
            print("❌ Error: No orders created. Skipping order items and payments.")
            conn.commit()
            conn.close()
            return
        
        # 7. Insert Order Items (2000 order items)
        print("📋 Inserting 2000 order items...")
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
            except mysql.connector.Error:
                continue
        print(f"   ✓ Total order items: {order_items_count}")
        
        # 8. Insert Payments (750 payments)
        print("💳 Inserting 750 payments...")
        payment_methods = ['credit_card', 'debit_card', 'upi', 'net_banking', 'wallet']
        payment_statuses = ['pending', 'completed', 'failed', 'refunded']
        payments_count = 0
        for i in range(750):
            try:
                cursor.execute(
                    "INSERT INTO payments (order_id, method, status, amount) VALUES (%s, %s, %s, %s)",
                    (random.choice(order_ids),
                     random.choice(payment_methods),
                     random.choice(payment_statuses),
                     round(random.uniform(10.0, 1000.0), 2))
                )
                payments_count += 1
                if (i + 1) % 100 == 0:
                    print(f"   ✓ {i + 1} payments inserted")
            except mysql.connector.Error:
                continue
        print(f"   ✓ Total payments: {payments_count}")
        
        conn.commit()
        print("\n✅ Sample data insertion completed successfully!")
        print(f"📊 Final Summary:")
        print(f"   • Categories: {len(category_ids)}")
        print(f"   • Products: {len(product_ids)}")
        print(f"   • Customers: {len(customer_ids)}")
        print(f"   • Sellers: {len(seller_ids)}")
        print(f"   • Seller Products: {len(seller_product_ids)}")
        print(f"   • Orders: {len(order_ids)}")
        print(f"   • Order Items: {order_items_count}")
        print(f"   • Payments: {payments_count}")
        
    except mysql.connector.Error as err:
        print(f"\n❌ Database Error: {err}")
        conn.rollback()
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    try:
        confirm = input("⚠️  This will insert 6000+ records into your database. Continue? (yes/no): ")
        if confirm.lower() in ['yes', 'y']:
            insert_all_data()
        else:
            print("❌ Operation cancelled.")
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user.")
    except Exception as e:
        print(f"❌ Error: {e}")
