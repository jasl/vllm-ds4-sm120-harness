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
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 41.667945
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 318, "total_tokens": 2972, "completion_tokens": 2654, "prompt_tokens_details": null}`
- Prompt tokens: 318
- Completion tokens: 2654
- Total tokens: 2972

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

let ticketsData = [];
let nextId = 1;
let fileLock = false;
let lockQueue = [];

function acquireLock(callback) {
    if (!fileLock) {
        fileLock = true;
        callback();
    } else {
        lockQueue.push(callback);
    }
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
            const raw = fs.readFileSync(DATA_FILE, 'utf8');
            if (raw.trim()) {
                const parsed = JSON.parse(raw);
                ticketsData = parsed.tickets || [];
                nextId = parsed.nextId || 1;
            } else {
                ticketsData = [];
                nextId = 1;
            }
        } else {
            ticketsData = [];
            nextId = 1;
            saveTicketsSync();
        }
    } catch (err) {
        ticketsData = [];
        nextId = 1;
    }
}

function saveTicketsSync() {
    const data = JSON.stringify({ tickets: ticketsData, nextId: nextId }, null, 2);
    fs.writeFileSync(DATA_FILE, data, 'utf8');
}

function saveTicketsAsync() {
    return new Promise((resolve, reject) => {
        const data = JSON.stringify({ tickets: ticketsData, nextId: nextId }, null, 2);
        fs.writeFile(DATA_FILE, data, 'utf8', (err) => {
            if (err) reject(err);
            else resolve();
        });
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
    if (body.priority && !['low', 'medium', 'high'].includes(body.priority)) {
        errors.push('priority must be low, medium, or high');
    }
    if (body.status && !['open', 'in_progress', 'resolved'].includes(body.status)) {
        errors.push('status must be open, in_progress, or resolved');
    }
    return errors;
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

function parseURL(reqUrl) {
    const url = new URL(reqUrl, `http://${HOST}:${PORT}`);
    const pathParts = url.pathname.split('/').filter(Boolean);
    const params = Object.fromEntries(url.searchParams);
    return { pathParts, params, url };
}

function getBody(req) {
    return new Promise((resolve, reject) => {
        let body = '';
        req.on('data', chunk => {
            body += chunk.toString();
        });
        req.on('end', () => {
            try {
                resolve(body ? JSON.parse(body) : {});
            } catch (e) {
                reject(new Error('Invalid JSON'));
            }
        });
        req.on('error', reject);
    });
}

function getTicketById(id) {
    const numId = parseInt(id);
    if (isNaN(numId)) return null;
    return ticketsData.find(t => t.id === numId) || null;
}

function getMetrics() {
    const now = new Date();
    const metrics = {
        byStatus: { open: 0, in_progress: 0, resolved: 0 },
        byPriority: { low: 0, medium: 0, high: 0 },
        averageOpenAgeSeconds: 0
    };

    let totalAgeSeconds = 0;
    let openCount = 0;

    ticketsData.forEach(ticket => {
        if (metrics.byStatus.hasOwnProperty(ticket.status)) {
            metrics.byStatus[ticket.status]++;
        }
        if (metrics.byPriority.hasOwnProperty(ticket.priority)) {
            metrics.byPriority[ticket.priority]++;
        }
        if (ticket.status === 'open' || ticket.status === 'in_progress') {
            const created = new Date(ticket.created_at);
            const ageMs = now - created;
            const ageSeconds = Math.floor(ageMs / 1000);
            totalAgeSeconds += ageSeconds;
            openCount++;
        }
    });

    if (openCount > 0) {
        metrics.averageOpenAgeSeconds = Math.floor(totalAgeSeconds / openCount);
    }

    return metrics;
}

const server = http.createServer(async (req, res) => {
    const { pathParts, params, url } = parseURL(req.url);
    const method = req.method.toUpperCase();

    // Handle CORS preflight
    if (method === 'OPTIONS') {
        res.writeHead(204, {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '86400'
        });
        res.end();
        return;
    }

    // GET /tickets
    if (method === 'GET' && pathParts.length === 1 && pathParts[0] === 'tickets' && !params.id) {
        acquireLock(async () => {
            try {
                let result = [...ticketsData];
                if (params.status) {
                    result = result.filter(t => t.status === params.status);
                }
                if (params.priority) {
                    result = result.filter(t => t.priority === params.priority);
                }
                sendJSON(res, 200, result);
            } catch (err) {
                sendJSON(res, 500, { error: 'Internal server error' });
            } finally {
                releaseLock();
            }
        });
        return;
    }

    // POST /tickets
    if (method === 'POST' && pathParts.length === 1 && pathParts[0] === 'tickets') {
        let body;
        try {
            body = await getBody(req);
        } catch (e) {
            sendJSON(res, 400, { error: 'Invalid JSON in request body' });
            return;
        }

        const errors = validateTicket(body);
        if (errors.length > 0) {
            sendJSON(res, 400, { error: 'Validation failed', details: errors });
            return;
        }

        acquireLock(async () => {
            try {
                const now = new Date().toISOString();
                const ticket = {
                    id: nextId++,
                    subject: body.subject.trim(),
                    description: body.description.trim(),
                    priority: body.priority || 'medium',
                    status: body.status || 'open',
                    created_at: now,
                    updated_at: now
                };
                ticketsData.push(ticket);
                saveTicketsSync();
                sendJSON(res, 201, ticket);
            } catch (err) {
                sendJSON(res, 500, { error: 'Internal server error' });
            } finally {
                releaseLock();
            }
        });
        return;
    }

    // GET /tickets/{id}
    if (method === 'GET' && pathParts.length === 2 && pathParts[0] === 'tickets') {
        acquireLock(async () => {
            try {
                const ticket = getTicketById(pathParts[1]);
                if (!ticket) {
                    sendJSON(res, 404, { error: 'Ticket not found' });
                    return;
                }
                sendJSON(res, 200, ticket);
            } catch (err) {
                sendJSON(res, 500, { error: 'Internal server error' });
            } finally {
                releaseLock();
            }
        });
        return;
    }

    // PATCH /tickets/{id}
    if (method === 'PATCH' && pathParts.length === 2 && pathParts[0] === 'tickets') {
        let body;
        try {
            body = await getBody(req);
        } catch (e) {
            sendJSON(res, 400, { error: 'Invalid JSON in request body' });
            return;
        }

        if (Object.keys(body).length === 0) {
            sendJSON(res, 400, { error: 'No fields provided for update' });
            return;
        }

        const allowedFields = ['subject', 'description', 'priority', 'status'];
        const updateFields = {};
        for (const key of allowedFields) {
            if (body[key] !== undefined) {
                if (key === 'priority' && !['low', 'medium', 'high'].includes(body[key])) {
                    sendJSON(res, 400, { error: 'priority must be low, medium, or high' });
                    return;
                }
                if (key === 'status' && !['open', 'in_progress', 'resolved'].includes(body[key])) {
                    sendJSON(res, 400, { error: 'status must be open, in_progress, or resolved' });
                    return;
                }
                if ((key === 'subject' || key === 'description') && (typeof body[key] !== 'string' || body[key].trim() === '')) {
                    sendJSON(res, 400, { error: `${key} must be a non-empty string` });
                    return;
                }
                updateFields[key] = key === 'subject' || key === 'description' ? body[key].trim() : body[key];
            }
        }

        acquireLock(async () => {
            try {
                const ticket = getTicketById(pathParts[1]);
                if (!ticket) {
                    sendJSON(res, 404, { error: 'Ticket not found' });
                    return;
                }
                Object.assign(ticket, updateFields);
                ticket.updated_at = new Date().toISOString();
                saveTicketsSync();
                sendJSON(res, 200, ticket);
            } catch (err) {
                sendJSON(res, 500, { error: 'Internal server error' });
            } finally {
                releaseLock();
            }
        });
        return;
    }

    // DELETE /tickets/{id}
    if (method === 'DELETE' && pathParts.length === 2 && pathParts[0] === 'tickets') {
        acquireLock(async () => {
            try {
                const index = ticketsData.findIndex(t => t.id === parseInt(pathParts[1]));
                if (index === -1) {
                    sendJSON(res, 404, { error: 'Ticket not found' });
                    return;
                }
                ticketsData.splice(index, 1);
                saveTicketsSync();
                sendJSON(res, 200, { message: 'Ticket deleted successfully' });
            } catch (err) {
                sendJSON(res, 500, { error: 'Internal server error' });
            } finally {
                releaseLock();
            }
        });
        return;
    }

    // GET /metrics
    if (method === 'GET' && pathParts.length === 1 && pathParts[0] === 'metrics') {
        acquireLock(async () => {
            try {
                const metrics = getMetrics();
                sendJSON(res, 200, metrics);
            } catch (err) {
                sendJSON(res, 500, { error: 'Internal server error' });
            } finally {
                releaseLock();
            }
        });
        return;
    }

    // Route not found
    sendJSON(res, 404, { error: 'Route not found' });
});

// Initialize data
loadTickets();

server.listen(PORT, HOST, () => {
    console.log(`Server running at http://${HOST}:${PORT}/`);
});
```
````
