# Generation Transcript

- Case: `en_code_be_001`
- Language group: `en`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `2`
- Thinking mode: `think-max`
- Thinking strength: `max`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 18.83599
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 318, "total_tokens": 2957, "completion_tokens": 2639, "prompt_tokens_details": null}`
- Prompt tokens: 318
- Completion tokens: 2639
- Total tokens: 2957

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

const HOST = '127.0.0.1';
const PORT = 8080;
const DATA_FILE = path.join(__dirname, 'tickets.json');

// File locking mechanism for safe concurrent access
let fileLock = false;
const lockQueue = [];

function acquireLock() {
    return new Promise((resolve) => {
        if (!fileLock) {
            fileLock = true;
            resolve();
        } else {
            lockQueue.push(resolve);
        }
    });
}

function releaseLock() {
    if (lockQueue.length > 0) {
        const next = lockQueue.shift();
        next();
    } else {
        fileLock = false;
    }
}

// Data access functions
async function readTickets() {
    await acquireLock();
    try {
        if (!fs.existsSync(DATA_FILE)) {
            fs.writeFileSync(DATA_FILE, '[]', 'utf8');
            return [];
        }
        const data = fs.readFileSync(DATA_FILE, 'utf8');
        return JSON.parse(data);
    } catch (err) {
        return [];
    } finally {
        releaseLock();
    }
}

async function writeTickets(tickets) {
    await acquireLock();
    try {
        fs.writeFileSync(DATA_FILE, JSON.stringify(tickets, null, 2), 'utf8');
        return true;
    } catch (err) {
        return false;
    } finally {
        releaseLock();
    }
}

// CORS headers
function setCorsHeaders(res) {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
}

// Helper to send JSON response
function sendJSON(res, statusCode, data) {
    res.writeHead(statusCode, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(data));
}

// Generate unique ID
function generateId() {
    return crypto.randomBytes(16).toString('hex');
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
                resolve(JSON.parse(body));
            } catch (err) {
                reject(new Error('Invalid JSON'));
            }
        });
        req.on('error', (err) => {
            reject(err);
        });
    });
}

// Parse URL and query parameters
function parseUrl(req) {
    const url = new URL(req.url, `http://${req.headers.host || HOST}`);
    return url;
}

// Extract ID from path pattern /tickets/{id}
function extractTicketId(pathname) {
    const match = pathname.match(/^\/tickets\/([a-f0-9]+)$/);
    return match ? match[1] : null;
}

// Validate ticket fields
function validateTicket(body, isUpdate = false) {
    const errors = [];

    if (!isUpdate) {
        if (!body.subject || typeof body.subject !== 'string' || body.subject.trim() === '') {
            errors.push('subject is required and must be a non-empty string');
        }
        if (!body.description || typeof body.description !== 'string' || body.description.trim() === '') {
            errors.push('description is required and must be a non-empty string');
        }
    } else {
        if (body.subject !== undefined && (typeof body.subject !== 'string' || body.subject.trim() === '')) {
            errors.push('subject must be a non-empty string');
        }
        if (body.description !== undefined && (typeof body.description !== 'string' || body.description.trim() === '')) {
            errors.push('description must be a non-empty string');
        }
    }

    if (body.priority !== undefined && !['low', 'medium', 'high'].includes(body.priority)) {
        errors.push('priority must be one of: low, medium, high');
    }

    if (body.status !== undefined && !['open', 'in_progress', 'resolved'].includes(body.status)) {
        errors.push('status must be one of: open, in_progress, resolved');
    }

    return errors;
}

// Request handlers
async function handleGetTickets(req, res) {
    const url = parseUrl(req);
    const statusFilter = url.searchParams.get('status');
    const priorityFilter = url.searchParams.get('priority');

    const tickets = await readTickets();

    let filtered = tickets;
    if (statusFilter) {
        filtered = filtered.filter(t => t.status === statusFilter);
    }
    if (priorityFilter) {
        filtered = filtered.filter(t => t.priority === priorityFilter);
    }

    sendJSON(res, 200, filtered);
}

async function handlePostTickets(req, res) {
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
        id: generateId(),
        subject: body.subject.trim(),
        description: body.description.trim(),
        priority: body.priority || 'medium',
        status: 'open',
        created_at: now,
        updated_at: now
    };

    const tickets = await readTickets();
    tickets.push(ticket);
    const success = await writeTickets(tickets);

    if (success) {
        sendJSON(res, 201, ticket);
    } else {
        sendJSON(res, 500, { error: 'Failed to save ticket' });
    }
}

async function handleGetTicket(req, res, id) {
    const tickets = await readTickets();
    const ticket = tickets.find(t => t.id === id);

    if (!ticket) {
        sendJSON(res, 404, { error: 'Ticket not found' });
        return;
    }

    sendJSON(res, 200, ticket);
}

async function handlePatchTicket(req, res, id) {
    let body;
    try {
        body = await parseBody(req);
    } catch (err) {
        sendJSON(res, 400, { error: 'Invalid JSON in request body' });
        return;
    }

    const errors = validateTicket(body, true);
    if (errors.length > 0) {
        sendJSON(res, 400, { error: 'Validation failed', details: errors });
        return;
    }

    const tickets = await readTickets();
    const index = tickets.findIndex(t => t.id === id);

    if (index === -1) {
        sendJSON(res, 404, { error: 'Ticket not found' });
        return;
    }

    const now = new Date().toISOString();
    const updatedTicket = { ...tickets[index] };

    if (body.subject !== undefined) updatedTicket.subject = body.subject.trim();
    if (body.description !== undefined) updatedTicket.description = body.description.trim();
    if (body.priority !== undefined) updatedTicket.priority = body.priority;
    if (body.status !== undefined) updatedTicket.status = body.status;
    updatedTicket.updated_at = now;

    tickets[index] = updatedTicket;
    const success = await writeTickets(tickets);

    if (success) {
        sendJSON(res, 200, updatedTicket);
    } else {
        sendJSON(res, 500, { error: 'Failed to update ticket' });
    }
}

async function handleDeleteTicket(req, res, id) {
    const tickets = await readTickets();
    const index = tickets.findIndex(t => t.id === id);

    if (index === -1) {
        sendJSON(res, 404, { error: 'Ticket not found' });
        return;
    }

    tickets.splice(index, 1);
    const success = await writeTickets(tickets);

    if (success) {
        sendJSON(res, 200, { message: 'Ticket deleted successfully' });
    } else {
        sendJSON(res, 500, { error: 'Failed to delete ticket' });
    }
}

async function handleMetrics(req, res) {
    const tickets = await readTickets();

    // Count by status
    const statusCounts = { open: 0, in_progress: 0, resolved: 0 };
    // Count by priority
    const priorityCounts = { low: 0, medium: 0, high: 0 };

    let totalAgeSeconds = 0;
    let openTicketCount = 0;
    const now = new Date();

    tickets.forEach(ticket => {
        // Status counts
        if (statusCounts.hasOwnProperty(ticket.status)) {
            statusCounts[ticket.status]++;
        }

        // Priority counts
        if (priorityCounts.hasOwnProperty(ticket.priority)) {
            priorityCounts[ticket.priority]++;
        }

        // Age of open tickets
        if (ticket.status === 'open') {
            const createdAt = new Date(ticket.created_at);
            const ageSeconds = Math.floor((now - createdAt) / 1000);
            totalAgeSeconds += ageSeconds;
            openTicketCount++;
        }
    });

    const averageAge = openTicketCount > 0 ? Math.floor(totalAgeSeconds / openTicketCount) : 0;

    sendJSON(res, 200, {
        status_counts: statusCounts,
        priority_counts: priorityCounts,
        average_open_age_seconds: averageAge
    });
}

// Main request handler
async function handleRequest(req, res) {
    setCorsHeaders(res);

    // Handle preflight
    if (req.method === 'OPTIONS') {
        res.writeHead(204);
        res.end();
        return;
    }

    const url = parseUrl(req);
    const pathname = url.pathname;
    const ticketId = extractTicketId(pathname);

    try {
        // Route handling
        if (pathname === '/tickets' && req.method === 'GET') {
            await handleGetTickets(req, res);
        } else if (pathname === '/tickets' && req.method === 'POST') {
            await handlePostTickets(req, res);
        } else if (pathname === '/metrics' && req.method === 'GET') {
            await handleMetrics(req, res);
        } else if (ticketId && req.method === 'GET') {
            await handleGetTicket(req, res, ticketId);
        } else if (ticketId && req.method === 'PATCH') {
            await handlePatchTicket(req, res, ticketId);
        } else if (ticketId && req.method === 'DELETE') {
            await handleDeleteTicket(req, res, ticketId);
        } else if (pathname.startsWith('/tickets/') && ticketId && req.method === 'OPTIONS') {
            res.writeHead(204);
            res.end();
        } else if (pathname.startsWith('/tickets/') && !ticketId) {
            sendJSON(res, 400, { error: 'Invalid ticket ID format' });
        } else if (pathname === '/tickets' && !['GET', 'POST', 'OPTIONS'].includes(req.method)) {
            sendJSON(res, 405, { error: 'Method not allowed' });
        } else {
            sendJSON(res, 404, { error: 'Route not found' });
        }
    } catch (err) {
        console.error('Server error:', err);
        sendJSON(res, 500, { error: 'Internal server error' });
    }
}

// Create and start server
const server = http.createServer(handleRequest);

server.listen(PORT, HOST, () => {
    console.log(`Server running at http://${HOST}:${PORT}/`);
});
```
````
