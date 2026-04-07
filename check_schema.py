import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",               
    password="Janvistar800",  
    database="ecommerce_db"
)

cursor = conn.cursor()

tables = ['customers', 'sellers', 'products', 'categories']

for table in tables:
    print(f"\n📋 Table: {table}")
    cursor.execute(f"DESCRIBE {table}")
    for row in cursor.fetchall():
        print(f"   • {row[0]} ({row[1]})")

conn.close()
