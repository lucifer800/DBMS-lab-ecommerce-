import mysql.connector
from faker import Faker
import random

fake = Faker()

def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",               
        password="Janvistar800",  
        database="ecommerce_db"
    )

# Realistic product names by category
PRODUCTS = {
    'Electronics': [
        'Samsung Galaxy S23', 'iPhone 15 Pro', 'MacBook Air M2', 'Dell XPS 15', 
        'Sony WH-1000XM5 Headphones', 'iPad Air', 'Apple Watch Series 9',
        'Samsung 55" QLED TV', 'Canon EOS R6', 'PlayStation 5', 'Xbox Series X',
        'Bose SoundLink Speaker', 'Kindle Paperwhite', 'GoPro Hero 12',
        'Ring Video Doorbell', 'Nest Thermostat', 'Logitech MX Master Mouse'
    ],
    'Clothing': [
        'Levi\'s 501 Jeans', 'Nike Air Max Sneakers', 'Adidas Hoodie',
        'Calvin Klein T-Shirt', 'Tommy Hilfiger Polo', 'Ray-Ban Sunglasses',
        'North Face Jacket', 'Puma Track Pants', 'H&M Summer Dress',
        'Zara Blazer', 'Uniqlo Sweater', 'Gap Denim Jacket', 'Vans Old Skool'
    ],
    'Books': [
        'Atomic Habits - James Clear', '1984 - George Orwell', 
        'Harry Potter Box Set', 'The Alchemist - Paulo Coelho',
        'Sapiens - Yuval Harari', 'Educated - Tara Westover',
        'Becoming - Michelle Obama', 'Think Like a Monk - Jay Shetty'
    ],
    'Home & Kitchen': [
        'Instant Pot Duo', 'Ninja Air Fryer', 'KitchenAid Stand Mixer',
        'Dyson V15 Vacuum', 'Nespresso Coffee Machine', 'Cuisinart Blender',
        'Le Creuset Dutch Oven', 'OXO Good Grips Knife Set',
        'Bedding Set Queen Size', 'Bath Towel Set', 'Throw Pillows'
    ],
    'Sports': [
        'Yoga Mat Premium', 'Dumbbells Set 20kg', 'Resistance Bands',
        'Running Shoes Brooks', 'Gym Bag Nike', 'Water Bottle 1L',
        'Fitness Tracker Fitbit', 'Tennis Racket Wilson', 'Basketball Spalding'
    ],
    'Toys': [
        'LEGO Star Wars Set', 'Barbie Dreamhouse', 'Hot Wheels Track',
        'Nerf Blaster', 'Play-Doh Mega Pack', 'Monopoly Board Game',
        'Nintendo Switch Games', 'Action Figures Marvel'
    ],
    'Beauty': [
        'Maybelline Mascara', 'L\'Oreal Face Cream', 'Neutrogena Sunscreen',
        'CeraVe Moisturizer', 'The Ordinary Serum', 'NYX Makeup Palette',
        'Olaplex Hair Treatment', 'Dove Body Wash', 'Gillette Razor Set'
    ],
    'Automotive': [
        'Michelin Tires Set', 'Bosch Car Battery', 'Car Phone Mount',
        'Dash Cam 4K', 'Car Vacuum Cleaner', 'Motor Oil 5W-30',
        'Windshield Wipers', 'Car Air Freshener', 'Jump Starter Kit'
    ],
    'Jewelry': [
        'Sterling Silver Necklace', 'Diamond Stud Earrings', 'Gold Bracelet',
        'Pandora Charm', 'Men\'s Watch Fossil', 'Wedding Band Set',
        'Pearl Pendant', 'Engagement Ring'
    ],
    'Health': [
        'Multivitamin Gummies', 'Protein Powder Whey', 'Omega-3 Fish Oil',
        'Vitamin D3 Supplement', 'Probiotic Capsules', 'Collagen Peptides',
        'First Aid Kit', 'Blood Pressure Monitor', 'Thermometer Digital'
    ]
}

print("⚠️  WARNING: This will DELETE all existing data and insert fresh realistic data!")
confirm = input("Continue? (yes/no): ")

if confirm.lower() not in ['yes', 'y']:
    print("❌ Operation cancelled.")
    exit()

conn = connect_db()
cursor = conn.cursor()

print("\n🗑️  Clearing existing data...")
cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
cursor.execute("TRUNCATE TABLE payments")
cursor.execute("TRUNCATE TABLE order_items")
cursor.execute("TRUNCATE TABLE orders")
cursor.execute("TRUNCATE TABLE seller_products")
cursor.execute("TRUNCATE TABLE products")
cursor.execute("TRUNCATE TABLE sellers")
cursor.execute("TRUNCATE TABLE customers")
cursor.execute("TRUNCATE TABLE categories")
cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
print("   ✓ All tables cleared")

print("\n🚀 Inserting realistic e-commerce data...")

# 1. Categories
print("📁 Inserting categories...")
category_map = {}
for cat in PRODUCTS.keys():
    cursor.execute("INSERT INTO categories (name) VALUES (%s)", (cat,))
    category_map[cat] = cursor.lastrowid
print(f"   ✓ {len(category_map)} categories inserted")

# 2. Products
print("📦 Inserting products...")
product_ids = []
for category, products in PRODUCTS.items():
    for product_name in products:
        sku = fake.unique.bothify(text='SKU-####-????')
        desc = f"High-quality {product_name}. {fake.sentence()}"
        cursor.execute(
            "INSERT INTO products (sku, name, description, category_id) VALUES (%s, %s, %s, %s)",
            (sku, product_name, desc, category_map[category])
        )
        product_ids.append(cursor.lastrowid)

# Add more products to reach 1000
while len(product_ids) < 1000:
    cat = random.choice(list(PRODUCTS.keys()))
    base_product = random.choice(PRODUCTS[cat])
    variant = random.choice(['Pro', 'Plus', 'Premium', 'Deluxe', 'Standard', 'Mini'])
    color = random.choice(['Black', 'White', 'Blue', 'Red', 'Silver'])
    product_name = f"{base_product} - {variant} {color}"
    sku = fake.unique.bothify(text='SKU-####-????')
    desc = f"{product_name}. {fake.sentence()}"
    try:
        cursor.execute(
            "INSERT INTO products (sku, name, description, category_id) VALUES (%s, %s, %s, %s)",
            (sku, product_name, desc, category_map[cat])
        )
        product_ids.append(cursor.lastrowid)
    except:
        pass

print(f"   ✓ {len(product_ids)} products inserted")

# 3. Customers
print("👤 Inserting 1500 customers...")
customer_ids = []
for i in range(1500):
    cursor.execute(
        "INSERT INTO customers (email, first_name, last_name, phone) VALUES (%s, %s, %s, %s)",
        (fake.unique.email(), fake.first_name(), 
         fake.last_name(), fake.phone_number())
    )
    customer_ids.append(cursor.lastrowid)
print(f"   ✓ {len(customer_ids)} customers inserted")

# 4. Sellers
print("🏪 Inserting 200 sellers...")
seller_ids = []
for i in range(200):
    cursor.execute(
        "INSERT INTO sellers (email, name, phone) VALUES (%s, %s, %s)",
        (fake.unique.company_email(), fake.company(), 
         fake.phone_number())
    )
    seller_ids.append(cursor.lastrowid)
print(f"   ✓ {len(seller_ids)} sellers inserted")

# 5. Seller Products
print("🔗 Inserting seller-product mappings...")
seller_product_ids = []
for product_id in product_ids:
    # Each product sold by 1-3 sellers
    num_sellers = random.randint(1, 3)
    for _ in range(num_sellers):
        seller = random.choice(seller_ids)
        price = round(random.uniform(10, 2000), 2)
        stock = random.randint(0, 500)
        try:
            cursor.execute(
                "INSERT INTO seller_products (seller_id, product_id, price, stock) VALUES (%s, %s, %s, %s)",
                (seller, product_id, price, stock)
            )
            seller_product_ids.append(cursor.lastrowid)
        except:
            pass
print(f"   ✓ {len(seller_product_ids)} seller-products inserted")

# 6. Orders
print("🛒 Inserting 1000 orders...")
order_ids = []
statuses = ['pending', 'processing', 'shipped', 'delivered', 'cancelled']
for i in range(1000):
    total = round(random.uniform(50, 5000), 2)
    cursor.execute(
        "INSERT INTO orders (customer_id, status, total_amount) VALUES (%s, %s, %s)",
        (random.choice(customer_ids), random.choice(statuses), total)
    )
    order_ids.append(cursor.lastrowid)
print(f"   ✓ {len(order_ids)} orders inserted")

# 7. Order Items
print("📋 Inserting order items...")
order_items_count = 0
for order_id in order_ids:
    # Each order has 1-5 items
    num_items = random.randint(1, 5)
    for _ in range(num_items):
        sp = random.choice(seller_product_ids)
        qty = random.randint(1, 3)
        price = round(random.uniform(10, 500), 2)
        cursor.execute(
            "INSERT INTO order_items (order_id, seller_product_id, quantity, price) VALUES (%s, %s, %s, %s)",
            (order_id, sp, qty, price)
        )
        order_items_count += 1
print(f"   ✓ {order_items_count} order items inserted")

# 8. Payments
print("💳 Inserting payments...")
methods = ['credit_card', 'debit_card', 'upi', 'net_banking', 'wallet']
statuses = ['pending', 'completed', 'failed', 'refunded']
payments_count = 0
for order_id in order_ids:
    # 75% orders have payments
    if random.random() < 0.75:
        cursor.execute(
            "INSERT INTO payments (order_id, method, status, amount) VALUES (%s, %s, %s, %s)",
            (order_id, random.choice(methods), random.choice(statuses),
             round(random.uniform(50, 5000), 2))
        )
        payments_count += 1
print(f"   ✓ {payments_count} payments inserted")

conn.commit()
print("\n✅ Realistic e-commerce data insertion completed!")
print(f"📊 Final Summary:")
print(f"   • Categories: {len(category_map)}")
print(f"   • Products: {len(product_ids)} (realistic names!)")
print(f"   • Customers: {len(customer_ids)}")
print(f"   • Sellers: {len(seller_ids)}")
print(f"   • Seller Products: {len(seller_product_ids)}")
print(f"   • Orders: {len(order_ids)}")
print(f"   • Order Items: {order_items_count}")
print(f"   • Payments: {payments_count}")
conn.close()
