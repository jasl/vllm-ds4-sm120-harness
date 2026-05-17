# Generation Transcript

- Case: `en_code_be_001`
- Language group: `en`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `2`
- Thinking mode: `non-thinking`
- Thinking strength: `default`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 23.993384
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 318, "total_tokens": 2697, "completion_tokens": 2379, "prompt_tokens_details": null}`
- Prompt tokens: 318
- Completion tokens: 2379
- Total tokens: 2697

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

// File locking mechanism for sequential access
let fileLock = Promise.resolve();

function acquireLock() {
    let release;
    const promise = new Promise(resolve => { release = resolve; });
    const prevLock = fileLock;
    fileLock = promise;
    return prevLock.then(() => release);
}

async function readTickets() {
    try {
        const data = await fs.promises.readFile(DATA_FILE, 'utf8');
        return JSON.parse(data);
    } catch (err) {
        if (err.code === 'ENOENT') {
            return [];
        }
        throw err;
    }
}

async function writeTickets(tickets) {
    await fs.promises.writeFile(DATA_FILE, JSON.stringify(tickets, null, 2), 'utf8');
}

function generateId(tickets) {
    if (tickets.length === 0) return 1;
    return Math.max(...tickets.map(t => t.id)) + 1;
}

function validateTicket(body) {
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

function getRoute(req) {
    const url = new URL(req.url, `http://${req.headers.host}`);
    const pathParts = url.pathname.split('/').filter(p => p !== '');
    const method = req.method;

    // Handle CORS preflight
    if (method === 'OPTIONS') {
        return { route: 'cors' };
    }

    // GET /tickets
    if (method === 'GET' && pathParts.length === 1 && pathParts[0] === 'tickets') {
        return { route: 'getTickets', query: url.searchParams };
    }

    // POST /tickets
    if (method === 'POST' && pathParts.length === 1 && pathParts[0] === 'tickets') {
        return { route: 'createTicket' };
    }

    // GET /tickets/{id}
    if (method === 'GET' && pathParts.length === 2 && pathParts[0] === 'tickets') {
        const id = parseInt(pathParts[1]);
        if (!isNaN(id)) {
            return { route: 'getTicket', id };
        }
    }

    // PATCH /tickets/{id}
    if (method === 'PATCH' && pathParts.length === 2 && pathParts[0] === 'tickets') {
        const id = parseInt(pathParts[1]);
        if (!isNaN(id)) {
            return { route: 'updateTicket', id };
        }
    }

    // DELETE /tickets/{id}
    if (method === 'DELETE' && pathParts.length === 2 && pathParts[0] === 'tickets') {
        const id = parseInt(pathParts[1]);
        if (!isNaN(id)) {
            return { route: 'deleteTicket', id };
        }
    }

    // GET /metrics
    if (method === 'GET' && pathParts.length === 1 && pathParts[0] === 'metrics') {
        return { route: 'getMetrics' };
    }

    return { route: 'notFound' };
}

async function handleRequest(req, res) {
    const routeInfo = getRoute(req);

    if (routeInfo.route === 'cors') {
        sendJSON(res, 204, {});
        return;
    }

    try {
        const release = await acquireLock();
        try {
            const tickets = await readTickets();

            switch (routeInfo.route) {
                case 'getTickets': {
                    let filtered = [...tickets];
                    const statusFilter = routeInfo.query.get('status');
                    const priorityFilter = routeInfo.query.get('priority');

                    if (statusFilter && ['open', 'in_progress', 'resolved'].includes(statusFilter)) {
                        filtered = filtered.filter(t => t.status === statusFilter);
                    }
                    if (priorityFilter && ['low', 'medium', 'high'].includes(priorityFilter)) {
                        filtered = filtered.filter(t => t.priority === priorityFilter);
                    }

                    sendJSON(res, 200, filtered);
                    break;
                }

                case 'createTicket': {
                    let body;
                    try {
                        body = await parseBody(req);
                    } catch (err) {
                        sendJSON(res, 400, { error: 'Invalid JSON in request body' });
                        return;
                    }

                    const errors = validateTicket(body);
                    if (errors.length > 0) {
                        sendJSON(res, 400, { error: 'Validation failed', details: errors });
                        return;
                    }

                    const now = new Date().toISOString();
                    const ticket = {
                        id: generateId(tickets),
                        subject: body.subject.trim(),
                        description: body.description.trim(),
                        priority: body.priority,
                        status: 'open',
                        created_at: now,
                        updated_at: now
                    };

                    tickets.push(ticket);
                    await writeTickets(tickets);

                    sendJSON(res, 201, ticket);
                    break;
                }

                case 'getTicket': {
                    const ticket = tickets.find(t => t.id === routeInfo.id);
                    if (!ticket) {
                        sendJSON(res, 404, { error: 'Ticket not found' });
                        return;
                    }
                    sendJSON(res, 200, ticket);
                    break;
                }

                case 'updateTicket': {
                    const index = tickets.findIndex(t => t.id === routeInfo.id);
                    if (index === -1) {
                        sendJSON(res, 404, { error: 'Ticket not found' });
                        return;
                    }

                    let body;
                    try {
                        body = await parseBody(req);
                    } catch (err) {
                        sendJSON(res, 400, { error: 'Invalid JSON in request body' });
                        return;
                    }

                    const allowedFields = ['subject', 'description', 'priority', 'status'];
                    const updates = {};

                    for (const field of allowedFields) {
                        if (body[field] !== undefined) {
                            if (field === 'subject' || field === 'description') {
                                if (typeof body[field] !== 'string' || body[field].trim() === '') {
                                    sendJSON(res, 400, { error: `${field} must be a non-empty string` });
                                    return;
                                }
                                updates[field] = body[field].trim();
                            } else if (field === 'priority') {
                                if (!['low', 'medium', 'high'].includes(body[field])) {
                                    sendJSON(res, 400, { error: 'priority must be one of: low, medium, high' });
                                    return;
                                }
                                updates[field] = body[field];
                            } else if (field === 'status') {
                                if (!['open', 'in_progress', 'resolved'].includes(body[field])) {
                                    sendJSON(res, 400, { error: 'status must be one of: open, in_progress, resolved' });
                                    return;
                                }
                                updates[field] = body[field];
                            }
                        }
                    }

                    if (Object.keys(updates).length === 0) {
                        sendJSON(res, 400, { error: 'No valid fields to update' });
                        return;
                    }

                    tickets[index] = {
                        ...tickets[index],
                        ...updates,
                        updated_at: new Date().toISOString()
                    };

                    await writeTickets(tickets);
                    sendJSON(res, 200, tickets[index]);
                    break;
                }

                case 'deleteTicket': {
                    const index = tickets.findIndex(t => t.id === routeInfo.id);
                    if (index === -1) {
                        sendJSON(res, 404, { error: 'Ticket not found' });
                        return;
                    }

                    tickets.splice(index, 1);
                    await writeTickets(tickets);
                    sendJSON(res, 200, { message: 'Ticket deleted successfully' });
                    break;
                }

                case 'getMetrics': {
                    const now = new Date();
                    const countsByStatus = { open: 0, in_progress: 0, resolved: 0 };
                    const countsByPriority = { low: 0, medium: 0, high: 0 };
                    let totalOpenAgeSeconds = 0;
                    let openCount = 0;

                    for (const ticket of tickets) {
                        countsByStatus[ticket.status]++;
                        countsByPriority[ticket.priority]++;

                        if (ticket.status === 'open') {
                            const created = new Date(ticket.created_at);
                            totalOpenAgeSeconds += (now - created) / 1000;
                            openCount++;
                        }
                    }

                    const metrics = {
                        counts_by_status: countsByStatus,
                        counts_by_priority: countsByPriority,
                        average_open_age_seconds: openCount > 0 ? totalOpenAgeSeconds / openCount : 0
                    };

                    sendJSON(res, 200, metrics);
                    break;
                }

                case 'notFound':
                default: {
                    sendJSON(res, 404, { error: 'Route not found' });
                    break;
                }
            }
        } finally {
            release();
        }
    } catch (err) {
        console.error('Server error:', err);
        if (!res.headersSent) {
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
