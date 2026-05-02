# Generation Transcript

- Case: `en_code_be_001`
- Language group: `en`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `2`
- Thinking mode: `non-thinking`
- Thinking strength: `disabled`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 45.745753
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 318, "total_tokens": 3220, "completion_tokens": 2902, "prompt_tokens_details": null}`
- Prompt tokens: 318
- Completion tokens: 2902
- Total tokens: 3220

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
    this.lockQueue = [];
    this.locked = false;
    this.ensureFile();
  }

  ensureFile() {
    if (!fs.existsSync(this.filePath)) {
      fs.writeFileSync(this.filePath, '[]', 'utf8');
    }
  }

  acquireLock() {
    return new Promise((resolve) => {
      if (!this.locked) {
        this.locked = true;
        resolve();
      } else {
        this.lockQueue.push(resolve);
      }
    });
  }

  releaseLock() {
    if (this.lockQueue.length > 0) {
      const next = this.lockQueue.shift();
      next();
    } else {
      this.locked = false;
    }
  }

  async readTickets() {
    await this.acquireLock();
    try {
      const data = fs.readFileSync(this.filePath, 'utf8');
      return JSON.parse(data);
    } finally {
      this.releaseLock();
    }
  }

  async writeTickets(tickets) {
    await this.acquireLock();
    try {
      fs.writeFileSync(this.filePath, JSON.stringify(tickets, null, 2), 'utf8');
    } finally {
      this.releaseLock();
    }
  }
}

const store = new TicketStore(DATA_FILE);

function generateId() {
  return Date.now().toString(36) + Math.random().toString(36).substr(2, 9);
}

function getTimestamp() {
  return new Date().toISOString();
}

function validateTicketInput(body) {
  const errors = [];
  if (!body.subject || typeof body.subject !== 'string' || body.subject.trim() === '') {
    errors.push('subject is required and must be a non-empty string');
  }
  if (!body.description || typeof body.description !== 'string' || body.description.trim() === '') {
    errors.push('description is required and must be a non-empty string');
  }
  if (body.priority && !['low', 'medium', 'high'].includes(body.priority)) {
    errors.push('priority must be one of: low, medium, high');
  }
  if (body.status && !['open', 'in_progress', 'resolved'].includes(body.status)) {
    errors.push('status must be one of: open, in_progress, resolved');
  }
  return errors;
}

function validateTicketUpdate(body) {
  const errors = [];
  const validFields = ['subject', 'description', 'priority', 'status'];
  const providedFields = Object.keys(body).filter(k => validFields.includes(k));

  if (providedFields.length === 0) {
    errors.push('At least one valid field (subject, description, priority, status) must be provided');
  }

  if (body.subject !== undefined && (typeof body.subject !== 'string' || body.subject.trim() === '')) {
    errors.push('subject must be a non-empty string');
  }
  if (body.description !== undefined && (typeof body.description !== 'string' || body.description.trim() === '')) {
    errors.push('description must be a non-empty string');
  }
  if (body.priority !== undefined && !['low', 'medium', 'high'].includes(body.priority)) {
    errors.push('priority must be one of: low, medium, high');
  }
  if (body.status !== undefined && !['open', 'in_progress', 'resolved'].includes(body.status)) {
    errors.push('status must be one of: open, in_progress, resolved');
  }

  return errors;
}

function sendJSON(res, statusCode, data) {
  res.writeHead(statusCode, {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type'
  });
  res.end(JSON.stringify(data));
}

function parseBody(req) {
  return new Promise((resolve, reject) => {
    let body = '';
    req.on('data', chunk => {
      body += chunk.toString();
      if (body.length > 1e6) {
        req.destroy();
        reject(new Error('Request body too large'));
      }
    });
    req.on('end', () => {
      if (!body) {
        resolve(null);
        return;
      }
      try {
        resolve(JSON.parse(body));
      } catch (e) {
        reject(new Error('Invalid JSON'));
      }
    });
    req.on('error', reject);
  });
}

function parseUrl(url) {
  const [pathPart, queryString] = url.split('?');
  const params = {};
  if (queryString) {
    queryString.split('&').forEach(pair => {
      const [key, value] = pair.split('=').map(decodeURIComponent);
      params[key] = value;
    });
  }
  return { path: pathPart, params };
}

// Route handlers
async function handleGetTickets(req, res, params) {
  try {
    const tickets = await store.readTickets();
    let filtered = [...tickets];

    if (params.status) {
      filtered = filtered.filter(t => t.status === params.status);
    }
    if (params.priority) {
      filtered = filtered.filter(t => t.priority === params.priority);
    }

    sendJSON(res, 200, filtered);
  } catch (err) {
    sendJSON(res, 500, { error: 'Internal server error' });
  }
}

async function handleCreateTicket(req, res) {
  try {
    const body = await parseBody(req);
    if (!body) {
      sendJSON(res, 400, { error: 'Request body is required' });
      return;
    }

    const errors = validateTicketInput(body);
    if (errors.length > 0) {
      sendJSON(res, 400, { error: 'Validation failed', details: errors });
      return;
    }

    const tickets = await store.readTickets();
    const now = getTimestamp();
    const ticket = {
      id: generateId(),
      subject: body.subject.trim(),
      description: body.description.trim(),
      priority: body.priority || 'low',
      status: 'open',
      created_at: now,
      updated_at: now
    };

    tickets.push(ticket);
    await store.writeTickets(tickets);

    sendJSON(res, 201, ticket);
  } catch (err) {
    if (err.message === 'Invalid JSON') {
      sendJSON(res, 400, { error: 'Invalid JSON in request body' });
    } else {
      sendJSON(res, 500, { error: 'Internal server error' });
    }
  }
}

async function handleGetTicket(req, res, ticketId) {
  try {
    const tickets = await store.readTickets();
    const ticket = tickets.find(t => t.id === ticketId);

    if (!ticket) {
      sendJSON(res, 404, { error: 'Ticket not found' });
      return;
    }

    sendJSON(res, 200, ticket);
  } catch (err) {
    sendJSON(res, 500, { error: 'Internal server error' });
  }
}

async function handleUpdateTicket(req, res, ticketId) {
  try {
    const body = await parseBody(req);
    if (!body) {
      sendJSON(res, 400, { error: 'Request body is required' });
      return;
    }

    const errors = validateTicketUpdate(body);
    if (errors.length > 0) {
      sendJSON(res, 400, { error: 'Validation failed', details: errors });
      return;
    }

    const tickets = await store.readTickets();
    const index = tickets.findIndex(t => t.id === ticketId);

    if (index === -1) {
      sendJSON(res, 404, { error: 'Ticket not found' });
      return;
    }

    const now = getTimestamp();
    const updatedTicket = {
      ...tickets[index],
      updated_at: now
    };

    if (body.subject) updatedTicket.subject = body.subject.trim();
    if (body.description) updatedTicket.description = body.description.trim();
    if (body.priority) updatedTicket.priority = body.priority;
    if (body.status) updatedTicket.status = body.status;

    tickets[index] = updatedTicket;
    await store.writeTickets(tickets);

    sendJSON(res, 200, updatedTicket);
  } catch (err) {
    if (err.message === 'Invalid JSON') {
      sendJSON(res, 400, { error: 'Invalid JSON in request body' });
    } else {
      sendJSON(res, 500, { error: 'Internal server error' });
    }
  }
}

async function handleDeleteTicket(req, res, ticketId) {
  try {
    const tickets = await store.readTickets();
    const index = tickets.findIndex(t => t.id === ticketId);

    if (index === -1) {
      sendJSON(res, 404, { error: 'Ticket not found' });
      return;
    }

    tickets.splice(index, 1);
    await store.writeTickets(tickets);

    sendJSON(res, 200, { message: 'Ticket deleted successfully' });
  } catch (err) {
    sendJSON(res, 500, { error: 'Internal server error' });
  }
}

async function handleGetMetrics(req, res) {
  try {
    const tickets = await store.readTickets();
    const now = new Date();

    const statusCounts = { open: 0, in_progress: 0, resolved: 0 };
    const priorityCounts = { low: 0, medium: 0, high: 0 };
    let openTicketsAgeSum = 0;
    let openTicketCount = 0;

    tickets.forEach(ticket => {
      // Status counts
      if (statusCounts.hasOwnProperty(ticket.status)) {
        statusCounts[ticket.status]++;
      }

      // Priority counts
      if (priorityCounts.hasOwnProperty(ticket.priority)) {
        priorityCounts[ticket.priority]++;
      }

      // Average age of open tickets
      if (ticket.status === 'open') {
        const created = new Date(ticket.created_at);
        const ageInSeconds = (now - created) / 1000;
        openTicketsAgeSum += ageInSeconds;
        openTicketCount++;
      }
    });

    const metrics = {
      by_status: statusCounts,
      by_priority: priorityCounts,
      avg_age_open_seconds: openTicketCount > 0 ? (openTicketsAgeSum / openTicketCount) : 0
    };

    sendJSON(res, 200, metrics);
  } catch (err) {
    sendJSON(res, 500, { error: 'Internal server error' });
  }
}

function handleOptions(req, res) {
  res.writeHead(204, {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Max-Age': '86400'
  });
  res.end();
}

const server = http.createServer(async (req, res) => {
  const { path, params } = parseUrl(req.url);
  const method = req.method.toUpperCase();

  // CORS preflight
  if (method === 'OPTIONS') {
    handleOptions(req, res);
    return;
  }

  // Route matching
  try {
    if (path === '/tickets' && method === 'GET') {
      await handleGetTickets(req, res, params);
    } else if (path === '/tickets' && method === 'POST') {
      await handleCreateTicket(req, res);
    } else if (path === '/metrics' && method === 'GET') {
      await handleGetMetrics(req, res);
    } else if (path.startsWith('/tickets/')) {
      const ticketId = path.slice(9);
      if (!ticketId) {
        sendJSON(res, 400, { error: 'Ticket ID is required' });
        return;
      }

      if (method === 'GET') {
        await handleGetTicket(req, res, ticketId);
      } else if (method === 'PATCH') {
        await handleUpdateTicket(req, res, ticketId);
      } else if (method === 'DELETE') {
        await handleDeleteTicket(req, res, ticketId);
      } else {
        sendJSON(res, 405, { error: 'Method not allowed' });
      }
    } else {
      sendJSON(res, 404, { error: 'Route not found' });
    }
  } catch (err) {
    console.error('Server error:', err);
    sendJSON(res, 500, { error: 'Internal server error' });
  }
});

server.listen(PORT, HOST, () => {
  console.log(`Help-desk API server running at http://${HOST}:${PORT}`);
});
```
````
