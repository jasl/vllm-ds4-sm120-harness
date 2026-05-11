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
- Elapsed seconds: 14.598534
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 318, "total_tokens": 2895, "completion_tokens": 2577, "prompt_tokens_details": null}`
- Prompt tokens: 318
- Completion tokens: 2577
- Total tokens: 2895

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
const crypto = require('crypto');

const HOST = '127.0.0.1';
const PORT = 8080;
const DATA_FILE = path.join(__dirname, 'tickets.json');

class TicketStore {
  constructor(filePath) {
    this.filePath = filePath;
    this.tickets = [];
    this.lock = Promise.resolve();
    this.load();
  }

  load() {
    try {
      if (fs.existsSync(this.filePath)) {
        const data = fs.readFileSync(this.filePath, 'utf8');
        this.tickets = JSON.parse(data);
      } else {
        this.tickets = [];
        this.saveSync();
      }
    } catch (err) {
      console.error('Error loading tickets:', err);
      this.tickets = [];
    }
  }

  saveSync() {
    try {
      fs.writeFileSync(this.filePath, JSON.stringify(this.tickets, null, 2), 'utf8');
    } catch (err) {
      console.error('Error saving tickets:', err);
    }
  }

  acquireLock() {
    let release;
    const promise = new Promise(resolve => { release = resolve; });
    const previousLock = this.lock;
    this.lock = this.lock.then(() => promise);
    return previousLock.then(() => release);
  }

  async read() {
    const release = await this.acquireLock();
    try {
      const data = fs.readFileSync(this.filePath, 'utf8');
      this.tickets = JSON.parse(data);
      return this.tickets;
    } finally {
      release();
    }
  }

  async write(tickets) {
    const release = await this.acquireLock();
    try {
      this.tickets = tickets;
      fs.writeFileSync(this.filePath, JSON.stringify(tickets, null, 2), 'utf8');
    } finally {
      release();
    }
  }

  getAll() {
    return [...this.tickets];
  }

  getById(id) {
    return this.tickets.find(t => t.id === id);
  }

  add(ticket) {
    this.tickets.push(ticket);
    this.saveSync();
    return ticket;
  }

  update(id, updates) {
    const index = this.tickets.findIndex(t => t.id === id);
    if (index === -1) return null;
    this.tickets[index] = { ...this.tickets[index], ...updates, updated_at: new Date().toISOString() };
    this.saveSync();
    return this.tickets[index];
  }

  delete(id) {
    const index = this.tickets.findIndex(t => t.id === id);
    if (index === -1) return false;
    this.tickets.splice(index, 1);
    this.saveSync();
    return true;
  }
}

const store = new TicketStore(DATA_FILE);

function generateId() {
  return crypto.randomUUID();
}

function validateTicket(body) {
  const errors = [];
  if (!body.subject || typeof body.subject !== 'string' || body.subject.trim() === '') {
    errors.push('subject is required and must be a non-empty string');
  }
  if (!body.description || typeof body.description !== 'string' || body.description.trim() === '') {
    errors.push('description is required and must be a non-empty string');
  }
  const validPriorities = ['low', 'medium', 'high'];
  if (!body.priority || !validPriorities.includes(body.priority)) {
    errors.push('priority must be one of: low, medium, high');
  }
  return errors;
}

function parseBody(req) {
  return new Promise((resolve, reject) => {
    let body = '';
    req.on('data', chunk => { body += chunk; });
    req.on('end', () => {
      try {
        resolve(JSON.parse(body));
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

function parseURL(url) {
  const [pathname, queryString] = url.split('?');
  const params = {};
  if (queryString) {
    queryString.split('&').forEach(pair => {
      const [key, value] = pair.split('=').map(decodeURIComponent);
      params[key] = value;
    });
  }
  return { pathname, params };
}

function calculateMetrics(tickets) {
  const statusCounts = { open: 0, in_progress: 0, resolved: 0 };
  const priorityCounts = { low: 0, medium: 0, high: 0 };
  let totalAgeSeconds = 0;
  let openCount = 0;
  const now = new Date();

  tickets.forEach(ticket => {
    if (statusCounts.hasOwnProperty(ticket.status)) {
      statusCounts[ticket.status]++;
    }
    if (priorityCounts.hasOwnProperty(ticket.priority)) {
      priorityCounts[ticket.priority]++;
    }
    if (ticket.status === 'open') {
      const createdAt = new Date(ticket.created_at);
      const ageSeconds = (now - createdAt) / 1000;
      totalAgeSeconds += ageSeconds;
      openCount++;
    }
  });

  return {
    statusCounts,
    priorityCounts,
    averageOpenAgeSeconds: openCount > 0 ? (totalAgeSeconds / openCount) : 0
  };
}

async function handleRequest(req, res) {
  const { pathname, params } = parseURL(req.url);
  const method = req.method.toUpperCase();

  // Handle CORS preflight
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

  try {
    // GET /tickets
    if (method === 'GET' && pathname === '/tickets') {
      await store.read();
      let tickets = store.getAll();

      if (params.status) {
        tickets = tickets.filter(t => t.status === params.status);
      }
      if (params.priority) {
        tickets = tickets.filter(t => t.priority === params.priority);
      }

      sendJSON(res, 200, tickets);
      return;
    }

    // POST /tickets
    if (method === 'POST' && pathname === '/tickets') {
      const body = await parseBody(req);
      const errors = validateTicket(body);
      if (errors.length > 0) {
        sendJSON(res, 400, { error: 'Validation failed', details: errors });
        return;
      }

      await store.read();
      const now = new Date().toISOString();
      const ticket = {
        id: generateId(),
        subject: body.subject.trim(),
        description: body.description.trim(),
        priority: body.priority,
        status: 'open',
        created_at: now,
        updated_at: now
      };
      store.add(ticket);
      sendJSON(res, 201, ticket);
      return;
    }

    // GET /tickets/{id}
    const getMatch = pathname.match(/^\/tickets\/([a-f0-9-]+)$/);
    if (method === 'GET' && getMatch) {
      const id = getMatch[1];
      await store.read();
      const ticket = store.getById(id);
      if (!ticket) {
        sendJSON(res, 404, { error: 'Ticket not found' });
        return;
      }
      sendJSON(res, 200, ticket);
      return;
    }

    // PATCH /tickets/{id}
    const patchMatch = pathname.match(/^\/tickets\/([a-f0-9-]+)$/);
    if (method === 'PATCH' && patchMatch) {
      const id = patchMatch[1];
      const body = await parseBody(req);

      // Validate fields if provided
      const errors = [];
      if (body.subject !== undefined && (typeof body.subject !== 'string' || body.subject.trim() === '')) {
        errors.push('subject must be a non-empty string');
      }
      if (body.description !== undefined && (typeof body.description !== 'string' || body.description.trim() === '')) {
        errors.push('description must be a non-empty string');
      }
      const validPriorities = ['low', 'medium', 'high'];
      if (body.priority !== undefined && !validPriorities.includes(body.priority)) {
        errors.push('priority must be one of: low, medium, high');
      }
      const validStatuses = ['open', 'in_progress', 'resolved'];
      if (body.status !== undefined && !validStatuses.includes(body.status)) {
        errors.push('status must be one of: open, in_progress, resolved');
      }
      if (errors.length > 0) {
        sendJSON(res, 400, { error: 'Validation failed', details: errors });
        return;
      }

      await store.read();
      const ticket = store.getById(id);
      if (!ticket) {
        sendJSON(res, 404, { error: 'Ticket not found' });
        return;
      }

      const updates = {};
      if (body.subject !== undefined) updates.subject = body.subject.trim();
      if (body.description !== undefined) updates.description = body.description.trim();
      if (body.priority !== undefined) updates.priority = body.priority;
      if (body.status !== undefined) updates.status = body.status;

      if (Object.keys(updates).length === 0) {
        sendJSON(res, 400, { error: 'No valid fields to update' });
        return;
      }

      const updatedTicket = store.update(id, updates);
      sendJSON(res, 200, updatedTicket);
      return;
    }

    // DELETE /tickets/{id}
    const deleteMatch = pathname.match(/^\/tickets\/([a-f0-9-]+)$/);
    if (method === 'DELETE' && deleteMatch) {
      const id = deleteMatch[1];
      await store.read();
      const deleted = store.delete(id);
      if (!deleted) {
        sendJSON(res, 404, { error: 'Ticket not found' });
        return;
      }
      sendJSON(res, 200, { message: 'Ticket deleted successfully' });
      return;
    }

    // GET /metrics
    if (method === 'GET' && pathname === '/metrics') {
      await store.read();
      const tickets = store.getAll();
      const metrics = calculateMetrics(tickets);
      sendJSON(res, 200, metrics);
      return;
    }

    // Unknown route
    sendJSON(res, 404, { error: 'Route not found' });

  } catch (err) {
    if (err.message === 'Invalid JSON') {
      sendJSON(res, 400, { error: 'Invalid JSON in request body' });
    } else {
      console.error('Server error:', err);
      sendJSON(res, 500, { error: 'Internal server error' });
    }
  }
}

const server = http.createServer(handleRequest);

server.listen(PORT, HOST, () => {
  console.log(`Server running at http://${HOST}:${PORT}/`);
});
```
````
