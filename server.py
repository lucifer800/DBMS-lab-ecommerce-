import os
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

from flask import Flask, jsonify, request
import mysql.connector
from mysql.connector import Error

app = Flask(__name__, static_folder="web", static_url_path="")

DB_CONFIG = {
    "host": os.getenv("ECOM_DB_HOST", "localhost"),
    "user": os.getenv("ECOM_DB_USER", "root"),
    "password": os.getenv("ECOM_DB_PASSWORD", "12345678"),
    "database": os.getenv("ECOM_DB_NAME", "ecommerce_db"),
    "port": int(os.getenv("ECOM_DB_PORT", "3306")),
}

SSL_CA = os.getenv("ECOM_DB_SSL_CA", "").strip()
SSL_DISABLED = os.getenv("ECOM_DB_SSL_DISABLED", "false").lower() == "true"
SSL_VERIFY = os.getenv("ECOM_DB_SSL_VERIFY", "true").lower() == "true"


def connect_db():
    config = dict(DB_CONFIG)
    if SSL_DISABLED:
        config["ssl_disabled"] = True
    elif SSL_CA:
        config["ssl_ca"] = SSL_CA
        config["ssl_verify_cert"] = SSL_VERIFY
    return mysql.connector.connect(**config)


def serialize_value(value):
    if isinstance(value, (datetime, date)):
        return value.isoformat(sep=" ")
    if isinstance(value, Decimal):
        return float(value)
    return value


def serialize_row(row):
    if row is None:
        return None
    return {key: serialize_value(value) for key, value in row.items()}


def serialize_rows(rows):
    return [serialize_row(row) for row in rows]


def parse_decimal(value, default=None):
    if value is None or value == "":
        return default
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return default


def fetch_all(query, params=None):
    conn = connect_db()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(query, params or ())
        return serialize_rows(cursor.fetchall())
    finally:
        cursor.close()
        conn.close()


def fetch_one(query, params=None):
    conn = connect_db()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(query, params or ())
        return serialize_row(cursor.fetchone())
    finally:
        cursor.close()
        conn.close()


def execute_write(query, params=None):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute(query, params or ())
        conn.commit()
        return cursor.lastrowid, cursor.rowcount
    finally:
        cursor.close()
        conn.close()


def require_fields(payload, fields):
    missing = []
    for field in fields:
        value = payload.get(field)
        if value is None or value == "":
            missing.append(field)
    return missing


def json_error(message, status=400):
    return jsonify({"message": message}), status


@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,OPTIONS"
    return response


@app.route("/api/<path:unused>", methods=["OPTIONS"])
def api_options(unused):
    return "", 204


@app.route("/")
def index():
    return app.send_static_file("index.html")


@app.route("/api/products", methods=["GET"])
def list_products():
    rows = fetch_all(
        """
        SELECT product_id, sku, name, description, category_id, created_at
        FROM products
        ORDER BY created_at DESC, product_id DESC
        """
    )
    return jsonify(rows)


@app.route("/api/catalog", methods=["GET"])
def list_catalog():
    rows = fetch_all(
        """
        SELECT
            sp.seller_product_id,
            p.product_id,
            p.sku,
            p.name,
            p.description,
            p.category_id,
            p.created_at,
            s.name AS seller,
            sp.price,
            sp.stock
        FROM products p
        LEFT JOIN seller_products sp
            ON sp.product_id = p.product_id
           AND sp.is_active = 1
        LEFT JOIN sellers s ON sp.seller_id = s.seller_id
        ORDER BY p.created_at DESC, p.product_id DESC, sp.seller_product_id DESC
        """
    )
    return jsonify(rows)


@app.route("/api/products", methods=["POST"])
def create_product():
    payload = request.get_json(silent=True) or {}
    missing = require_fields(payload, ["sku", "name", "description", "category_id"])
    if missing:
        return json_error(f"Missing fields: {', '.join(missing)}")

    last_id, _ = execute_write(
        """
        INSERT INTO products (sku, name, description, category_id)
        VALUES (%s, %s, %s, %s)
        """,
        (payload["sku"], payload["name"], payload["description"], payload["category_id"]),
    )
    seller_id = payload.get("seller_id")
    price = payload.get("price")
    stock = payload.get("stock")
    if seller_id is not None and price is not None and price != "":
        if stock is None or stock == "":
            stock = 0
        execute_write(
            """
            INSERT INTO seller_products (seller_id, product_id, price, stock)
            VALUES (%s, %s, %s, %s)
            """,
            (seller_id, last_id, price, stock),
        )
    product = fetch_one(
        """
        SELECT product_id, sku, name, description, category_id, created_at
        FROM products
        WHERE product_id = %s
        """,
        (last_id,),
    )
    return jsonify({"message": "Product added", "product": product}), 201


@app.route("/api/products/<int:product_id>", methods=["PUT"])
def update_product(product_id):
    payload = request.get_json(silent=True) or {}
    missing = require_fields(payload, ["name"])
    if missing:
        return json_error("Missing field: name")

    _, rowcount = execute_write(
        "UPDATE products SET name = %s WHERE product_id = %s",
        (payload["name"], product_id),
    )
    if rowcount == 0:
        return json_error("Product not found", 404)

    product = fetch_one(
        """
        SELECT product_id, sku, name, description, category_id, created_at
        FROM products
        WHERE product_id = %s
        """,
        (product_id,),
    )
    return jsonify({"message": "Product updated", "product": product})


@app.route("/api/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    conn = connect_db()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT product_id FROM products WHERE product_id = %s",
            (product_id,),
        )
        product = cursor.fetchone()
        if product is None:
            return json_error("Product not found", 404)

        try:
            cursor.execute(
                "DELETE FROM products WHERE product_id = %s",
                (product_id,),
            )
            conn.commit()
            return jsonify({"message": "Product has been deleted successfully"})
        except Error as error:
            # FK-referenced products are soft-deleted from active catalog/inventory.
            if getattr(error, "errno", None) != 1451:
                conn.rollback()
                raise
            conn.rollback()

        cursor.execute(
            """
            UPDATE seller_products
            SET is_active = 0
            WHERE product_id = %s AND is_active = 1
            """,
            (product_id,),
        )
        hidden_listings = cursor.rowcount
        conn.commit()

        if hidden_listings == 0:
            return json_error(
                "Product cannot be deleted because it is linked to previous orders",
                400,
            )

        return jsonify(
            {
                "message": "Product has been deleted successfully",
                "mode": "soft-delete",
                "hidden_listings": hidden_listings,
            }
        )
    finally:
        cursor.close()
        conn.close()


@app.route("/api/customers", methods=["GET"])
def list_customers():
    rows = fetch_all(
        """
        SELECT customer_id, first_name, last_name, email
        FROM customers
        ORDER BY customer_id ASC
        """
    )
    return jsonify(rows)


@app.route("/api/insights/top-products", methods=["GET"])
def top_products():
    rows = fetch_all(
        """
        SELECT p.name, SUM(oi.quantity) AS sold
        FROM order_items oi
        JOIN seller_products sp ON oi.seller_product_id = sp.seller_product_id
        JOIN products p ON sp.product_id = p.product_id
        GROUP BY p.product_id
        ORDER BY sold DESC
        LIMIT 10
        """
    )
    return jsonify(rows)


@app.route("/api/insights/top-customers", methods=["GET"])
def top_customers():
    rows = fetch_all(
        """
        SELECT c.first_name AS name, COUNT(o.order_id) AS total_orders
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
        GROUP BY c.customer_id
        ORDER BY total_orders DESC
        LIMIT 10
        """
    )
    return jsonify(rows)


@app.route("/api/inventory", methods=["GET"])
def inventory():
    rows = fetch_all(
        """
        SELECT s.name AS seller, p.name AS product, sp.stock
        FROM seller_products sp
        JOIN sellers s ON sp.seller_id = s.seller_id
        JOIN products p ON sp.product_id = p.product_id
        WHERE sp.is_active = 1
        ORDER BY sp.stock ASC
        """
    )
    return jsonify(rows)


@app.route("/api/orders", methods=["GET"])
def list_orders():
    status_param = request.args.get("status", "")
    statuses = [status.strip() for status in status_param.split(",") if status.strip()]
    if statuses:
        placeholders = ", ".join(["%s"] * len(statuses))
        query = (
            "SELECT order_id, status, total_amount, placed_at "
            f"FROM orders WHERE status IN ({placeholders}) "
            "ORDER BY placed_at DESC"
        )
        rows = fetch_all(query, tuple(statuses))
    else:
        rows = fetch_all(
            """
            SELECT order_id, status, total_amount, placed_at
            FROM orders
            ORDER BY placed_at DESC
            """
        )
    return jsonify(rows)


@app.route("/api/orders", methods=["POST"])
def create_order():
    payload = request.get_json(silent=True) or {}
    missing = require_fields(payload, ["customer_id", "seller_product_id", "quantity"])
    if missing:
        return json_error(f"Missing fields: {', '.join(missing)}")

    try:
        customer_id = int(payload.get("customer_id"))
    except (TypeError, ValueError):
        return json_error("Invalid customer ID")

    if customer_id <= 0:
        return json_error("Customer ID must be greater than 0")

    try:
        seller_product_id = int(payload.get("seller_product_id"))
    except (TypeError, ValueError):
        return json_error("Invalid seller product ID")

    if seller_product_id <= 0:
        return json_error("Seller product ID must be greater than 0")

    try:
        quantity = int(payload.get("quantity"))
    except (TypeError, ValueError):
        return json_error("Invalid quantity")

    if quantity <= 0:
        return json_error("Quantity must be greater than 0")

    cgst_rate = parse_decimal(payload.get("cgst_rate"), Decimal("9"))
    sgst_rate = parse_decimal(payload.get("sgst_rate"), Decimal("9"))
    if cgst_rate is None or sgst_rate is None:
        return json_error("Invalid GST rate")

    shipping_address_id = payload.get("shipping_address_id")
    if shipping_address_id in (None, ""):
        shipping_address_id = None
    else:
        try:
            shipping_address_id = int(shipping_address_id)
        except (TypeError, ValueError):
            return json_error("Invalid shipping address ID")
        if shipping_address_id <= 0:
            return json_error("Shipping address ID must be greater than 0")

    conn = connect_db()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT customer_id FROM customers WHERE customer_id = %s",
            (customer_id,),
        )
        if cursor.fetchone() is None:
            return json_error("Customer not found", 400)

        if shipping_address_id is not None:
            cursor.execute(
                "SELECT address_id FROM addresses WHERE address_id = %s AND customer_id = %s",
                (shipping_address_id, customer_id),
            )
            if cursor.fetchone() is None:
                return json_error("Shipping address not found for customer", 400)

        cursor.execute(
            """
            SELECT
                sp.seller_product_id,
                sp.price,
                sp.stock,
                p.name AS product_name,
                s.name AS seller
            FROM seller_products sp
            JOIN products p ON sp.product_id = p.product_id
            JOIN sellers s ON sp.seller_id = s.seller_id
            WHERE sp.seller_product_id = %s AND sp.is_active = 1
            """,
            (seller_product_id,),
        )
        listing = cursor.fetchone()
        if listing is None:
            return json_error("Listing not found", 404)

        if listing["stock"] is not None and quantity > listing["stock"]:
            return json_error("Insufficient stock", 400)

        unit_price = listing["price"]
        subtotal = unit_price * quantity
        cgst_amount = (subtotal * cgst_rate) / Decimal("100")
        sgst_amount = (subtotal * sgst_rate) / Decimal("100")
        total_amount = subtotal + cgst_amount + sgst_amount

        cursor.execute(
            """
            INSERT INTO orders (customer_id, shipping_address_id, status, total_amount)
            VALUES (%s, %s, %s, %s)
            """,
            (customer_id, shipping_address_id, "pending", total_amount),
        )
        order_id = cursor.lastrowid

        cursor.execute(
            """
            INSERT INTO order_items (order_id, seller_product_id, quantity, unit_price, line_total)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (order_id, seller_product_id, quantity, unit_price, subtotal),
        )

        if listing["stock"] is not None:
            cursor.execute(
                """
                UPDATE seller_products
                SET stock = stock - %s
                WHERE seller_product_id = %s
                """,
                (quantity, seller_product_id),
            )

        conn.commit()
    finally:
        cursor.close()
        conn.close()

    summary = {
        "order_id": order_id,
        "product": listing["product_name"],
        "seller": listing["seller"],
        "unit_price": unit_price,
        "quantity": quantity,
        "line_total": subtotal,
        "cgst_rate": cgst_rate,
        "cgst_amount": cgst_amount,
        "sgst_rate": sgst_rate,
        "sgst_amount": sgst_amount,
        "total_payable": total_amount,
    }
    order = {
        "order_id": order_id,
        "customer_id": customer_id,
        "status": "pending",
        "total_amount": total_amount,
    }
    return jsonify(
        {
            "message": "Order created",
            "order": serialize_row(order),
            "summary": serialize_row(summary),
        }
    ), 201


@app.route("/api/orders/<int:order_id>/status", methods=["POST"])
def update_order_status(order_id):
    payload = request.get_json(silent=True) or {}
    status = payload.get("status")
    if not status:
        return json_error("Missing field: status")

    allowed = {"pending", "processing", "shipped", "cancelled"}
    if status not in allowed:
        return json_error("Invalid status", 400)

    _, rowcount = execute_write(
        "UPDATE orders SET status = %s WHERE order_id = %s",
        (status, order_id),
    )
    if rowcount == 0:
        return json_error("Order not found", 404)

    order = fetch_one(
        "SELECT order_id, status, total_amount, placed_at FROM orders WHERE order_id = %s",
        (order_id,),
    )
    return jsonify({"message": "Order updated", "order": order})


@app.route("/api/payments", methods=["GET"])
def list_payments():
    rows = fetch_all(
        """
        SELECT p.payment_id, o.order_id, p.method, p.status, p.amount, p.created_at
        FROM payments p
        JOIN orders o ON p.order_id = o.order_id
        ORDER BY p.created_at DESC
        """
    )
    return jsonify(rows)


@app.errorhandler(Error)
def handle_db_error(error):
    return json_error(f"Database error: {error}", 500)


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)
