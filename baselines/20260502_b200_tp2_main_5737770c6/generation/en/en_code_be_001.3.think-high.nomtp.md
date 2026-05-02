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
- Elapsed seconds: 21.274997
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 318, "total_tokens": 2927, "completion_tokens": 2609, "prompt_tokens_details": null}`
- Prompt tokens: 318
- Completion tokens: 2609
- Total tokens: 2927

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

// File locking mechanism for sequential writes
let writeLock = false;
const writeQueue = [];

function acquireLock() {
    return new Promise((resolve) => {
        if (!writeLock) {
            writeLock = true;
            resolve();
        } else {
            writeQueue.push(resolve);
        }
    });
}

function releaseLock() {
    if (writeQueue.length > 0) {
        const next = writeQueue.shift();
        next();
    } else {
        writeLock = false;
    }
}

// Read tickets from file
function readTickets() {
    try {
        if (!fs.existsSync(DATA_FILE)) {
            return [];
        }
        const data = fs.readFileSync(DATA_FILE, 'utf8');
        return JSON.parse(data);
    } catch (err) {
        return [];
    }
}

// Write tickets to file safely
async function writeTickets(tickets) {
    await acquireLock();
    try {
        const tempFile = DATA_FILE + '.tmp';
        fs.writeFileSync(tempFile, JSON.stringify(tickets, null, 2), 'utf8');
        fs.renameSync(tempFile, DATA_FILE);
    } finally {
        releaseLock();
    }
}

// Generate unique ID
function generateId() {
    return crypto.randomBytes(16).toString('hex');
}

// Validate ticket fields
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

// Parse JSON body
function parseBody(req) {
    return new Promise((resolve, reject) => {
        let body = '';
        req.on('data', chunk => {
            body += chunk.toString();
        });
        req.on('end', () => {
            try {
                if (!body) {
                    resolve({});
                    return;
                }
                resolve(JSON.parse(body));
            } catch (err) {
                reject(new Error('Invalid JSON'));
            }
        });
        req.on('error', reject);
    });
}

// Send JSON response
function sendJson(res, statusCode, data) {
    res.writeHead(statusCode, {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type'
    });
    res.end(JSON.stringify(data));
}

// Parse URL and query parameters
function parseUrl(url) {
    const [pathname, queryString] = url.split('?');
    const query = {};
    if (queryString) {
        queryString.split('&').forEach(pair => {
            const [key, value] = pair.split('=');
            query[decodeURIComponent(key)] = decodeURIComponent(value || '');
        });
    }
    return { pathname: pathname.replace(/\/+$/, '') || '/', query };
}

// Route handler
async function handleRequest(req, res) {
    const { pathname, query } = parseUrl(req.url);
    const method = req.method.toUpperCase();

    // CORS preflight
    if (method === 'OPTIONS') {
        res.writeHead(204, {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type'
        });
        res.end();
        return;
    }

    try {
        // Route matching
        if (pathname === '/tickets' && method === 'GET') {
            await handleGetTickets(req, res, query);
        } else if (pathname === '/tickets' && method === 'POST') {
            await handlePostTicket(req, res);
        } else if (pathname.match(/^\/tickets\/([a-f0-9]+)$/) && method === 'GET') {
            const id = pathname.match(/^\/tickets\/([a-f0-9]+)$/)[1];
            await handleGetTicket(req, res, id);
        } else if (pathname.match(/^\/tickets\/([a-f0-9]+)$/) && method === 'PATCH') {
            const id = pathname.match(/^\/tickets\/([a-f0-9]+)$/)[1];
            await handlePatchTicket(req, res, id);
        } else if (pathname.match(/^\/tickets\/([a-f0-9]+)$/) && method === 'DELETE') {
            const id = pathname.match(/^\/tickets\/([a-f0-9]+)$/)[1];
            await handleDeleteTicket(req, res, id);
        } else if (pathname === '/metrics' && method === 'GET') {
            await handleGetMetrics(req, res);
        } else {
            sendJson(res, 404, { error: 'Route not found' });
        }
    } catch (err) {
        if (err.message === 'Invalid JSON') {
            sendJson(res, 400, { error: 'Invalid JSON in request body' });
        } else {
            sendJson(res, 500, { error: 'Internal server error' });
        }
    }
}

// GET /tickets
async function handleGetTickets(req, res, query) {
    const tickets = readTickets();
    let filtered = [...tickets];

    if (query.status) {
        filtered = filtered.filter(t => t.status === query.status);
    }
    if (query.priority) {
        filtered = filtered.filter(t => t.priority === query.priority);
    }

    sendJson(res, 200, filtered);
}

// POST /tickets
async function handlePostTicket(req, res) {
    const body = await parseBody(req);
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
        priority: body.priority || 'low',
        status: body.status || 'open',
        created_at: now,
        updated_at: now
    };

    const tickets = readTickets();
    tickets.push(ticket);
    await writeTickets(tickets);

    sendJson(res, 201, ticket);
}

// GET /tickets/:id
async function handleGetTicket(req, res, id) {
    const tickets = readTickets();
    const ticket = tickets.find(t => t.id === id);

    if (!ticket) {
        sendJson(res, 404, { error: 'Ticket not found' });
        return;
    }

    sendJson(res, 200, ticket);
}

// PATCH /tickets/:id
async function handlePatchTicket(req, res, id) {
    const body = await parseBody(req);
    const tickets = readTickets();
    const index = tickets.findIndex(t => t.id === id);

    if (index === -1) {
        sendJson(res, 404, { error: 'Ticket not found' });
        return;
    }

    // Validate fields if provided
    const errors = [];
    if (body.subject !== undefined && (typeof body.subject !== 'string' || body.subject.trim() === '')) {
        errors.push('subject must be a non-empty string');
    }
    if (body.description !== undefined && (typeof body.description !== 'string' || body.description.trim() === '')) {
        errors.push('description must be a non-empty string');
    }
    if (body.priority !== undefined && !['low', 'medium', 'high'].includes(body.priority)) {
        errors.push('priority must be one of: low, medium, high');
    }
    if (body.status !== undefined && !['open', 'in_progress', 'resolved'].includes(body.status)) {
        errors.push('status must be one of: open, in_progress, resolved');
    }

    if (errors.length > 0) {
        sendJson(res, 400, { error: 'Validation failed', details: errors });
        return;
    }

    const ticket = tickets[index];
    if (body.subject !== undefined) ticket.subject = body.subject.trim();
    if (body.description !== undefined) ticket.description = body.description.trim();
    if (body.priority !== undefined) ticket.priority = body.priority;
    if (body.status !== undefined) ticket.status = body.status;
    ticket.updated_at = new Date().toISOString();

    tickets[index] = ticket;
    await writeTickets(tickets);

    sendJson(res, 200, ticket);
}

// DELETE /tickets/:id
async function handleDeleteTicket(req, res, id) {
    const tickets = readTickets();
    const index = tickets.findIndex(t => t.id === id);

    if (index === -1) {
        sendJson(res, 404, { error: 'Ticket not found' });
        return;
    }

    tickets.splice(index, 1);
    await writeTickets(tickets);

    sendJson(res, 200, { message: 'Ticket deleted successfully' });
}

// GET /metrics
async function handleGetMetrics(req, res) {
    const tickets = readTickets();
    const now = new Date();

    const statusCounts = { open: 0, in_progress: 0, resolved: 0 };
    const priorityCounts = { low: 0, medium: 0, high: 0 };
    let openTicketsAgeSum = 0;
    let openTicketCount = 0;

    tickets.forEach(ticket => {
        // Status counts
        if (statusCounts.hasOwnProperty(ticket.status)) {
            statusCounts[ticket.status]++;
        }

        // Priority counts
        if (priorityCounts.hasOwnProperty(ticket.priority)) {
            priorityCounts[ticket.priority]++;
        }

        // Average age of open tickets
        if (ticket.status === 'open') {
            const created = new Date(ticket.created_at);
            const ageInSeconds = (now - created) / 1000;
            openTicketsAgeSum += ageInSeconds;
            openTicketCount++;
        }
    });

    const averageAgeInSeconds = openTicketCount > 0 ? openTicketsAgeSum / openTicketCount : 0;

    sendJson(res, 200, {
        byStatus: statusCounts,
        byPriority: priorityCounts,
        averageOpenTicketAgeSeconds: Math.round(averageAgeInSeconds * 100) / 100
    });
}

// Create server
const server = http.createServer(handleRequest);

server.listen(PORT, HOST, () => {
    console.log(`Server running at http://${HOST}:${PORT}/`);
});

// Handle graceful shutdown
process.on('SIGINT', () => {
    console.log('\nShutting down server...');
    server.close(() => {
        console.log('Server stopped.');
        process.exit(0);
    });
});

process.on('SIGTERM', () => {
    server.close(() => {
        process.exit(0);
    });
});
```
````
