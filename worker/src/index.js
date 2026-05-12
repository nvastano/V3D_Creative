const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
};

function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { ...CORS, 'Content-Type': 'application/json' },
  });
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: CORS });
    }

    // POST /orders — save a new order
    if (request.method === 'POST' && url.pathname === '/orders') {
      let data;
      try {
        data = await request.json();
      } catch {
        return json({ error: 'Invalid JSON' }, 400);
      }

      if (!data.productName || !data.name || !data.email) {
        return json({ error: 'Missing required fields' }, 400);
      }

      // Store the full order details as JSON so nothing is lost
      const details = { ...data };
      delete details.productName;
      delete details.name;
      delete details.email;
      delete details.quantity;
      delete details.totalPrice;
      delete details.timestamp;

      await env.DB.prepare(
        `INSERT INTO orders (product, customer_name, email, quantity, total_price, details)
         VALUES (?, ?, ?, ?, ?, ?)`
      ).bind(
        data.productName,
        data.name,
        data.email,
        parseInt(data.quantity) || 1,
        data.totalPrice || '',
        JSON.stringify(details)
      ).run();

      return json({ success: true });
    }

    // GET /orders?key=ADMIN_KEY — fetch all orders for admin page
    if (request.method === 'GET' && url.pathname === '/orders') {
      if (url.searchParams.get('key') !== env.ADMIN_KEY) {
        return json({ error: 'Unauthorized' }, 401);
      }
      const { results } = await env.DB.prepare(
        'SELECT * FROM orders ORDER BY id DESC'
      ).all();
      return json(results);
    }

    return json({ error: 'Not found' }, 404);
  },
};
