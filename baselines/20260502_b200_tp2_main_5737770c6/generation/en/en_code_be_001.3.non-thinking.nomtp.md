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
- Elapsed seconds: 18.926819
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 318, "total_tokens": 2648, "completion_tokens": 2330, "prompt_tokens_details": null}`
- Prompt tokens: 318
- Completion tokens: 2330
- Total tokens: 2648

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

// File locking mechanism for sequential access
let fileLock = Promise.resolve();

function withFileLock(fn) {
    return fileLock = fileLock.then(fn, fn);
}

function readTickets() {
    try {
        const data = fs.readFileSync(DATA_FILE, 'utf-8');
        return JSON.parse(data);
    } catch (err) {
        if (err.code === 'ENOENT') {
            return [];
        }
        throw err;
    }
}

function writeTickets(tickets) {
    fs.writeFileSync(DATA_FILE, JSON.stringify(tickets, null, 2), 'utf-8');
}

function generateId() {
    return crypto.randomUUID();
}

function getTimestamp() {
    return new Date().toISOString();
}

function parseUrl(url) {
    const [pathname, queryString] = url.split('?');
    const params = {};
    if (queryString) {
        queryString.split('&').forEach(pair => {
            const [key, value] = pair.split('=');
            params[decodeURIComponent(key)] = decodeURIComponent(value || '');
        });
    }
    return { pathname, params };
}

function matchRoute(pathname) {
    if (pathname === '/tickets') {
        return { route: 'tickets', id: null };
    }
    if (pathname === '/metrics') {
        return { route: 'metrics', id: null };
    }
    const match = pathname.match(/^\/tickets\/([a-f0-9-]+)$/);
    if (match) {
        return { route: 'ticket', id: match[1] };
    }
    return null;
}

function sendResponse(res, statusCode, data) {
    const body = JSON.stringify(data);
    res.writeHead(statusCode, {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Content-Length': Buffer.byteLength(body)
    });
    res.end(body);
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
    if (body.subject && typeof body.subject === 'string') {
        body.subject = body.subject.trim();
    }
    if (body.description && typeof body.description === 'string') {
        body.description = body.description.trim();
    }
    return errors;
}

function validatePatchFields(body) {
    const validFields = ['subject', 'description', 'priority', 'status'];
    const errors = [];
    const updates = {};

    for (const field of validFields) {
        if (body[field] !== undefined) {
            if (field === 'subject' || field === 'description') {
                if (typeof body[field] !== 'string' || body[field].trim() === '') {
                    errors.push(`${field} must be a non-empty string`);
                    continue;
                }
                updates[field] = body[field].trim();
            } else if (field === 'priority') {
                if (!['low', 'medium', 'high'].includes(body[field])) {
                    errors.push('priority must be low, medium, or high');
                    continue;
                }
                updates[field] = body[field];
            } else if (field === 'status') {
                if (!['open', 'in_progress', 'resolved'].includes(body[field])) {
                    errors.push('status must be open, in_progress, or resolved');
                    continue;
                }
                updates[field] = body[field];
            }
        }
    }

    if (Object.keys(updates).length === 0) {
        errors.push('at least one valid field must be provided');
    }

    return { errors, updates };
}

function getMetrics(tickets) {
    const statusCounts = { open: 0, in_progress: 0, resolved: 0 };
    const priorityCounts = { low: 0, medium: 0, high: 0 };
    let openAgeSum = 0;
    let openCount = 0;
    const now = new Date();

    tickets.forEach(ticket => {
        if (statusCounts[ticket.status] !== undefined) {
            statusCounts[ticket.status]++;
        }
        if (priorityCounts[ticket.priority] !== undefined) {
            priorityCounts[ticket.priority]++;
        }
        if (ticket.status === 'open') {
            const created = new Date(ticket.created_at);
            const ageSeconds = (now - created) / 1000;
            openAgeSum += ageSeconds;
            openCount++;
        }
    });

    return {
        status_counts: statusCounts,
        priority_counts: priorityCounts,
        average_open_age_seconds: openCount > 0 ? Math.round(openAgeSum / openCount * 100) / 100 : 0
    };
}

const server = http.createServer((req, res) => {
    const { pathname, params } = parseUrl(req.url);
    const route = matchRoute(pathname);

    if (!route) {
        sendResponse(res, 404, { error: 'Not found', message: `Route ${pathname} not found` });
        return;
    }

    if (req.method === 'OPTIONS') {
        res.writeHead(204, {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type'
        });
        res.end();
        return;
    }

    let body = '';
    req.on('data', chunk => {
        body += chunk;
        if (body.length > 1e6) {
            sendResponse(res, 413, { error: 'Request too large' });
            req.destroy();
        }
    });

    req.on('end', () => {
        withFileLock(() => {
            try {
                const tickets = readTickets();

                if (route.route === 'metrics') {
                    if (req.method !== 'GET') {
                        sendResponse(res, 405, { error: 'Method not allowed', message: 'Only GET is allowed for /metrics' });
                        return;
                    }
                    const metrics = getMetrics(tickets);
                    sendResponse(res, 200, metrics);
                    return;
                }

                if (route.route === 'tickets') {
                    if (req.method === 'GET') {
                        let filtered = [...tickets];
                        if (params.status) {
                            filtered = filtered.filter(t => t.status === params.status);
                        }
                        if (params.priority) {
                            filtered = filtered.filter(t => t.priority === params.priority);
                        }
                        sendResponse(res, 200, filtered);
                        return;
                    }

                    if (req.method === 'POST') {
                        let parsedBody;
                        try {
                            parsedBody = JSON.parse(body);
                        } catch (e) {
                            sendResponse(res, 400, { error: 'Invalid JSON' });
                            return;
                        }

                        const errors = validateTicket(parsedBody);
                        if (errors.length > 0) {
                            sendResponse(res, 400, { error: 'Validation failed', details: errors });
                            return;
                        }

                        const timestamp = getTimestamp();
                        const newTicket = {
                            id: generateId(),
                            subject: parsedBody.subject,
                            description: parsedBody.description,
                            priority: parsedBody.priority || 'low',
                            status: parsedBody.status || 'open',
                            created_at: timestamp,
                            updated_at: timestamp
                        };

                        tickets.push(newTicket);
                        writeTickets(tickets);
                        sendResponse(res, 201, newTicket);
                        return;
                    }

                    sendResponse(res, 405, { error: 'Method not allowed', message: 'Use GET to list or POST to create' });
                    return;
                }

                if (route.route === 'ticket') {
                    const ticketIndex = tickets.findIndex(t => t.id === route.id);

                    if (ticketIndex === -1) {
                        sendResponse(res, 404, { error: 'Not found', message: `Ticket ${route.id} not found` });
                        return;
                    }

                    if (req.method === 'GET') {
                        sendResponse(res, 200, tickets[ticketIndex]);
                        return;
                    }

                    if (req.method === 'PATCH') {
                        let parsedBody;
                        try {
                            parsedBody = JSON.parse(body);
                        } catch (e) {
                            sendResponse(res, 400, { error: 'Invalid JSON' });
                            return;
                        }

                        const { errors, updates } = validatePatchFields(parsedBody);
                        if (errors.length > 0) {
                            sendResponse(res, 400, { error: 'Validation failed', details: errors });
                            return;
                        }

                        Object.assign(tickets[ticketIndex], updates);
                        tickets[ticketIndex].updated_at = getTimestamp();
                        writeTickets(tickets);
                        sendResponse(res, 200, tickets[ticketIndex]);
                        return;
                    }

                    if (req.method === 'DELETE') {
                        const deletedTicket = tickets.splice(ticketIndex, 1)[0];
                        writeTickets(tickets);
                        sendResponse(res, 200, { message: 'Ticket deleted', ticket: deletedTicket });
                        return;
                    }

                    sendResponse(res, 405, { error: 'Method not allowed', message: 'Use GET, PATCH, or DELETE' });
                    return;
                }
            } catch (err) {
                console.error('Server error:', err);
                sendResponse(res, 500, { error: 'Internal server error' });
            }
        });
    });
});

server.listen(PORT, HOST, () => {
    console.log(`Server running at http://${HOST}:${PORT}/`);
});
```
````
