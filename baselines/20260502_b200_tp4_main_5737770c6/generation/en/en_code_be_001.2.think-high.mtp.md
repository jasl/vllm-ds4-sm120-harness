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
- Elapsed seconds: 8.299344
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 318, "total_tokens": 2734, "completion_tokens": 2416, "prompt_tokens_details": null}`
- Prompt tokens: 318
- Completion tokens: 2416
- Total tokens: 2734

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
    constructor() {
        this.tickets = [];
        this.load();
    }

    load() {
        try {
            const data = fs.readFileSync(DATA_FILE, 'utf8');
            this.tickets = JSON.parse(data);
        } catch (err) {
            if (err.code === 'ENOENT') {
                this.tickets = [];
                this.saveSync();
            } else {
                throw err;
            }
        }
    }

    saveSync() {
        fs.writeFileSync(DATA_FILE, JSON.stringify(this.tickets, null, 2), 'utf8');
    }

    saveAsync() {
        return new Promise((resolve, reject) => {
            fs.writeFile(DATA_FILE, JSON.stringify(this.tickets, null, 2), 'utf8', (err) => {
                if (err) reject(err);
                else resolve();
            });
        });
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
        return this.tickets.find(t => t.id === id) || null;
    }

    create(ticketData) {
        const now = new Date().toISOString();
        const ticket = {
            id: crypto.randomUUID(),
            subject: ticketData.subject,
            description: ticketData.description || '',
            priority: ticketData.priority || 'low',
            status: 'open',
            created_at: now,
            updated_at: now
        };
        this.tickets.push(ticket);
        this.saveSync();
        return ticket;
    }

    update(id, updates) {
        const index = this.tickets.findIndex(t => t.id === id);
        if (index === -1) return null;

        const allowedFields = ['subject', 'description', 'priority', 'status'];
        const now = new Date().toISOString();

        for (const field of allowedFields) {
            if (updates[field] !== undefined) {
                this.tickets[index][field] = updates[field];
            }
        }
        this.tickets[index].updated_at = now;
        this.saveSync();
        return this.tickets[index];
    }

    delete(id) {
        const index = this.tickets.findIndex(t => t.id === id);
        if (index === -1) return false;
        this.tickets.splice(index, 1);
        this.saveSync();
        return true;
    }

    getMetrics() {
        const metrics = {
            status_counts: { open: 0, in_progress: 0, resolved: 0 },
            priority_counts: { low: 0, medium: 0, high: 0 },
            average_open_age_seconds: 0
        };

        const openTickets = [];
        const now = new Date();

        for (const ticket of this.tickets) {
            metrics.status_counts[ticket.status]++;
            metrics.priority_counts[ticket.priority]++;

            if (ticket.status === 'open') {
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
}

const store = new TicketStore();

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
    const urlObj = new URL(url, `http://${HOST}:${PORT}`);
    const pathParts = urlObj.pathname.split('/').filter(Boolean);
    const queryParams = Object.fromEntries(urlObj.searchParams);
    return { pathParts, queryParams };
}

function validateTicketData(data) {
    const errors = [];
    if (!data.subject || typeof data.subject !== 'string' || data.subject.trim() === '') {
        errors.push('subject is required and must be a non-empty string');
    }
    if (data.description !== undefined && typeof data.description !== 'string') {
        errors.push('description must be a string');
    }
    if (data.priority !== undefined && !['low', 'medium', 'high'].includes(data.priority)) {
        errors.push('priority must be one of: low, medium, high');
    }
    if (data.status !== undefined && !['open', 'in_progress', 'resolved'].includes(data.status)) {
        errors.push('status must be one of: open, in_progress, resolved');
    }
    return errors;
}

function validateUpdateData(data) {
    const errors = [];
    if (data.subject !== undefined && (typeof data.subject !== 'string' || data.subject.trim() === '')) {
        errors.push('subject must be a non-empty string');
    }
    if (data.description !== undefined && typeof data.description !== 'string') {
        errors.push('description must be a string');
    }
    if (data.priority !== undefined && !['low', 'medium', 'high'].includes(data.priority)) {
        errors.push('priority must be one of: low, medium, high');
    }
    if (data.status !== undefined && !['open', 'in_progress', 'resolved'].includes(data.status)) {
        errors.push('status must be one of: open, in_progress, resolved');
    }
    return errors;
}

function isValidMethod(method, allowedMethods) {
    return allowedMethods.includes(method);
}

const server = http.createServer(async (req, res) => {
    // Handle CORS preflight
    if (req.method === 'OPTIONS') {
        res.writeHead(204, {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '86400'
        });
        res.end();
        return;
    }

    try {
        const { pathParts, queryParams } = parseURL(req.url);

        // Route: GET /tickets
        if (pathParts.length === 1 && pathParts[0] === 'tickets' && req.method === 'GET') {
            const filters = {};
            if (queryParams.status && ['open', 'in_progress', 'resolved'].includes(queryParams.status)) {
                filters.status = queryParams.status;
            }
            if (queryParams.priority && ['low', 'medium', 'high'].includes(queryParams.priority)) {
                filters.priority = queryParams.priority;
            }
            const tickets = store.getAll(filters);
            sendJSON(res, 200, tickets);
            return;
        }

        // Route: POST /tickets
        if (pathParts.length === 1 && pathParts[0] === 'tickets' && req.method === 'POST') {
            const body = await parseBody(req);
            const errors = validateTicketData(body);
            if (errors.length > 0) {
                sendJSON(res, 400, { error: 'Validation failed', details: errors });
                return;
            }
            const ticket = store.create(body);
            sendJSON(res, 201, ticket);
            return;
        }

        // Route: GET /tickets/{id}
        if (pathParts.length === 2 && pathParts[0] === 'tickets' && req.method === 'GET') {
            const ticket = store.getById(pathParts[1]);
            if (!ticket) {
                sendJSON(res, 404, { error: 'Ticket not found' });
                return;
            }
            sendJSON(res, 200, ticket);
            return;
        }

        // Route: PATCH /tickets/{id}
        if (pathParts.length === 2 && pathParts[0] === 'tickets' && req.method === 'PATCH') {
            const ticket = store.getById(pathParts[1]);
            if (!ticket) {
                sendJSON(res, 404, { error: 'Ticket not found' });
                return;
            }
            const body = await parseBody(req);
            const errors = validateUpdateData(body);
            if (errors.length > 0) {
                sendJSON(res, 400, { error: 'Validation failed', details: errors });
                return;
            }
            if (Object.keys(body).length === 0) {
                sendJSON(res, 400, { error: 'No fields to update' });
                return;
            }
            const updated = store.update(pathParts[1], body);
            sendJSON(res, 200, updated);
            return;
        }

        // Route: DELETE /tickets/{id}
        if (pathParts.length === 2 && pathParts[0] === 'tickets' && req.method === 'DELETE') {
            const deleted = store.delete(pathParts[1]);
            if (!deleted) {
                sendJSON(res, 404, { error: 'Ticket not found' });
                return;
            }
            sendJSON(res, 200, { message: 'Ticket deleted' });
            return;
        }

        // Route: GET /metrics
        if (pathParts.length === 1 && pathParts[0] === 'metrics' && req.method === 'GET') {
            const metrics = store.getMetrics();
            sendJSON(res, 200, metrics);
            return;
        }

        // 404 for unknown routes
        sendJSON(res, 404, { error: 'Route not found' });

    } catch (err) {
        if (err.message === 'Invalid JSON') {
            sendJSON(res, 400, { error: 'Invalid JSON in request body' });
        } else {
            console.error('Server error:', err);
            sendJSON(res, 500, { error: 'Internal server error' });
        }
    }
});

server.listen(PORT, HOST, () => {
    console.log(`Server running at http://${HOST}:${PORT}/`);
});
```
````
