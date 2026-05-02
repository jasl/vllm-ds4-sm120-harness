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
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 14.565508
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 318, "total_tokens": 2363, "completion_tokens": 2045, "prompt_tokens_details": null}`
- Prompt tokens: 318
- Completion tokens: 2045
- Total tokens: 2363

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

const PORT = 8080;
const HOST = '127.0.0.1';
const DATA_FILE = path.join(__dirname, 'tickets.json');

function loadTickets() {
    try {
        const data = fs.readFileSync(DATA_FILE, 'utf8');
        return JSON.parse(data);
    } catch (err) {
        return [];
    }
}

function saveTickets(tickets) {
    fs.writeFileSync(DATA_FILE, JSON.stringify(tickets, null, 2), 'utf8');
}

function generateId() {
    return crypto.randomUUID();
}

function getTimestamp() {
    return new Date().toISOString();
}

function parseUrl(url) {
    const parsed = new URL(url, `http://${HOST}:${PORT}`);
    const pathname = parsed.pathname;
    const params = Object.fromEntries(parsed.searchParams);
    return { pathname, params };
}

function matchRoute(pathname) {
    if (pathname === '/tickets') {
        return { route: 'tickets', id: null };
    }
    if (pathname.startsWith('/tickets/')) {
        const id = pathname.slice(9);
        if (id && id.length > 0) {
            return { route: 'ticket', id };
        }
    }
    if (pathname === '/metrics') {
        return { route: 'metrics', id: null };
    }
    return { route: null, id: null };
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

function validatePatch(body) {
    const errors = [];
    if (body.subject !== undefined && (typeof body.subject !== 'string' || body.subject.trim().length === 0)) {
        errors.push('subject must be a non-empty string');
    }
    if (body.description !== undefined && (typeof body.description !== 'string' || body.description.trim().length === 0)) {
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

function getMetrics(tickets) {
    const now = new Date();
    const statusCounts = { open: 0, in_progress: 0, resolved: 0 };
    const priorityCounts = { low: 0, medium: 0, high: 0 };
    let totalOpenAgeSeconds = 0;
    let openCount = 0;

    tickets.forEach(ticket => {
        if (statusCounts.hasOwnProperty(ticket.status)) {
            statusCounts[ticket.status]++;
        }
        if (priorityCounts.hasOwnProperty(ticket.priority)) {
            priorityCounts[ticket.priority]++;
        }
        if (ticket.status === 'open') {
            const created = new Date(ticket.created_at);
            const ageSeconds = (now - created) / 1000;
            totalOpenAgeSeconds += ageSeconds;
            openCount++;
        }
    });

    const averageAgeSeconds = openCount > 0 ? totalOpenAgeSeconds / openCount : 0;

    return {
        statusCounts,
        priorityCounts,
        averageAgeSeconds: Math.round(averageAgeSeconds * 100) / 100
    };
}

function sendResponse(res, statusCode, data) {
    res.writeHead(statusCode, {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type'
    });
    res.end(JSON.stringify(data));
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

const server = http.createServer(async (req, res) => {
    if (req.method === 'OPTIONS') {
        res.writeHead(204, {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type'
        });
        res.end();
        return;
    }

    const { pathname, params } = parseUrl(req.url);
    const { route, id } = matchRoute(pathname);

    if (!route) {
        sendResponse(res, 404, { error: 'Route not found' });
        return;
    }

    try {
        let tickets = loadTickets();

        switch (route) {
            case 'tickets': {
                if (req.method === 'GET') {
                    let filtered = tickets;
                    if (params.status) {
                        filtered = filtered.filter(t => t.status === params.status);
                    }
                    if (params.priority) {
                        filtered = filtered.filter(t => t.priority === params.priority);
                    }
                    sendResponse(res, 200, filtered);
                } else if (req.method === 'POST') {
                    const body = await getBody(req);
                    const errors = validateTicket(body);
                    if (errors.length > 0) {
                        sendResponse(res, 400, { error: 'Validation failed', details: errors });
                        return;
                    }
                    const now = getTimestamp();
                    const ticket = {
                        id: generateId(),
                        subject: body.subject.trim(),
                        description: body.description.trim(),
                        priority: body.priority || 'low',
                        status: 'open',
                        created_at: now,
                        updated_at: now
                    };
                    tickets.push(ticket);
                    saveTickets(tickets);
                    sendResponse(res, 201, ticket);
                } else {
                    sendResponse(res, 405, { error: 'Method not allowed' });
                }
                break;
            }
            case 'ticket': {
                const index = tickets.findIndex(t => t.id === id);
                if (index === -1) {
                    sendResponse(res, 404, { error: 'Ticket not found' });
                    return;
                }

                if (req.method === 'GET') {
                    sendResponse(res, 200, tickets[index]);
                } else if (req.method === 'PATCH') {
                    const body = await getBody(req);
                    const errors = validatePatch(body);
                    if (errors.length > 0) {
                        sendResponse(res, 400, { error: 'Validation failed', details: errors });
                        return;
                    }
                    const now = getTimestamp();
                    const ticket = tickets[index];
                    if (body.subject !== undefined) ticket.subject = body.subject.trim();
                    if (body.description !== undefined) ticket.description = body.description.trim();
                    if (body.priority !== undefined) ticket.priority = body.priority;
                    if (body.status !== undefined) ticket.status = body.status;
                    ticket.updated_at = now;
                    tickets[index] = ticket;
                    saveTickets(tickets);
                    sendResponse(res, 200, ticket);
                } else if (req.method === 'DELETE') {
                    tickets.splice(index, 1);
                    saveTickets(tickets);
                    sendResponse(res, 200, { message: 'Ticket deleted successfully' });
                } else {
                    sendResponse(res, 405, { error: 'Method not allowed' });
                }
                break;
            }
            case 'metrics': {
                if (req.method === 'GET') {
                    const metrics = getMetrics(tickets);
                    sendResponse(res, 200, metrics);
                } else {
                    sendResponse(res, 405, { error: 'Method not allowed' });
                }
                break;
            }
            default: {
                sendResponse(res, 404, { error: 'Route not found' });
            }
        }
    } catch (err) {
        if (err.message === 'Invalid JSON') {
            sendResponse(res, 400, { error: 'Invalid JSON in request body' });
        } else {
            sendResponse(res, 500, { error: 'Internal server error' });
        }
    }
});

server.listen(PORT, HOST, () => {
    console.log(`Server running at http://${HOST}:${PORT}/`);
});
```
````
