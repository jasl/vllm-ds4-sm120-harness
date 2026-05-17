const http = require('http');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const DATA_FILE = path.join(__dirname, 'tickets.json');
const PORT = process.env.PORT || 8080;
const HOST = '127.0.0.1';

// Load existing tickets or start with empty array
let tickets = [];
try {
  const raw = fs.readFileSync(DATA_FILE, 'utf8');
  tickets = JSON.parse(raw);
} catch (err) {
  if (err.code !== 'ENOENT') {
    console.error('Failed to load tickets.json:', err.message);
    process.exit(1);
  }
  // File does not exist – start with empty list
}

function saveTickets() {
  fs.writeFileSync(DATA_FILE, JSON.stringify(tickets, null, 2), 'utf8');
}

function sendJSON(res, status, data) {
  res.writeHead(status, {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
  });
  res.end(JSON.stringify(data));
}

const server = http.createServer((req, res) => {
  // CORS preflight
  if (req.method === 'OPTIONS') {
    res.writeHead(204, {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    });
    res.end();
    return;
  }

  const parsedUrl = new URL(req.url, `http://${req.headers.host || 'localhost'}`);
  const pathname = parsedUrl.pathname;
  const method = req.method.toUpperCase();

  // ---------- routes ----------

  // GET /tickets
  if (method === 'GET' && pathname === '/tickets') {
    const statusFilter = parsedUrl.searchParams.get('status');
    const priorityFilter = parsedUrl.searchParams.get('priority');

    let result = tickets;

    if (statusFilter) {
      if (!['open', 'in_progress', 'resolved'].includes(statusFilter)) {
        sendJSON(res, 400, { error: 'Invalid status filter' });
        return;
      }
      result = result.filter(t => t.status === statusFilter);
    }
    if (priorityFilter) {
      if (!['low', 'medium', 'high'].includes(priorityFilter)) {
        sendJSON(res, 400, { error: 'Invalid priority filter' });
        return;
      }
      result = result.filter(t => t.priority === priorityFilter);
    }

    sendJSON(res, 200, result);
    return;
  }

  // GET /metrics
  if (method === 'GET' && pathname === '/metrics') {
    const now = new Date();
    const metrics = {
      byStatus: { open: 0, in_progress: 0, resolved: 0 },
      byPriority: { low: 0, medium: 0, high: 0 },
      averageAgeOpenSeconds: 0,
    };

    let totalAge = 0;
    let openCount = 0;

    for (const t of tickets) {
      metrics.byStatus[t.status]++;
      metrics.byPriority[t.priority]++;
      if (t.status === 'open') {
        totalAge += (now - new Date(t.created_at)) / 1000;
        openCount++;
      }
    }

    if (openCount > 0) {
      metrics.averageAgeOpenSeconds = totalAge / openCount;
    }

    sendJSON(res, 200, metrics);
    return;
  }

  // POST /tickets
  if (method === 'POST' && pathname === '/tickets') {
    let body = '';
    req.on('data', chunk => (body += chunk));
    req.on('end', () => {
      let data;
      try {
        data = JSON.parse(body);
      } catch (e) {
        sendJSON(res, 400, { error: 'Invalid JSON' });
        return;
      }

      // Validate required fields
      if (!data.subject || typeof data.subject !== 'string' || data.subject.trim() === '') {
        sendJSON(res, 400, { error: 'subject is required and must be a non-empty string' });
        return;
      }
      if (!data.description || typeof data.description !== 'string' || data.description.trim() === '') {
        sendJSON(res, 400, { error: 'description is required and must be a non-empty string' });
        return;
      }

      // Apply defaults
      const now = new Date().toISOString();
      const priority = ['low', 'medium', 'high'].includes(data.priority) ? data.priority : 'medium';
      const status = ['open', 'in_progress', 'resolved'].includes(data.status) ? data.status : 'open';

      const ticket = {
        id: crypto.randomUUID(),
        subject: data.subject.trim(),
        description: data.description.trim(),
        priority,
        status,
        created_at: now,
        updated_at: now,
      };

      tickets.push(ticket);
      saveTickets();
      sendJSON(res, 201, ticket);
    });
    return;
  }

  // /tickets/:id
  const ticketMatch = pathname.match(/^\/tickets\/([^/]+)$/);
  if (ticketMatch) {
    const id = ticketMatch[1];
    const idx = tickets.findIndex(t => t.id === id);
    const ticket = tickets[idx];

    // GET /tickets/:id
    if (method === 'GET') {
      if (!ticket) {
        sendJSON(res, 404, { error: 'Ticket not found' });
        return;
      }
      sendJSON(res, 200, ticket);
      return;
    }

    // PATCH /tickets/:id
    if (method === 'PATCH') {
      if (!ticket) {
        sendJSON(res, 404, { error: 'Ticket not found' });
        return;
      }

      let body = '';
      req.on('data', chunk => (body += chunk));
      req.on('end', () => {
        let updates;
        try {
          updates = JSON.parse(body);
        } catch (e) {
          sendJSON(res, 400, { error: 'Invalid JSON' });
          return;
        }

        // Validate and apply each editable field
        if (updates.subject !== undefined) {
          if (typeof updates.subject !== 'string' || updates.subject.trim() === '') {
            sendJSON(res, 400, { error: 'subject must be a non-empty string' });
            return;
          }
          ticket.subject = updates.subject.trim();
        }
        if (updates.description !== undefined) {
          if (typeof updates.description !== 'string' || updates.description.trim() === '') {
            sendJSON(res, 400, { error: 'description must be a non-empty string' });
            return;
          }
          ticket.description = updates.description.trim();
        }
        if (updates.priority !== undefined) {
          if (!['low', 'medium', 'high'].includes(updates.priority)) {
            sendJSON(res, 400, { error: 'priority must be one of: low, medium, high' });
            return;
          }
          ticket.priority = updates.priority;
        }
        if (updates.status !== undefined) {
          if (!['open', 'in_progress', 'resolved'].includes(updates.status)) {
            sendJSON(res, 400, { error: 'status must be one of: open, in_progress, resolved' });
            return;
          }
          ticket.status = updates.status;
        }

        ticket.updated_at = new Date().toISOString();
        tickets[idx] = ticket;
        saveTickets();
        sendJSON(res, 200, ticket);
      });
      return;
    }

    // DELETE /tickets/:id
    if (method === 'DELETE') {
      if (!ticket) {
        sendJSON(res, 404, { error: 'Ticket not found' });
        return;
      }
      tickets.splice(idx, 1);
      saveTickets();
      sendJSON(res, 200, { message: 'Ticket deleted' });
      return;
    }

    // Unsupported method on /tickets/:id
    sendJSON(res, 405, { error: 'Method not allowed' });
    return;
  }

  // Catch-all: route not found
  sendJSON(res, 404, { error: 'Not found' });
});

server.listen(PORT, HOST, () => {
  console.log(`Server running at http://${HOST}:${PORT}/`);
});
