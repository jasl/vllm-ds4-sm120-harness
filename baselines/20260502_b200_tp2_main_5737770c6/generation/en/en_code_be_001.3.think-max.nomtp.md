# Generation Transcript

- Case: `en_code_be_001`
- Language group: `en`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `3`
- Thinking mode: `think-max`
- Thinking strength: `max`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 19.531601
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 318, "total_tokens": 2712, "completion_tokens": 2394, "prompt_tokens_details": null}`
- Prompt tokens: 318
- Completion tokens: 2394
- Total tokens: 2712

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
import http from 'http';
import fs from 'fs/promises';
import path from 'path';
import url from 'url';

const DATA_FILE = path.join(process.cwd(), 'tickets.json');
const PORT = process.env.PORT || 8080;
const HOST = '127.0.0.1';

class TicketStore {
  constructor(filePath) {
    this.filePath = filePath;
    this.writeLock = Promise.resolve();
  }

  async readTickets() {
    try {
      const data = await fs.readFile(this.filePath, 'utf8');
      return JSON.parse(data);
    } catch (err) {
      if (err.code === 'ENOENT') {
        return [];
      }
      throw err;
    }
  }

  async writeTickets(tickets) {
    const oldWrite = this.writeLock;
    this.writeLock = new Promise(async (resolve) => {
      await oldWrite;
      try {
        await fs.writeFile(this.filePath, JSON.stringify(tickets, null, 2));
      } catch (err) {
        console.error('Write failed:', err);
      }
      resolve();
    });
    return this.writeLock;
  }

  generateId(tickets) {
    if (tickets.length === 0) return 1;
    return Math.max(...tickets.map(t => t.id)) + 1;
  }

  async createTicket(data) {
    const tickets = await this.readTickets();
    const now = new Date().toISOString();
    const ticket = {
      id: this.generateId(tickets),
      subject: data.subject,
      description: data.description,
      priority: data.priority,
      status: 'open',
      created_at: now,
      updated_at: now
    };
    tickets.push(ticket);
    await this.writeTickets(tickets);
    return ticket;
  }

  async getTicket(id) {
    const tickets = await this.readTickets();
    return tickets.find(t => t.id === id) || null;
  }

  async updateTicket(id, data) {
    const tickets = await this.readTickets();
    const index = tickets.findIndex(t => t.id === id);
    if (index === -1) return null;

    const now = new Date().toISOString();
    const allowedFields = ['subject', 'description', 'priority', 'status'];

    for (const field of allowedFields) {
      if (data[field] !== undefined) {
        tickets[index][field] = data[field];
      }
    }
    tickets[index].updated_at = now;

    await this.writeTickets(tickets);
    return tickets[index];
  }

  async deleteTicket(id) {
    const tickets = await this.readTickets();
    const index = tickets.findIndex(t => t.id === id);
    if (index === -1) return false;

    tickets.splice(index, 1);
    await this.writeTickets(tickets);
    return true;
  }

  async getMetrics() {
    const tickets = await this.readTickets();
    const now = Date.now();

    const statusCounts = { open: 0, in_progress: 0, resolved: 0 };
    const priorityCounts = { low: 0, medium: 0, high: 0 };
    let totalAgeOpen = 0;
    let openCount = 0;

    for (const ticket of tickets) {
      statusCounts[ticket.status] = (statusCounts[ticket.status] || 0) + 1;
      priorityCounts[ticket.priority] = (priorityCounts[ticket.priority] || 0) + 1;

      if (ticket.status === 'open') {
        const created = new Date(ticket.created_at).getTime();
        totalAgeOpen += (now - created) / 1000;
        openCount++;
      }
    }

    return {
      statusCounts,
      priorityCounts,
      averageOpenAgeSeconds: openCount > 0 ? totalAgeOpen / openCount : 0
    };
  }
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

  if (!data.subject || typeof data.subject !== 'string' || data.subject.trim().length === 0) {
    errors.push('subject is required and must be a non-empty string');
  }

  if (!data.description || typeof data.description !== 'string' || data.description.trim().length === 0) {
    errors.push('description is required and must be a non-empty string');
  }

  if (!data.priority || !['low', 'medium', 'high'].includes(data.priority)) {
    errors.push('priority must be one of: low, medium, high');
  }

  return errors;
}

function validateUpdateData(data) {
  const errors = [];
  const validStatuses = ['open', 'in_progress', 'resolved'];
  const validPriorities = ['low', 'medium', 'high'];

  if (data.subject !== undefined && (typeof data.subject !== 'string' || data.subject.trim().length === 0)) {
    errors.push('subject must be a non-empty string');
  }

  if (data.description !== undefined && (typeof data.description !== 'string' || data.description.trim().length === 0)) {
    errors.push('description must be a non-empty string');
  }

  if (data.priority !== undefined && !validPriorities.includes(data.priority)) {
    errors.push('priority must be one of: low, medium, high');
  }

  if (data.status !== undefined && !validStatuses.includes(data.status)) {
    errors.push('status must be one of: open, in_progress, resolved');
  }

  return errors;
}

async function handleRequest(req, res) {
  const parsedUrl = url.parse(req.url, true);
  const pathname = parsedUrl.pathname;
  const method = req.method.toUpperCase();

  const store = new TicketStore(DATA_FILE);

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
    // GET /metrics
    if (pathname === '/metrics' && method === 'GET') {
      const metrics = await store.getMetrics();
      sendJSON(res, 200, metrics);
      return;
    }

    // GET /tickets
    if (pathname === '/tickets' && method === 'GET') {
      let tickets = await store.readTickets();

      if (parsedUrl.query.status) {
        tickets = tickets.filter(t => t.status === parsedUrl.query.status);
      }

      if (parsedUrl.query.priority) {
        tickets = tickets.filter(t => t.priority === parsedUrl.query.priority);
      }

      sendJSON(res, 200, tickets);
      return;
    }

    // POST /tickets
    if (pathname === '/tickets' && method === 'POST') {
      const data = await parseBody(req);
      const errors = validateTicketData(data);

      if (errors.length > 0) {
        sendJSON(res, 400, { error: 'Validation failed', details: errors });
        return;
      }

      data.subject = data.subject.trim();
      data.description = data.description.trim();

      const ticket = await store.createTicket(data);
      sendJSON(res, 201, ticket);
      return;
    }

    // Dynamic routes for /tickets/{id}
    const ticketMatch = pathname.match(/^\/tickets\/(\d+)$/);

    if (ticketMatch) {
      const id = parseInt(ticketMatch[1], 10);

      // GET /tickets/{id}
      if (method === 'GET') {
        const ticket = await store.getTicket(id);
        if (!ticket) {
          sendJSON(res, 404, { error: 'Ticket not found' });
          return;
        }
        sendJSON(res, 200, ticket);
        return;
      }

      // PATCH /tickets/{id}
      if (method === 'PATCH') {
        const data = await parseBody(req);
        const errors = validateUpdateData(data);

        if (errors.length > 0) {
          sendJSON(res, 400, { error: 'Validation failed', details: errors });
          return;
        }

        if (data.subject) data.subject = data.subject.trim();
        if (data.description) data.description = data.description.trim();

        const ticket = await store.updateTicket(id, data);
        if (!ticket) {
          sendJSON(res, 404, { error: 'Ticket not found' });
          return;
        }
        sendJSON(res, 200, ticket);
        return;
      }

      // DELETE /tickets/{id}
      if (method === 'DELETE') {
        const deleted = await store.deleteTicket(id);
        if (!deleted) {
          sendJSON(res, 404, { error: 'Ticket not found' });
          return;
        }
        sendJSON(res, 200, { message: 'Ticket deleted successfully' });
        return;
      }

      sendJSON(res, 405, { error: 'Method not allowed' });
      return;
    }

    sendJSON(res, 404, { error: 'Route not found' });

  } catch (err) {
    if (err.message === 'Invalid JSON') {
      sendJSON(res, 400, { error: 'Invalid JSON in request body' });
    } else if (err.message === 'Request body too large') {
      sendJSON(res, 413, { error: 'Request body too large' });
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
