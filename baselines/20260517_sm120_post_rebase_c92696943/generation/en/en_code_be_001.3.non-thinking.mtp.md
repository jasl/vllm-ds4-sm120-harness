# Generation Transcript

- Case: `en_code_be_001`
- Language group: `en`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `3`
- Thinking mode: `non-thinking`
- Thinking strength: `disabled`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 13.277985
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 318, "total_tokens": 2870, "completion_tokens": 2552, "prompt_tokens_details": null}`
- Prompt tokens: 318
- Completion tokens: 2552
- Total tokens: 2870

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

const PORT = 8080;
const HOST = '127.0.0.1';
const DATA_FILE = path.join(__dirname, 'tickets.json');

const CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type'
};

let tickets = [];
let writeQueue = Promise.resolve();

function loadTickets() {
    try {
        if (fs.existsSync(DATA_FILE)) {
            const data = fs.readFileSync(DATA_FILE, 'utf8');
            tickets = JSON.parse(data);
        } else {
            tickets = [];
            saveTicketsSync();
        }
    } catch (err) {
        console.error('Error loading tickets:', err);
        tickets = [];
    }
}

function saveTicketsSync() {
    try {
        fs.writeFileSync(DATA_FILE, JSON.stringify(tickets, null, 2), 'utf8');
    } catch (err) {
        console.error('Error saving tickets:', err);
        throw err;
    }
}

function saveTicketsAsync() {
    return new Promise((resolve, reject) => {
        fs.writeFile(DATA_FILE, JSON.stringify(tickets, null, 2), 'utf8', (err) => {
            if (err) reject(err);
            else resolve();
        });
    });
}

function updateWriteQueue() {
    writeQueue = writeQueue.then(() => saveTicketsAsync()).catch(err => {
        console.error('Write queue error:', err);
    });
}

function generateId() {
    return Date.now().toString(36) + Math.random().toString(36).substr(2, 9);
}

function validateTicket(body) {
    const errors = [];
    if (!body.subject || typeof body.subject !== 'string' || body.subject.trim().length === 0) {
        errors.push('subject is required and must be a non-empty string');
    }
    if (!body.description || typeof body.description !== 'string' || body.description.trim().length === 0) {
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

function parseUrl(url) {
    const parsed = new URL(url, `http://${HOST}:${PORT}`);
    const pathname = parsed.pathname;
    const params = {};
    parsed.searchParams.forEach((value, key) => {
        params[key] = value;
    });
    return { pathname, params };
}

function getBody(req) {
    return new Promise((resolve, reject) => {
        let body = '';
        req.on('data', chunk => {
            body += chunk;
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

function sendJson(res, statusCode, data) {
    res.writeHead(statusCode, {
        'Content-Type': 'application/json',
        ...CORS_HEADERS
    });
    res.end(JSON.stringify(data));
}

function handleGetTickets(req, res, params) {
    let filtered = [...tickets];

    if (params.status) {
        filtered = filtered.filter(t => t.status === params.status);
    }
    if (params.priority) {
        filtered = filtered.filter(t => t.priority === params.priority);
    }

    sendJson(res, 200, filtered);
}

function handlePostTickets(req, res) {
    getBody(req).then(body => {
        const errors = validateTicket(body);
        if (errors.length > 0) {
            sendJson(res, 400, { error: 'Validation failed', details: errors });
            return;
        }

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
        updateWriteQueue();
        sendJson(res, 201, ticket);
    }).catch(err => {
        sendJson(res, 400, { error: err.message });
    });
}

function handleGetTicket(req, res, id) {
    const ticket = tickets.find(t => t.id === id);
    if (!ticket) {
        sendJson(res, 404, { error: 'Ticket not found' });
        return;
    }
    sendJson(res, 200, ticket);
}

function handlePatchTicket(req, res, id) {
    const index = tickets.findIndex(t => t.id === id);
    if (index === -1) {
        sendJson(res, 404, { error: 'Ticket not found' });
        return;
    }

    getBody(req).then(body => {
        const allowedFields = ['subject', 'description', 'priority', 'status'];
        const updates = {};

        for (const field of allowedFields) {
            if (body[field] !== undefined) {
                if (field === 'priority' && !['low', 'medium', 'high'].includes(body[field])) {
                    sendJson(res, 400, { error: 'priority must be low, medium, or high' });
                    return;
                }
                if (field === 'status' && !['open', 'in_progress', 'resolved'].includes(body[field])) {
                    sendJson(res, 400, { error: 'status must be open, in_progress, or resolved' });
                    return;
                }
                if (field === 'subject' && (typeof body[field] !== 'string' || body[field].trim().length === 0)) {
                    sendJson(res, 400, { error: 'subject must be a non-empty string' });
                    return;
                }
                if (field === 'description' && (typeof body[field] !== 'string' || body[field].trim().length === 0)) {
                    sendJson(res, 400, { error: 'description must be a non-empty string' });
                    return;
                }
                updates[field] = typeof body[field] === 'string' ? body[field].trim() : body[field];
            }
        }

        if (Object.keys(updates).length === 0) {
            sendJson(res, 400, { error: 'No valid fields to update' });
            return;
        }

        updates.updated_at = new Date().toISOString();
        tickets[index] = { ...tickets[index], ...updates };
        updateWriteQueue();
        sendJson(res, 200, tickets[index]);
    }).catch(err => {
        sendJson(res, 400, { error: err.message });
    });
}

function handleDeleteTicket(req, res, id) {
    const index = tickets.findIndex(t => t.id === id);
    if (index === -1) {
        sendJson(res, 404, { error: 'Ticket not found' });
        return;
    }

    const deleted = tickets.splice(index, 1)[0];
    updateWriteQueue();
    sendJson(res, 200, { message: 'Ticket deleted', ticket: deleted });
}

function handleMetrics(req, res) {
    const now = new Date();
    const metrics = {
        status_counts: { open: 0, in_progress: 0, resolved: 0 },
        priority_counts: { low: 0, medium: 0, high: 0 },
        average_open_age_seconds: 0
    };

    let totalAgeSeconds = 0;
    let openCount = 0;

    for (const ticket of tickets) {
        if (metrics.status_counts[ticket.status] !== undefined) {
            metrics.status_counts[ticket.status]++;
        }
        if (metrics.priority_counts[ticket.priority] !== undefined) {
            metrics.priority_counts[ticket.priority]++;
        }

        if (ticket.status === 'open') {
            const created = new Date(ticket.created_at);
            const ageSeconds = Math.floor((now - created) / 1000);
            totalAgeSeconds += ageSeconds;
            openCount++;
        }
    }

    metrics.average_open_age_seconds = openCount > 0 ? Math.floor(totalAgeSeconds / openCount) : 0;

    sendJson(res, 200, metrics);
}

function handleOptions(req, res) {
    res.writeHead(204, CORS_HEADERS);
    res.end();
}

function handleNotFound(req, res) {
    sendJson(res, 404, { error: 'Not found' });
}

function handleMethodNotAllowed(req, res) {
    sendJson(res, 405, { error: 'Method not allowed' });
}

function handleBadRequest(req, res) {
    sendJson(res, 400, { error: 'Bad request' });
}

const server = http.createServer((req, res) => {
    try {
        const { pathname, params } = parseUrl(req.url);
        const method = req.method.toUpperCase();

        if (method === 'OPTIONS') {
            handleOptions(req, res);
            return;
        }

        // GET /tickets
        if (pathname === '/tickets' && method === 'GET') {
            handleGetTickets(req, res, params);
            return;
        }

        // POST /tickets
        if (pathname === '/tickets' && method === 'POST') {
            handlePostTickets(req, res);
            return;
        }

        // GET /tickets/{id}
        const getMatch = pathname.match(/^\/tickets\/([a-zA-Z0-9]+)$/);
        if (getMatch && method === 'GET') {
            handleGetTicket(req, res, getMatch[1]);
            return;
        }

        // PATCH /tickets/{id}
        if (getMatch && method === 'PATCH') {
            handlePatchTicket(req, res, getMatch[1]);
            return;
        }

        // DELETE /tickets/{id}
        if (getMatch && method === 'DELETE') {
            handleDeleteTicket(req, res, getMatch[1]);
            return;
        }

        // GET /metrics
        if (pathname === '/metrics' && method === 'GET') {
            handleMetrics(req, res);
            return;
        }

        // Handle unsupported methods on existing routes
        if (pathname === '/tickets' && !['GET', 'POST', 'OPTIONS'].includes(method)) {
            handleMethodNotAllowed(req, res);
            return;
        }

        if (getMatch && !['GET', 'PATCH', 'DELETE', 'OPTIONS'].includes(method)) {
            handleMethodNotAllowed(req, res);
            return;
        }

        if (pathname === '/metrics' && method !== 'GET') {
            handleMethodNotAllowed(req, res);
            return;
        }

        handleNotFound(req, res);
    } catch (err) {
        console.error('Server error:', err);
        sendJson(res, 500, { error: 'Internal server error' });
    }
});

loadTickets();

server.listen(PORT, HOST, () => {
    console.log(`Server running at http://${HOST}:${PORT}`);
});
```
````
