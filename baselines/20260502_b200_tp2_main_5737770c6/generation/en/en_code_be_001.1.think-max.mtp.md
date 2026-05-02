# Generation Transcript

- Case: `en_code_be_001`
- Language group: `en`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `1`
- Thinking mode: `think-max`
- Thinking strength: `max`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 9.760196
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 318, "total_tokens": 3164, "completion_tokens": 2846, "prompt_tokens_details": null}`
- Prompt tokens: 318
- Completion tokens: 2846
- Total tokens: 3164

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
const url = require('url');

const PORT = 8080;
const HOST = '127.0.0.1';
const DATA_FILE = path.join(__dirname, 'tickets.json');

// CORS headers
const CORS_HEADERS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
  'Content-Type': 'application/json'
};

// Data file operations with simple locking
let fileLock = false;
const lockQueue = [];

function acquireLock() {
  return new Promise((resolve) => {
    if (!fileLock) {
      fileLock = true;
      resolve();
    } else {
      lockQueue.push(resolve);
    }
  });
}

function releaseLock() {
  if (lockQueue.length > 0) {
    const next = lockQueue.shift();
    next();
  } else {
    fileLock = false;
  }
}

function readTickets() {
  return new Promise((resolve, reject) => {
    fs.readFile(DATA_FILE, 'utf8', (err, data) => {
      if (err) {
        if (err.code === 'ENOENT') {
          resolve([]);
        } else {
          reject(err);
        }
      } else {
        try {
          resolve(JSON.parse(data));
        } catch (parseErr) {
          reject(parseErr);
        }
      }
    });
  });
}

function writeTickets(tickets) {
  return new Promise((resolve, reject) => {
    fs.writeFile(DATA_FILE, JSON.stringify(tickets, null, 2), 'utf8', (err) => {
      if (err) {
        reject(err);
      } else {
        resolve();
      }
    });
  });
}

function generateId() {
  return Date.now().toString(36) + Math.random().toString(36).substr(2, 5);
}

function getTimestamp() {
  return new Date().toISOString();
}

function validateTicket(body) {
  const errors = [];

  if (!body.subject || typeof body.subject !== 'string' || body.subject.trim() === '') {
    errors.push('subject is required and must be a non-empty string');
  }

  if (!body.description || typeof body.description !== 'string' || body.description.trim() === '') {
    errors.push('description is required and must be a non-empty string');
  }

  if (body.priority) {
    if (!['low', 'medium', 'high'].includes(body.priority)) {
      errors.push('priority must be low, medium, or high');
    }
  }

  if (body.status) {
    if (!['open', 'in_progress', 'resolved'].includes(body.status)) {
      errors.push('status must be open, in_progress, or resolved');
    }
  }

  return errors;
}

function parseBody(req) {
  return new Promise((resolve, reject) => {
    let body = '';
    req.on('data', (chunk) => {
      body += chunk.toString();
    });
    req.on('end', () => {
      if (!body) {
        resolve({});
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

function sendResponse(res, statusCode, data) {
  res.writeHead(statusCode, CORS_HEADERS);
  res.end(JSON.stringify(data));
}

function getAgeInSeconds(createdAt) {
  const created = new Date(createdAt);
  const now = new Date();
  return Math.floor((now - created) / 1000);
}

// Route handlers
async function handleGetTickets(req, res, queryParams) {
  await acquireLock();
  try {
    const tickets = await readTickets();
    let filtered = tickets;

    if (queryParams.status) {
      filtered = filtered.filter(t => t.status === queryParams.status);
    }

    if (queryParams.priority) {
      filtered = filtered.filter(t => t.priority === queryParams.priority);
    }

    sendResponse(res, 200, filtered);
  } catch (err) {
    sendResponse(res, 500, { error: 'Internal server error' });
  } finally {
    releaseLock();
  }
}

async function handleCreateTicket(req, res) {
  let body;
  try {
    body = await parseBody(req);
  } catch (e) {
    sendResponse(res, 400, { error: 'Invalid JSON' });
    return;
  }

  const errors = validateTicket(body);
  if (errors.length > 0) {
    sendResponse(res, 400, { error: 'Validation failed', details: errors });
    return;
  }

  await acquireLock();
  try {
    const tickets = await readTickets();
    const now = getTimestamp();

    const newTicket = {
      id: generateId(),
      subject: body.subject.trim(),
      description: body.description.trim(),
      priority: body.priority || 'low',
      status: body.status || 'open',
      created_at: now,
      updated_at: now
    };

    tickets.push(newTicket);
    await writeTickets(tickets);
    sendResponse(res, 201, newTicket);
  } catch (err) {
    sendResponse(res, 500, { error: 'Internal server error' });
  } finally {
    releaseLock();
  }
}

async function handleGetTicket(req, res, id) {
  await acquireLock();
  try {
    const tickets = await readTickets();
    const ticket = tickets.find(t => t.id === id);

    if (!ticket) {
      sendResponse(res, 404, { error: 'Ticket not found' });
      return;
    }

    sendResponse(res, 200, ticket);
  } catch (err) {
    sendResponse(res, 500, { error: 'Internal server error' });
  } finally {
    releaseLock();
  }
}

async function handleUpdateTicket(req, res, id) {
  let body;
  try {
    body = await parseBody(req);
  } catch (e) {
    sendResponse(res, 400, { error: 'Invalid JSON' });
    return;
  }

  // Validate fields if provided
  const errors = [];
  if (body.subject !== undefined && (typeof body.subject !== 'string' || body.subject.trim() === '')) {
    errors.push('subject must be a non-empty string');
  }
  if (body.description !== undefined && (typeof body.description !== 'string' || body.description.trim() === '')) {
    errors.push('description must be a non-empty string');
  }
  if (body.priority !== undefined && !['low', 'medium', 'high'].includes(body.priority)) {
    errors.push('priority must be low, medium, or high');
  }
  if (body.status !== undefined && !['open', 'in_progress', 'resolved'].includes(body.status)) {
    errors.push('status must be open, in_progress, or resolved');
  }

  if (errors.length > 0) {
    sendResponse(res, 400, { error: 'Validation failed', details: errors });
    return;
  }

  await acquireLock();
  try {
    const tickets = await readTickets();
    const index = tickets.findIndex(t => t.id === id);

    if (index === -1) {
      sendResponse(res, 404, { error: 'Ticket not found' });
      return;
    }

    const now = getTimestamp();
    const updatedTicket = { ...tickets[index], updated_at: now };

    if (body.subject !== undefined) updatedTicket.subject = body.subject.trim();
    if (body.description !== undefined) updatedTicket.description = body.description.trim();
    if (body.priority !== undefined) updatedTicket.priority = body.priority;
    if (body.status !== undefined) updatedTicket.status = body.status;

    tickets[index] = updatedTicket;
    await writeTickets(tickets);
    sendResponse(res, 200, updatedTicket);
  } catch (err) {
    sendResponse(res, 500, { error: 'Internal server error' });
  } finally {
    releaseLock();
  }
}

async function handleDeleteTicket(req, res, id) {
  await acquireLock();
  try {
    const tickets = await readTickets();
    const index = tickets.findIndex(t => t.id === id);

    if (index === -1) {
      sendResponse(res, 404, { error: 'Ticket not found' });
      return;
    }

    tickets.splice(index, 1);
    await writeTickets(tickets);
    sendResponse(res, 200, { message: 'Ticket deleted' });
  } catch (err) {
    sendResponse(res, 500, { error: 'Internal server error' });
  } finally {
    releaseLock();
  }
}

async function handleMetrics(req, res) {
  await acquireLock();
  try {
    const tickets = await readTickets();
    const now = new Date();

    const statusCounts = { open: 0, in_progress: 0, resolved: 0 };
    const priorityCounts = { low: 0, medium: 0, high: 0 };
    let totalOpenAge = 0;
    let openCount = 0;

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
        totalOpenAge += (now - created) / 1000;
        openCount++;
      }

      // Also count in_progress for age calculation if needed
      if (ticket.status === 'in_progress') {
        const created = new Date(ticket.created_at);
        totalOpenAge += (now - created) / 1000;
        openCount++;
      }
    });

    const averageAge = openCount > 0 ? totalOpenAge / openCount : 0;

    sendResponse(res, 200, {
      status_counts: statusCounts,
      priority_counts: priorityCounts,
      average_open_ticket_age_seconds: Math.round(averageAge * 100) / 100
    });
  } catch (err) {
    sendResponse(res, 500, { error: 'Internal server error' });
  } finally {
    releaseLock();
  }
}

// Request router
async function handleRequest(req, res) {
  const parsedUrl = url.parse(req.url, true);
  const pathname = parsedUrl.pathname;
  const method = req.method.toUpperCase();

  // Handle CORS preflight
  if (method === 'OPTIONS') {
    res.writeHead(204, CORS_HEADERS);
    res.end();
    return;
  }

  // Route matching
  const ticketIdMatch = pathname.match(/^\/tickets\/([a-zA-Z0-9]+)$/);
  const ticketsMatch = pathname === '/tickets';
  const metricsMatch = pathname === '/metrics';

  try {
    if (ticketsMatch && method === 'GET') {
      await handleGetTickets(req, res, parsedUrl.query);
    } else if (ticketsMatch && method === 'POST') {
      await handleCreateTicket(req, res);
    } else if (ticketIdMatch && method === 'GET') {
      await handleGetTicket(req, res, ticketIdMatch[1]);
    } else if (ticketIdMatch && method === 'PATCH') {
      await handleUpdateTicket(req, res, ticketIdMatch[1]);
    } else if (ticketIdMatch && method === 'DELETE') {
      await handleDeleteTicket(req, res, ticketIdMatch[1]);
    } else if (metricsMatch && method === 'GET') {
      await handleMetrics(req, res);
    } else {
      // Check if route exists but method not allowed
      const isTicketRoute = pathname === '/tickets' || pathname.match(/^\/tickets\//);
      const isMetricsRoute = pathname === '/metrics';

      if (isTicketRoute || isMetricsRoute) {
        sendResponse(res, 405, { error: 'Method not allowed' });
      } else {
        sendResponse(res, 404, { error: 'Route not found' });
      }
    }
  } catch (err) {
    console.error('Request handler error:', err);
    sendResponse(res, 500, { error: 'Internal server error' });
  }
}

// Create server
const server = http.createServer(handleRequest);

server.listen(PORT, HOST, () => {
  console.log(`Server running at http://${HOST}:${PORT}/`);
});
```
````
