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
- Elapsed seconds: 19.06928
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 318, "total_tokens": 2986, "completion_tokens": 2668, "prompt_tokens_details": null}`
- Prompt tokens: 318
- Completion tokens: 2668
- Total tokens: 2986

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
const HOST = '127.0.0.1';
const PORT = 8080;

class TicketStore {
    constructor(filePath) {
        this.filePath = filePath;
        this.data = [];
        this.lock = null;
        this.loadData();
    }

    loadData() {
        try {
            if (fs.existsSync(this.filePath)) {
                const raw = fs.readFileSync(this.filePath, 'utf8');
                this.data = JSON.parse(raw);
            } else {
                this.data = [];
                this.saveDataSync();
            }
        } catch (err) {
            console.error('Failed to load tickets.json, starting with empty array');
            this.data = [];
        }
    }

    saveDataSync() {
        try {
            fs.writeFileSync(this.filePath, JSON.stringify(this.data, null, 2), 'utf8');
        } catch (err) {
            console.error('Failed to save tickets.json');
        }
    }

    acquireLock() {
        if (this.lock) {
            return false;
        }
        this.lock = new Promise((resolve) => {
            this._unlock = resolve;
        });
        return true;
    }

    releaseLock() {
        if (this._unlock) {
            this._unlock();
            this.lock = null;
            this._unlock = null;
        }
    }

    async withLock(callback) {
        if (!this.acquireLock()) {
            return { error: 'Server busy, please retry', status: 503 };
        }
        try {
            const result = await callback(this.data);
            this.saveDataSync();
            return result;
        } finally {
            this.releaseLock();
        }
    }

    generateId() {
        if (this.data.length === 0) return 1;
        return Math.max(...this.data.map(t => t.id)) + 1;
    }

    getTimestamp() {
        return new Date().toISOString();
    }

    getAll(status, priority) {
        let filtered = [...this.data];
        if (status) {
            filtered = filtered.filter(t => t.status === status);
        }
        if (priority) {
            filtered = filtered.filter(t => t.priority === priority);
        }
        return { tickets: filtered };
    }

    getById(id) {
        const ticket = this.data.find(t => t.id === id);
        if (!ticket) {
            return { error: 'Ticket not found', status: 404 };
        }
        return { ticket };
    }

    create(subject, description, priority) {
        const errors = [];
        if (!subject || typeof subject !== 'string' || subject.trim().length === 0) {
            errors.push('subject is required and must be a non-empty string');
        }
        if (!description || typeof description !== 'string' || description.trim().length === 0) {
            errors.push('description is required and must be a non-empty string');
        }
        const validPriorities = ['low', 'medium', 'high'];
        if (!priority || !validPriorities.includes(priority)) {
            errors.push('priority must be one of: low, medium, high');
        }
        if (errors.length > 0) {
            return { error: errors.join('; '), status: 400 };
        }

        const now = this.getTimestamp();
        const ticket = {
            id: this.generateId(),
            subject: subject.trim(),
            description: description.trim(),
            priority: priority,
            status: 'open',
            created_at: now,
            updated_at: now
        };
        this.data.push(ticket);
        return { ticket, status: 201 };
    }

    update(id, updates) {
        const index = this.data.findIndex(t => t.id === id);
        if (index === -1) {
            return { error: 'Ticket not found', status: 404 };
        }

        const allowedFields = ['subject', 'description', 'priority', 'status'];
        const validPriorities = ['low', 'medium', 'high'];
        const validStatuses = ['open', 'in_progress', 'resolved'];
        const errors = [];

        for (const key of Object.keys(updates)) {
            if (!allowedFields.includes(key)) {
                errors.push(`Invalid field: ${key}`);
            }
        }

        if (updates.subject !== undefined) {
            if (typeof updates.subject !== 'string' || updates.subject.trim().length === 0) {
                errors.push('subject must be a non-empty string');
            }
        }
        if (updates.description !== undefined) {
            if (typeof updates.description !== 'string' || updates.description.trim().length === 0) {
                errors.push('description must be a non-empty string');
            }
        }
        if (updates.priority !== undefined) {
            if (!validPriorities.includes(updates.priority)) {
                errors.push('priority must be one of: low, medium, high');
            }
        }
        if (updates.status !== undefined) {
            if (!validStatuses.includes(updates.status)) {
                errors.push('status must be one of: open, in_progress, resolved');
            }
        }

        if (errors.length > 0) {
            return { error: errors.join('; '), status: 400 };
        }

        const ticket = this.data[index];
        if (updates.subject !== undefined) ticket.subject = updates.subject.trim();
        if (updates.description !== undefined) ticket.description = updates.description.trim();
        if (updates.priority !== undefined) ticket.priority = updates.priority;
        if (updates.status !== undefined) ticket.status = updates.status;
        ticket.updated_at = this.getTimestamp();

        return { ticket };
    }

    delete(id) {
        const index = this.data.findIndex(t => t.id === id);
        if (index === -1) {
            return { error: 'Ticket not found', status: 404 };
        }
        const deleted = this.data.splice(index, 1)[0];
        return { message: 'Ticket deleted', ticket: deleted };
    }

    getMetrics() {
        const now = new Date();
        const statusCounts = { open: 0, in_progress: 0, resolved: 0 };
        const priorityCounts = { low: 0, medium: 0, high: 0 };
        let totalOpenAge = 0;
        let openCount = 0;

        for (const ticket of this.data) {
            // Status counts
            if (statusCounts[ticket.status] !== undefined) {
                statusCounts[ticket.status]++;
            }

            // Priority counts
            if (priorityCounts[ticket.priority] !== undefined) {
                priorityCounts[ticket.priority]++;
            }

            // Age calculation for open tickets
            if (ticket.status === 'open') {
                const created = new Date(ticket.created_at);
                const ageMs = now - created;
                totalOpenAge += ageMs;
                openCount++;
            }
        }

        const averageAgeSeconds = openCount > 0 ? Math.floor(totalOpenAge / openCount / 1000) : 0;

        return {
            by_status: statusCounts,
            by_priority: priorityCounts,
            average_open_age_seconds: averageAgeSeconds
        };
    }
}

const store = new TicketStore(DATA_FILE);

// Simple URL pattern matching
function parsePath(url) {
    const parsed = new URL(url, 'http://localhost');
    const pathParts = parsed.pathname.split('/').filter(Boolean);
    const query = Object.fromEntries(parsed.searchParams.entries());
    return { pathParts, query, pathname: parsed.pathname };
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

function getBody(req) {
    return new Promise((resolve, reject) => {
        let body = '';
        req.on('data', chunk => {
            body += chunk;
            if (body.length > 1e6) {
                req.destroy();
                reject(new Error('Request body too large'));
            }
        });
        req.on('end', () => {
            resolve(body);
        });
        req.on('error', reject);
    });
}

function parseJSONBody(body) {
    try {
        return JSON.parse(body);
    } catch (e) {
        return null;
    }
}

async function handleRequest(req, res) {
    const { pathParts, query, pathname } = parsePath(req.url);
    const method = req.method.toUpperCase();

    // Handle CORS preflight
    if (method === 'OPTIONS') {
        sendJSON(res, 204, '');
        return;
    }

    // Route matching
    if (pathname === '/tickets' && method === 'GET') {
        const result = await store.withLock((data) => {
            return store.getAll(query.status, query.priority);
        });
        sendJSON(res, 200, result);
        return;
    }

    if (pathname === '/tickets' && method === 'POST') {
        const body = await getBody(req);
        const parsed = parseJSONBody(body);
        if (!parsed) {
            sendJSON(res, 400, { error: 'Invalid JSON body' });
            return;
        }
        const result = await store.withLock((data) => {
            return store.create(parsed.subject, parsed.description, parsed.priority);
        });
        const statusCode = result.status || 200;
        delete result.status;
        sendJSON(res, statusCode, result);
        return;
    }

    if (pathParts.length === 2 && pathParts[0] === 'tickets' && method === 'GET') {
        const id = parseInt(pathParts[1]);
        if (isNaN(id)) {
            sendJSON(res, 400, { error: 'Invalid ticket ID' });
            return;
        }
        const result = await store.withLock((data) => {
            return store.getById(id);
        });
        const statusCode = result.status || 200;
        delete result.status;
        sendJSON(res, statusCode, result);
        return;
    }

    if (pathParts.length === 2 && pathParts[0] === 'tickets' && method === 'PATCH') {
        const id = parseInt(pathParts[1]);
        if (isNaN(id)) {
            sendJSON(res, 400, { error: 'Invalid ticket ID' });
            return;
        }
        const body = await getBody(req);
        const parsed = parseJSONBody(body);
        if (!parsed) {
            sendJSON(res, 400, { error: 'Invalid JSON body' });
            return;
        }
        const result = await store.withLock((data) => {
            return store.update(id, parsed);
        });
        const statusCode = result.status || 200;
        delete result.status;
        sendJSON(res, statusCode, result);
        return;
    }

    if (pathParts.length === 2 && pathParts[0] === 'tickets' && method === 'DELETE') {
        const id = parseInt(pathParts[1]);
        if (isNaN(id)) {
            sendJSON(res, 400, { error: 'Invalid ticket ID' });
            return;
        }
        const result = await store.withLock((data) => {
            return store.delete(id);
        });
        const statusCode = result.status || 200;
        delete result.status;
        sendJSON(res, statusCode, result);
        return;
    }

    if (pathname === '/metrics' && method === 'GET') {
        const result = await store.withLock((data) => {
            return store.getMetrics();
        });
        sendJSON(res, 200, result);
        return;
    }

    // Unknown route or method
    sendJSON(res, 404, { error: 'Not found' });
}

const server = http.createServer(handleRequest);

server.listen(PORT, HOST, () => {
    console.log(`Server running at http://${HOST}:${PORT}/`);
});
```
````
