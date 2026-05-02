# Generation Transcript

- Case: `en_code_be_001`
- Language group: `en`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `1`
- Thinking mode: `non-thinking`
- Thinking strength: `disabled`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 9.153099
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 318, "total_tokens": 2964, "completion_tokens": 2646, "prompt_tokens_details": null}`
- Prompt tokens: 318
- Completion tokens: 2646
- Total tokens: 2964

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
const HOST = '127.0.0.1';
const PORT = 8080;

// Initialize data file if it doesn't exist
function initDataFile() {
    if (!fs.existsSync(DATA_FILE)) {
        fs.writeFileSync(DATA_FILE, JSON.stringify({ tickets: [], nextId: 1 }, null, 2), 'utf8');
    }
}

// Read data from file with retry logic for concurrent access
function readData() {
    try {
        const data = fs.readFileSync(DATA_FILE, 'utf8');
        return JSON.parse(data);
    } catch (err) {
        if (err.code === 'ENOENT') {
            initDataFile();
            return readData();
        }
        throw err;
    }
}

// Write data to atomically to prevent corruption
function writeData(data) {
    const tmpFile = DATA_FILE + '.tmp';
    fs.writeFileSync(tmpFile, JSON.stringify(data, null, 2), 'utf8');
    fs.renameSync(tmpFile, DATA_FILE);
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
        errors.push('priority must be low, medium, or high');
    }
    if (body.status && !['open', 'in_progress', 'resolved'].includes(body.status)) {
        errors.push('status must be open, in_progress, or resolved');
    }
    return errors;
}

// Generate current timestamp
function now() {
    return new Date().toISOString();
}

// Parse JSON body
function parseBody(req) {
    return new Promise((resolve, reject) => {
        let body = '';
        req.on('data', chunk => {
            body += chunk.toString();
            if (body.length > 1e6) {
                req.destroy();
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

// Extract ID from URL path
function extractId(url) {
    const match = url.match(/^\/tickets\/(\d+)$/);
    return match ? parseInt(match[1], 10) : null;
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

// Handle GET /tickets
function handleGetTickets(req, res) {
    const url = new URL(req.url, `http://${HOST}:${PORT}`);
    const statusFilter = url.searchParams.get('status');
    const priorityFilter = url.searchParams.get('priority');

    const data = readData();
    let tickets = data.tickets;

    if (statusFilter) {
        tickets = tickets.filter(t => t.status === statusFilter);
    }
    if (priorityFilter) {
        tickets = tickets.filter(t => t.priority === priorityFilter);
    }

    sendJson(res, 200, { tickets });
}

// Handle POST /tickets
async function handlePostTickets(req, res) {
    try {
        const body = await parseBody(req);
        const errors = validateTicket(body);

        if (errors.length > 0) {
            sendJson(res, 400, { error: 'Validation failed', details: errors });
            return;
        }

        const data = readData();
        const ticket = {
            id: data.nextId,
            subject: body.subject.trim(),
            description: body.description.trim(),
            priority: body.priority || 'low',
            status: body.status || 'open',
            created_at: now(),
            updated_at: now()
        };

        data.tickets.push(ticket);
        data.nextId++;
        writeData(data);

        sendJson(res, 201, { ticket });
    } catch (err) {
        if (err.message === 'Invalid JSON' || err.message === 'Request body too large') {
            sendJson(res, 400, { error: err.message });
        } else {
            sendJson(res, 500, { error: 'Internal server error' });
        }
    }
}

// Handle GET /tickets/:id
function handleGetTicket(req, res) {
    const id = extractId(req.url);
    if (!id) {
        sendJson(res, 400, { error: 'Invalid ticket ID' });
        return;
    }

    const data = readData();
    const ticket = data.tickets.find(t => t.id === id);

    if (!ticket) {
        sendJson(res, 404, { error: 'Ticket not found' });
        return;
    }

    sendJson(res, 200, { ticket });
}

// Handle PATCH /tickets/:id
async function handlePatchTicket(req, res) {
    const id = extractId(req.url);
    if (!id) {
        sendJson(res, 400, { error: 'Invalid ticket ID' });
        return;
    }

    try {
        const body = await parseBody(req);
        const allowedFields = ['subject', 'description', 'priority', 'status'];
        const updates = {};

        for (const field of allowedFields) {
            if (body[field] !== undefined) {
                if (field === 'subject' || field === 'description') {
                    if (typeof body[field] !== 'string' || body[field].trim() === '') {
                        sendJson(res, 400, { error: `${field} must be a non-empty string` });
                        return;
                    }
                    updates[field] = body[field].trim();
                } else if (field === 'priority') {
                    if (!['low', 'medium', 'high'].includes(body[field])) {
                        sendJson(res, 400, { error: 'priority must be low, medium, or high' });
                        return;
                    }
                    updates[field] = body[field];
                } else if (field === 'status') {
                    if (!['open', 'in_progress', 'resolved'].includes(body[field])) {
                        sendJson(res, 400, { error: 'status must be open, in_progress, or resolved' });
                        return;
                    }
                    updates[field] = body[field];
                }
            }
        }

        if (Object.keys(updates).length === 0) {
            sendJson(res, 400, { error: 'No valid fields to update' });
            return;
        }

        const data = readData();
        const index = data.tickets.findIndex(t => t.id === id);

        if (index === -1) {
            sendJson(res, 404, { error: 'Ticket not found' });
            return;
        }

        data.tickets[index] = { ...data.tickets[index], ...updates, updated_at: now() };
        writeData(data);

        sendJson(res, 200, { ticket: data.tickets[index] });
    } catch (err) {
        if (err.message === 'Invalid JSON' || err.message === 'Request body too large') {
            sendJson(res, 400, { error: err.message });
        } else {
            sendJson(res, 500, { error: 'Internal server error' });
        }
    }
}

// Handle DELETE /tickets/:id
function handleDeleteTicket(req, res) {
    const id = extractId(req.url);
    if (!id) {
        sendJson(res, 400, { error: 'Invalid ticket ID' });
        return;
    }

    const data = readData();
    const index = data.tickets.findIndex(t => t.id === id);

    if (index === -1) {
        sendJson(res, 404, { error: 'Ticket not found' });
        return;
    }

    data.tickets.splice(index, 1);
    writeData(data);

    sendJson(res, 200, { message: 'Ticket deleted successfully' });
}

// Handle GET /metrics
function handleGetMetrics(req, res) {
    const data = readData();
    const tickets = data.tickets;

    // Count by status
    const statusCounts = { open: 0, in_progress: 0, resolved: 0 };
    // Count by priority
    const priorityCounts = { low: 0, medium: 0, high: 0 };
    // Average age of open tickets in seconds
    let totalAgeMs = 0;
    let openTicketCount = 0;
    const now = Date.now();

    for (const ticket of tickets) {
        statusCounts[ticket.status] = (statusCounts[ticket.status] || 0) + 1;
        priorityCounts[ticket.priority] = (priorityCounts[ticket.priority] || 0) + 1;

        if (ticket.status === 'open') {
            const createdAt = new Date(ticket.created_at).getTime();
            totalAgeMs += now - createdAt;
            openTicketCount++;
        }
    }

    const averageAgeSeconds = openTicketCount > 0 ? Math.floor(totalAgeMs / openTicketCount / 1000) : 0;

    sendJson(res, 200, {
        status_counts: statusCounts,
        priority_counts: priorityCounts,
        average_age_open_seconds: averageAgeSeconds
    });
}

// Main request handler
async function handleRequest(req, res) {
    const url = new URL(req.url, `http://${HOST}:${PORT}`);
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

    try {
        // Route handling
        if (url.pathname === '/tickets') {
            if (method === 'GET') {
                handleGetTickets(req, res);
            } else if (method === 'POST') {
                await handlePostTickets(req, res);
            } else {
                sendJson(res, 405, { error: 'Method not allowed' });
            }
        } else if (url.pathname.match(/^\/tickets\/\d+$/)) {
            if (method === 'GET') {
                handleGetTicket(req, res);
            } else if (method === 'PATCH') {
                await handlePatchTicket(req, res);
            } else if (method === 'DELETE') {
                handleDeleteTicket(req, res);
            } else {
                sendJson(res, 405, { error: 'Method not allowed' });
            }
        } else if (url.pathname === '/metrics' && method === 'GET') {
            handleGetMetrics(req, res);
        } else {
            sendJson(res, 404, { error: 'Route not found' });
        }
    } catch (err) {
        console.error('Server error:', err);
        sendJson(res, 500, { error: 'Internal server error' });
    }
}

// Start server
initDataFile();
const server = http.createServer(handleRequest);

server.listen(PORT, HOST, () => {
    console.log(`Server running at http://${HOST}:${PORT}/`);
});
```
````
