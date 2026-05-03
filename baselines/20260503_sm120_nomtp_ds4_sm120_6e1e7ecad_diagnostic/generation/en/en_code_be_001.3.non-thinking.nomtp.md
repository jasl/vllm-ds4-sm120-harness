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
- Elapsed seconds: 46.450184
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 318, "total_tokens": 3273, "completion_tokens": 2955, "prompt_tokens_details": null}`
- Prompt tokens: 318
- Completion tokens: 2955
- Total tokens: 3273

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
const url = require('url');

const PORT = process.env.PORT || 8080;
const HOST = '127.0.0.1';
const DATA_FILE = path.join(__dirname, 'tickets.json');

// File locking mechanism
let lockPromise = Promise.resolve();

function acquireLock() {
    let resolve;
    const promise = new Promise(r => resolve = r);
    const previous = lockPromise;
    lockPromise = promise;
    return previous;
}

function releaseLock() {
    lockPromise = lockPromise.then(() => {});
}

// Read tickets from file
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

// Write tickets to file
async function writeTickets(tickets) {
    await fs.promises.writeFile(DATA_FILE, JSON.stringify(tickets, null, 2), 'utf8');
}

// Generate unique ID
function generateId() {
    return Date.now().toString(36) + Math.random().toString(36).substr(2, 9);
}

// Validate ticket data
function validateTicket(data) {
    const errors = [];

    if (!data.subject || typeof data.subject !== 'string' || data.subject.trim().length === 0) {
        errors.push('subject is required and must be a non-empty string');
    }

    if (!data.description || typeof data.description !== 'string' || data.description.trim().length === 0) {
        errors.push('description is required and must be a non-empty string');
    }

    if (data.priority && !['low', 'medium', 'high'].includes(data.priority)) {
        errors.push('priority must be one of: low, medium, high');
    }

    if (data.status && !['open', 'in_progress', 'resolved'].includes(data.status)) {
        errors.push('status must be one of: open, in_progress, resolved');
    }

    return errors;
}

// Validate partial update data
function validatePartialUpdate(data) {
    const errors = [];

    if (data.subject !== undefined && (typeof data.subject !== 'string' || data.subject.trim().length === 0)) {
        errors.push('subject must be a non-empty string');
    }

    if (data.description !== undefined && (typeof data.description !== 'string' || data.description.trim().length === 0)) {
        errors.push('description must be a non-empty string');
    }

    if (data.priority !== undefined && !['low', 'medium', 'high'].includes(data.priority)) {
        errors.push('priority must be one of: low, medium, high');
    }

    if (data.status !== undefined && !['open', 'in_progress', 'resolved'].includes(data.status)) {
        errors.push('status must be one of: open, in_progress, resolved');
    }

    return errors;
}

// Send JSON response
function sendJSON(res, statusCode, data) {
    res.writeHead(statusCode, {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type'
    });
    res.end(JSON.stringify(data));
}

// Parse request body
function parseBody(req) {
    return new Promise((resolve, reject) => {
        let body = '';
        req.on('data', chunk => {
            body += chunk.toString();
            if (body.length > 1024 * 1024) {
                reject(new Error('Request body too large'));
            }
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

// Parse URL parameters
function parseQueryParams(reqUrl) {
    const parsed = url.parse(reqUrl, true);
    return parsed.query;
}

// Parse URL path
function parsePath(reqUrl) {
    const parsed = url.parse(reqUrl);
    return parsed.pathname;
}

// Get ticket by ID
function getTicketById(tickets, id) {
    return tickets.find(t => t.id === id);
}

// Calculate metrics
function calculateMetrics(tickets) {
    const metrics = {
        status: {
            open: 0,
            in_progress: 0,
            resolved: 0
        },
        priority: {
            low: 0,
            medium: 0,
            high: 0
        },
        average_age_open_seconds: 0
    };

    const now = Date.now();
    let totalAge = 0;
    let openCount = 0;

    for (const ticket of tickets) {
        // Count by status
        if (metrics.status[ticket.status] !== undefined) {
            metrics.status[ticket.status]++;
        }

        // Count by priority
        if (metrics.priority[ticket.priority] !== undefined) {
            metrics.priority[ticket.priority]++;
        }

        // Calculate age for open tickets
        if (ticket.status === 'open') {
            const created = new Date(ticket.created_at).getTime();
            totalAge += (now - created) / 1000;
            openCount++;
        }
    }

    if (openCount > 0) {
        metrics.average_age_open_seconds = Math.round(totalAge / openCount);
    }

    return metrics;
}

// Handle GET /tickets
async function handleGetTickets(req, res) {
    try {
        await acquireLock();
        const tickets = await readTickets();
        const query = parseQueryParams(req.url);
        let filtered = tickets;

        if (query.status) {
            filtered = filtered.filter(t => t.status === query.status);
        }

        if (query.priority) {
            filtered = filtered.filter(t => t.priority === query.priority);
        }

        sendJSON(res, 200, filtered);
    } catch (err) {
        sendJSON(res, 500, { error: 'Internal server error' });
    } finally {
        releaseLock();
    }
}

// Handle POST /tickets
async function handlePostTickets(req, res) {
    try {
        const body = await parseBody(req);
        const errors = validateTicket(body);

        if (errors.length > 0) {
            sendJSON(res, 400, { error: 'Validation failed', details: errors });
            return;
        }

        await acquireLock();
        const tickets = await readTickets();

        const now = new Date().toISOString();
        const ticket = {
            id: generateId(),
            subject: body.subject.trim(),
            description: body.description.trim(),
            priority: body.priority || 'medium',
            status: body.status || 'open',
            created_at: now,
            updated_at: now
        };

        tickets.push(ticket);
        await writeTickets(tickets);

        sendJSON(res, 201, ticket);
    } catch (err) {
        if (err.message === 'Invalid JSON' || err.message === 'Request body too large') {
            sendJSON(res, 400, { error: err.message });
        } else {
            sendJSON(res, 500, { error: 'Internal server error' });
        }
    } finally {
        releaseLock();
    }
}

// Handle GET /tickets/{id}
async function handleGetTicket(req, res, id) {
    try {
        await acquireLock();
        const tickets = await readTickets();
        const ticket = getTicketById(tickets, id);

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
}

// Handle PATCH /tickets/{id}
async function handlePatchTicket(req, res, id) {
    try {
        const body = await parseBody(req);
        const errors = validatePartialUpdate(body);

        if (errors.length > 0) {
            sendJSON(res, 400, { error: 'Validation failed', details: errors });
            return;
        }

        if (Object.keys(body).length === 0) {
            sendJSON(res, 400, { error: 'No fields to update' });
            return;
        }

        // Check if any valid fields are being updated
        const validFields = ['subject', 'description', 'priority', 'status'];
        const hasValidField = Object.keys(body).some(key => validFields.includes(key));

        if (!hasValidField) {
            sendJSON(res, 400, { error: 'No valid fields to update' });
            return;
        }

        await acquireLock();
        const tickets = await readTickets();
        const index = tickets.findIndex(t => t.id === id);

        if (index === -1) {
            sendJSON(res, 404, { error: 'Ticket not found' });
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

        sendJSON(res, 200, ticket);
    } catch (err) {
        if (err.message === 'Invalid JSON' || err.message === 'Request body too large') {
            sendJSON(res, 400, { error: err.message });
        } else {
            sendJSON(res, 500, { error: 'Internal server error' });
        }
    } finally {
        releaseLock();
    }
}

// Handle DELETE /tickets/{id}
async function handleDeleteTicket(req, res, id) {
    try {
        await acquireLock();
        let tickets = await readTickets();
        const index = tickets.findIndex(t => t.id === id);

        if (index === -1) {
            sendJSON(res, 404, { error: 'Ticket not found' });
            return;
        }

        tickets.splice(index, 1);
        await writeTickets(tickets);

        sendJSON(res, 200, { message: 'Ticket deleted successfully' });
    } catch (err) {
        sendJSON(res, 500, { error: 'Internal server error' });
    } finally {
        releaseLock();
    }
}

// Handle GET /metrics
async function handleGetMetrics(req, res) {
    try {
        await acquireLock();
        const tickets = await readTickets();
        const metrics = calculateMetrics(tickets);

        sendJSON(res, 200, metrics);
    } catch (err) {
        sendJSON(res, 500, { error: 'Internal server error' });
    } finally {
        releaseLock();
    }
}

// Handle OPTIONS request
function handleOptions(req, res) {
    res.writeHead(204, {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Max-Age': '86400'
    });
    res.end();
}

// Main request handler
async function handleRequest(req, res) {
    const method = req.method;
    const pathname = parsePath(req.url);

    // CORS preflight
    if (method === 'OPTIONS') {
        handleOptions(req, res);
        return;
    }

    // Route matching
    try {
        if (pathname === '/tickets' && method === 'GET') {
            await handleGetTickets(req, res);
        } else if (pathname === '/tickets' && method === 'POST') {
            await handlePostTickets(req, res);
        } else if (pathname === '/metrics' && method === 'GET') {
            await handleGetMetrics(req, res);
        } else if (pathname.startsWith('/tickets/')) {
            const id = pathname.substring('/tickets/'.length);

            if (!id || id.length === 0) {
                sendJSON(res, 400, { error: 'Invalid ticket ID' });
                return;
            }

            switch (method) {
                case 'GET':
                    await handleGetTicket(req, res, id);
                    break;
                case 'PATCH':
                    await handlePatchTicket(req, res, id);
                    break;
                case 'DELETE':
                    await handleDeleteTicket(req, res, id);
                    break;
                default:
                    sendJSON(res, 405, { error: 'Method not allowed' });
            }
        } else {
            sendJSON(res, 404, { error: 'Not found' });
        }
    } catch (err) {
        console.error(err);
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
