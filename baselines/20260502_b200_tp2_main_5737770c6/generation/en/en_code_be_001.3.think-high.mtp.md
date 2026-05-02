# Generation Transcript

- Case: `en_code_be_001`
- Language group: `en`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `3`
- Thinking mode: `think-high`
- Thinking strength: `high`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 10.271144
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 318, "total_tokens": 3330, "completion_tokens": 3012, "prompt_tokens_details": null}`
- Prompt tokens: 318
- Completion tokens: 3012
- Total tokens: 3330

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

const DATA_FILE = path.join(__dirname, 'tickets.json');
const PORT = 8080;
const HOST = '127.0.0.1';

class TicketStore {
    constructor(filePath) {
        this.filePath = filePath;
        this.lock = false;
        this.waitQueue = [];
        this.tickets = [];
        this.nextId = 1;
        this.load();
    }

    load() {
        try {
            if (fs.existsSync(this.filePath)) {
                const data = fs.readFileSync(this.filePath, 'utf8');
                const parsed = JSON.parse(data);
                this.tickets = parsed.tickets || [];
                this.nextId = parsed.nextId || 1;
            } else {
                this.tickets = [];
                this.nextId = 1;
                this.save();
            }
        } catch (err) {
            console.error('Error loading tickets:', err);
            this.tickets = [];
            this.nextId = 1;
            this.save();
        }
    }

    save() {
        try {
            const data = JSON.stringify({
                tickets: this.tickets,
                nextId: this.nextId
            });
            fs.writeFileSync(this.filePath, data, 'utf8');
        } catch (err) {
            console.error('Error saving tickets:', err);
        }
    }

    async acquireLock() {
        while (this.lock) {
            await new Promise(resolve => this.waitQueue.push(resolve));
        }
        this.lock = true;
    }

    releaseLock() {
        this.lock = false;
        if (this.waitQueue.length > 0) {
            const next = this.waitQueue.shift();
            next();
        }
    }

    async getAll(filters = {}) {
        await this.acquireLock();
        try {
            let result = [...this.tickets];

            if (filters.status) {
                result = result.filter(t => t.status === filters.status);
            }
            if (filters.priority) {
                result = result.filter(t => t.priority === filters.priority);
            }

            return { success: true, data: result };
        } finally {
            this.releaseLock();
        }
    }

    async getById(id) {
        await this.acquireLock();
        try {
            const ticket = this.tickets.find(t => t.id === id);
            if (!ticket) {
                return { success: false, error: 'Ticket not found', status: 404 };
            }
            return { success: true, data: ticket };
        } finally {
            this.releaseLock();
        }
    }

    async create(ticketData) {
        const errors = [];

        if (!ticketData.subject || typeof ticketData.subject !== 'string' || ticketData.subject.trim() === '') {
            errors.push('subject is required and must be a non-empty string');
        }
        if (!ticketData.description || typeof ticketData.description !== 'string' || ticketData.description.trim() === '') {
            errors.push('description is required and must be a non-empty string');
        }
        if (ticketData.priority && !['low', 'medium', 'high'].includes(ticketData.priority)) {
            errors.push('priority must be one of: low, medium, high');
        }
        if (!ticketData.priority) {
            errors.push('priority is required');
        }

        if (errors.length > 0) {
            return { success: false, error: errors.join('; '), status: 400 };
        }

        await this.acquireLock();
        try {
            const now = new Date().toISOString();
            const ticket = {
                id: this.nextId++,
                subject: ticketData.subject.trim(),
                description: ticketData.description.trim(),
                priority: ticketData.priority,
                status: 'open',
                created_at: now,
                updated_at: now
            };

            this.tickets.push(ticket);
            this.save();

            return { success: true, data: ticket, status: 201 };
        } finally {
            this.releaseLock();
        }
    }

    async update(id, updates) {
        await this.acquireLock();
        try {
            const index = this.tickets.findIndex(t => t.id === id);
            if (index === -1) {
                return { success: false, error: 'Ticket not found', status: 404 };
            }

            const allowedFields = ['subject', 'description', 'priority', 'status'];
            const validUpdates = {};

            for (const field of allowedFields) {
                if (updates[field] !== undefined) {
                    if (field === 'priority' && !['low', 'medium', 'high'].includes(updates[field])) {
                        return { success: false, error: 'priority must be one of: low, medium, high', status: 400 };
                    }
                    if (field === 'status' && !['open', 'in_progress', 'resolved'].includes(updates[field])) {
                        return { success: false, error: 'status must be one of: open, in_progress, resolved', status: 400 };
                    }
                    if ((field === 'subject' || field === 'description') && (typeof updates[field] !== 'string' || updates[field].trim() === '')) {
                        return { success: false, error: `${field} must be a non-empty string`, status: 400 };
                    }
                    validUpdates[field] = updates[field].trim ? updates[field].trim() : updates[field];
                }
            }

            if (Object.keys(validUpdates).length === 0) {
                return { success: false, error: 'No valid fields to update', status: 400 };
            }

            const ticket = this.tickets[index];
            Object.assign(ticket, validUpdates);
            ticket.updated_at = new Date().toISOString();

            this.save();

            return { success: true, data: ticket };
        } finally {
            this.releaseLock();
        }
    }

    async delete(id) {
        await this.acquireLock();
        try {
            const index = this.tickets.findIndex(t => t.id === id);
            if (index === -1) {
                return { success: false, error: 'Ticket not found', status: 404 };
            }

            const ticket = this.tickets.splice(index, 1)[0];
            this.save();

            return { success: true, data: ticket };
        } finally {
            this.releaseLock();
        }
    }

    async getMetrics() {
        await this.acquireLock();
        try {
            const now = new Date();
            const metrics = {
                by_status: {
                    open: 0,
                    in_progress: 0,
                    resolved: 0
                },
                by_priority: {
                    low: 0,
                    medium: 0,
                    high: 0
                },
                average_age_open_seconds: 0
            };

            let totalAgeSeconds = 0;
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
                if (ticket.status !== 'resolved') {
                    const created = new Date(ticket.created_at);
                    const ageSeconds = (now - created) / 1000;
                    totalAgeSeconds += ageSeconds;
                    openCount++;
                }
            }

            metrics.average_age_open_seconds = openCount > 0 ? totalAgeSeconds / openCount : 0;

            return { success: true, data: metrics };
        } finally {
            this.releaseLock();
        }
    }
}

const store = new TicketStore(DATA_FILE);

function sendJSON(res, statusCode, data) {
    const body = JSON.stringify(data);
    res.writeHead(statusCode, {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Accept',
        'Content-Length': Buffer.byteLength(body)
    });
    res.end(body);
}

function parseBody(req) {
    return new Promise((resolve, reject) => {
        let body = '';
        req.on('data', chunk => {
            body += chunk.toString();
            if (body.length > 1048576) { // 1MB limit
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

function parseURL(url) {
    const [pathname, queryString] = url.split('?');
    const params = {};

    if (queryString) {
        const pairs = queryString.split('&');
        for (const pair of pairs) {
            const [key, value] = pair.split('=').map(decodeURIComponent);
            if (key) {
                params[key] = value;
            }
        }
    }

    return { pathname: pathname.replace(/\/$/, '') || '/', params };
}

function parsePath(pathname) {
    const parts = pathname.split('/').filter(Boolean);

    if (parts.length === 1 && parts[0] === 'tickets') {
        return { resource: 'tickets', id: null };
    }
    if (parts.length === 2 && parts[0] === 'tickets') {
        const id = parseInt(parts[1], 10);
        if (isNaN(id)) {
            return { resource: 'invalid', id: null };
        }
        return { resource: 'tickets', id };
    }
    if (parts.length === 1 && parts[0] === 'metrics') {
        return { resource: 'metrics', id: null };
    }

    return { resource: 'unknown', id: null };
}

async function handleRequest(req, res) {
    // Handle CORS preflight
    if (req.method === 'OPTIONS') {
        res.writeHead(204, {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Accept',
            'Access-Control-Max-Age': '86400'
        });
        res.end();
        return;
    }

    const { pathname, params } = parseURL(req.url);
    const { resource, id } = parsePath(pathname);

    try {
        switch (resource) {
            case 'tickets': {
                if (id === null && req.method === 'GET') {
                    // GET /tickets
                    const filters = {};
                    if (params.status && ['open', 'in_progress', 'resolved'].includes(params.status)) {
                        filters.status = params.status;
                    }
                    if (params.priority && ['low', 'medium', 'high'].includes(params.priority)) {
                        filters.priority = params.priority;
                    }
                    const result = await store.getAll(filters);
                    sendJSON(res, 200, result.data);
                } else if (id === null && req.method === 'POST') {
                    // POST /tickets
                    const body = await parseBody(req);
                    const result = await store.create(body);
                    sendJSON(res, result.status || 200, result.success ? result.data : { error: result.error });
                } else if (id !== null && req.method === 'GET') {
                    // GET /tickets/:id
                    const result = await store.getById(id);
                    sendJSON(res, result.status || 200, result.success ? result.data : { error: result.error });
                } else if (id !== null && req.method === 'PATCH') {
                    // PATCH /tickets/:id
                    const body = await parseBody(req);
                    const result = await store.update(id, body);
                    sendJSON(res, result.status || 200, result.success ? result.data : { error: result.error });
                } else if (id !== null && req.method === 'DELETE') {
                    // DELETE /tickets/:id
                    const result = await store.delete(id);
                    sendJSON(res, result.status || 200, result.success ? result.data : { error: result.error });
                } else {
                    sendJSON(res, 405, { error: 'Method not allowed' });
                }
                break;
            }
            case 'metrics': {
                if (req.method === 'GET') {
                    const result = await store.getMetrics();
                    sendJSON(res, 200, result.data);
                } else {
                    sendJSON(res, 405, { error: 'Method not allowed' });
                }
                break;
            }
            default: {
                sendJSON(res, 404, { error: 'Route not found' });
            }
        }
    } catch (err) {
        if (err.message === 'Invalid JSON') {
            sendJSON(res, 400, { error: 'Invalid JSON in request body' });
        } else if (err.message === 'Request body too large') {
            sendJSON(res, 413, { error: 'Request body too large' });
        } else {
            console.error('Unhandled error:', err);
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
