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
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 42.773482
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 318, "total_tokens": 3042, "completion_tokens": 2724, "prompt_tokens_details": null}`
- Prompt tokens: 318
- Completion tokens: 2724
- Total tokens: 3042

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

const DATA_FILE = path.join(__dirname, 'tickets.json');
const HOST = '127.0.0.1';
const PORT = 8080;

class TicketStore {
    constructor() {
        this.filePath = DATA_FILE;
        this.tickets = [];
        this.nextId = 1;
        this.lock = false;
        this.queue = [];
        this.load();
    }

    load() {
        try {
            if (fs.existsSync(this.filePath)) {
                const data = fs.readFileSync(this.filePath, 'utf8');
                if (data) {
                    const parsed = JSON.parse(data);
                    this.tickets = parsed.tickets || [];
                    this.nextId = parsed.nextId || 1;
                }
            } else {
                this.saveSync();
            }
        } catch (err) {
            this.tickets = [];
            this.nextId = 1;
            this.saveSync();
        }
    }

    saveSync() {
        const data = JSON.stringify({ tickets: this.tickets, nextId: this.nextId }, null, 2);
        fs.writeFileSync(this.filePath, data, 'utf8');
    }

    async save() {
        return new Promise((resolve, reject) => {
            const data = JSON.stringify({ tickets: this.tickets, nextId: this.nextId }, null, 2);
            fs.writeFile(this.filePath, data, 'utf8', (err) => {
                if (err) reject(err);
                else resolve();
            });
        });
    }

    async acquireLock() {
        while (this.lock) {
            await new Promise(resolve => this.queue.push(resolve));
        }
        this.lock = true;
    }

    releaseLock() {
        this.lock = false;
        const next = this.queue.shift();
        if (next) {
            next();
        }
    }

    async readWriteOperation(operation) {
        await this.acquireLock();
        try {
            const result = await operation();
            await this.save();
            return result;
        } finally {
            this.releaseLock();
        }
    }

    getAll(status, priority) {
        let result = this.tickets;
        if (status) {
            result = result.filter(t => t.status === status);
        }
        if (priority) {
            result = result.filter(t => t.priority === priority);
        }
        return result;
    }

    getById(id) {
        return this.tickets.find(t => t.id === id) || null;
    }

    async create(subject, description, priority, status) {
        return this.readWriteOperation(() => {
            const ticket = {
                id: this.nextId++,
                subject,
                description,
                priority,
                status: status || 'open',
                created_at: new Date().toISOString(),
                updated_at: new Date().toISOString()
            };
            this.tickets.push(ticket);
            return ticket;
        });
    }

    async update(id, fields) {
        return this.readWriteOperation(() => {
            const ticket = this.tickets.find(t => t.id === id);
            if (!ticket) return null;

            if (fields.subject !== undefined) ticket.subject = fields.subject;
            if (fields.description !== undefined) ticket.description = fields.description;
            if (fields.priority !== undefined) ticket.priority = fields.priority;
            if (fields.status !== undefined) ticket.status = fields.status;
            ticket.updated_at = new Date().toISOString();
            return ticket;
        });
    }

    async delete(id) {
        return this.readWriteOperation(() => {
            const index = this.tickets.findIndex(t => t.id === id);
            if (index === -1) return false;
            this.tickets.splice(index, 1);
            return true;
        });
    }

    getMetrics() {
        const now = new Date();
        const statusCounts = { open: 0, in_progress: 0, resolved: 0 };
        const priorityCounts = { low: 0, medium: 0, high: 0 };
        let totalAgeSeconds = 0;
        let openCount = 0;

        for (const ticket of this.tickets) {
            if (statusCounts[ticket.status] !== undefined) {
                statusCounts[ticket.status]++;
            }
            if (priorityCounts[ticket.priority] !== undefined) {
                priorityCounts[ticket.priority]++;
            }
            if (ticket.status === 'open') {
                const created = new Date(ticket.created_at);
                const ageSeconds = (now - created) / 1000;
                totalAgeSeconds += ageSeconds;
                openCount++;
            }
        }

        return {
            status_counts: statusCounts,
            priority_counts: priorityCounts,
            average_open_age_seconds: openCount > 0 ? totalAgeSeconds / openCount : 0
        };
    }
}

const store = new TicketStore();

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
                reject(new Error('Payload too large'));
            }
        });
        req.on('end', () => {
            try {
                if (!body) {
                    resolve({});
                    return;
                }
                resolve(JSON.parse(body));
            } catch (err) {
                reject(new Error('Invalid JSON'));
            }
        });
        req.on('error', reject);
    });
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
        errors.push('priority must be low, medium, or high');
    }
    if (body.status && !['open', 'in_progress', 'resolved'].includes(body.status)) {
        errors.push('status must be open, in_progress, or resolved');
    }
    return errors;
}

function validateTicketUpdate(body) {
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
    return errors;
}

const server = http.createServer(async (req, res) => {
    const parsedUrl = url.parse(req.url, true);
    const pathname = parsedUrl.pathname;
    const method = req.method;

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
        // GET /metrics
        if (pathname === '/metrics' && method === 'GET') {
            const metrics = store.getMetrics();
            sendJSON(res, 200, metrics);
            return;
        }

        // GET /tickets
        if (pathname === '/tickets' && method === 'GET') {
            const { status, priority } = parsedUrl.query;
            const tickets = store.getAll(status, priority);
            sendJSON(res, 200, tickets);
            return;
        }

        // POST /tickets
        if (pathname === '/tickets' && method === 'POST') {
            let body;
            try {
                body = await parseBody(req);
            } catch (err) {
                if (err.message === 'Invalid JSON') {
                    sendJSON(res, 400, { error: 'Invalid JSON in request body' });
                    return;
                }
                if (err.message === 'Payload too large') {
                    sendJSON(res, 413, { error: 'Request body too large' });
                    return;
                }
                throw err;
            }

            const errors = validateTicketInput(body);
            if (errors.length > 0) {
                sendJSON(res, 400, { error: 'Validation failed', details: errors });
                return;
            }

            const ticket = await store.create(
                body.subject.trim(),
                body.description.trim(),
                body.priority || 'low',
                body.status || 'open'
            );
            sendJSON(res, 201, ticket);
            return;
        }

        // Routes with ID parameter
        const ticketMatch = pathname.match(/^\/tickets\/(\d+)$/);
        if (ticketMatch) {
            const id = parseInt(ticketMatch[1], 10);

            // GET /tickets/{id}
            if (method === 'GET') {
                const ticket = store.getById(id);
                if (!ticket) {
                    sendJSON(res, 404, { error: `Ticket with id ${id} not found` });
                    return;
                }
                sendJSON(res, 200, ticket);
                return;
            }

            // PATCH /tickets/{id}
            if (method === 'PATCH') {
                let body;
                try {
                    body = await parseBody(req);
                } catch (err) {
                    if (err.message === 'Invalid JSON') {
                        sendJSON(res, 400, { error: 'Invalid JSON in request body' });
                        return;
                    }
                    if (err.message === 'Payload too large') {
                        sendJSON(res, 413, { error: 'Request body too large' });
                        return;
                    }
                    throw err;
                }

                const errors = validateTicketUpdate(body);
                if (errors.length > 0) {
                    sendJSON(res, 400, { error: 'Validation failed', details: errors });
                    return;
                }

                const updateFields = {};
                if (body.subject !== undefined) updateFields.subject = body.subject.trim();
                if (body.description !== undefined) updateFields.description = body.description.trim();
                if (body.priority !== undefined) updateFields.priority = body.priority;
                if (body.status !== undefined) updateFields.status = body.status;

                const ticket = await store.update(id, updateFields);
                if (!ticket) {
                    sendJSON(res, 404, { error: `Ticket with id ${id} not found` });
                    return;
                }
                sendJSON(res, 200, ticket);
                return;
            }

            // DELETE /tickets/{id}
            if (method === 'DELETE') {
                const deleted = await store.delete(id);
                if (!deleted) {
                    sendJSON(res, 404, { error: `Ticket with id ${id} not found` });
                    return;
                }
                sendJSON(res, 204, null);
                return;
            }

            // Method not allowed on /tickets/{id}
            sendJSON(res, 405, { error: `Method ${method} not allowed` });
            return;
        }

        // Unknown route
        sendJSON(res, 404, { error: `Route ${method} ${pathname} not found` });

    } catch (err) {
        console.error('Server error:', err);
        sendJSON(res, 500, { error: 'Internal server error' });
    }
});

server.listen(PORT, HOST, () => {
    console.log(`Server running at http://${HOST}:${PORT}/`);
});
```
````
