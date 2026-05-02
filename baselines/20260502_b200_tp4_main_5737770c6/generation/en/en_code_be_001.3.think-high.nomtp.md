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
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 14.838255
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 318, "total_tokens": 2400, "completion_tokens": 2082, "prompt_tokens_details": null}`
- Prompt tokens: 318
- Completion tokens: 2082
- Total tokens: 2400

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

function readTickets() {
    try {
        const data = fs.readFileSync(DATA_FILE, 'utf8');
        return JSON.parse(data);
    } catch (err) {
        if (err.code === 'ENOENT') {
            return [];
        }
        throw err;
    }
}

function writeTickets(tickets) {
    fs.writeFileSync(DATA_FILE, JSON.stringify(tickets, null, 2), 'utf8');
}

function generateId(tickets) {
    if (tickets.length === 0) return 1;
    const maxId = Math.max(...tickets.map(t => t.id));
    return maxId + 1;
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
        errors.push('priority must be one of: low, medium, high');
    }
    if (body.status && !['open', 'in_progress', 'resolved'].includes(body.status)) {
        errors.push('status must be one of: open, in_progress, resolved');
    }
    return errors;
}

function parseBody(request) {
    return new Promise((resolve, reject) => {
        let body = '';
        request.on('data', chunk => {
            body += chunk.toString();
        });
        request.on('end', () => {
            try {
                resolve(body ? JSON.parse(body) : {});
            } catch (err) {
                reject(new Error('Invalid JSON'));
            }
        });
        request.on('error', reject);
    });
}

function sendJSON(response, statusCode, data) {
    response.writeHead(statusCode, {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type'
    });
    response.end(JSON.stringify(data));
}

function getFilteredTickets(queryParams) {
    let tickets = readTickets();
    const { status, priority } = queryParams;

    if (status) {
        tickets = tickets.filter(t => t.status === status);
    }
    if (priority) {
        tickets = tickets.filter(t => t.priority === priority);
    }

    return tickets;
}

function calculateMetrics() {
    const tickets = readTickets();
    const now = new Date();
    const metrics = {
        byStatus: { open: 0, in_progress: 0, resolved: 0 },
        byPriority: { low: 0, medium: 0, high: 0 },
        averageAgeOpenSeconds: 0
    };

    let totalAgeSeconds = 0;
    let openCount = 0;

    tickets.forEach(ticket => {
        if (metrics.byStatus[ticket.status] !== undefined) {
            metrics.byStatus[ticket.status]++;
        }
        if (metrics.byPriority[ticket.priority] !== undefined) {
            metrics.byPriority[ticket.priority]++;
        }

        if (ticket.status === 'open' || ticket.status === 'in_progress') {
            const createdAt = new Date(ticket.created_at);
            const ageSeconds = (now - createdAt) / 1000;
            totalAgeSeconds += ageSeconds;
            openCount++;
        }
    });

    if (openCount > 0) {
        metrics.averageAgeOpenSeconds = totalAgeSeconds / openCount;
    }

    return metrics;
}

function parsePath(url) {
    const parsed = new URL(url, `http://${HOST}:${PORT}`);
    const pathParts = parsed.pathname.split('/').filter(Boolean);
    return { pathParts, queryParams: Object.fromEntries(parsed.searchParams) };
}

const server = http.createServer(async (req, res) => {
    try {
        const { pathParts, queryParams } = parsePath(req.url);

        // Handle CORS preflight
        if (req.method === 'OPTIONS') {
            sendJSON(res, 204, {});
            return;
        }

        // Router
        if (pathParts.length === 0) {
            sendJSON(res, 404, { error: 'Not found' });
            return;
        }

        if (pathParts[0] === 'tickets') {
            if (pathParts.length === 1) {
                // /tickets
                if (req.method === 'GET') {
                    const tickets = getFilteredTickets(queryParams);
                    sendJSON(res, 200, tickets);
                } else if (req.method === 'POST') {
                    const body = await parseBody(req);
                    const errors = validateTicket(body);
                    if (errors.length > 0) {
                        sendJSON(res, 400, { error: 'Validation failed', details: errors });
                        return;
                    }

                    const tickets = readTickets();
                    const now = new Date().toISOString();
                    const ticket = {
                        id: generateId(tickets),
                        subject: body.subject.trim(),
                        description: body.description.trim(),
                        priority: body.priority || 'low',
                        status: body.status || 'open',
                        created_at: now,
                        updated_at: now
                    };
                    tickets.push(ticket);
                    writeTickets(tickets);
                    sendJSON(res, 201, ticket);
                } else {
                    sendJSON(res, 405, { error: 'Method not allowed' });
                }
            } else if (pathParts.length === 2) {
                // /tickets/{id}
                const id = parseInt(pathParts[1], 10);
                if (isNaN(id)) {
                    sendJSON(res, 400, { error: 'Invalid ticket ID' });
                    return;
                }

                const tickets = readTickets();
                const ticketIndex = tickets.findIndex(t => t.id === id);

                if (ticketIndex === -1) {
                    sendJSON(res, 404, { error: 'Ticket not found' });
                    return;
                }

                if (req.method === 'GET') {
                    sendJSON(res, 200, tickets[ticketIndex]);
                } else if (req.method === 'PATCH') {
                    const body = await parseBody(req);
                    const allowedFields = ['subject', 'description', 'priority', 'status'];
                    const updates = {};

                    for (const field of allowedFields) {
                        if (body[field] !== undefined) {
                            if (field === 'priority' && !['low', 'medium', 'high'].includes(body[field])) {
                                sendJSON(res, 400, { error: `Invalid priority: ${body[field]}` });
                                return;
                            }
                            if (field === 'status' && !['open', 'in_progress', 'resolved'].includes(body[field])) {
                                sendJSON(res, 400, { error: `Invalid status: ${body[field]}` });
                                return;
                            }
                            if ((field === 'subject' || field === 'description') &&
                                (typeof body[field] !== 'string' || body[field].trim() === '')) {
                                sendJSON(res, 400, { error: `${field} must be a non-empty string` });
                                return;
                            }
                            updates[field] = body[field].trim ? body[field].trim() : body[field];
                        }
                    }

                    if (Object.keys(updates).length === 0) {
                        sendJSON(res, 400, { error: 'No valid fields to update' });
                        return;
                    }

                    updates.updated_at = new Date().toISOString();
                    tickets[ticketIndex] = { ...tickets[ticketIndex], ...updates };
                    writeTickets(tickets);
                    sendJSON(res, 200, tickets[ticketIndex]);
                } else if (req.method === 'DELETE') {
                    const deletedTicket = tickets.splice(ticketIndex, 1)[0];
                    writeTickets(tickets);
                    sendJSON(res, 200, { message: 'Ticket deleted', ticket: deletedTicket });
                } else {
                    sendJSON(res, 405, { error: 'Method not allowed' });
                }
            } else {
                sendJSON(res, 404, { error: 'Not found' });
            }
        } else if (pathParts[0] === 'metrics') {
            if (req.method === 'GET') {
                const metrics = calculateMetrics();
                sendJSON(res, 200, metrics);
            } else {
                sendJSON(res, 405, { error: 'Method not allowed' });
            }
        } else {
            sendJSON(res, 404, { error: 'Route not found' });
        }
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
