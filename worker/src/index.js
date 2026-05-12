const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
};

function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { ...CORS, 'Content-Type': 'application/json' },
  });
}

function authed(url, env) {
  return url.searchParams.get('key') === env.ADMIN_KEY;
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: CORS });
    }

    // GET /orders?key=... — list all orders (admin)
    if (request.method === 'GET' && url.pathname === '/orders') {
      if (!authed(url, env)) return json({ error: 'Unauthorized' }, 401);
      const { results } = await env.DB.prepare(
        'SELECT * FROM orders ORDER BY id DESC'
      ).all();
      return json(results);
    }

    // POST /orders — new order from customer form
    if (request.method === 'POST' && url.pathname === '/orders') {
      let data;
      try { data = await request.json(); } catch { return json({ error: 'Invalid JSON' }, 400); }

      // Admin creating order directly
      if (authed(url, env)) {
        await env.DB.prepare(
          `INSERT INTO orders (received_at, product, customer_name, email, quantity, total_price, details, source)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)`
        ).bind(
          data.received_at || new Date().toISOString().replace('T', ' ').slice(0, 19),
          data.product || '',
          data.customer_name || '',
          data.email || '',
          parseInt(data.quantity) || 1,
          data.total_price || '',
          data.details || '{}',
          data.source || 'Admin'
        ).run();
        return json({ success: true });
      }

      // Customer form submission
      if (!data.productName || !data.name) return json({ error: 'Missing required fields' }, 400);
      const details = { ...data };
      delete details.productName; delete details.name; delete details.email;
      delete details.quantity; delete details.totalPrice; delete details.timestamp;
      await env.DB.prepare(
        `INSERT INTO orders (product, customer_name, email, quantity, total_price, details)
         VALUES (?, ?, ?, ?, ?, ?)`
      ).bind(
        data.productName, data.name, data.email || '',
        parseInt(data.quantity) || 1, data.totalPrice || '',
        JSON.stringify(details)
      ).run();
      return json({ success: true });
    }

    // PUT /orders/:id?key=... — update an order (admin)
    const idMatch = /^\/orders\/(\d+)$/.exec(url.pathname);
    if (idMatch) {
      if (!authed(url, env)) return json({ error: 'Unauthorized' }, 401);
      const id = idMatch[1];

      if (request.method === 'PUT') {
        let data;
        try { data = await request.json(); } catch { return json({ error: 'Invalid JSON' }, 400); }
        await env.DB.prepare(
          `UPDATE orders SET product=?, customer_name=?, email=?, quantity=?, total_price=?, details=?, source=?, received_at=? WHERE id=?`
        ).bind(
          data.product || '', data.customer_name || '', data.email || '',
          parseInt(data.quantity) || 1, data.total_price || '',
          data.details || '{}', data.source || '', data.received_at || '',
          id
        ).run();
        return json({ success: true });
      }

      if (request.method === 'DELETE') {
        await env.DB.prepare('DELETE FROM orders WHERE id=?').bind(id).run();
        return json({ success: true });
      }
    }

    return json({ error: 'Not found' }, 404);
  },
};
