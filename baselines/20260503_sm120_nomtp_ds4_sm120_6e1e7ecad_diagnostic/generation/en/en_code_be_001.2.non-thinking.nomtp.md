# Generation Transcript

- Case: `en_code_be_001`
- Language group: `en`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `2`
- Thinking mode: `non-thinking`
- Thinking strength: `disabled`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 37.522872
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 318, "total_tokens": 2710, "completion_tokens": 2392, "prompt_tokens_details": null}`
- Prompt tokens: 318
- Completion tokens: 2392
- Total tokens: 2710

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
    const tempFile = DATA_FILE + '.tmp';
    fs.writeFileSync(tempFile, JSON.stringify(tickets, null, 2), 'utf8');
    fs.renameSync(tempFile, DATA_FILE);
}

function generateId() {
    return crypto.randomUUID();
}

function getTimestamp() {
    return new Date().toISOString();
}

function corsHeaders(res) {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
}

function sendJson(res, statusCode, data) {
    res.writeHead(statusCode, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(data));
}

function parseUrl(reqUrl) {
    const url = new URL(reqUrl, `http://${HOST}:${PORT}`);
    const pathParts = url.pathname.split('/').filter(Boolean);
    return { url, pathParts };
}

function parseBody(req) {
    return new Promise((resolve, reject) => {
        let body = '';
        req.on('data', chunk => {
            body += chunk.toString();
        });
        req.on('end', () => {
            if (!body) {
                resolve({});
                return;
            }
            try {
                resolve(JSON.parse(body));
            } catch (err) {
                reject(new Error('Invalid JSON'));
            }
        });
        req.on('error', reject);
    });
}

function validateTicketBody(body, isUpdate = false) {
    const allowedFields = ['subject', 'description', 'priority', 'status'];
    const validPriorities = ['low', 'medium', 'high'];
    const validStatuses = ['open', 'in_progress', 'resolved'];

    if (!isUpdate) {
        if (!body.subject || typeof body.subject !== 'string' || body.subject.trim() === '') {
            return 'subject is required and must be a non-empty string';
        }
        if (!body.description || typeof body.description !== 'string' || body.description.trim() === '') {
            return 'description is required and must be a non-empty string';
        }
        if (!body.priority || !validPriorities.includes(body.priority)) {
            return 'priority must be one of: low, medium, high';
        }
        if (!body.status || !validStatuses.includes(body.status)) {
            return 'status must be one of: open, in_progress, resolved';
        }
    } else {
        for (const key of Object.keys(body)) {
            if (!allowedFields.includes(key)) {
                return `Invalid field: ${key}`;
            }
        }
        if (body.priority && !validPriorities.includes(body.priority)) {
            return 'priority must be one of: low, medium, high';
        }
        if (body.status && !validStatuses.includes(body.status)) {
            return 'status must be one of: open, in_progress, resolved';
        }
        if (body.subject !== undefined && (typeof body.subject !== 'string' || body.subject.trim() === '')) {
            return 'subject must be a non-empty string';
        }
        if (body.description !== undefined && (typeof body.description !== 'string' || body.description.trim() === '')) {
            return 'description must be a non-empty string';
        }
    }
    return null;
}

function handleGetTickets(req, res, url) {
    const tickets = readTickets();
    const status = url.searchParams.get('status');
    const priority = url.searchParams.get('priority');

    let filtered = tickets;

    if (status) {
        filtered = filtered.filter(t => t.status === status);
    }
    if (priority) {
        filtered = filtered.filter(t => t.priority === priority);
    }

    sendJson(res, 200, filtered);
}

async function handlePostTicket(req, res) {
    try {
        const body = await parseBody(req);
        const error = validateTicketBody(body, false);
        if (error) {
            sendJson(res, 400, { error });
            return;
        }

        const tickets = readTickets();
        const now = getTimestamp();
        const newTicket = {
            id: generateId(),
            subject: body.subject.trim(),
            description: body.description.trim(),
            priority: body.priority,
            status: body.status,
            created_at: now,
            updated_at: now
        };

        tickets.push(newTicket);
        writeTickets(tickets);

        sendJson(res, 201, newTicket);
    } catch (err) {
        if (err.message === 'Invalid JSON') {
            sendJson(res, 400, { error: 'Invalid JSON in request body' });
        } else {
            sendJson(res, 500, { error: 'Internal server error' });
        }
    }
}

function handleGetTicket(req, res, id) {
    const tickets = readTickets();
    const ticket = tickets.find(t => t.id === id);

    if (!ticket) {
        sendJson(res, 404, { error: 'Ticket not found' });
        return;
    }

    sendJson(res, 200, ticket);
}

async function handlePatchTicket(req, res, id) {
    try {
        const body = await parseBody(req);
        const error = validateTicketBody(body, true);
        if (error) {
            sendJson(res, 400, { error });
            return;
        }

        const tickets = readTickets();
        const index = tickets.findIndex(t => t.id === id);

        if (index === -1) {
            sendJson(res, 404, { error: 'Ticket not found' });
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
        writeTickets(tickets);

        sendJson(res, 200, ticket);
    } catch (err) {
        if (err.message === 'Invalid JSON') {
            sendJson(res, 400, { error: 'Invalid JSON in request body' });
        } else {
            sendJson(res, 500, { error: 'Internal server error' });
        }
    }
}

function handleDeleteTicket(req, res, id) {
    const tickets = readTickets();
    const index = tickets.findIndex(t => t.id === id);

    if (index === -1) {
        sendJson(res, 404, { error: 'Ticket not found' });
        return;
    }

    tickets.splice(index, 1);
    writeTickets(tickets);

    sendJson(res, 200, { message: 'Ticket deleted successfully' });
}

function handleGetMetrics(req, res) {
    const tickets = readTickets();
    const now = new Date();

    const statusCounts = { open: 0, in_progress: 0, resolved: 0 };
    const priorityCounts = { low: 0, medium: 0, high: 0 };
    let totalAgeSeconds = 0;
    let openTicketCount = 0;

    for (const ticket of tickets) {
        if (statusCounts.hasOwnProperty(ticket.status)) {
            statusCounts[ticket.status]++;
        }
        if (priorityCounts.hasOwnProperty(ticket.priority)) {
            priorityCounts[ticket.priority]++;
        }

        if (ticket.status === 'open') {
            const created = new Date(ticket.created_at);
            const ageSeconds = (now - created) / 1000;
            totalAgeSeconds += ageSeconds;
            openTicketCount++;
        }
    }

    const metrics = {
        status_counts: statusCounts,
        priority_counts: priorityCounts,
        average_open_age_seconds: openTicketCount > 0 ? totalAgeSeconds / openTicketCount : 0
    };

    sendJson(res, 200, metrics);
}

function handleOptions(req, res) {
    corsHeaders(res);
    res.writeHead(204);
    res.end();
}

function handleNotFound(req, res) {
    sendJson(res, 404, { error: 'Route not found' });
}

function handleMethodNotAllowed(req, res) {
    sendJson(res, 405, { error: 'Method not allowed' });
}

const server = http.createServer(async (req, res) => {
    corsHeaders(res);

    if (req.method === 'OPTIONS') {
        handleOptions(req, res);
        return;
    }

    const { url, pathParts } = parseUrl(req.url);

    try {
        if (pathParts.length === 1 && pathParts[0] === 'tickets') {
            if (req.method === 'GET') {
                handleGetTickets(req, res, url);
            } else if (req.method === 'POST') {
                await handlePostTicket(req, res);
            } else {
                handleMethodNotAllowed(req, res);
            }
        } else if (pathParts.length === 2 && pathParts[0] === 'tickets') {
            const id = pathParts[1];
            if (req.method === 'GET') {
                handleGetTicket(req, res, id);
            } else if (req.method === 'PATCH') {
                await handlePatchTicket(req, res, id);
            } else if (req.method === 'DELETE') {
                handleDeleteTicket(req, res, id);
            } else {
                handleMethodNotAllowed(req, res);
            }
        } else if (pathParts.length === 1 && pathParts[0] === 'metrics') {
            if (req.method === 'GET') {
                handleGetMetrics(req, res);
            } else {
                handleMethodNotAllowed(req, res);
            }
        } else if (pathParts.length === 1 && pathParts[0] === '') {
            sendJson(res, 200, { message: 'Help Desk Ticket API', endpoints: ['/tickets', '/tickets/{id}', '/metrics'] });
        } else {
            handleNotFound(req, res);
        }
    } catch (err) {
        sendJson(res, 500, { error: 'Internal server error' });
    }
});

server.listen(PORT, HOST, () => {
    console.log(`Server running at http://${HOST}:${PORT}/`);
});
```
````
