# Generation Transcript

- Case: `en_code_be_001`
- Language group: `en`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `1`
- Thinking mode: `non-thinking`
- Thinking strength: `disabled`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 29.089449
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 318, "total_tokens": 2783, "completion_tokens": 2465, "prompt_tokens_details": null}`
- Prompt tokens: 318
- Completion tokens: 2465
- Total tokens: 2783

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

let tickets = [];
let nextId = 1;
let fileLock = false;
let lockQueue = [];

function acquireLock(callback) {
    if (fileLock) {
        lockQueue.push(callback);
        return;
    }
    fileLock = true;
    callback();
}

function releaseLock() {
    fileLock = false;
    if (lockQueue.length > 0) {
        const next = lockQueue.shift();
        fileLock = true;
        next();
    }
}

function loadTickets() {
    try {
        if (fs.existsSync(DATA_FILE)) {
            const data = fs.readFileSync(DATA_FILE, 'utf8');
            tickets = JSON.parse(data);
            if (Array.isArray(tickets)) {
                nextId = tickets.reduce((max, t) => Math.max(max, t.id || 0), 0) + 1;
            } else {
                tickets = [];
                nextId = 1;
            }
        } else {
            tickets = [];
            nextId = 1;
        }
    } catch (err) {
        tickets = [];
        nextId = 1;
    }
}

function saveTickets() {
    try {
        fs.writeFileSync(DATA_FILE, JSON.stringify(tickets, null, 2), 'utf8');
        return true;
    } catch (err) {
        return false;
    }
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

function parseBody(req, callback) {
    let body = '';
    req.on('data', chunk => {
        body += chunk.toString();
        if (body.length > 1e6) {
            req.destroy();
            callback(new Error('Request body too large'), null);
        }
    });
    req.on('end', () => {
        try {
            const parsed = JSON.parse(body || '{}');
            callback(null, parsed);
        } catch (err) {
            callback(new Error('Invalid JSON'), null);
        }
    });
    req.on('error', err => {
        callback(err, null);
    });
}

function validateTicket(body) {
    const errors = [];
    if (!body.subject || typeof body.subject !== 'string' || body.subject.trim() === '') {
        errors.push('subject is required and must be a non-empty string');
    }
    if (!body.description || typeof body.description !== 'string' || body.description.trim() === '') {
        errors.push('description is required and must be a non-empty string');
    }
    const validPriorities = ['low', 'medium', 'high'];
    if (body.priority && !validPriorities.includes(body.priority)) {
        errors.push(`priority must be one of: ${validPriorities.join(', ')}`);
    }
    const validStatuses = ['open', 'in_progress', 'resolved'];
    if (body.status && !validStatuses.includes(body.status)) {
        errors.push(`status must be one of: ${validStatuses.join(', ')}`);
    }
    return errors;
}

function parseURL(url) {
    const parsed = new URL(url, `http://${HOST}:${PORT}`);
    const pathParts = parsed.pathname.split('/').filter(Boolean);
    const query = {};
    parsed.searchParams.forEach((value, key) => {
        query[key] = value;
    });
    return { pathParts, query };
}

function handleTickets(req, res, pathParts, query) {
    if (pathParts.length === 0) {
        // GET /tickets or POST /tickets
        if (req.method === 'GET') {
            let filtered = [...tickets];
            if (query.status) {
                filtered = filtered.filter(t => t.status === query.status);
            }
            if (query.priority) {
                filtered = filtered.filter(t => t.priority === query.priority);
            }
            sendJSON(res, 200, filtered);
        } else if (req.method === 'POST') {
            parseBody(req, (err, body) => {
                if (err) {
                    sendJSON(res, 400, { error: err.message });
                    return;
                }
                const validationErrors = validateTicket(body);
                if (validationErrors.length > 0) {
                    sendJSON(res, 400, { error: 'Validation failed', details: validationErrors });
                    return;
                }
                const now = new Date().toISOString();
                const ticket = {
                    id: nextId++,
                    subject: body.subject.trim(),
                    description: body.description.trim(),
                    priority: body.priority || 'low',
                    status: 'open',
                    created_at: now,
                    updated_at: now
                };
                tickets.push(ticket);
                if (!saveTickets()) {
                    sendJSON(res, 500, { error: 'Failed to save data' });
                    return;
                }
                sendJSON(res, 201, ticket);
            });
        } else {
            sendJSON(res, 405, { error: 'Method not allowed' });
        }
    } else if (pathParts.length === 1) {
        const id = parseInt(pathParts[0], 10);
        if (isNaN(id)) {
            sendJSON(res, 400, { error: 'Invalid ticket ID' });
            return;
        }
        const ticketIndex = tickets.findIndex(t => t.id === id);
        if (ticketIndex === -1) {
            sendJSON(res, 404, { error: 'Ticket not found' });
            return;
        }
        if (req.method === 'GET') {
            sendJSON(res, 200, tickets[ticketIndex]);
        } else if (req.method === 'PATCH') {
            parseBody(req, (err, body) => {
                if (err) {
                    sendJSON(res, 400, { error: err.message });
                    return;
                }
                const ticket = tickets[ticketIndex];
                const validPriorities = ['low', 'medium', 'high'];
                const validStatuses = ['open', 'in_progress', 'resolved'];

                if (body.subject !== undefined) {
                    if (typeof body.subject !== 'string' || body.subject.trim() === '') {
                        sendJSON(res, 400, { error: 'subject must be a non-empty string' });
                        return;
                    }
                    ticket.subject = body.subject.trim();
                }
                if (body.description !== undefined) {
                    if (typeof body.description !== 'string' || body.description.trim() === '') {
                        sendJSON(res, 400, { error: 'description must be a non-empty string' });
                        return;
                    }
                    ticket.description = body.description.trim();
                }
                if (body.priority !== undefined) {
                    if (!validPriorities.includes(body.priority)) {
                        sendJSON(res, 400, { error: `priority must be one of: ${validPriorities.join(', ')}` });
                        return;
                    }
                    ticket.priority = body.priority;
                }
                if (body.status !== undefined) {
                    if (!validStatuses.includes(body.status)) {
                        sendJSON(res, 400, { error: `status must be one of: ${validStatuses.join(', ')}` });
                        return;
                    }
                    ticket.status = body.status;
                }
                ticket.updated_at = new Date().toISOString();
                tickets[ticketIndex] = ticket;
                if (!saveTickets()) {
                    sendJSON(res, 500, { error: 'Failed to save data' });
                    return;
                }
                sendJSON(res, 200, ticket);
            });
        } else if (req.method === 'DELETE') {
            tickets.splice(ticketIndex, 1);
            if (!saveTickets()) {
                sendJSON(res, 500, { error: 'Failed to save data' });
                return;
            }
            sendJSON(res, 200, { message: 'Ticket deleted' });
        } else {
            sendJSON(res, 405, { error: 'Method not allowed' });
        }
    } else {
        sendJSON(res, 404, { error: 'Not found' });
    }
}

function handleMetrics(req, res) {
    if (req.method !== 'GET') {
        sendJSON(res, 405, { error: 'Method not allowed' });
        return;
    }

    const statusCounts = { open: 0, in_progress: 0, resolved: 0 };
    const priorityCounts = { low: 0, medium: 0, high: 0 };
    let totalAgeOpen = 0;
    let openCount = 0;
    const now = Date.now();

    tickets.forEach(ticket => {
        if (statusCounts.hasOwnProperty(ticket.status)) {
            statusCounts[ticket.status]++;
        }
        if (priorityCounts.hasOwnProperty(ticket.priority)) {
            priorityCounts[ticket.priority]++;
        }
        if (ticket.status === 'open' || ticket.status === 'in_progress') {
            const created = new Date(ticket.created_at).getTime();
            if (!isNaN(created)) {
                totalAgeOpen += (now - created) / 1000;
                openCount++;
            }
        }
    });

    const metrics = {
        by_status: statusCounts,
        by_priority: priorityCounts,
        average_age_open_seconds: openCount > 0 ? totalAgeOpen / openCount : 0
    };

    sendJSON(res, 200, metrics);
}

function handleRequest(req, res) {
    // CORS preflight
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

    const { pathParts, query } = parseURL(req.url);

    if (pathParts.length === 0) {
        sendJSON(res, 200, { message: 'Help Desk Ticket API', version: '1.0.0' });
        return;
    }

    if (pathParts[0] === 'tickets') {
        acquireLock(() => {
            try {
                handleTickets(req, res, pathParts.slice(1), query);
            } finally {
                releaseLock();
            }
        });
    } else if (pathParts[0] === 'metrics') {
        acquireLock(() => {
            try {
                handleMetrics(req, res);
            } finally {
                releaseLock();
            }
        });
    } else {
        sendJSON(res, 404, { error: 'Route not found' });
    }
}

// Initialize data
loadTickets();

const server = http.createServer(handleRequest);

server.listen(PORT, HOST, () => {
    console.log(`Server running at http://${HOST}:${PORT}/`);
});
```
````
