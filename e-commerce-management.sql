DROP DATABASE IF EXISTS ecommerce_db;
CREATE DATABASE ecommerce_db;
USE ecommerce_db;



CREATE TABLE categories (
  category_id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL UNIQUE,
  parent_id INT DEFAULT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (parent_id) REFERENCES categories(category_id)
);

CREATE TABLE customers (
  customer_id INT AUTO_INCREMENT PRIMARY KEY,
  first_name VARCHAR(100) NOT NULL,
  last_name VARCHAR(100),
  email VARCHAR(255) NOT NULL UNIQUE,
  phone VARCHAR(30),
  password VARCHAR(255) NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE sellers (
  seller_id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  email VARCHAR(255) UNIQUE,
  phone VARCHAR(30),
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE products (
  product_id INT AUTO_INCREMENT PRIMARY KEY,
  sku VARCHAR(64) UNIQUE,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  category_id INT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (category_id) REFERENCES categories(category_id)
);

CREATE TABLE seller_products (
  seller_product_id INT AUTO_INCREMENT PRIMARY KEY,
  seller_id INT NOT NULL,
  product_id INT NOT NULL,
  price DECIMAL(10,2) NOT NULL CHECK (price >= 0),
  stock INT NOT NULL DEFAULT 0,
  is_active INT DEFAULT 1,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  UNIQUE (seller_id, product_id),
  FOREIGN KEY (seller_id) REFERENCES sellers(seller_id),
  FOREIGN KEY (product_id) REFERENCES products(product_id)
);

CREATE TABLE addresses (
  address_id INT AUTO_INCREMENT PRIMARY KEY,
  customer_id INT NOT NULL,
  label VARCHAR(50),
  recipient_name VARCHAR(200),
  line1 VARCHAR(255) NOT NULL,
  city VARCHAR(100),
  state VARCHAR(100),
  postal_code VARCHAR(30),
  country VARCHAR(100),
  phone VARCHAR(30),
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE orders (
  order_id INT AUTO_INCREMENT PRIMARY KEY,
  customer_id INT NOT NULL,
  shipping_address_id INT,
  status VARCHAR(20) DEFAULT 'pending',
  total_amount DECIMAL(12,2) DEFAULT 0.00,
  placed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
  FOREIGN KEY (shipping_address_id) REFERENCES addresses(address_id)
);

CREATE TABLE order_items (
  order_item_id INT AUTO_INCREMENT PRIMARY KEY,
  order_id INT NOT NULL,
  seller_product_id INT NOT NULL,
  quantity INT NOT NULL,
  unit_price DECIMAL(10,2) NOT NULL,
  line_total DECIMAL(12,2) NOT NULL,
  FOREIGN KEY (order_id) REFERENCES orders(order_id),
  FOREIGN KEY (seller_product_id) REFERENCES seller_products(seller_product_id)
);

CREATE TABLE payments (
  payment_id INT AUTO_INCREMENT PRIMARY KEY,
  order_id INT NOT NULL,
  amount DECIMAL(12,2) NOT NULL,
  method VARCHAR(20) DEFAULT 'card',
  status VARCHAR(20) DEFAULT 'pending',
  transaction_ref VARCHAR(255),
  paid_at DATETIME,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (order_id) REFERENCES orders(order_id)
);

CREATE TABLE inventory_logs (
  log_id INT AUTO_INCREMENT PRIMARY KEY,
  seller_product_id INT NOT NULL,
  change_qty INT NOT NULL,
  reason VARCHAR(100),
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (seller_product_id) REFERENCES seller_products(seller_product_id)
);

INSERT INTO categories (name) VALUES
('Electronics'), ('Clothing'), ('Books');

select * from categories;

INSERT INTO sellers (name, email, phone) VALUES
('TechZone', 'contact@techzone.com', '9123456789'),
('StyleHub', 'info@stylehub.com', '9876543210');

INSERT INTO customers (first_name, last_name, email, phone, password) VALUES
('Aarav', 'Sharma', 'aarav@gmail.com', '8888888888', 'pass123'),
('Diya', 'Patel', 'diya@gmail.com', '9999999999', 'pass456');

INSERT INTO addresses (customer_id, label, recipient_name, line1, city, state, postal_code, country, phone)
VALUES
(1, 'Home', 'Aarav Sharma', '123 MG Road', 'Mumbai', 'MH', '400001', 'India', '8888888888'),
(2, 'Office', 'Diya Patel', '45 Nehru Street', 'Ahmedabad', 'GJ', '380001', 'India', '9999999999');

INSERT INTO products (sku, name, description, category_id) VALUES
('E1001', 'Wireless Mouse', 'Bluetooth mouse', 1),
('E1002', 'Smartphone', '5G Android Phone', 1),
('C2001', 'T-Shirt', 'Cotton round-neck T-shirt', 2),
('B3001', 'DBMS Textbook', 'Database Management Systems Book', 3);

INSERT INTO seller_products (seller_id, product_id, price, stock)
VALUES
(1, 1, 499.00, 20),
(1, 2, 15999.00, 10),
(2, 3, 699.00, 50),
(1, 4, 399.00, 30);

INSERT INTO orders (customer_id, shipping_address_id, status, total_amount)
VALUES
(1, 1, 'processing', 16498.00),
(2, 2, 'pending', 699.00);

INSERT INTO order_items (order_id, seller_product_id, quantity, unit_price, line_total)
VALUES
(1, 1, 1, 499.00, 499.00),
(1, 2, 1, 15999.00, 15999.00),
(2, 3, 1, 699.00, 699.00);

INSERT INTO payments (order_id, amount, method, status, transaction_ref, paid_at)
VALUES
(1, 16498.00, 'card', 'completed', 'TXN1001', NOW()),
(2, 699.00, 'cod', 'pending', NULL, NULL);

INSERT INTO inventory_logs (seller_product_id, change_qty, reason)
VALUES
(1, -1, 'Order #1'),
(2, -1, 'Order #1'),
(3, -1, 'Order #2');

-- top selling products
SELECT p.name, SUM(oi.quantity) AS total_sold
FROM order_items oi
JOIN seller_products sp ON oi.seller_product_id = sp.seller_product_id
JOIN products p ON sp.product_id = p.product_id
GROUP BY p.product_id
ORDER BY total_sold DESC;

-- frequent customers;
SELECT c.first_name, COUNT(o.order_id) AS total_orders
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY c.customer_id
ORDER BY total_orders DESC;