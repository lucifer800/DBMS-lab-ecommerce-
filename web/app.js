const origin = window.location.origin;
const isFileOrigin = origin === "null" || origin.startsWith("file:");
const defaultApiBase = isFileOrigin ? "" : origin;

const state = {
  demo: true,
  apiBase: defaultApiBase,
};

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
    { product_id: 101, quantity: 6 },
    { product_id: 102, quantity: 4 },
    { product_id: 101, quantity: 2 },
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
    { seller: "Northwind", product: "Aurora Lamp", stock: 14 },
    { seller: "Skyline", product: "Vault Backpack", stock: 6 },
  ],
};

const consoleEl = document.getElementById("consoleOutput");
const apiStatusEl = document.getElementById("apiStatus");
const statOrders = document.getElementById("statOrders");
const statProducts = document.getElementById("statProducts");
const statPayments = document.getElementById("statPayments");
const logs = [];

function updateStatusLabel() {
  apiStatusEl.textContent = state.demo ? "Demo" : "API";
}

function refreshStats() {
  statOrders.textContent = mock.orders.length.toString();
  statProducts.textContent = mock.products.length.toString();
  statPayments.textContent = mock.payments.length.toString();
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
  return normalized;
}

function getTopProducts() {
  const totals = {};
  for (const item of mock.orderItems) {
    totals[item.product_id] = (totals[item.product_id] || 0) + item.quantity;
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
    return { message: "Product added", product };
  },
  "view-products": async () => mock.products,
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
  "view-products": async () => apiRequest("/api/products", "GET"),
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
};

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
  } catch (error) {
    logLine(`Error: ${action}`, error?.message || error);
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
      await dispatch(action, payload, element);
      element.reset();
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

refreshStats();
updateStatusLabel();

if (apiBaseInput) {
  apiBaseInput.value = state.apiBase;
}

logLine("Boot", "Console online. Demo data loaded.");

if (demoToggle) {
  demoToggle.addEventListener("click", () => {
    state.demo = !state.demo;
    demoToggle.textContent = state.demo ? "Demo mode: On" : "Demo mode: Off";
    updateStatusLabel();
    logLine("Mode", state.demo ? "Demo mode enabled" : "API mode enabled");
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
      logLine("API base set", state.apiBase);
    } else {
      logLine("API base", "Cleared");
    }
  });
}

if (clearConsole) {
  clearConsole.addEventListener("click", () => {
    logs.length = 0;
    consoleEl.textContent = "Console cleared.";
  });
}
