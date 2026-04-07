import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch
import numpy as np

# Set up the figure
fig, ax = plt.subplots(figsize=(28, 20))
ax.set_xlim(0, 28)
ax.set_ylim(0, 20)
ax.axis('off')

# Define colors
entity_color = '#E8F4F8'
relationship_color = '#FFE6E6'
pk_color = '#FFD700'

def draw_entity(ax, x, y, name, attributes, width=3, height=2.5):
    """Draw an entity (rectangle) with attributes listed inside"""
    rect = FancyBboxPatch((x - width/2, y - height/2), width, height,
                          boxstyle="round,pad=0.05", 
                          edgecolor='black', facecolor=entity_color, linewidth=2.5)
    ax.add_patch(rect)
    
    # Draw entity name
    ax.text(x, y + height/2 - 0.3, name, ha='center', va='center', 
            fontsize=11, fontweight='bold')
    
    # Draw horizontal line
    ax.plot([x - width/2, x + width/2], [y + height/2 - 0.5, y + height/2 - 0.5], 
            'k-', linewidth=1.5)
    
    # Draw attributes
    y_offset = y + height/2 - 0.8
    for attr, is_pk in attributes:
        if is_pk:
            ax.text(x, y_offset, f"🔑 {attr}", ha='center', va='top', 
                   fontsize=8, fontweight='bold', color='#B8860B')
        else:
            ax.text(x, y_offset, f"• {attr}", ha='center', va='top', 
                   fontsize=7.5)
        y_offset -= 0.25

def draw_relationship(ax, x, y, name, width=1.5, height=1.0):
    """Draw a relationship (diamond)"""
    diamond_points = np.array([[x, y + height], [x + width, y], 
                               [x, y - height], [x - width, y]])
    diamond_patch = patches.Polygon(diamond_points, closed=True, 
                                   edgecolor='black', facecolor=relationship_color, linewidth=2)
    ax.add_patch(diamond_patch)
    ax.text(x, y, name, ha='center', va='center', fontsize=9, fontweight='bold')

def draw_line(ax, x1, y1, x2, y2, linewidth=1.5):
    """Draw a line connecting entities/relationships"""
    ax.plot([x1, x2], [y1, y2], 'k-', linewidth=linewidth)

def add_cardinality(ax, x, y, text):
    """Add cardinality label"""
    ax.text(x, y, text, fontsize=10, fontweight='bold', 
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='black', linewidth=1.5))

# Title
ax.text(14, 19, 'E-Commerce Order Management System - ER Diagram', 
        ha='center', fontsize=18, fontweight='bold')

# ===== ENTITIES =====

# Top Row - Categories, Products, Sellers
categories_attrs = [
    ('category_id', True), ('name', False), ('parent_id', False), ('created_at', False)
]
draw_entity(ax, 4, 15.5, 'CATEGORIES', categories_attrs)

products_attrs = [
    ('product_id', True), ('sku', False), ('name', False), 
    ('description', False), ('category_id (FK)', False), ('created_at', False)
]
draw_entity(ax, 14, 15.5, 'PRODUCTS', products_attrs)

sellers_attrs = [
    ('seller_id', True), ('name', False), ('email', False), 
    ('phone', False), ('created_at', False)
]
draw_entity(ax, 24, 15.5, 'SELLERS', sellers_attrs)

# Middle Row - Customers, Seller_Products, Inventory_Logs
customers_attrs = [
    ('customer_id', True), ('first_name', False), ('last_name', False),
    ('email', False), ('phone', False), ('password', False), ('created_at', False)
]
draw_entity(ax, 4, 10.5, 'CUSTOMERS', customers_attrs)

seller_products_attrs = [
    ('seller_product_id', True), ('seller_id (FK)', False), ('product_id (FK)', False),
    ('price', False), ('stock', False), ('is_active', False), ('created_at', False)
]
draw_entity(ax, 14, 10.5, 'SELLER_PRODUCTS', seller_products_attrs, 3.5, 3)

inventory_logs_attrs = [
    ('log_id', True), ('seller_product_id (FK)', False),
    ('change_qty', False), ('reason', False), ('created_at', False)
]
draw_entity(ax, 24, 10.5, 'INVENTORY_LOGS', inventory_logs_attrs)

# Bottom Row - Addresses, Orders, Order_Items, Payments
addresses_attrs = [
    ('address_id', True), ('customer_id (FK)', False), ('label', False),
    ('recipient_name', False), ('line1', False), ('city', False),
    ('state', False), ('postal_code', False), ('country', False), ('phone', False)
]
draw_entity(ax, 4, 4.5, 'ADDRESSES', addresses_attrs, 3.2, 3.5)

orders_attrs = [
    ('order_id', True), ('customer_id (FK)', False), ('shipping_address_id (FK)', False),
    ('status', False), ('total_amount', False), ('placed_at', False)
]
draw_entity(ax, 11, 4.5, 'ORDERS', orders_attrs, 3.2, 2.8)

order_items_attrs = [
    ('order_item_id', True), ('order_id (FK)', False), ('seller_product_id (FK)', False),
    ('quantity', False), ('unit_price', False), ('line_total', False)
]
draw_entity(ax, 18, 4.5, 'ORDER_ITEMS', order_items_attrs, 3.2, 2.8)

payments_attrs = [
    ('payment_id', True), ('order_id (FK)', False), ('amount', False),
    ('method', False), ('status', False), ('transaction_ref', False),
    ('paid_at', False), ('created_at', False)
]
draw_entity(ax, 25, 4.5, 'PAYMENTS', payments_attrs, 3, 3)

# ===== RELATIONSHIPS =====

# Categories -> Products (HAS)
draw_relationship(ax, 9, 15.5, 'HAS', 1.2, 0.8)
draw_line(ax, 5.5, 15.5, 7.8, 15.5)
draw_line(ax, 10.2, 15.5, 12.5, 15.5)
add_cardinality(ax, 6.5, 16, '1')
add_cardinality(ax, 11.5, 16, 'N')

# Products -> Seller_Products (OFFERED_BY)
draw_relationship(ax, 14, 13, 'OFFERED_BY', 1.2, 0.8)
draw_line(ax, 14, 13.9, 14, 13.8)
draw_line(ax, 14, 12.2, 14, 12)
add_cardinality(ax, 13.3, 13.5, '1')
add_cardinality(ax, 13.3, 12.5, 'N')

# Sellers -> Seller_Products (SELLS)
draw_relationship(ax, 19, 13, 'SELLS', 1.2, 0.8)
draw_line(ax, 22.5, 14.2, 20.2, 13.8)
draw_line(ax, 17.8, 12.2, 15.75, 11.5)
add_cardinality(ax, 21.5, 14, '1')
add_cardinality(ax, 16.5, 12, 'N')

# Customers -> Addresses (HAS)
draw_relationship(ax, 4, 7.5, 'HAS', 1.0, 0.7)
draw_line(ax, 4, 8.5, 4, 8.2)
draw_line(ax, 4, 6.8, 4, 6.3)
add_cardinality(ax, 3.3, 8, '1')
add_cardinality(ax, 3.3, 7, 'N')

# Customers -> Orders (PLACES)
draw_relationship(ax, 7.5, 7.5, 'PLACES', 1.2, 0.8)
draw_line(ax, 5.5, 9.2, 6.5, 8.2)
draw_line(ax, 8.5, 6.8, 9.4, 5.8)
add_cardinality(ax, 6, 8.8, '1')
add_cardinality(ax, 9, 6.5, 'N')

# Addresses -> Orders (SHIPS_TO)
draw_relationship(ax, 7.5, 4.5, 'SHIPS_TO', 1.2, 0.8)
draw_line(ax, 5.6, 4.5, 6.3, 4.5)
draw_line(ax, 8.7, 4.5, 9.4, 4.5)
add_cardinality(ax, 6, 5, '1')
add_cardinality(ax, 9, 5, 'N')

# Orders -> Order_Items (CONTAINS)
draw_relationship(ax, 14.5, 4.5, 'CONTAINS', 1.2, 0.8)
draw_line(ax, 12.6, 4.5, 13.3, 4.5)
draw_line(ax, 15.7, 4.5, 16.4, 4.5)
add_cardinality(ax, 13, 5, '1')
add_cardinality(ax, 16, 5, 'N')

# Seller_Products -> Order_Items (ORDERED)
draw_relationship(ax, 16, 7.5, 'ORDERED', 1.2, 0.8)
draw_line(ax, 15, 9.2, 15.5, 8.3)
draw_line(ax, 17, 6.7, 17.5, 5.8)
add_cardinality(ax, 14.5, 8.8, '1')
add_cardinality(ax, 17.5, 6.5, 'M')

# Orders -> Payments (HAS_PAYMENT)
draw_relationship(ax, 18, 4.5, 'PAYMENT', 1.2, 0.8)
draw_line(ax, 21.4, 4.5, 19.2, 4.5)
draw_line(ax, 16.8, 4.5, 14.6, 4.5)
add_cardinality(ax, 15, 5, '1')
add_cardinality(ax, 20.5, 5, 'N')

# Seller_Products -> Inventory_Logs (LOGS)
draw_relationship(ax, 19, 10.5, 'LOGS', 1.2, 0.8)
draw_line(ax, 15.75, 10.5, 17.8, 10.5)
draw_line(ax, 20.2, 10.5, 22.5, 10.5)
add_cardinality(ax, 17, 11, '1')
add_cardinality(ax, 21, 11, 'N')

# Self-relationship for Categories (PARENT_OF)
draw_relationship(ax, 1.5, 13, 'PARENT_OF', 1.0, 0.7)
# Draw arc for self-relationship
ax.annotate('', xy=(2.5, 14.2), xytext=(1.5, 13.7),
            arrowprops=dict(arrowstyle='-', connectionstyle="arc3,rad=.3", lw=1.5))
ax.annotate('', xy=(1.5, 12.3), xytext=(2.5, 13),
            arrowprops=dict(arrowstyle='-', connectionstyle="arc3,rad=.3", lw=1.5))
add_cardinality(ax, 0.8, 13.5, '0..1')
add_cardinality(ax, 0.8, 12.5, 'N')

# Legend
legend_x, legend_y = 24, 1.5
ax.text(legend_x - 3, legend_y + 1.5, 'Legend:', fontsize=12, fontweight='bold')

# Entity example
entity_rect = FancyBboxPatch((legend_x - 4, legend_y + 0.3), 2, 0.8,
                            boxstyle="round,pad=0.05", 
                            edgecolor='black', facecolor=entity_color, linewidth=2)
ax.add_patch(entity_rect)
ax.text(legend_x - 3, legend_y + 0.7, 'Entity', ha='center', va='center', fontsize=9, fontweight='bold')

# Relationship example
rel_points = np.array([[legend_x - 3, legend_y - 0.4], [legend_x - 2.3, legend_y - 0.8], 
                       [legend_x - 3, legend_y - 1.2], [legend_x - 3.7, legend_y - 0.8]])
rel_patch = patches.Polygon(rel_points, closed=True, 
                           edgecolor='black', facecolor=relationship_color, linewidth=2)
ax.add_patch(rel_patch)
ax.text(legend_x - 3, legend_y - 0.8, 'Relation', ha='center', va='center', fontsize=8, fontweight='bold')

# Attribute notation
ax.text(legend_x - 3, legend_y - 1.8, '🔑 = Primary Key', ha='center', fontsize=9)
ax.text(legend_x - 3, legend_y - 2.2, '• = Attribute', ha='center', fontsize=9)
ax.text(legend_x - 3, legend_y - 2.6, 'FK = Foreign Key', ha='center', fontsize=9)

plt.tight_layout()
plt.savefig('/Users/janvi/Desktop/dbms project/ecommerce_er_diagram.png', dpi=300, bbox_inches='tight', facecolor='white')
print("✅ ER Diagram generated successfully!")
print("📁 Saved as: ecommerce_er_diagram.png")
print("📊 The diagram shows all entities, relationships, and cardinalities in a clean layout.")
plt.show()
