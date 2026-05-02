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
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 9.023096
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 318, "total_tokens": 2933, "completion_tokens": 2615, "prompt_tokens_details": null}`
- Prompt tokens: 318
- Completion tokens: 2615
- Total tokens: 2933

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
        this.lockQueue = [];
        this.locked = false;
        this.load();
    }

    load() {
        try {
            const data = fs.readFileSync(this.filePath, 'utf-8');
            this.tickets = JSON.parse(data);
        } catch (err) {
            this.tickets = [];
            this.saveSync();
        }
    }

    saveSync() {
        fs.writeFileSync(this.filePath, JSON.stringify(this.tickets, null, 2), 'utf-8');
    }

    acquireLock() {
        return new Promise((resolve) => {
            const tryLock = () => {
                if (!this.locked) {
                    this.locked = true;
                    resolve();
                } else {
                    this.lockQueue.push(tryLock);
                }
            };
            tryLock();
        });
    }

    releaseLock() {
        this.locked = false;
        if (this.lockQueue.length > 0) {
            const next = this.lockQueue.shift();
            next();
        }
    }

    async getAll(filter = {}) {
        await this.acquireLock();
        try {
            let result = [...this.tickets];
            if (filter.status) {
                result = result.filter(t => t.status === filter.status);
            }
            if (filter.priority) {
                result = result.filter(t => t.priority === filter.priority);
            }
            return result;
        } finally {
            this.releaseLock();
        }
    }

    async getById(id) {
        await this.acquireLock();
        try {
            return this.tickets.find(t => t.id === id) || null;
        } finally {
            this.releaseLock();
        }
    }

    async create(ticketData) {
        await this.acquireLock();
        try {
            const now = new Date().toISOString();
            const ticket = {
                id: crypto.randomUUID(),
                subject: ticketData.subject,
                description: ticketData.description,
                priority: ticketData.priority,
                status: 'open',
                created_at: now,
                updated_at: now
            };
            this.tickets.push(ticket);
            this.saveSync();
            return ticket;
        } finally {
            this.releaseLock();
        }
    }

    async update(id, updates) {
        await this.acquireLock();
        try {
            const index = this.tickets.findIndex(t => t.id === id);
            if (index === -1) return null;

            const allowedFields = ['subject', 'description', 'priority', 'status'];
            for (const field of allowedFields) {
                if (updates[field] !== undefined) {
                    this.tickets[index][field] = updates[field];
                }
            }
            this.tickets[index].updated_at = new Date().toISOString();
            this.saveSync();
            return this.tickets[index];
        } finally {
            this.releaseLock();
        }
    }

    async delete(id) {
        await this.acquireLock();
        try {
            const index = this.tickets.findIndex(t => t.id === id);
            if (index === -1) return false;
            this.tickets.splice(index, 1);
            this.saveSync();
            return true;
        } finally {
            this.releaseLock();
        }
    }

    async getMetrics() {
        await this.acquireLock();
        try {
            const now = Date.now();
            const metrics = {
                by_status: { open: 0, in_progress: 0, resolved: 0 },
                by_priority: { low: 0, medium: 0, high: 0 },
                average_age_of_open_tickets_seconds: 0
            };

            let totalAge = 0;
            let openCount = 0;

            for (const ticket of this.tickets) {
                // Count by status
                if (metrics.by_status[ticket.status] !== undefined) {
                    metrics.by_status[ticket.status]++;
                }

                // Count by priority
                if (metrics.by_priority[ticket.priority] !== undefined) {
                    metrics.by_priority[ticket.priority]++;
                }

                // Calculate age for open tickets
                if (ticket.status === 'open') {
                    const createdAt = new Date(ticket.created_at).getTime();
                    totalAge += (now - createdAt) / 1000;
                    openCount++;
                }
            }

            if (openCount > 0) {
                metrics.average_age_of_open_tickets_seconds = Math.round(totalAge / openCount);
            }

            return metrics;
        } finally {
            this.releaseLock();
        }
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
    res.writeHead(statusCode, {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type'
    });
    res.end(JSON.stringify(data));
}

function parseURL(url) {
    const [pathPart, queryString] = url.split('?');
    const params = {};
    if (queryString) {
        queryString.split('&').forEach(pair => {
            const [key, value] = pair.split('=');
            params[decodeURIComponent(key)] = decodeURIComponent(value || '');
        });
    }
    return { path: pathPart, params };
}

function validateTicketData(data) {
    const errors = [];
    if (!data.subject || typeof data.subject !== 'string' || data.subject.trim() === '') {
        errors.push('subject is required and must be a non-empty string');
    }
    if (!data.description || typeof data.description !== 'string' || data.description.trim() === '') {
        errors.push('description is required and must be a non-empty string');
    }
    if (!data.priority || !['low', 'medium', 'high'].includes(data.priority)) {
        errors.push('priority must be one of: low, medium, high');
    }
    return errors;
}

function validateUpdateData(data) {
    const errors = [];
    const validFields = ['subject', 'description', 'priority', 'status'];
    const validPriorities = ['low', 'medium', 'high'];
    const validStatuses = ['open', 'in_progress', 'resolved'];

    for (const field of Object.keys(data)) {
        if (!validFields.includes(field)) {
            errors.push(`Invalid field: ${field}`);
        }
    }

    if (data.subject !== undefined && (typeof data.subject !== 'string' || data.subject.trim() === '')) {
        errors.push('subject must be a non-empty string');
    }
    if (data.description !== undefined && (typeof data.description !== 'string' || data.description.trim() === '')) {
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
    const { path, params } = parseURL(req.url);
    const method = req.method.toUpperCase();

    // CORS preflight
    if (method === 'OPTIONS') {
        sendJSON(res, 200, {});
        return;
    }

    try {
        // Route: GET /tickets
        if (path === '/tickets' && method === 'GET') {
            const filter = {};
            if (params.status && ['open', 'in_progress', 'resolved'].includes(params.status)) {
                filter.status = params.status;
            }
            if (params.priority && ['low', 'medium', 'high'].includes(params.priority)) {
                filter.priority = params.priority;
            }
            const tickets = await store.getAll(filter);
            sendJSON(res, 200, tickets);
            return;
        }

        // Route: POST /tickets
        if (path === '/tickets' && method === 'POST') {
            const data = await parseBody(req);
            const errors = validateTicketData(data);
            if (errors.length > 0) {
                sendJSON(res, 400, { error: 'Validation failed', details: errors });
                return;
            }
            const ticket = await store.create({
                subject: data.subject.trim(),
                description: data.description.trim(),
                priority: data.priority
            });
            sendJSON(res, 201, ticket);
            return;
        }

        // Route: GET /metrics
        if (path === '/metrics' && method === 'GET') {
            const metrics = await store.getMetrics();
            sendJSON(res, 200, metrics);
            return;
        }

        // Route: /tickets/{id}
        const ticketMatch = path.match(/^\/tickets\/([a-f0-9-]+)$/);
        if (ticketMatch) {
            const id = ticketMatch[1];

            // GET /tickets/{id}
            if (method === 'GET') {
                const ticket = await store.getById(id);
                if (!ticket) {
                    sendJSON(res, 404, { error: 'Ticket not found' });
                    return;
                }
                sendJSON(res, 200, ticket);
                return;
            }

            // PATCH /tickets/{id}
            if (method === 'PATCH') {
                const ticket = await store.getById(id);
                if (!ticket) {
                    sendJSON(res, 404, { error: 'Ticket not found' });
                    return;
                }
                const data = await parseBody(req);
                const errors = validateUpdateData(data);
                if (errors.length > 0) {
                    sendJSON(res, 400, { error: 'Validation failed', details: errors });
                    return;
                }
                if (Object.keys(data).length === 0) {
                    sendJSON(res, 400, { error: 'No valid fields to update' });
                    return;
                }
                const updated = await store.update(id, data);
                sendJSON(res, 200, updated);
                return;
            }

            // DELETE /tickets/{id}
            if (method === 'DELETE') {
                const deleted = await store.delete(id);
                if (!deleted) {
                    sendJSON(res, 404, { error: 'Ticket not found' });
                    return;
                }
                sendJSON(res, 200, { message: 'Ticket deleted' });
                return;
            }

            sendJSON(res, 405, { error: 'Method not allowed' });
            return;
        }

        // Route not found
        sendJSON(res, 404, { error: 'Not found' });

    } catch (err) {
        if (err.message === 'Invalid JSON') {
            sendJSON(res, 400, { error: 'Invalid JSON in request body' });
        } else {
            console.error(err);
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
