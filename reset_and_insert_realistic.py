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

# Realistic product catalog
PRODUCT_CATALOG = {
    'Electronics': [
        'iPhone 15 Pro Max', 'Samsung Galaxy S24', 'MacBook Pro 16"', 'iPad Air', 
        'Sony WH-1000XM5 Headphones', 'AirPods Pro', 'Apple Watch Series 9',
        'Samsung 65" QLED TV', 'LG OLED TV 55"', 'Canon EOS R6 Camera',
        'Sony PlayStation 5', 'Xbox Series X', 'Nintendo Switch OLED',
        'Dell XPS 15 Laptop', 'HP Pavilion Desktop', 'Logitech MX Master 3 Mouse',
        'Bose QuietComfort Earbuds', 'GoPro Hero 12', 'DJI Mini 3 Pro Drone',
        'Kindle Paperwhite', 'iPad Pro 12.9"', 'Samsung Galaxy Tab S9'
    ],
    'Clothing': [
        "Levi's 501 Original Jeans", 'Nike Air Max 90 Sneakers', 'Adidas Ultraboost',
        'North Face Thermoball Jacket', 'Patagonia Fleece Pullover', 'Columbia Rain Jacket',
        'Calvin Klein Cotton T-Shirt', 'Tommy Hilfiger Polo Shirt', 'Ralph Lauren Sweater',
        'Zara Slim Fit Chinos', 'H&M Summer Dress', 'Gap Hoodie',
        'Vans Old Skool Sneakers', 'Converse Chuck Taylor', 'Ray-Ban Aviator Sunglasses',
        'Timberland Boots', 'Puma Track Pants', 'Under Armour Sports Bra'
    ],
    'Books': [
        'Atomic Habits by James Clear', '1984 by George Orwell', 'Sapiens by Yuval Harari',
        'The Alchemist by Paulo Coelho', 'Educated by Tara Westover',
        'Becoming by Michelle Obama', 'Think and Grow Rich', 'Rich Dad Poor Dad',
        'Harry Potter Complete Set', 'The Hobbit by J.R.R. Tolkien',
        'To Kill a Mockingbird', 'The Great Gatsby', 'Pride and Prejudice'
    ],
    'Home & Kitchen': [
        'Instant Pot Duo 7-in-1', 'Ninja Air Fryer XL', 'KitchenAid Stand Mixer',
        'Dyson V15 Cordless Vacuum', 'iRobot Roomba j7+', 'Nespresso Vertuo Coffee Maker',
        'Cuisinart Food Processor', 'Vitamix Blender', 'Le Creuset Dutch Oven',
        'All-Clad Stainless Cookware Set', 'Bedding Comforter Set Queen',
        'Egyptian Cotton Sheet Set', 'Memory Foam Pillow Set', 'Weighted Blanket'
    ],
    'Sports': [
        'Yoga Mat Premium 6mm', 'Adjustable Dumbbells 50lb', 'Resistance Bands Set',
        'Treadmill Folding', 'Exercise Bike Stationary', 'Pull-up Bar Doorway',
        'Fitbit Charge 6', 'Garmin Forerunner 255', 'Hydro Flask Water Bottle',
        'Wilson Tennis Racket', 'Spalding Basketball', 'Nike Soccer Ball',
        'Gym Bag with Shoe Compartment', 'Foam Roller for Recovery'
    ],
    'Toys': [
        'LEGO Star Wars Millennium Falcon', 'LEGO Technic Bugatti', 'Hot Wheels Track Set',
        'Barbie Dreamhouse', 'Nerf Elite Blaster', 'Play-Doh Mega Pack',
        'Monopoly Board Game', 'Uno Card Game', 'Jenga Classic',
        'Nintendo Switch Games - Mario Kart', 'PS5 Game - Spider-Man',
        'Action Figures Marvel Avengers', 'Baby Yoda Plush Toy'
    ],
    'Beauty': [
        'CeraVe Moisturizing Cream', 'The Ordinary Niacinamide Serum', 'Olaplex Hair Treatment',
        'Neutrogena Hydro Boost', 'Maybelline Sky High Mascara', 'NYX Makeup Palette',
        "L'Oreal Paris Face Cream", 'Dove Body Wash', 'Gillette Fusion Razor',
        'Oral-B Electric Toothbrush', 'Crest Whitening Strips', 'Cetaphil Gentle Cleanser'
    ],
    'Automotive': [
        'Michelin Defender Tires (Set of 4)', 'Bosch Car Battery', 'Garmin Dash Cam',
        'Car Phone Mount Magnetic', 'Armor All Car Vacuum', 'Castrol Motor Oil 5W-30',
        'Rain-X Windshield Wipers', 'Meguiars Car Wax Kit', 'Portable Jump Starter',
        'WeatherTech Floor Mats', 'Car Air Freshener Pack'
    ],
    'Jewelry': [
        'Sterling Silver Necklace', '14K Gold Earrings', 'Diamond Stud Earrings 1ct',
        'Pandora Charm Bracelet', 'Fossil Mens Watch', 'Michael Kors Watch',
        'Engagement Ring White Gold', 'Wedding Band Set', 'Pearl Pendant Necklace',
        'Gold Chain Bracelet', 'Birthstone Ring'
    ],
    'Health': [
        'Multivitamin Gummies', 'Whey Protein Powder 5lb', 'Omega-3 Fish Oil 1000mg',
        'Vitamin D3 5000 IU', 'Probiotics 50 Billion CFU', 'Collagen Peptides Powder',
        'First Aid Kit Complete', 'Blood Pressure Monitor', 'Digital Thermometer',
        'Melatonin Sleep Aid', 'Glucosamine Joint Support', 'Apple Cider Vinegar Gummies'
    ]
}

print("⚠️  This will DELETE ALL existing data and insert 1000 realistic products!")
confirm = input("Continue? (yes/no): ")

if confirm.lower() not in ['yes', 'y']:
    print("❌ Cancelled.")
    exit()

conn = connect_db()
cursor = conn.cursor()

print("\n🗑️  Clearing all data...")
cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
tables = ['payments', 'order_items', 'orders', 'seller_products', 'products', 'sellers', 'customers', 'categories']
for table in tables:
    cursor.execute(f"TRUNCATE TABLE {table}")
    print(f"   ✓ Cleared {table}")
cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

print("\n🚀 Inserting realistic data...\n")

# Categories
print("📁 Categories...")
category_map = {}
for cat in PRODUCT_CATALOG.keys():
    cursor.execute("INSERT INTO categories (name) VALUES (%s)", (cat,))
    category_map[cat] = cursor.lastrowid
print(f"   ✓ {len(category_map)} categories")

# Products - exactly 1000
print("📦 Products...")
product_ids = []
product_count = 0

# Insert base products
for category, products in PRODUCT_CATALOG.items():
    for product_name in products:
        sku = fake.unique.bothify(text='SKU-####-????')
        desc = f"{product_name} - High quality product with excellent features."
        cursor.execute(
            "INSERT INTO products (sku, name, description, category_id) VALUES (%s, %s, %s, %s)",
            (sku, product_name, desc, category_map[category])
        )
        product_ids.append(cursor.lastrowid)
        product_count += 1

# Add variants to reach exactly 1000
variants = ['Black', 'White', 'Blue', 'Red', 'Silver', 'Gold', 'Gray']
sizes = ['Small', 'Medium', 'Large', 'XL', 'Pro', 'Plus', 'Premium']

while product_count < 1000:
    cat = random.choice(list(PRODUCT_CATALOG.keys()))
    base = random.choice(PRODUCT_CATALOG[cat])
    variant = f"{base} - {random.choice(variants)} {random.choice(sizes)}"
    sku = fake.unique.bothify(text='SKU-####-????')
    desc = f"{variant} - Premium variant with enhanced features."
    try:
        cursor.execute(
            "INSERT INTO products (sku, name, description, category_id) VALUES (%s, %s, %s, %s)",
            (sku, variant, desc, category_map[cat])
        )
        product_ids.append(cursor.lastrowid)
        product_count += 1
    except:
        continue

print(f"   ✓ {len(product_ids)} products")

# Customers - 1500
print("👤 Customers...")
customer_ids = []
for i in range(1500):
    cursor.execute(
        "INSERT INTO customers (email, password, first_name, last_name, phone) VALUES (%s, %s, %s, %s, %s)",
        (fake.unique.email(), fake.password(), fake.first_name(), fake.last_name(), fake.phone_number())
    )
    customer_ids.append(cursor.lastrowid)
print(f"   ✓ {len(customer_ids)} customers")

# Sellers - 200
print("🏪 Sellers...")
seller_ids = []
for i in range(200):
    cursor.execute(
        "INSERT INTO sellers (email, name, phone) VALUES (%s, %s, %s)",
        (fake.unique.company_email(), fake.company(), fake.phone_number())
    )
    seller_ids.append(cursor.lastrowid)
print(f"   ✓ {len(seller_ids)} sellers")

# Seller Products - 1500
print("🔗 Seller Products...")
seller_product_ids = []
for i in range(1500):
    try:
        cursor.execute(
            "INSERT INTO seller_products (seller_id, product_id, price, stock) VALUES (%s, %s, %s, %s)",
            (random.choice(seller_ids), random.choice(product_ids),
             round(random.uniform(10, 2000), 2), random.randint(0, 500))
        )
        seller_product_ids.append(cursor.lastrowid)
    except:
        continue
print(f"   ✓ {len(seller_product_ids)} seller-products")

# Orders - 1000
print("🛒 Orders...")
order_ids = []
statuses = ['pending', 'processing', 'shipped', 'delivered', 'cancelled']
for i in range(1000):
    cursor.execute(
        "INSERT INTO orders (customer_id, status, total_amount) VALUES (%s, %s, %s)",
        (random.choice(customer_ids), random.choice(statuses), round(random.uniform(50, 5000), 2))
    )
    order_ids.append(cursor.lastrowid)
print(f"   ✓ {len(order_ids)} orders")

# Order Items - 2000
print("📋 Order Items...")
for i in range(2000):
    # Get the price from seller_products table
    sp_id = random.choice(seller_product_ids)
    cursor.execute("SELECT price FROM seller_products WHERE seller_product_id = %s", (sp_id,))
    price = cursor.fetchone()[0]
    quantity = random.randint(1, 3)
    line_total = round(price * quantity, 2)
    
    cursor.execute(
        "INSERT INTO order_items (order_id, seller_product_id, quantity, unit_price, line_total) VALUES (%s, %s, %s, %s, %s)",
        (random.choice(order_ids), sp_id, quantity, price, line_total)
    )
print(f"   ✓ 2000 order items")

# Payments - 750
print("💳 Payments...")
methods = ['credit_card', 'debit_card', 'upi', 'net_banking', 'wallet']
payment_statuses = ['pending', 'completed', 'failed', 'refunded']
for i in range(750):
    cursor.execute(
        "INSERT INTO payments (order_id, method, status, amount) VALUES (%s, %s, %s, %s)",
        (random.choice(order_ids), random.choice(methods),
         random.choice(payment_statuses), round(random.uniform(50, 5000), 2))
    )
print(f"   ✓ 750 payments")

conn.commit()
print("\n✅ Complete! Database now has realistic e-commerce data:")
print(f"   • 10 Categories")
print(f"   • 1000 Realistic Products (iPhone, Nike, LEGO, etc.)")
print(f"   • 1500 Customers")
print(f"   • 200 Sellers")
print(f"   • 1500 Seller-Products")
print(f"   • 1000 Orders")
print(f"   • 2000 Order Items")
print(f"   • 750 Payments")
conn.close()
