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
- Elapsed seconds: 15.650674
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 318, "total_tokens": 2511, "completion_tokens": 2193, "prompt_tokens_details": null}`
- Prompt tokens: 318
- Completion tokens: 2193
- Total tokens: 2511

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

const DATA_FILE = path.join(__dirname, 'tickets.json');
const HOST = '127.0.0.1';
const PORT = 8080;

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

function generateId() {
    return crypto.randomUUID();
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

function sendResponse(res, statusCode, data) {
    res.writeHead(statusCode, {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type'
    });
    res.end(JSON.stringify(data));
}

function handleCors(req, res) {
    if (req.method === 'OPTIONS') {
        sendResponse(res, 204, {});
        return true;
    }
    return false;
}

function validateTicket(body) {
    const errors = [];
    if (!body.subject || typeof body.subject !== 'string') {
        errors.push('subject is required and must be a string');
    }
    if (!body.description || typeof body.description !== 'string') {
        errors.push('description is required and must be a string');
    }
    const priorities = ['low', 'medium', 'high'];
    if (!body.priority || !priorities.includes(body.priority)) {
        errors.push('priority must be one of: low, medium, high');
    }
    const statuses = ['open', 'in_progress', 'resolved'];
    if (!body.status || !statuses.includes(body.status)) {
        errors.push('status must be one of: open, in_progress, resolved');
    }
    return errors;
}

function getTickets(req, res) {
    const url = new URL(req.url, `http://${req.headers.host}`);
    const statusFilter = url.searchParams.get('status');
    const priorityFilter = url.searchParams.get('priority');

    let tickets = readTickets();

    if (statusFilter) {
        tickets = tickets.filter(t => t.status === statusFilter);
    }
    if (priorityFilter) {
        tickets = tickets.filter(t => t.priority === priorityFilter);
    }

    sendResponse(res, 200, tickets);
}

async function createTicket(req, res) {
    try {
        const body = await parseBody(req);
        const errors = validateTicket(body);

        if (errors.length > 0) {
            sendResponse(res, 400, { error: 'Validation failed', details: errors });
            return;
        }

        const tickets = readTickets();
        const now = new Date().toISOString();

        const ticket = {
            id: generateId(),
            subject: body.subject,
            description: body.description,
            priority: body.priority,
            status: body.status,
            created_at: now,
            updated_at: now
        };

        tickets.push(ticket);
        writeTickets(tickets);

        sendResponse(res, 201, ticket);
    } catch (err) {
        if (err.message === 'Invalid JSON') {
            sendResponse(res, 400, { error: 'Invalid JSON in request body' });
        } else {
            sendResponse(res, 500, { error: 'Internal server error' });
        }
    }
}

function getTicket(req, res, id) {
    const tickets = readTickets();
    const ticket = tickets.find(t => t.id === id);

    if (!ticket) {
        sendResponse(res, 404, { error: 'Ticket not found' });
        return;
    }

    sendResponse(res, 200, ticket);
}

async function updateTicket(req, res, id) {
    try {
        const body = await parseBody(req);
        const tickets = readTickets();
        const index = tickets.findIndex(t => t.id === id);

        if (index === -1) {
            sendResponse(res, 404, { error: 'Ticket not found' });
            return;
        }

        const allowedFields = ['subject', 'description', 'priority', 'status'];
        const updates = {};

        for (const field of allowedFields) {
            if (body[field] !== undefined) {
                if (field === 'priority' && !['low', 'medium', 'high'].includes(body[field])) {
                    sendResponse(res, 400, { error: 'priority must be one of: low, medium, high' });
                    return;
                }
                if (field === 'status' && !['open', 'in_progress', 'resolved'].includes(body[field])) {
                    sendResponse(res, 400, { error: 'status must be one of: open, in_progress, resolved' });
                    return;
                }
                updates[field] = body[field];
            }
        }

        if (Object.keys(updates).length === 0) {
            sendResponse(res, 400, { error: 'No valid fields to update' });
            return;
        }

        tickets[index] = {
            ...tickets[index],
            ...updates,
            updated_at: new Date().toISOString()
        };

        writeTickets(tickets);
        sendResponse(res, 200, tickets[index]);
    } catch (err) {
        if (err.message === 'Invalid JSON') {
            sendResponse(res, 400, { error: 'Invalid JSON in request body' });
        } else {
            sendResponse(res, 500, { error: 'Internal server error' });
        }
    }
}

function deleteTicket(req, res, id) {
    const tickets = readTickets();
    const index = tickets.findIndex(t => t.id === id);

    if (index === -1) {
        sendResponse(res, 404, { error: 'Ticket not found' });
        return;
    }

    tickets.splice(index, 1);
    writeTickets(tickets);

    sendResponse(res, 200, { message: 'Ticket deleted successfully' });
}

function getMetrics(req, res) {
    const tickets = readTickets();
    const now = new Date();

    const statusCounts = {
        open: 0,
        in_progress: 0,
        resolved: 0
    };

    const priorityCounts = {
        low: 0,
        medium: 0,
        high: 0
    };

    let totalOpenAgeSeconds = 0;
    let openTicketCount = 0;

    for (const ticket of tickets) {
        statusCounts[ticket.status]++;
        priorityCounts[ticket.priority]++;

        if (ticket.status === 'open') {
            const created = new Date(ticket.created_at);
            const ageSeconds = (now - created) / 1000;
            totalOpenAgeSeconds += ageSeconds;
            openTicketCount++;
        }
    }

    const metrics = {
        status_counts: statusCounts,
        priority_counts: priorityCounts,
        average_open_age_seconds: openTicketCount > 0 ? Math.round(totalOpenAgeSeconds / openTicketCount) : 0
    };

    sendResponse(res, 200, metrics);
}

function routeRequest(req, res) {
    if (handleCors(req, res)) return;

    const url = new URL(req.url, `http://${req.headers.host}`);
    const pathParts = url.pathname.split('/').filter(Boolean);

    try {
        if (pathParts.length === 0 || pathParts[0] !== 'tickets' && pathParts[0] !== 'metrics') {
            sendResponse(res, 404, { error: 'Route not found' });
            return;
        }

        if (pathParts[0] === 'metrics' && pathParts.length === 1) {
            if (req.method === 'GET') {
                getMetrics(req, res);
            } else {
                sendResponse(res, 405, { error: 'Method not allowed' });
            }
            return;
        }

        if (pathParts[0] === 'tickets') {
            if (pathParts.length === 1) {
                if (req.method === 'GET') {
                    getTickets(req, res);
                } else if (req.method === 'POST') {
                    createTicket(req, res);
                } else {
                    sendResponse(res, 405, { error: 'Method not allowed' });
                }
            } else if (pathParts.length === 2) {
                const id = pathParts[1];
                if (req.method === 'GET') {
                    getTicket(req, res, id);
                } else if (req.method === 'PATCH') {
                    updateTicket(req, res, id);
                } else if (req.method === 'DELETE') {
                    deleteTicket(req, res, id);
                } else {
                    sendResponse(res, 405, { error: 'Method not allowed' });
                }
            } else {
                sendResponse(res, 404, { error: 'Route not found' });
            }
        }
    } catch (err) {
        sendResponse(res, 500, { error: 'Internal server error' });
    }
}

const server = http.createServer(routeRequest);

server.listen(PORT, HOST, () => {
    console.log(`Server running at http://${HOST}:${PORT}/`);
});
```
````
