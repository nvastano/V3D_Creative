const ADMIN_KEY = 'eKw4FTjnfLHIwBO';

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

function authed(url) {
  return url.searchParams.get('key') === ADMIN_KEY;
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: CORS });
    }

    // ── Orders ────────────────────────────────────────────────────────────────

    if (request.method === 'GET' && url.pathname === '/orders') {
      if (!authed(url)) return json({ error: 'Unauthorized' }, 401);
      const { results } = await env.DB.prepare('SELECT * FROM orders ORDER BY id DESC').all();
      return json(results);
    }

    if (request.method === 'POST' && url.pathname === '/orders') {
      let data;
      try { data = await request.json(); } catch { return json({ error: 'Invalid JSON' }, 400); }

      if (authed(url)) {
        await env.DB.prepare(
          `INSERT INTO orders (received_at, product, customer_name, email, quantity, total_price, details, source)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)`
        ).bind(
          data.received_at || new Date().toISOString().replace('T', ' ').slice(0, 19),
          data.product || '', data.customer_name || '', data.email || '',
          parseInt(data.quantity) || 1, data.total_price || '',
          data.details || '{}', data.source || 'Admin'
        ).run();
        return json({ success: true });
      }

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

    const orderMatch = /^\/orders\/(\d+)$/.exec(url.pathname);
    if (orderMatch) {
      if (!authed(url)) return json({ error: 'Unauthorized' }, 401);
      const id = orderMatch[1];
      if (request.method === 'PUT') {
        let data;
        try { data = await request.json(); } catch { return json({ error: 'Invalid JSON' }, 400); }
        await env.DB.prepare(
          `UPDATE orders SET product=?, customer_name=?, email=?, quantity=?, total_price=?, details=?, source=?, received_at=? WHERE id=?`
        ).bind(
          data.product || '', data.customer_name || '', data.email || '',
          parseInt(data.quantity) || 1, data.total_price || '',
          data.details || '{}', data.source || '', data.received_at || '', id
        ).run();
        return json({ success: true });
      }
      if (request.method === 'DELETE') {
        await env.DB.prepare('DELETE FROM orders WHERE id=?').bind(id).run();
        return json({ success: true });
      }
    }

    // ── Inventory ─────────────────────────────────────────────────────────────

    // GET /inventory — public: list all items with claim counts
    if (request.method === 'GET' && url.pathname === '/inventory') {
      const { results } = await env.DB.prepare(`
        SELECT i.*,
          COUNT(CASE WHEN c.status IN ('pending','paid') THEN 1 END) AS claimed_count
        FROM inventory i
        LEFT JOIN claims c ON c.inventory_id = i.id
        GROUP BY i.id
        ORDER BY i.id DESC
      `).all();
      return json(results);
    }

    // POST /inventory?key= — admin: create item
    if (request.method === 'POST' && url.pathname === '/inventory') {
      if (!authed(url)) return json({ error: 'Unauthorized' }, 401);
      let data;
      try { data = await request.json(); } catch { return json({ error: 'Invalid JSON' }, 400); }
      await env.DB.prepare(
        `INSERT INTO inventory (name, description, price, color, image_url, quantity) VALUES (?, ?, ?, ?, ?, ?)`
      ).bind(
        data.name || '', data.description || '', parseFloat(data.price) || 0,
        data.color || '', data.image_url || '', parseInt(data.quantity) || 1
      ).run();
      return json({ success: true });
    }

    const invMatch = /^\/inventory\/(\d+)$/.exec(url.pathname);
    if (invMatch) {
      const id = invMatch[1];

      // PUT /inventory/:id?key= — admin: update item
      if (request.method === 'PUT') {
        if (!authed(url)) return json({ error: 'Unauthorized' }, 401);
        let data;
        try { data = await request.json(); } catch { return json({ error: 'Invalid JSON' }, 400); }
        await env.DB.prepare(
          `UPDATE inventory SET name=?, description=?, price=?, color=?, image_url=?, quantity=? WHERE id=?`
        ).bind(
          data.name || '', data.description || '', parseFloat(data.price) || 0,
          data.color || '', data.image_url || '', parseInt(data.quantity) || 1, id
        ).run();
        return json({ success: true });
      }

      // DELETE /inventory/:id?key= — admin: delete item and its claims
      if (request.method === 'DELETE') {
        if (!authed(url)) return json({ error: 'Unauthorized' }, 401);
        await env.DB.prepare('DELETE FROM claims WHERE inventory_id=?').bind(id).run();
        await env.DB.prepare('DELETE FROM inventory WHERE id=?').bind(id).run();
        return json({ success: true });
      }
    }

    // ── Claims ────────────────────────────────────────────────────────────────

    // GET /claims?key= — admin: list all claims with item info
    if (request.method === 'GET' && url.pathname === '/claims') {
      if (!authed(url)) return json({ error: 'Unauthorized' }, 401);
      const { results } = await env.DB.prepare(`
        SELECT c.*, i.name AS item_name, i.price AS item_price, i.color AS item_color
        FROM claims c
        JOIN inventory i ON i.id = c.inventory_id
        ORDER BY c.id DESC
      `).all();
      return json(results);
    }

    // POST /claims — public: claim an item
    if (request.method === 'POST' && url.pathname === '/claims') {
      let data;
      try { data = await request.json(); } catch { return json({ error: 'Invalid JSON' }, 400); }
      if (!data.inventory_id || !data.claimer_name) return json({ error: 'Missing fields' }, 400);

      // Check availability
      const item = await env.DB.prepare('SELECT * FROM inventory WHERE id=?').bind(data.inventory_id).first();
      if (!item) return json({ error: 'Item not found' }, 404);
      const { count } = await env.DB.prepare(
        `SELECT COUNT(*) AS count FROM claims WHERE inventory_id=? AND status IN ('pending','paid')`
      ).bind(data.inventory_id).first();
      if (count >= item.quantity) return json({ error: 'No longer available' }, 409);

      await env.DB.prepare(
        `INSERT INTO claims (inventory_id, claimer_name) VALUES (?, ?)`
      ).bind(data.inventory_id, data.claimer_name.trim()).run();
      return json({ success: true, item_name: item.name, price: item.price });
    }

    const claimMatch = /^\/claims\/(\d+)$/.exec(url.pathname);
    if (claimMatch) {
      if (!authed(url)) return json({ error: 'Unauthorized' }, 401);
      const id = claimMatch[1];

      // PUT /claims/:id?key= — admin: update status
      if (request.method === 'PUT') {
        let data;
        try { data = await request.json(); } catch { return json({ error: 'Invalid JSON' }, 400); }
        await env.DB.prepare('UPDATE claims SET status=? WHERE id=?').bind(data.status || 'pending', id).run();
        return json({ success: true });
      }

      // DELETE /claims/:id?key= — admin: remove claim
      if (request.method === 'DELETE') {
        await env.DB.prepare('DELETE FROM claims WHERE id=?').bind(id).run();
        return json({ success: true });
      }
    }

    return json({ error: 'Not found' }, 404);
  },
};
