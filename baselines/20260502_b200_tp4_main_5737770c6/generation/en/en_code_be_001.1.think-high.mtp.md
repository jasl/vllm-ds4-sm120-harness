# Generation Transcript

- Case: `en_code_be_001`
- Language group: `en`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `1`
- Thinking mode: `think-high`
- Thinking strength: `high`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 9.34776
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 318, "total_tokens": 3089, "completion_tokens": 2771, "prompt_tokens_details": null}`
- Prompt tokens: 318
- Completion tokens: 2771
- Total tokens: 3089

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
        this.data = [];
        this.lockQueue = [];
        this.locked = false;
        this.load();
    }

    load() {
        try {
            if (fs.existsSync(this.filePath)) {
                const content = fs.readFileSync(this.filePath, 'utf8');
                this.data = JSON.parse(content);
                if (!Array.isArray(this.data)) {
                    this.data = [];
                }
            } else {
                this.data = [];
                this.saveSync();
            }
        } catch (err) {
            this.data = [];
            this.saveSync();
        }
    }

    saveSync() {
        try {
            fs.writeFileSync(this.filePath, JSON.stringify(this.data, null, 2), 'utf8');
        } catch (err) {
            console.error('Error saving data:', err);
        }
    }

    async acquireLock() {
        return new Promise((resolve) => {
            const tryAcquire = () => {
                if (!this.locked) {
                    this.locked = true;
                    resolve();
                } else {
                    this.lockQueue.push(tryAcquire);
                }
            };
            tryAcquire();
        });
    }

    releaseLock() {
        this.locked = false;
        if (this.lockQueue.length > 0) {
            const next = this.lockQueue.shift();
            next();
        }
    }

    async readAll() {
        await this.acquireLock();
        try {
            this.load();
            return [...this.data];
        } finally {
            this.releaseLock();
        }
    }

    async findById(id) {
        await this.acquireLock();
        try {
            this.load();
            const ticket = this.data.find(t => t.id === id);
            return ticket ? { ...ticket } : null;
        } finally {
            this.releaseLock();
        }
    }

    async create(ticket) {
        await this.acquireLock();
        try {
            this.load();
            const now = new Date().toISOString();
            const newTicket = {
                id: this.generateId(),
                subject: ticket.subject,
                description: ticket.description,
                priority: ticket.priority,
                status: 'open',
                created_at: now,
                updated_at: now
            };
            this.data.push(newTicket);
            this.saveSync();
            return { ...newTicket };
        } finally {
            this.releaseLock();
        }
    }

    async update(id, updates) {
        await this.acquireLock();
        try {
            this.load();
            const index = this.data.findIndex(t => t.id === id);
            if (index === -1) {
                return null;
            }
            const allowedFields = ['subject', 'description', 'priority', 'status'];
            const now = new Date().toISOString();
            for (const field of allowedFields) {
                if (updates[field] !== undefined) {
                    this.data[index][field] = updates[field];
                }
            }
            this.data[index].updated_at = now;
            this.saveSync();
            return { ...this.data[index] };
        } finally {
            this.releaseLock();
        }
    }

    async delete(id) {
        await this.acquireLock();
        try {
            this.load();
            const index = this.data.findIndex(t => t.id === id);
            if (index === -1) {
                return false;
            }
            this.data.splice(index, 1);
            this.saveSync();
            return true;
        } finally {
            this.releaseLock();
        }
    }

    async getMetrics() {
        await this.acquireLock();
        try {
            this.load();
            const metrics = {
                status_counts: { open: 0, in_progress: 0, resolved: 0 },
                priority_counts: { low: 0, medium: 0, high: 0 },
                average_open_age_seconds: 0
            };

            const now = new Date();
            let totalOpenAge = 0;
            let openCount = 0;

            for (const ticket of this.data) {
                if (metrics.status_counts[ticket.status] !== undefined) {
                    metrics.status_counts[ticket.status]++;
                }
                if (metrics.priority_counts[ticket.priority] !== undefined) {
                    metrics.priority_counts[ticket.priority]++;
                }
                if (ticket.status === 'open') {
                    const created = new Date(ticket.created_at);
                    totalOpenAge += (now - created) / 1000;
                    openCount++;
                }
            }

            if (openCount > 0) {
                metrics.average_open_age_seconds = totalOpenAge / openCount;
            }

            return metrics;
        } finally {
            this.releaseLock();
        }
    }

    generateId() {
        const chars = 'abcdefghijklmnopqrstuvwxyz0123456789';
        let id = '';
        for (let i = 0; i < 8; i++) {
            id += chars.charAt(Math.floor(Math.random() * chars.length));
        }
        return id;
    }
}

const ticketStore = new TicketStore(DATA_FILE);

function parseBody(request) {
    return new Promise((resolve, reject) => {
        let body = '';
        request.on('data', chunk => {
            body += chunk.toString();
        });
        request.on('end', () => {
            try {
                const parsed = body ? JSON.parse(body) : {};
                resolve(parsed);
            } catch (err) {
                reject(new Error('Invalid JSON'));
            }
        });
        request.on('error', reject);
    });
}

function sendJSON(response, statusCode, data) {
    const body = JSON.stringify(data);
    response.writeHead(statusCode, {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type'
    });
    response.end(body);
}

function getPathSegments(url) {
    const pathname = new URL(url, `http://${HOST}`).pathname;
    return pathname.split('/').filter(Boolean);
}

function validateTicketData(body) {
    const errors = [];
    if (!body.subject || typeof body.subject !== 'string' || body.subject.trim() === '') {
        errors.push('subject is required and must be a non-empty string');
    }
    if (!body.description || typeof body.description !== 'string' || body.description.trim() === '') {
        errors.push('description is required and must be a non-empty string');
    }
    if (!body.priority || !['low', 'medium', 'high'].includes(body.priority)) {
        errors.push('priority must be one of: low, medium, high');
    }
    return errors;
}

function validateUpdateData(body) {
    const errors = [];
    const validFields = ['subject', 'description', 'priority', 'status'];
    const validPriorities = ['low', 'medium', 'high'];
    const validStatuses = ['open', 'in_progress', 'resolved'];

    for (const field of validFields) {
        if (body[field] !== undefined) {
            if (field === 'subject' || field === 'description') {
                if (typeof body[field] !== 'string' || body[field].trim() === '') {
                    errors.push(`${field} must be a non-empty string`);
                }
            } else if (field === 'priority') {
                if (!validPriorities.includes(body[field])) {
                    errors.push('priority must be one of: low, medium, high');
                }
            } else if (field === 'status') {
                if (!validStatuses.includes(body[field])) {
                    errors.push('status must be one of: open, in_progress, resolved');
                }
            }
        }
    }

    if (Object.keys(body).length === 0) {
        errors.push('No valid fields to update');
    }

    return errors;
}

async function handleRequest(request, response) {
    const segments = getPathSegments(request.url);
    const method = request.method.toUpperCase();

    // Handle CORS preflight
    if (method === 'OPTIONS') {
        sendJSON(response, 200, {});
        return;
    }

    try {
        // GET /tickets
        if (method === 'GET' && segments.length === 1 && segments[0] === 'tickets') {
            const url = new URL(request.url, `http://${HOST}`);
            const statusFilter = url.searchParams.get('status');
            const priorityFilter = url.searchParams.get('priority');

            const tickets = await ticketStore.readAll();
            let filtered = tickets;

            if (statusFilter && ['open', 'in_progress', 'resolved'].includes(statusFilter)) {
                filtered = filtered.filter(t => t.status === statusFilter);
            }
            if (priorityFilter && ['low', 'medium', 'high'].includes(priorityFilter)) {
                filtered = filtered.filter(t => t.priority === priorityFilter);
            }

            sendJSON(response, 200, filtered);
            return;
        }

        // POST /tickets
        if (method === 'POST' && segments.length === 1 && segments[0] === 'tickets') {
            const body = await parseBody(request);
            const errors = validateTicketData(body);
            if (errors.length > 0) {
                sendJSON(response, 400, { error: 'Validation failed', details: errors });
                return;
            }

            const ticket = await ticketStore.create({
                subject: body.subject.trim(),
                description: body.description.trim(),
                priority: body.priority
            });
            sendJSON(response, 201, ticket);
            return;
        }

        // GET /tickets/{id}
        if (method === 'GET' && segments.length === 2 && segments[0] === 'tickets') {
            const id = segments[1];
            const ticket = await ticketStore.findById(id);
            if (!ticket) {
                sendJSON(response, 404, { error: 'Ticket not found' });
                return;
            }
            sendJSON(response, 200, ticket);
            return;
        }

        // PATCH /tickets/{id}
        if (method === 'PATCH' && segments.length === 2 && segments[0] === 'tickets') {
            const id = segments[1];
            const body = await parseBody(request);
            const errors = validateUpdateData(body);
            if (errors.length > 0) {
                sendJSON(response, 400, { error: 'Validation failed', details: errors });
                return;
            }

            const cleanUpdates = {};
            if (body.subject !== undefined) cleanUpdates.subject = body.subject.trim();
            if (body.description !== undefined) cleanUpdates.description = body.description.trim();
            if (body.priority !== undefined) cleanUpdates.priority = body.priority;
            if (body.status !== undefined) cleanUpdates.status = body.status;

            const ticket = await ticketStore.update(id, cleanUpdates);
            if (!ticket) {
                sendJSON(response, 404, { error: 'Ticket not found' });
                return;
            }
            sendJSON(response, 200, ticket);
            return;
        }

        // DELETE /tickets/{id}
        if (method === 'DELETE' && segments.length === 2 && segments[0] === 'tickets') {
            const id = segments[1];
            const deleted = await ticketStore.delete(id);
            if (!deleted) {
                sendJSON(response, 404, { error: 'Ticket not found' });
                return;
            }
            sendJSON(response, 200, { message: 'Ticket deleted' });
            return;
        }

        // GET /metrics
        if (method === 'GET' && segments.length === 1 && segments[0] === 'metrics') {
            const metrics = await ticketStore.getMetrics();
            sendJSON(response, 200, metrics);
            return;
        }

        // Unknown route
        sendJSON(response, 404, { error: 'Route not found' });

    } catch (err) {
        if (err.message === 'Invalid JSON') {
            sendJSON(response, 400, { error: 'Invalid JSON in request body' });
        } else {
            console.error('Server error:', err);
            sendJSON(response, 500, { error: 'Internal server error' });
        }
    }
}

const server = http.createServer(handleRequest);

server.listen(PORT, HOST, () => {
    console.log(`Server running at http://${HOST}:${PORT}/`);
});

module.exports = { TicketStore };
```
````
