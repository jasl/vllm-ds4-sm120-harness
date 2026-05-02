# Generation Transcript

- Case: `en_code_be_001`
- Language group: `en`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `2`
- Thinking mode: `think-high`
- Thinking strength: `high`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 7.813758
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 318, "total_tokens": 2599, "completion_tokens": 2281, "prompt_tokens_details": null}`
- Prompt tokens: 318
- Completion tokens: 2281
- Total tokens: 2599

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

class TicketQueue {
  constructor() {
    this.tickets = [];
    this.load();
  }

  load() {
    try {
      if (fs.existsSync(DATA_FILE)) {
        const data = fs.readFileSync(DATA_FILE, 'utf8');
        this.tickets = JSON.parse(data);
      } else {
        this.tickets = [];
        this.save();
      }
    } catch (err) {
      this.tickets = [];
      this.save();
    }
  }

  save() {
    try {
      fs.writeFileSync(DATA_FILE, JSON.stringify(this.tickets, null, 2), 'utf8');
    } catch (err) {
      console.error('Error saving tickets:', err);
    }
  }

  getAll(filters = {}) {
    let result = [...this.tickets];
    if (filters.status) {
      result = result.filter(t => t.status === filters.status);
    }
    if (filters.priority) {
      result = result.filter(t => t.priority === filters.priority);
    }
    return result;
  }

  getById(id) {
    return this.tickets.find(t => t.id === id);
  }

  create(ticketData) {
    const id = this.generateId();
    const now = new Date().toISOString();
    const ticket = {
      id,
      subject: ticketData.subject,
      description: ticketData.description || '',
      priority: ticketData.priority,
      status: ticketData.status || 'open',
      created_at: now,
      updated_at: now
    };
    this.tickets.push(ticket);
    this.save();
    return ticket;
  }

  update(id, updates) {
    const index = this.tickets.findIndex(t => t.id === id);
    if (index === -1) return null;

    const allowedFields = ['subject', 'description', 'priority', 'status'];
    const ticket = { ...this.tickets[index] };

    for (const field of allowedFields) {
      if (updates[field] !== undefined) {
        ticket[field] = updates[field];
      }
    }

    ticket.updated_at = new Date().toISOString();
    this.tickets[index] = ticket;
    this.save();
    return ticket;
  }

  delete(id) {
    const index = this.tickets.findIndex(t => t.id === id);
    if (index === -1) return false;
    this.tickets.splice(index, 1);
    this.save();
    return true;
  }

  getMetrics() {
    const now = new Date();
    const metrics = {
      by_status: { open: 0, in_progress: 0, resolved: 0 },
      by_priority: { low: 0, medium: 0, high: 0 },
      average_open_age_seconds: 0
    };

    let openTickets = [];
    for (const ticket of this.tickets) {
      if (metrics.by_status[ticket.status] !== undefined) {
        metrics.by_status[ticket.status]++;
      }
      if (metrics.by_priority[ticket.priority] !== undefined) {
        metrics.by_priority[ticket.priority]++;
      }
      if (ticket.status === 'open' || ticket.status === 'in_progress') {
        openTickets.push(ticket);
      }
    }

    if (openTickets.length > 0) {
      let totalAge = 0;
      for (const ticket of openTickets) {
        const created = new Date(ticket.created_at);
        totalAge += (now - created) / 1000;
      }
      metrics.average_open_age_seconds = Math.round(totalAge / openTickets.length);
    }

    return metrics;
  }

  generateId() {
    return 'ticket_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
  }
}

const ticketQueue = new TicketQueue();

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

function sendResponse(res, statusCode, data) {
  res.writeHead(statusCode, {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type'
  });
  res.end(JSON.stringify(data));
}

function validateTicketData(data) {
  const errors = [];

  if (!data.subject || typeof data.subject !== 'string' || data.subject.trim() === '') {
    errors.push('subject is required and must be a non-empty string');
  }

  const validPriorities = ['low', 'medium', 'high'];
  if (data.priority && !validPriorities.includes(data.priority)) {
    errors.push('priority must be one of: low, medium, high');
  }

  const validStatuses = ['open', 'in_progress', 'resolved'];
  if (data.status && !validStatuses.includes(data.status)) {
    errors.push('status must be one of: open, in_progress, resolved');
  }

  if (data.description && typeof data.description !== 'string') {
    errors.push('description must be a string');
  }

  return errors;
}

function validateUpdateData(data) {
  const errors = [];
  const validPriorities = ['low', 'medium', 'high'];
  const validStatuses = ['open', 'in_progress', 'resolved'];

  if (data.subject !== undefined && (typeof data.subject !== 'string' || data.subject.trim() === '')) {
    errors.push('subject must be a non-empty string');
  }

  if (data.priority !== undefined && !validPriorities.includes(data.priority)) {
    errors.push('priority must be one of: low, medium, high');
  }

  if (data.status !== undefined && !validStatuses.includes(data.status)) {
    errors.push('status must be one of: open, in_progress, resolved');
  }

  if (data.description !== undefined && typeof data.description !== 'string') {
    errors.push('description must be a string');
  }

  return errors;
}

const server = http.createServer(async (req, res) => {
  const parsedUrl = url.parse(req.url, true);
  const pathname = parsedUrl.pathname;
  const method = req.method.toUpperCase();

  // CORS preflight
  if (method === 'OPTIONS') {
    res.writeHead(204, {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type'
    });
    res.end();
    return;
  }

  try {
    // Routes
    if (pathname === '/tickets' && method === 'GET') {
      const filters = {};
      if (parsedUrl.query.status) filters.status = parsedUrl.query.status;
      if (parsedUrl.query.priority) filters.priority = parsedUrl.query.priority;
      const tickets = ticketQueue.getAll(filters);
      sendResponse(res, 200, { tickets });

    } else if (pathname === '/tickets' && method === 'POST') {
      const data = await parseBody(req);
      const errors = validateTicketData(data);

      if (errors.length > 0) {
        sendResponse(res, 400, { error: 'Validation failed', details: errors });
        return;
      }

      data.subject = data.subject.trim();
      const ticket = ticketQueue.create(data);
      sendResponse(res, 201, { ticket });

    } else if (pathname === '/metrics' && method === 'GET') {
      const metrics = ticketQueue.getMetrics();
      sendResponse(res, 200, { metrics });

    } else if (pathname.startsWith('/tickets/')) {
      const id = pathname.substring(9);

      if (!id) {
        sendResponse(res, 400, { error: 'Ticket ID is required' });
        return;
      }

      if (method === 'GET') {
        const ticket = ticketQueue.getById(id);
        if (!ticket) {
          sendResponse(res, 404, { error: 'Ticket not found' });
          return;
        }
        sendResponse(res, 200, { ticket });

      } else if (method === 'PATCH') {
        const ticket = ticketQueue.getById(id);
        if (!ticket) {
          sendResponse(res, 404, { error: 'Ticket not found' });
          return;
        }

        const data = await parseBody(req);
        const errors = validateUpdateData(data);

        if (errors.length > 0) {
          sendResponse(res, 400, { error: 'Validation failed', details: errors });
          return;
        }

        const updatedTicket = ticketQueue.update(id, data);
        sendResponse(res, 200, { ticket: updatedTicket });

      } else if (method === 'DELETE') {
        const deleted = ticketQueue.delete(id);
        if (!deleted) {
          sendResponse(res, 404, { error: 'Ticket not found' });
          return;
        }
        sendResponse(res, 200, { message: 'Ticket deleted successfully' });

      } else {
        sendResponse(res, 405, { error: 'Method not allowed' });
      }

    } else {
      sendResponse(res, 404, { error: 'Route not found' });
    }

  } catch (err) {
    if (err.message === 'Invalid JSON') {
      sendResponse(res, 400, { error: 'Invalid JSON in request body' });
    } else {
      console.error('Server error:', err);
      sendResponse(res, 500, { error: 'Internal server error' });
    }
  }
});

server.listen(PORT, HOST, () => {
  console.log(`Server running at http://${HOST}:${PORT}/`);
});
```
````
