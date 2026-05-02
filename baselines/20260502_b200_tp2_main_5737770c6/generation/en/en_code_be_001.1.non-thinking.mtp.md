# Generation Transcript

- Case: `en_code_be_001`
- Language group: `en`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `1`
- Thinking mode: `non-thinking`
- Thinking strength: `disabled`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 8.233089
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 318, "total_tokens": 2698, "completion_tokens": 2380, "prompt_tokens_details": null}`
- Prompt tokens: 318
- Completion tokens: 2380
- Total tokens: 2698

## Prompt

```markdown
Write a single-file Node.js HTTP server named `server.js`. Use only built-in Node.js modules; no Express, no npm packages. Keep the code under 1,000 lines.

Task: implement a small JSON API for a help-desk ticket queue stored in a local JSON file.

Data model:
- Ticket: `id`, `subject`, `description`, `priority` (`low`, `medium`, `high`), `status` (`open`, `in_progress`, `resolved`), `created_at`, `updated_at`.

API requirements:
1. `GET /tickets` with optional query params `status` and `priority`.
2. `POST /tickets` to create a ticket. Validate required fields.
3. `GET /tickets/{id}` to fetch one ticket.
4. `PATCH /tickets/{id}` to update `subject`, `description`, `priority`, or `status`.
5. `DELETE /tickets/{id}` to delete a ticket.
6. `GET /metrics` returning counts by status and priority plus average age of open tickets in seconds.

Engineering requirements:
- Read/write a `tickets.json` file safely enough for sequential requests.
- Return JSON for all responses, including errors.
- Include CORS headers for local browser testing.
- Handle invalid JSON, unknown routes, unsupported methods, and missing IDs.
- Start on `127.0.0.1:8080` by default.

Output only the complete JavaScript code. Do not include explanations.
```

## Assistant

````markdown
```javascript
const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = 8080;
const HOST = '127.0.0.1';
const DATA_FILE = path.join(__dirname, 'tickets.json');

class TicketStore {
  constructor(filePath) {
    this.filePath = filePath;
    this.tickets = [];
    this.writeLock = false;
    this.pendingWrites = [];
    this.load();
  }

  load() {
    try {
      if (fs.existsSync(this.filePath)) {
        const data = fs.readFileSync(this.filePath, 'utf8');
        this.tickets = JSON.parse(data);
        this.ensureValidStructure();
      } else {
        this.tickets = [];
        this.saveSync();
      }
    } catch (err) {
      console.error('Error loading tickets:', err.message);
      this.tickets = [];
      this.saveSync();
    }
  }

  ensureValidStructure() {
    if (!Array.isArray(this.tickets)) {
      this.tickets = [];
    }
    this.tickets = this.tickets.filter(t => t && typeof t === 'object');
  }

  saveSync() {
    try {
      fs.writeFileSync(this.filePath, JSON.stringify(this.tickets, null, 2), 'utf8');
    } catch (err) {
      console.error('Error saving tickets:', err.message);
    }
  }

  async save() {
    return new Promise((resolve, reject) => {
      const doWrite = () => {
        fs.writeFile(this.filePath, JSON.stringify(this.tickets, null, 2), 'utf8', (err) => {
          this.writeLock = false;
          if (err) {
            reject(err);
            return;
          }
          resolve();
          const next = this.pendingWrites.shift();
          if (next) {
            this.writeLock = true;
            next();
          }
        });
      };

      if (this.writeLock) {
        this.pendingWrites.push(doWrite);
      } else {
        this.writeLock = true;
        doWrite();
      }
    });
  }

  getAll(status, priority) {
    let result = [...this.tickets];
    if (status) {
      result = result.filter(t => t.status === status);
    }
    if (priority) {
      result = result.filter(t => t.priority === priority);
    }
    return result;
  }

  getById(id) {
    return this.tickets.find(t => t.id === id) || null;
  }

  async create(ticketData) {
    const ticket = {
      id: this.generateId(),
      subject: ticketData.subject,
      description: ticketData.description || '',
      priority: ticketData.priority || 'medium',
      status: ticketData.status || 'open',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    };
    this.tickets.push(ticket);
    await this.save();
    return ticket;
  }

  async update(id, updates) {
    const index = this.tickets.findIndex(t => t.id === id);
    if (index === -1) return null;

    const allowedFields = ['subject', 'description', 'priority', 'status'];
    const ticket = this.tickets[index];

    for (const field of allowedFields) {
      if (updates[field] !== undefined) {
        ticket[field] = updates[field];
      }
    }
    ticket.updated_at = new Date().toISOString();
    this.tickets[index] = ticket;
    await this.save();
    return ticket;
  }

  async delete(id) {
    const index = this.tickets.findIndex(t => t.id === id);
    if (index === -1) return false;
    this.tickets.splice(index, 1);
    await this.save();
    return true;
  }

  getMetrics() {
    const now = new Date();
    const metrics = {
      by_status: { open: 0, in_progress: 0, resolved: 0 },
      by_priority: { low: 0, medium: 0, high: 0 },
      average_open_age_seconds: 0
    };

    let openTicketsCount = 0;
    let totalAgeSeconds = 0;

    for (const ticket of this.tickets) {
      if (metrics.by_status[ticket.status] !== undefined) {
        metrics.by_status[ticket.status]++;
      }
      if (metrics.by_priority[ticket.priority] !== undefined) {
        metrics.by_priority[ticket.priority]++;
      }
      if (ticket.status === 'open') {
        openTicketsCount++;
        const created = new Date(ticket.created_at);
        totalAgeSeconds += (now - created) / 1000;
      }
    }

    metrics.average_open_age_seconds = openTicketsCount > 0
      ? Math.round(totalAgeSeconds / openTicketsCount)
      : 0;

    return metrics;
  }

  generateId() {
    return Date.now().toString(36) + Math.random().toString(36).substr(2, 9);
  }
}

const store = new TicketStore(DATA_FILE);

function parseBody(req) {
  return new Promise((resolve, reject) => {
    let body = '';
    req.on('data', chunk => {
      body += chunk.toString();
    });
    req.on('end', () => {
      try {
        resolve(body ? JSON.parse(body) : {});
      } catch (err) {
        reject(new Error('Invalid JSON'));
      }
    });
    req.on('error', reject);
  });
}

function sendJSON(res, statusCode, data) {
  const body = JSON.stringify(data);
  res.writeHead(statusCode, {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Content-Length': Buffer.byteLength(body)
  });
  res.end(body);
}

function validateTicket(ticketData, isUpdate = false) {
  const errors = [];

  if (!ticketData.subject && !isUpdate) {
    errors.push('subject is required');
  }

  if (ticketData.priority && !['low', 'medium', 'high'].includes(ticketData.priority)) {
    errors.push('priority must be low, medium, or high');
  }

  if (ticketData.status && !['open', 'in_progress', 'resolved'].includes(ticketData.status)) {
    errors.push('status must be open, in_progress, or resolved');
  }

  return errors;
}

function parseId(url) {
  const match = url.match(/^\/tickets\/([a-zA-Z0-9]+)$/);
  return match ? match[1] : null;
}

function parseURL(url) {
  const [pathname, queryString] = url.split('?');
  const params = {};
  if (queryString) {
    queryString.split('&').forEach(pair => {
      const [key, value] = pair.split('=');
      if (key) params[decodeURIComponent(key)] = decodeURIComponent(value || '');
    });
  }
  return { pathname, params };
}

const server = http.createServer(async (req, res) => {
  try {
    const { pathname, params } = parseURL(req.url);
    const method = req.method.toUpperCase();

    // CORS preflight
    if (method === 'OPTIONS') {
      res.writeHead(204, {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Max-Age': '86400'
      });
      res.end();
      return;
    }

    // Routes
    if (pathname === '/tickets' && method === 'GET') {
      const status = params.status || null;
      const priority = params.priority || null;
      const tickets = store.getAll(status, priority);
      sendJSON(res, 200, tickets);

    } else if (pathname === '/tickets' && method === 'POST') {
      const body = await parseBody(req);
      const errors = validateTicket(body, false);
      if (errors.length > 0) {
        sendJSON(res, 400, { error: 'Validation failed', details: errors });
        return;
      }
      const ticket = await store.create(body);
      sendJSON(res, 201, ticket);

    } else if (pathname === '/metrics' && method === 'GET') {
      const metrics = store.getMetrics();
      sendJSON(res, 200, metrics);

    } else if (pathname.startsWith('/tickets/')) {
      const id = parseId(pathname);
      if (!id) {
        sendJSON(res, 400, { error: 'Invalid ticket ID format' });
        return;
      }

      if (method === 'GET') {
        const ticket = store.getById(id);
        if (!ticket) {
          sendJSON(res, 404, { error: 'Ticket not found' });
          return;
        }
        sendJSON(res, 200, ticket);

      } else if (method === 'PATCH') {
        const body = await parseBody(req);
        if (Object.keys(body).length === 0) {
          sendJSON(res, 400, { error: 'No fields to update' });
          return;
        }
        const errors = validateTicket(body, true);
        if (errors.length > 0) {
          sendJSON(res, 400, { error: 'Validation failed', details: errors });
          return;
        }
        const ticket = await store.update(id, body);
        if (!ticket) {
          sendJSON(res, 404, { error: 'Ticket not found' });
          return;
        }
        sendJSON(res, 200, ticket);

      } else if (method === 'DELETE') {
        const deleted = await store.delete(id);
        if (!deleted) {
          sendJSON(res, 404, { error: 'Ticket not found' });
          return;
        }
        sendJSON(res, 200, { message: 'Ticket deleted', id });

      } else {
        sendJSON(res, 405, { error: 'Method not allowed' });
      }

    } else {
      sendJSON(res, 404, { error: 'Route not found' });
    }

  } catch (err) {
    if (err.message === 'Invalid JSON') {
      sendJSON(res, 400, { error: 'Invalid JSON in request body' });
    } else {
      console.error('Server error:', err);
      sendJSON(res, 500, { error: 'Internal server error' });
    }
  }
});

server.listen(PORT, HOST, () => {
  console.log(`Server running at http://${HOST}:${PORT}/`);
});
```
````
