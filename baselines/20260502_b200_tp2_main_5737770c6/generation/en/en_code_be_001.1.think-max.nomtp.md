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
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 23.697693
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 318, "total_tokens": 3194, "completion_tokens": 2876, "prompt_tokens_details": null}`
- Prompt tokens: 318
- Completion tokens: 2876
- Total tokens: 3194

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

const HOST = '127.0.0.1';
const PORT = 8080;
const DATA_FILE = path.join(__dirname, 'tickets.json');

class TicketStore {
  constructor(filePath) {
    this.filePath = filePath;
    this.data = { tickets: [], nextId: 1 };
    this.lock = false;
    this.queue = [];
    this.load();
  }

  load() {
    try {
      if (fs.existsSync(this.filePath)) {
        const raw = fs.readFileSync(this.filePath, 'utf8');
        this.data = JSON.parse(raw);
      }
    } catch (err) {
      console.error('Failed to load data file:', err.message);
    }
  }

  save() {
    try {
      fs.writeFileSync(this.filePath, JSON.stringify(this.data, null, 2), 'utf8');
    } catch (err) {
      console.error('Failed to save data file:', err.message);
      throw err;
    }
  }

  async acquireLock() {
    while (this.lock) {
      await new Promise(resolve => this.queue.push(resolve));
    }
    this.lock = true;
  }

  releaseLock() {
    this.lock = false;
    if (this.queue.length > 0) {
      const next = this.queue.shift();
      next();
    }
  }

  async readTickets(status, priority) {
    await this.acquireLock();
    try {
      let tickets = [...this.data.tickets];
      if (status) {
        tickets = tickets.filter(t => t.status === status);
      }
      if (priority) {
        tickets = tickets.filter(t => t.priority === priority);
      }
      return tickets;
    } finally {
      this.releaseLock();
    }
  }

  async createTicket(ticketData) {
    await this.acquireLock();
    try {
      const now = new Date().toISOString();
      const ticket = {
        id: this.data.nextId++,
        subject: ticketData.subject,
        description: ticketData.description,
        priority: ticketData.priority,
        status: 'open',
        created_at: now,
        updated_at: now
      };
      this.data.tickets.push(ticket);
      this.save();
      return ticket;
    } finally {
      this.releaseLock();
    }
  }

  async getTicket(id) {
    await this.acquireLock();
    try {
      return this.data.tickets.find(t => t.id === id) || null;
    } finally {
      this.releaseLock();
    }
  }

  async updateTicket(id, updates) {
    await this.acquireLock();
    try {
      const ticket = this.data.tickets.find(t => t.id === id);
      if (!ticket) return null;

      const allowedFields = ['subject', 'description', 'priority', 'status'];
      for (const field of allowedFields) {
        if (updates[field] !== undefined) {
          if (field === 'priority' && !['low', 'medium', 'high'].includes(updates[field])) {
            throw new Error(`Invalid priority: ${updates[field]}`);
          }
          if (field === 'status' && !['open', 'in_progress', 'resolved'].includes(updates[field])) {
            throw new Error(`Invalid status: ${updates[field]}`);
          }
          ticket[field] = updates[field];
        }
      }
      ticket.updated_at = new Date().toISOString();
      this.save();
      return ticket;
    } finally {
      this.releaseLock();
    }
  }

  async deleteTicket(id) {
    await this.acquireLock();
    try {
      const index = this.data.tickets.findIndex(t => t.id === id);
      if (index === -1) return false;
      this.data.tickets.splice(index, 1);
      this.save();
      return true;
    } finally {
      this.releaseLock();
    }
  }

  async getMetrics() {
    await this.acquireLock();
    try {
      const tickets = this.data.tickets;
      const now = new Date();

      const statusCounts = { open: 0, in_progress: 0, resolved: 0 };
      const priorityCounts = { low: 0, medium: 0, high: 0 };
      let totalAgeSeconds = 0;
      let openTicketCount = 0;

      for (const ticket of tickets) {
        if (statusCounts[ticket.status] !== undefined) {
          statusCounts[ticket.status]++;
        }
        if (priorityCounts[ticket.priority] !== undefined) {
          priorityCounts[ticket.priority]++;
        }
        if (ticket.status === 'open') {
          const created = new Date(ticket.created_at);
          totalAgeSeconds += (now - created) / 1000;
          openTicketCount++;
        }
      }

      return {
        status_counts: statusCounts,
        priority_counts: priorityCounts,
        average_open_age_seconds: openTicketCount > 0 ? totalAgeSeconds / openTicketCount : 0
      };
    } finally {
      this.releaseLock();
    }
  }
}

class RequestHandler {
  constructor(store) {
    this.store = store;
    this.routes = {
      'GET /tickets': this.handleGetTickets.bind(this),
      'POST /tickets': this.handlePostTicket.bind(this),
      'GET /tickets/:id': this.handleGetTicket.bind(this),
      'PATCH /tickets/:id': this.handlePatchTicket.bind(this),
      'DELETE /tickets/:id': this.handleDeleteTicket.bind(this),
      'GET /metrics': this.handleGetMetrics.bind(this)
    };
  }

  parseUrl(url) {
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

  matchRoute(method, pathname) {
    const pathParts = pathname.split('/').filter(Boolean);

    for (const [routeKey, handler] of Object.entries(this.routes)) {
      const [routeMethod, ...routeParts] = routeKey.split(' ');
      const routePath = routeParts.join('/');
      const routePathParts = routePath.split('/').filter(Boolean);

      if (routeMethod !== method) continue;
      if (pathParts.length !== routePathParts.length) continue;

      const routeParams = {};
      let match = true;

      for (let i = 0; i < pathParts.length; i++) {
        if (routePathParts[i].startsWith(':')) {
          routeParams[routePathParts[i].slice(1)] = pathParts[i];
        } else if (routePathParts[i] !== pathParts[i]) {
          match = false;
          break;
        }
      }

      if (match) {
        return { handler, params: routeParams };
      }
    }
    return null;
  }

  setCorsHeaders(res) {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  }

  sendJson(res, statusCode, data) {
    res.writeHead(statusCode, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(data));
  }

  async handleRequest(req, res) {
    this.setCorsHeaders(res);

    if (req.method === 'OPTIONS') {
      res.writeHead(204);
      res.end();
      return;
    }

    const { pathname, params: queryParams } = this.parseUrl(req.url);
    const route = this.matchRoute(req.method, pathname);

    if (!route) {
      this.sendJson(res, 404, { error: 'Not found', message: `Route ${req.method} ${pathname} not found` });
      return;
    }

    try {
      await route.handler(req, res, route.params, queryParams);
    } catch (err) {
      this.sendJson(res, 500, { error: 'Internal server error', message: err.message });
    }
  }

  async handleGetTickets(req, res, params, queryParams) {
    const tickets = await this.store.readTickets(queryParams.status, queryParams.priority);
    this.sendJson(res, 200, tickets);
  }

  async handlePostTicket(req, res) {
    let body = '';
    req.on('data', chunk => { body += chunk; });

    await new Promise(resolve => req.on('end', resolve));

    let data;
    try {
      data = JSON.parse(body);
    } catch (err) {
      this.sendJson(res, 400, { error: 'Bad request', message: 'Invalid JSON' });
      return;
    }

    const errors = [];
    if (!data.subject || typeof data.subject !== 'string') errors.push('subject is required and must be a string');
    if (!data.description || typeof data.description !== 'string') errors.push('description is required and must be a string');
    if (data.priority && !['low', 'medium', 'high'].includes(data.priority)) {
      errors.push('priority must be one of: low, medium, high');
    }

    if (errors.length > 0) {
      this.sendJson(res, 400, { error: 'Validation failed', message: errors.join('; ') });
      return;
    }

    const ticketData = {
      subject: data.subject,
      description: data.description,
      priority: data.priority || 'medium'
    };

    const ticket = await this.store.createTicket(ticketData);
    this.sendJson(res, 201, ticket);
  }

  async handleGetTicket(req, res, params) {
    const id = parseInt(params.id);
    if (isNaN(id)) {
      this.sendJson(res, 400, { error: 'Bad request', message: 'Invalid ticket ID' });
      return;
    }

    const ticket = await this.store.getTicket(id);
    if (!ticket) {
      this.sendJson(res, 404, { error: 'Not found', message: `Ticket with id ${id} not found` });
      return;
    }

    this.sendJson(res, 200, ticket);
  }

  async handlePatchTicket(req, res, params) {
    const id = parseInt(params.id);
    if (isNaN(id)) {
      this.sendJson(res, 400, { error: 'Bad request', message: 'Invalid ticket ID' });
      return;
    }

    let body = '';
    req.on('data', chunk => { body += chunk; });

    await new Promise(resolve => req.on('end', resolve));

    let data;
    try {
      data = JSON.parse(body);
    } catch (err) {
      this.sendJson(res, 400, { error: 'Bad request', message: 'Invalid JSON' });
      return;
    }

    const allowedFields = ['subject', 'description', 'priority', 'status'];
    const hasField = allowedFields.some(f => data[f] !== undefined);
    if (!hasField) {
      this.sendJson(res, 400, { error: 'Bad request', message: 'No valid fields to update' });
      return;
    }

    try {
      const ticket = await this.store.updateTicket(id, data);
      if (!ticket) {
        this.sendJson(res, 404, { error: 'Not found', message: `Ticket with id ${id} not found` });
        return;
      }
      this.sendJson(res, 200, ticket);
    } catch (err) {
      this.sendJson(res, 400, { error: 'Validation failed', message: err.message });
    }
  }

  async handleDeleteTicket(req, res, params) {
    const id = parseInt(params.id);
    if (isNaN(id)) {
      this.sendJson(res, 400, { error: 'Bad request', message: 'Invalid ticket ID' });
      return;
    }

    const deleted = await this.store.deleteTicket(id);
    if (!deleted) {
      this.sendJson(res, 404, { error: 'Not found', message: `Ticket with id ${id} not found` });
      return;
    }

    this.sendJson(res, 200, { message: `Ticket ${id} deleted successfully` });
  }

  async handleGetMetrics(req, res) {
    const metrics = await this.store.getMetrics();
    this.sendJson(res, 200, metrics);
  }
}

const ticketStore = new TicketStore(DATA_FILE);
const requestHandler = new RequestHandler(ticketStore);

const server = http.createServer((req, res) => {
  requestHandler.handleRequest(req, res).catch(err => {
    console.error('Unhandled error:', err);
    requestHandler.sendJson(res, 500, { error: 'Internal server error', message: err.message });
  });
});

server.listen(PORT, HOST, () => {
  console.log(`Server running at http://${HOST}:${PORT}/`);
});
```
````
