# Generation Transcript

- Case: `en_code_be_001`
- Language group: `en`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `2`
- Thinking mode: `think-max`
- Thinking strength: `max`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 8.207401
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 318, "total_tokens": 2718, "completion_tokens": 2400, "prompt_tokens_details": null}`
- Prompt tokens: 318
- Completion tokens: 2400
- Total tokens: 2718

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

const HOST = '127.0.0.1';
const PORT = 8080;
const DATA_FILE = path.join(__dirname, 'tickets.json');

// Initialize data file if it doesn't exist
if (!fs.existsSync(DATA_FILE)) {
  fs.writeFileSync(DATA_FILE, '[]', 'utf-8');
}

function readTickets() {
  return new Promise((resolve, reject) => {
    fs.readFile(DATA_FILE, 'utf-8', (err, data) => {
      if (err) {
        reject(err);
        return;
      }
      try {
        resolve(JSON.parse(data));
      } catch (parseErr) {
        reject(parseErr);
      }
    });
  });
}

function writeTickets(tickets) {
  return new Promise((resolve, reject) => {
    fs.writeFile(DATA_FILE, JSON.stringify(tickets, null, 2), 'utf-8', (err) => {
      if (err) reject(err);
      else resolve();
    });
  });
}

function generateId() {
  return Date.now().toString(36) + Math.random().toString(36).substr(2, 5);
}

function validateTicket(body) {
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

function sendJSON(res, statusCode, data) {
  const body = JSON.stringify(data);
  res.writeHead(statusCode, {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type'
  });
  res.end(body);
}

function parseBody(req) {
  return new Promise((resolve, reject) => {
    let body = '';
    req.on('data', chunk => {
      body += chunk.toString();
    });
    req.on('end', () => {
      try {
        resolve(body ? JSON.parse(body) : {});
      } catch (e) {
        reject(new Error('Invalid JSON'));
      }
    });
    req.on('error', reject);
  });
}

async function handleGetTickets(req, res) {
  try {
    const query = url.parse(req.url, true).query;
    let tickets = await readTickets();

    if (query.status) {
      tickets = tickets.filter(t => t.status === query.status);
    }
    if (query.priority) {
      tickets = tickets.filter(t => t.priority === query.priority);
    }

    sendJSON(res, 200, tickets);
  } catch (err) {
    sendJSON(res, 500, { error: 'Internal server error' });
  }
}

async function handlePostTickets(req, res) {
  try {
    const body = await parseBody(req);
    const errors = validateTicket(body);

    if (errors.length > 0) {
      sendJSON(res, 400, { error: 'Validation failed', details: errors });
      return;
    }

    const tickets = await readTickets();
    const now = new Date().toISOString();
    const ticket = {
      id: generateId(),
      subject: body.subject.trim(),
      description: body.description.trim(),
      priority: body.priority || 'medium',
      status: 'open',
      created_at: now,
      updated_at: now
    };

    tickets.push(ticket);
    await writeTickets(tickets);
    sendJSON(res, 201, ticket);
  } catch (err) {
    if (err.message === 'Invalid JSON') {
      sendJSON(res, 400, { error: 'Invalid JSON in request body' });
    } else {
      sendJSON(res, 500, { error: 'Internal server error' });
    }
  }
}

async function handleGetTicketById(req, res, id) {
  try {
    const tickets = await readTickets();
    const ticket = tickets.find(t => t.id === id);

    if (!ticket) {
      sendJSON(res, 404, { error: 'Ticket not found' });
      return;
    }

    sendJSON(res, 200, ticket);
  } catch (err) {
    sendJSON(res, 500, { error: 'Internal server error' });
  }
}

async function handlePatchTicket(req, res, id) {
  try {
    const body = await parseBody(req);
    const tickets = await readTickets();
    const index = tickets.findIndex(t => t.id === id);

    if (index === -1) {
      sendJSON(res, 404, { error: 'Ticket not found' });
      return;
    }

    const allowedFields = ['subject', 'description', 'priority', 'status'];
    const updates = {};

    for (const field of allowedFields) {
      if (body[field] !== undefined) {
        if (field === 'priority' && !['low', 'medium', 'high'].includes(body[field])) {
          sendJSON(res, 400, { error: 'priority must be one of: low, medium, high' });
          return;
        }
        if (field === 'status' && !['open', 'in_progress', 'resolved'].includes(body[field])) {
          sendJSON(res, 400, { error: 'status must be one of: open, in_progress, resolved' });
          return;
        }
        if (typeof body[field] === 'string') {
          updates[field] = body[field].trim();
        } else {
          updates[field] = body[field];
        }
      }
    }

    if (Object.keys(updates).length === 0) {
      sendJSON(res, 400, { error: 'No valid fields to update' });
      return;
    }

    updates.updated_at = new Date().toISOString();
    tickets[index] = { ...tickets[index], ...updates };
    await writeTickets(tickets);
    sendJSON(res, 200, tickets[index]);
  } catch (err) {
    if (err.message === 'Invalid JSON') {
      sendJSON(res, 400, { error: 'Invalid JSON in request body' });
    } else {
      sendJSON(res, 500, { error: 'Internal server error' });
    }
  }
}

async function handleDeleteTicket(req, res, id) {
  try {
    const tickets = await readTickets();
    const index = tickets.findIndex(t => t.id === id);

    if (index === -1) {
      sendJSON(res, 404, { error: 'Ticket not found' });
      return;
    }

    tickets.splice(index, 1);
    await writeTickets(tickets);
    sendJSON(res, 200, { message: 'Ticket deleted successfully' });
  } catch (err) {
    sendJSON(res, 500, { error: 'Internal server error' });
  }
}

async function handleMetrics(req, res) {
  try {
    const tickets = await readTickets();
    const now = new Date();

    const statusCounts = { open: 0, in_progress: 0, resolved: 0 };
    const priorityCounts = { low: 0, medium: 0, high: 0 };
    let totalOpenAgeSeconds = 0;
    let openTicketCount = 0;

    for (const ticket of tickets) {
      statusCounts[ticket.status] = (statusCounts[ticket.status] || 0) + 1;
      priorityCounts[ticket.priority] = (priorityCounts[ticket.priority] || 0) + 1;

      if (ticket.status === 'open') {
        const createdAt = new Date(ticket.created_at);
        totalOpenAgeSeconds += (now - createdAt) / 1000;
        openTicketCount++;
      }
    }

    const metrics = {
      status_counts: statusCounts,
      priority_counts: priorityCounts,
      average_open_age_seconds: openTicketCount > 0 ? totalOpenAgeSeconds / openTicketCount : 0
    };

    sendJSON(res, 200, metrics);
  } catch (err) {
    sendJSON(res, 500, { error: 'Internal server error' });
  }
}

async function handleRequest(req, res) {
  const parsedUrl = url.parse(req.url, true);
  const pathname = parsedUrl.pathname;
  const method = req.method;

  // Handle CORS preflight
  if (method === 'OPTIONS') {
    res.writeHead(204, {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type'
    });
    res.end();
    return;
  }

  // Route matching
  const getTicketMatch = pathname.match(/^\/tickets\/([a-zA-Z0-9]+)$/);

  try {
    if (pathname === '/tickets' && method === 'GET') {
      await handleGetTickets(req, res);
    } else if (pathname === '/tickets' && method === 'POST') {
      await handlePostTickets(req, res);
    } else if (getTicketMatch && method === 'GET') {
      await handleGetTicketById(req, res, getTicketMatch[1]);
    } else if (getTicketMatch && method === 'PATCH') {
      await handlePatchTicket(req, res, getTicketMatch[1]);
    } else if (getTicketMatch && method === 'DELETE') {
      await handleDeleteTicket(req, res, getTicketMatch[1]);
    } else if (pathname === '/metrics' && method === 'GET') {
      await handleMetrics(req, res);
    } else if (pathname.startsWith('/tickets') || pathname.startsWith('/metrics')) {
      sendJSON(res, 405, { error: 'Method not allowed' });
    } else {
      sendJSON(res, 404, { error: 'Not found' });
    }
  } catch (err) {
    sendJSON(res, 500, { error: 'Internal server error' });
  }
}

const server = http.createServer(handleRequest);

server.listen(PORT, HOST, () => {
  console.log(`Server running at http://${HOST}:${PORT}/`);
});
```
````
