const origin = window.location.origin;
const isFileOrigin = origin === "null" || origin.startsWith("file:");
const defaultApiBase = isFileOrigin ? "" : origin;
const storedApiBase = localStorage.getItem("apiBase") || "";

const state = {
  demo: true,
  apiBase: storedApiBase || defaultApiBase,
};

const CURRENCY_LABEL = "INR";
const DEFAULT_GST_RATE = 9;

const mock = {
  products: [
    {
      product_id: 101,
      sku: "AUR-001",
      name: "Aurora Lamp",
      description: "Glow lamp with sculpted glass finish.",
      category_id: 3,
      created_at: "2026-04-01",
    },
    {
      product_id: 102,
      sku: "VLT-014",
      name: "Vault Backpack",
      description: "Urban carry with hidden compartments.",
      category_id: 4,
      created_at: "2026-04-02",
    },
  ],
  sellerProducts: [
    {
      seller_product_id: 201,
      seller_id: 1,
      product_id: 101,
      seller: "TechZone",
      price: 899,
      stock: 14,
    },
    {
      seller_product_id: 202,
      seller_id: 2,
      product_id: 102,
      seller: "StyleHub",
      price: 1299,
      stock: 6,
    },
  ],
  customers: [
    { customer_id: 1, first_name: "Ava" },
    { customer_id: 2, first_name: "Noah" },
    { customer_id: 3, first_name: "Liam" },
  ],
  orders: [
    { order_id: 5001, customer_id: 1, status: "pending", total_amount: 120.5 },
    { order_id: 5002, customer_id: 2, status: "processing", total_amount: 64.99 },
    { order_id: 5003, customer_id: 3, status: "shipped", total_amount: 39.0 },
  ],
  orderItems: [
    { seller_product_id: 201, quantity: 6 },
    { seller_product_id: 202, quantity: 4 },
    { seller_product_id: 201, quantity: 2 },
  ],
  payments: [
    {
      payment_id: 9001,
      order_id: 5001,
      method: "card",
      status: "pending",
      amount: 120.5,
      created_at: "2026-04-03",
    },
    {
      payment_id: 9002,
      order_id: 5002,
      method: "upi",
      status: "paid",
      amount: 64.99,
      created_at: "2026-04-02",
    },
  ],
  inventory: [
    { seller: "TechZone", product: "Aurora Lamp", stock: 14 },
    { seller: "StyleHub", product: "Vault Backpack", stock: 6 },
  ],
};

const consoleEl = document.getElementById("consoleOutput");
const apiStatusEl = document.getElementById("apiStatus");
const statOrders = document.getElementById("statOrders");
const statProducts = document.getElementById("statProducts");
const statPayments = document.getElementById("statPayments");
const logs = [];
let catalogItems = [];
let catalogById = new Map();
let lastTableAction = null;

function updateStatusLabel() {
  apiStatusEl.textContent = state.demo ? "Demo" : "API";
}

function refreshStats() {
  statOrders.textContent = mock.orders.length.toString();
  statProducts.textContent = mock.products.length.toString();
  statPayments.textContent = mock.payments.length.toString();
}

function formatCurrency(value) {
  const number = Number(value);
  if (!Number.isFinite(number)) {
    return "N/A";
  }
  return `${CURRENCY_LABEL} ${number.toFixed(2)}`;
}

function formatPercent(value) {
  const number = Number(value);
  if (!Number.isFinite(number)) {
    return "N/A";
  }
  return `${number.toFixed(2)}%`;
}

function formatTime(value) {
  const hours = String(value.getHours()).padStart(2, "0");
  const minutes = String(value.getMinutes()).padStart(2, "0");
  return `${hours}:${minutes}`;
}

function formatOutput(data) {
  if (typeof data === "string") {
    return data;
  }
  return JSON.stringify(data, null, 2);
}

function logLine(title, data) {
  const time = new Date().toISOString().slice(11, 19);
  const output = data ? `\n${formatOutput(data)}` : "";
  logs.push(`[${time}] ${title}${output}`);
  if (logs.length > 120) {
    logs.shift();
  }
  consoleEl.textContent = logs.join("\n\n");
  consoleEl.scrollTop = consoleEl.scrollHeight;
}

function parseNumber(value) {
  const parsed = Number(value);
  return Number.isNaN(parsed) ? value : parsed;
}

function normalizePayload(payload) {
  const normalized = { ...payload };
  if (normalized.product_id !== undefined) {
    normalized.product_id = parseNumber(normalized.product_id);
  }
  if (normalized.category_id !== undefined) {
    normalized.category_id = parseNumber(normalized.category_id);
  }
  if (normalized.order_id !== undefined) {
    normalized.order_id = parseNumber(normalized.order_id);
  }
  if (normalized.seller_product_id !== undefined) {
    normalized.seller_product_id = parseNumber(normalized.seller_product_id);
  }
  if (normalized.seller_id !== undefined) {
    normalized.seller_id = parseNumber(normalized.seller_id);
  }
  if (normalized.customer_id !== undefined) {
    normalized.customer_id = parseNumber(normalized.customer_id);
  }
  if (normalized.quantity !== undefined) {
    normalized.quantity = parseNumber(normalized.quantity);
  }
  if (normalized.cgst_rate !== undefined) {
    normalized.cgst_rate = parseNumber(normalized.cgst_rate);
  }
  if (normalized.sgst_rate !== undefined) {
    normalized.sgst_rate = parseNumber(normalized.sgst_rate);
  }
  if (normalized.shipping_address_id !== undefined) {
    normalized.shipping_address_id = parseNumber(normalized.shipping_address_id);
  }
  if (normalized.price !== undefined) {
    normalized.price = parseNumber(normalized.price);
  }
  if (normalized.stock !== undefined) {
    normalized.stock = parseNumber(normalized.stock);
  }
  return normalized;
}

function getTopProducts() {
  const totals = {};
  for (const item of mock.orderItems) {
    const productId = getProductIdFromOrderItem(item);
    if (!productId) {
      continue;
    }
    totals[productId] = (totals[productId] || 0) + item.quantity;
  }
  return Object.entries(totals)
    .map(([productId, sold]) => {
      const product = mock.products.find(
        (entry) => entry.product_id === Number(productId)
      );
      return {
        name: product ? product.name : `Product ${productId}`,
        sold,
      };
    })
    .sort((a, b) => b.sold - a.sold)
    .slice(0, 10);
}

function getListingById(sellerProductId) {
  return mock.sellerProducts.find(
    (entry) => entry.seller_product_id === Number(sellerProductId)
  );
}

function getProductIdFromOrderItem(item) {
  if (item.product_id !== undefined && item.product_id !== null) {
    return item.product_id;
  }
  if (item.seller_product_id !== undefined && item.seller_product_id !== null) {
    return getListingById(item.seller_product_id)?.product_id;
  }
  return null;
}

function getTopCustomers() {
  const totals = {};
  for (const order of mock.orders) {
    totals[order.customer_id] = (totals[order.customer_id] || 0) + 1;
  }
  return Object.entries(totals)
    .map(([customerId, total]) => {
      const customer = mock.customers.find(
        (entry) => entry.customer_id === Number(customerId)
      );
      return {
        name: customer ? customer.first_name : `Customer ${customerId}`,
        total_orders: total,
      };
    })
    .sort((a, b) => b.total_orders - a.total_orders)
    .slice(0, 10);
}

function buildCatalogRows() {
  return mock.sellerProducts.map((listing) => {
    const product = mock.products.find(
      (entry) => entry.product_id === listing.product_id
    );
    return {
      seller_product_id: listing.seller_product_id,
      product_id: listing.product_id,
      sku: product?.sku,
      name: product?.name,
      description: product?.description,
      category_id: product?.category_id,
      created_at: product?.created_at,
      seller: listing.seller,
      price: listing.price,
      stock: listing.stock,
    };
  });
}

function toNumber(value, fallback) {
  const number = Number(value);
  return Number.isFinite(number) ? number : fallback;
}

function calculateTotals(unitPrice, quantity, cgstRate, sgstRate) {
  const subtotal = unitPrice * quantity;
  const cgst = subtotal * (cgstRate / 100);
  const sgst = subtotal * (sgstRate / 100);
  const total = subtotal + cgst + sgst;
  return {
    subtotal,
    cgst,
    sgst,
    total,
  };
}

function updateCatalogSelect(items) {
  if (!orderProduct) {
    return;
  }
  const previous = orderProduct.value;
  orderProduct.innerHTML = "";

  if (!items || items.length === 0) {
    const option = document.createElement("option");
    option.value = "";
    option.textContent = "No products available";
    orderProduct.appendChild(option);
    orderProduct.disabled = true;
    return;
  }

  orderProduct.disabled = false;
  const placeholder = document.createElement("option");
  placeholder.value = "";
  placeholder.textContent = "Select a listing";
  placeholder.disabled = true;
  placeholder.selected = true;
  orderProduct.appendChild(placeholder);

  items.forEach((item) => {
    const option = document.createElement("option");
    option.value = String(item.seller_product_id);
    const priceLabel = formatCurrency(item.price);
    const stockLabel =
      item.stock === undefined || item.stock === null ? "Stock N/A" : `Stock ${item.stock}`;
    option.textContent = `${item.name || "Product"} | ${item.seller || "Seller"} | ${priceLabel} | ${stockLabel}`;
    orderProduct.appendChild(option);
  });

  if (previous && catalogById.has(previous)) {
    orderProduct.value = previous;
  } else if (items[0]) {
    orderProduct.value = String(items[0].seller_product_id);
  }
}

function updateOrderSummary() {
  if (!orderUnitPrice || !orderSubtotal || !orderCgst || !orderSgst || !orderTotal) {
    return;
  }

  const listing = orderProduct ? catalogById.get(orderProduct.value) : null;
  const quantity = Math.max(1, toNumber(orderQty?.value, 1));
  const cgstRate = Math.max(0, toNumber(cgstRateInput?.value, DEFAULT_GST_RATE));
  const sgstRate = Math.max(0, toNumber(sgstRateInput?.value, DEFAULT_GST_RATE));

  if (!listing || !Number.isFinite(Number(listing.price))) {
    orderUnitPrice.textContent = formatCurrency(0);
    orderSubtotal.textContent = formatCurrency(0);
    orderCgst.textContent = formatCurrency(0);
    orderSgst.textContent = formatCurrency(0);
    orderTotal.textContent = formatCurrency(0);
    if (orderStock) {
      orderStock.textContent = "N/A";
    }
    if (orderHint) {
      orderHint.textContent = "Select a product listing to see totals.";
    }
    if (orderSubmit) {
      orderSubmit.disabled = true;
    }
    return;
  }

  const unitPrice = Number(listing.price);
  const totals = calculateTotals(unitPrice, quantity, cgstRate, sgstRate);
  orderUnitPrice.textContent = formatCurrency(unitPrice);
  orderSubtotal.textContent = formatCurrency(totals.subtotal);
  orderCgst.textContent = formatCurrency(totals.cgst);
  orderSgst.textContent = formatCurrency(totals.sgst);
  orderTotal.textContent = formatCurrency(totals.total);
  if (orderStock) {
    const stockValue =
      listing.stock === undefined || listing.stock === null
        ? "N/A"
        : String(listing.stock);
    orderStock.textContent = stockValue;
  }

  if (orderHint) {
    const stockNote =
      listing.stock === undefined || listing.stock === null
        ? ""
        : ` Stock available: ${listing.stock}.`;
    orderHint.textContent = `Unit price from ${listing.seller}.${stockNote}`;
  }

  if (orderSubmit) {
    const hasStock = listing.stock !== undefined && listing.stock !== null;
    const exceedsStock = hasStock ? quantity > Number(listing.stock) : false;
    orderSubmit.disabled = exceedsStock;
    if (exceedsStock && orderHint) {
      orderHint.textContent = `Requested quantity exceeds stock. Available: ${listing.stock}.`;
    }
  }
}

async function loadCatalog() {
  if (!orderProduct) {
    return;
  }
  try {
    const items = state.demo ? buildCatalogRows() : await apiRequest("/api/catalog", "GET");
    catalogItems = Array.isArray(items) ? items : [];
    catalogById = new Map(
      catalogItems.map((item) => [String(item.seller_product_id), item])
    );
    updateCatalogSelect(catalogItems);
    updateOrderSummary();
    if (lastTableAction === "view-products" && dataPanel && !dataPanel.hidden) {
      renderTable("view-products", catalogItems);
    }
    if (orderHint) {
      if (catalogItems.length) {
        orderHint.textContent = `Prices refreshed at ${formatTime(new Date())}.`;
      } else {
        orderHint.textContent = "No listings available for pricing.";
      }
    }
  } catch (error) {
    if (orderHint) {
      orderHint.textContent = "Unable to load catalog prices.";
    }
    logLine("Error: catalog", error?.message || error);
  }
}

function selectCatalogItem(sellerProductId) {
  if (!orderProduct) {
    return;
  }
  const value = String(sellerProductId);
  if (!catalogById.has(value)) {
    return;
  }
  orderProduct.value = value;
  updateOrderSummary();
  orderProduct.focus();
  orderForm?.scrollIntoView({ behavior: "smooth", block: "center" });
}

const demoHandlers = {
  "add-product": async (payload) => {
    const nextId =
      Math.max(0, ...mock.products.map((item) => item.product_id)) + 1;
    const product = {
      product_id: nextId,
      sku: payload.sku,
      name: payload.name,
      description: payload.description,
      category_id: payload.category_id,
      created_at: new Date().toISOString().slice(0, 10),
    };
    mock.products.push(product);
    if (payload.seller_id && payload.price !== undefined && payload.price !== "") {
      const nextSellerProductId =
        Math.max(0, ...mock.sellerProducts.map((item) => item.seller_product_id)) +
        1;
      mock.sellerProducts.push({
        seller_product_id: nextSellerProductId,
        seller_id: payload.seller_id,
        product_id: product.product_id,
        seller: `Seller ${payload.seller_id}`,
        price: payload.price,
        stock: payload.stock || 0,
      });
    }
    return { message: "Product added", product };
  },
  "view-products": async () => buildCatalogRows(),
  "update-product": async (payload) => {
    const product = mock.products.find(
      (item) => item.product_id === payload.product_id
    );
    if (!product) {
      throw new Error("Product not found");
    }
    product.name = payload.name;
    return { message: "Product updated", product };
  },
  "delete-product": async (payload) => {
    const index = mock.products.findIndex(
      (item) => item.product_id === payload.product_id
    );
    if (index === -1) {
      throw new Error("Product not found");
    }
    const [removed] = mock.products.splice(index, 1);
    return { message: "Product deleted", product: removed };
  },
  "most-selling-products": async () => getTopProducts(),
  "most-frequent-customers": async () => getTopCustomers(),
  "track-inventory": async () => mock.inventory,
  "list-orders": async () =>
    mock.orders.filter((order) =>
      ["pending", "processing"].includes(order.status)
    ),
  "update-order-status": async (payload) => {
    const order = mock.orders.find((item) => item.order_id === payload.order_id);
    if (!order) {
      throw new Error("Order not found");
    }
    order.status = payload.status;
    return { message: "Order updated", order };
  },
  "payment-status": async () => {
    return [...mock.payments].sort((a, b) =>
      String(b.created_at).localeCompare(String(a.created_at))
    );
  },
  "create-order": async (payload) => {
    const listing = getListingById(payload.seller_product_id);
    if (!listing) {
      throw new Error("Listing not found");
    }
    const quantity = Math.max(1, toNumber(payload.quantity, 1));
    const cgstRate = Math.max(0, toNumber(payload.cgst_rate, DEFAULT_GST_RATE));
    const sgstRate = Math.max(0, toNumber(payload.sgst_rate, DEFAULT_GST_RATE));
    if (listing.stock !== undefined && listing.stock !== null && quantity > listing.stock) {
      throw new Error("Requested quantity exceeds stock");
    }
    const totals = calculateTotals(listing.price, quantity, cgstRate, sgstRate);
    const nextOrderId =
      Math.max(0, ...mock.orders.map((item) => item.order_id)) + 1;
    const order = {
      order_id: nextOrderId,
      customer_id: payload.customer_id,
      status: "pending",
      total_amount: totals.total,
    };
    mock.orders.push(order);
    mock.orderItems.push({
      seller_product_id: listing.seller_product_id,
      product_id: listing.product_id,
      quantity,
      unit_price: listing.price,
      line_total: totals.subtotal,
    });
    if (listing.stock !== undefined && listing.stock !== null) {
      listing.stock = Math.max(0, listing.stock - quantity);
    }
    return {
      message: "Order created",
      order,
      summary: {
        order_id: order.order_id,
        product: mock.products.find((item) => item.product_id === listing.product_id)
          ?.name,
        seller: listing.seller,
        unit_price: listing.price,
        quantity,
        line_total: totals.subtotal,
        cgst_rate: cgstRate,
        cgst_amount: totals.cgst,
        sgst_rate: sgstRate,
        sgst_amount: totals.sgst,
        total_payable: totals.total,
      },
    };
  },
};

async function apiRequest(path, method, payload) {
  const base = state.apiBase || "";
  if (!base && isFileOrigin) {
    throw new Error(
      "Open the site via http://localhost:5000 or set an API base URL."
    );
  }
  const url = base ? new URL(path, base).toString() : path;
  const options = {
    method,
    headers: { "Content-Type": "application/json" },
  };
  if (payload && method !== "GET" && method !== "DELETE") {
    options.body = JSON.stringify(payload);
  }
  const response = await fetch(url, options);
  const text = await response.text();
  let data;
  try {
    data = text ? JSON.parse(text) : null;
  } catch (error) {
    data = text;
  }
  if (!response.ok) {
    throw new Error(data?.message || `Request failed: ${response.status}`);
  }
  return data;
}

const apiHandlers = {
  "add-product": async (payload) => apiRequest("/api/products", "POST", payload),
  "view-products": async () => apiRequest("/api/catalog", "GET"),
  "update-product": async (payload) =>
    apiRequest(`/api/products/${payload.product_id}`, "PUT", payload),
  "delete-product": async (payload) =>
    apiRequest(`/api/products/${payload.product_id}`, "DELETE"),
  "most-selling-products": async () =>
    apiRequest("/api/insights/top-products", "GET"),
  "most-frequent-customers": async () =>
    apiRequest("/api/insights/top-customers", "GET"),
  "track-inventory": async () => apiRequest("/api/inventory", "GET"),
  "list-orders": async () =>
    apiRequest("/api/orders?status=pending,processing", "GET"),
  "update-order-status": async (payload) =>
    apiRequest(`/api/orders/${payload.order_id}/status`, "POST", payload),
  "payment-status": async () => apiRequest("/api/payments", "GET"),
  "create-order": async (payload) => apiRequest("/api/orders", "POST", payload),
};

const tableTitles = {
  "view-products": "Catalog with prices",
  "most-selling-products": "Top selling products",
  "most-frequent-customers": "Most frequent customers",
  "track-inventory": "Inventory overview",
  "list-orders": "Pending orders",
  "payment-status": "Recent payments",
  "create-order": "Order summary",
};

const tableConfigs = {
  "view-products": {
    columns: [
      "product_id",
      "sku",
      "name",
      "category_id",
      "seller",
      "price",
      "stock",
      "created_at",
    ],
    action: { label: "Order", field: "seller_product_id" },
  },
  "most-selling-products": { columns: ["name", "sold"] },
  "most-frequent-customers": { columns: ["name", "total_orders"] },
  "track-inventory": { columns: ["seller", "product", "stock"] },
  "list-orders": { columns: ["order_id", "status", "total_amount", "placed_at"] },
  "payment-status": {
    columns: ["payment_id", "order_id", "method", "status", "amount", "created_at"],
  },
  "create-order": {
    columns: [
      "order_id",
      "product",
      "seller",
      "unit_price",
      "quantity",
      "line_total",
      "cgst_rate",
      "cgst_amount",
      "sgst_rate",
      "sgst_amount",
      "total_payable",
    ],
  },
};

function formatCellValue(key, value) {
  if (value === undefined || value === null || value === "") {
    return "N/A";
  }
  const currencyKeys = new Set([
    "price",
    "total_amount",
    "amount",
    "unit_price",
    "line_total",
    "cgst_amount",
    "sgst_amount",
    "total_payable",
    "subtotal",
  ]);
  const percentKeys = new Set(["cgst_rate", "sgst_rate"]);
  if (currencyKeys.has(key)) {
    return formatCurrency(value);
  }
  if (percentKeys.has(key)) {
    return formatPercent(value);
  }
  return value;
}

function clearTableView() {
  if (!dataPanel || !dataTable) {
    return;
  }
  dataPanel.hidden = true;
  dataTable.querySelector("thead").innerHTML = "";
  dataTable.querySelector("tbody").innerHTML = "";
  if (tableEmpty) {
    tableEmpty.style.display = "block";
  }
}

function renderTable(action, rows) {
  if (!dataPanel || !dataTable || !Array.isArray(rows) || rows.length === 0) {
    clearTableView();
    return;
  }

  lastTableAction = action;

  const config = tableConfigs[action] || {};
  const columns = (config.columns || Object.keys(rows[0] || {})).filter((column) =>
    rows.some((row) => row[column] !== undefined)
  );
  const actionConfig = config.action;
  const showAction =
    actionConfig && rows.some((row) => row[actionConfig.field] !== undefined);

  dataPanel.hidden = false;
  if (dataTitle) {
    dataTitle.textContent = tableTitles[action] || "Latest results";
  }
  if (dataSubtitle) {
    dataSubtitle.textContent = `Rows: ${rows.length}`;
  }
  if (tableEmpty) {
    tableEmpty.style.display = "none";
  }

  const thead = dataTable.querySelector("thead");
  const tbody = dataTable.querySelector("tbody");
  thead.innerHTML = "";
  tbody.innerHTML = "";

  const headerRow = document.createElement("tr");
  columns.forEach((column) => {
    const th = document.createElement("th");
    th.textContent = column.replace(/_/g, " ");
    headerRow.appendChild(th);
  });
  if (showAction) {
    const th = document.createElement("th");
    th.textContent = "Action";
    headerRow.appendChild(th);
  }
  thead.appendChild(headerRow);

  rows.forEach((row) => {
    const tr = document.createElement("tr");
    columns.forEach((column) => {
      const td = document.createElement("td");
      td.textContent = formatCellValue(column, row[column]);
      tr.appendChild(td);
    });
    if (showAction) {
      const td = document.createElement("td");
      const button = document.createElement("button");
      button.className = "btn btn--mini btn--accent";
      button.type = "button";
      button.textContent = actionConfig.label || "Select";
      const actionValue = row[actionConfig.field];
      if (actionValue !== undefined && actionValue !== null) {
        button.addEventListener("click", () => {
          selectCatalogItem(actionValue);
        });
      } else {
        button.disabled = true;
      }
      td.appendChild(button);
      tr.appendChild(td);
    }
    tbody.appendChild(tr);
  });
}

function getTableData(action, data) {
  if (Array.isArray(data)) {
    return data;
  }
  if (action === "create-order" && data?.summary) {
    return [data.summary];
  }
  return null;
}

function buildSuccessMessage(summary) {
  if (!summary) {
    return "Order placed successfully.";
  }
  const orderId = summary.order_id ? `Order #${summary.order_id}` : "Order";
  const productLabel = summary.product ? ` for ${summary.product}` : "";
  const sellerLabel = summary.seller ? ` (${summary.seller})` : "";
  const totalLabel =
    summary.total_payable !== undefined && summary.total_payable !== null
      ? ` Total payable: ${formatCurrency(summary.total_payable)}.`
      : "";
  return `${orderId}${productLabel}${sellerLabel} confirmed.${totalLabel}`;
}

function showSuccessToast(summary) {
  if (!successToast) {
    return;
  }
  if (toastTitle) {
    toastTitle.textContent = "Payment successful";
  }
  if (toastMessage) {
    toastMessage.textContent = buildSuccessMessage(summary);
  }
  successToast.hidden = false;
  document.body.classList.add("toast-open");
  toastOk?.focus();
}

function hideSuccessToast() {
  if (!successToast) {
    return;
  }
  successToast.hidden = true;
  document.body.classList.remove("toast-open");
}

function showErrorToast(message) {
  const errorToast = document.getElementById("errorToast");
  if (!errorToast) {
    return;
  }
  const errorToastTitle = document.getElementById("errorToastTitle");
  const errorToastMessage = document.getElementById("errorToastMessage");
  if (errorToastTitle) {
    errorToastTitle.textContent = "Order failed";
  }
  if (errorToastMessage) {
    errorToastMessage.textContent = message || "Something went wrong. Please try again.";
  }
  errorToast.hidden = false;
  document.body.classList.add("toast-open");
  document.getElementById("errorToastOk")?.focus();
}

function hideErrorToast() {
  const errorToast = document.getElementById("errorToast");
  if (!errorToast) {
    return;
  }
  errorToast.hidden = true;
  document.body.classList.remove("toast-open");
}

function applyLocalStockDelta(sellerProductId, quantity) {
  if (!sellerProductId) {
    return;
  }
  const qty = Math.max(1, toNumber(quantity, 1));
  const listing = catalogById.get(String(sellerProductId));
  if (listing && listing.stock !== undefined && listing.stock !== null) {
    listing.stock = Math.max(0, Number(listing.stock) - qty);
  }
  const listIndex = catalogItems.findIndex(
    (item) => String(item.seller_product_id) === String(sellerProductId)
  );
  if (listIndex >= 0) {
    const current = catalogItems[listIndex];
    if (current.stock !== undefined && current.stock !== null) {
      current.stock = Math.max(0, Number(current.stock) - qty);
    }
  }
  if (state.demo && listing) {
    const productName =
      listing.name ||
      mock.products.find((item) => item.product_id === listing.product_id)?.name;
    const inventoryRow = mock.inventory.find(
      (row) => row.seller === listing.seller && row.product === productName
    );
    if (inventoryRow && inventoryRow.stock !== undefined && inventoryRow.stock !== null) {
      inventoryRow.stock = Math.max(0, Number(inventoryRow.stock) - qty);
    } else if (productName) {
      mock.inventory.push({
        seller: listing.seller || "Seller",
        product: productName,
        stock:
          listing.stock !== undefined && listing.stock !== null
            ? Number(listing.stock)
            : 0,
      });
    }
  }
  if (catalogItems.length) {
    updateCatalogSelect(catalogItems);
  }
  updateOrderSummary();
  if (lastTableAction === "view-products" && dataPanel && !dataPanel.hidden) {
    renderTable("view-products", catalogItems);
  }
}

async function refreshInventoryTable() {
  if (lastTableAction !== "track-inventory" || !dataPanel || dataPanel.hidden) {
    return;
  }
  try {
    const rows = state.demo ? mock.inventory : await apiRequest("/api/inventory", "GET");
    renderTable("track-inventory", rows);
  } catch (error) {
    logLine("Error: track-inventory", error?.message || error);
  }
}

async function dispatch(action, payload, sourceEl) {
  const button =
    sourceEl?.tagName === "FORM"
      ? sourceEl.querySelector("button[type=submit]")
      : sourceEl;
  if (button) {
    button.disabled = true;
  }

  try {
    const data = state.demo
      ? await demoHandlers[action](payload)
      : await apiHandlers[action](payload);
    logLine(`Action: ${action}`, data);
    refreshStats();
    const tableData = getTableData(action, data);
    if (tableData) {
      renderTable(action, tableData);
    }
    if (action === "create-order") {
      showSuccessToast(data?.summary || data?.order || data);
      applyLocalStockDelta(payload?.seller_product_id, data?.summary?.quantity || payload?.quantity);
      await refreshInventoryTable();
    }
    if (["add-product", "delete-product", "update-product", "create-order"].includes(action)) {
      await loadCatalog();
    }
  } catch (error) {
    logLine(`Error: ${action}`, error?.message || error);
    if (action === "create-order") {
      showErrorToast(error?.message || "Order could not be placed. Please try again.");
    }
  } finally {
    if (button) {
      button.disabled = false;
    }
  }
}

document.querySelectorAll("[data-action]").forEach((element) => {
  const action = element.dataset.action;
  if (element.tagName === "FORM") {
    element.addEventListener("submit", async (event) => {
      event.preventDefault();
      const formData = new FormData(element);
      const payload = normalizePayload(Object.fromEntries(formData.entries()));
      // Remove shipping_address_id if empty to allow NULL in database
      if (!payload.shipping_address_id || payload.shipping_address_id === 0 || payload.shipping_address_id === "") {
        delete payload.shipping_address_id;
      }
      await dispatch(action, payload, element);
      if (action !== "create-order") {
        element.reset();
      }
    });
  } else {
    element.addEventListener("click", async () => {
      await dispatch(action, {}, element);
    });
  }
});

const demoToggle = document.getElementById("demoToggle");
const connectToggle = document.getElementById("connectToggle");
const apiPanel = document.getElementById("apiPanel");
const apiBaseInput = document.getElementById("apiBase");
const saveApi = document.getElementById("saveApi");
const clearConsole = document.getElementById("clearConsole");
const dataPanel = document.getElementById("dataPanel");
const dataTitle = document.getElementById("dataTitle");
const dataSubtitle = document.getElementById("dataSubtitle");
const dataTable = document.getElementById("dataTable");
const tableEmpty = document.getElementById("tableEmpty");
const clearTable = document.getElementById("clearTable");
const orderForm = document.getElementById("orderForm");
const orderProduct = document.getElementById("orderProduct");
const orderQty = document.getElementById("orderQty");
const orderUnitPrice = document.getElementById("orderUnitPrice");
const orderSubtotal = document.getElementById("orderSubtotal");
const orderCgst = document.getElementById("orderCgst");
const orderSgst = document.getElementById("orderSgst");
const orderStock = document.getElementById("orderStock");
const orderTotal = document.getElementById("orderTotal");
const cgstRateInput = document.getElementById("cgstRate");
const sgstRateInput = document.getElementById("sgstRate");
const orderHint = document.getElementById("orderHint");
const refreshCatalog = document.getElementById("refreshCatalog");
const orderSubmit = orderForm?.querySelector("button[type=submit]");
const successToast = document.getElementById("successToast");
const toastTitle = document.getElementById("toastTitle");
const toastMessage = document.getElementById("toastMessage");
const toastOk = document.getElementById("toastOk");
const toastClose = document.getElementById("toastClose");

refreshStats();
updateStatusLabel();

if (apiBaseInput) {
  apiBaseInput.value = state.apiBase;
}

logLine("Boot", "Console online. Demo data loaded.");
loadCatalog();

if (clearTable) {
  clearTable.addEventListener("click", () => {
    clearTableView();
  });
}

if (refreshCatalog) {
  refreshCatalog.addEventListener("click", () => {
    loadCatalog();
  });
}

if (toastOk) {
  toastOk.addEventListener("click", () => {
    hideSuccessToast();
  });
}

if (toastClose) {
  toastClose.addEventListener("click", () => {
    hideSuccessToast();
  });
}

if (successToast) {
  successToast.addEventListener("click", (event) => {
    if (event.target === successToast) {
      hideSuccessToast();
    }
  });
}

const errorToastEl = document.getElementById("errorToast");
const errorToastOkEl = document.getElementById("errorToastOk");
const errorToastCloseEl = document.getElementById("errorToastClose");

if (errorToastOkEl) {
  errorToastOkEl.addEventListener("click", () => {
    hideErrorToast();
  });
}

if (errorToastCloseEl) {
  errorToastCloseEl.addEventListener("click", () => {
    hideErrorToast();
  });
}

if (errorToastEl) {
  errorToastEl.addEventListener("click", (event) => {
    if (event.target === errorToastEl) {
      hideErrorToast();
    }
  });
}

[orderProduct, orderQty, cgstRateInput, sgstRateInput].forEach((input) => {
  if (!input) {
    return;
  }
  input.addEventListener("input", () => {
    updateOrderSummary();
  });
  input.addEventListener("change", () => {
    updateOrderSummary();
  });
});

if (demoToggle) {
  demoToggle.addEventListener("click", () => {
    state.demo = !state.demo;
    demoToggle.textContent = state.demo ? "Demo mode: On" : "Demo mode: Off";
    updateStatusLabel();
    logLine("Mode", state.demo ? "Demo mode enabled" : "API mode enabled");
    loadCatalog();
  });
}

if (connectToggle) {
  connectToggle.addEventListener("click", () => {
    apiPanel.hidden = !apiPanel.hidden;
  });
}

if (saveApi) {
  saveApi.addEventListener("click", () => {
    state.apiBase = apiBaseInput.value.trim();
    if (state.apiBase) {
      localStorage.setItem("apiBase", state.apiBase);
      logLine("API base set", state.apiBase);
    } else {
      localStorage.removeItem("apiBase");
      logLine("API base", "Cleared");
    }
    loadCatalog();
  });
}

if (clearConsole) {
  clearConsole.addEventListener("click", () => {
    logs.length = 0;
    consoleEl.textContent = "Console cleared.";
  });
}
