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
- Elapsed seconds: 40.923695
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 318, "total_tokens": 2925, "completion_tokens": 2607, "prompt_tokens_details": null}`
- Prompt tokens: 318
- Completion tokens: 2607
- Total tokens: 2925

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

const DATA_FILE = path.join(__dirname, 'tickets.json');
const HOST = '127.0.0.1';
const PORT = 8080;

// Initialize data file if it doesn't exist
function initDataFile() {
    if (!fs.existsSync(DATA_FILE)) {
        fs.writeFileSync(DATA_FILE, JSON.stringify({ tickets: [], nextId: 1 }), 'utf8');
    }
}

// Read data from file
function readData() {
    try {
        const raw = fs.readFileSync(DATA_FILE, 'utf8');
        return JSON.parse(raw);
    } catch (err) {
        return { tickets: [], nextId: 1 };
    }
}

// Write data to file
function writeData(data) {
    try {
        fs.writeFileSync(DATA_FILE, JSON.stringify(data, null, 2), 'utf8');
        return true;
    } catch (err) {
        return false;
    }
}

// Set CORS headers
function setCORSHeaders(res) {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
}

// Send JSON response
function sendJSON(res, statusCode, data) {
    res.writeHead(statusCode, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(data));
}

// Send error response
function sendError(res, statusCode, message) {
    sendJSON(res, statusCode, { error: message });
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
                resolve(body ? JSON.parse(body) : {});
            } catch (err) {
                reject(new Error('Invalid JSON'));
            }
        });
        req.on('error', reject);
    });
}

// Validate ticket fields
function validateTicket(ticket, isUpdate = false) {
    const errors = [];

    if (!isUpdate) {
        if (!ticket.subject || typeof ticket.subject !== 'string' || ticket.subject.trim() === '') {
            errors.push('subject is required and must be a non-empty string');
        }
        if (!ticket.description || typeof ticket.description !== 'string' || ticket.description.trim() === '') {
            errors.push('description is required and must be a non-empty string');
        }
        if (!ticket.priority || !['low', 'medium', 'high'].includes(ticket.priority)) {
            errors.push('priority must be one of: low, medium, high');
        }
        if (!ticket.status || !['open', 'in_progress', 'resolved'].includes(ticket.status)) {
            errors.push('status must be one of: open, in_progress, resolved');
        }
    } else {
        if (ticket.subject !== undefined && (typeof ticket.subject !== 'string' || ticket.subject.trim() === '')) {
            errors.push('subject must be a non-empty string');
        }
        if (ticket.description !== undefined && (typeof ticket.description !== 'string' || ticket.description.trim() === '')) {
            errors.push('description must be a non-empty string');
        }
        if (ticket.priority !== undefined && !['low', 'medium', 'high'].includes(ticket.priority)) {
            errors.push('priority must be one of: low, medium, high');
        }
        if (ticket.status !== undefined && !['open', 'in_progress', 'resolved'].includes(ticket.status)) {
            errors.push('status must be one of: open, in_progress, resolved');
        }
    }

    return errors;
}

// Parse URL path
function parsePath(reqUrl) {
    const parsed = new URL(reqUrl, `http://${HOST}:${PORT}`);
    const pathParts = parsed.pathname.split('/').filter(p => p);
    const query = Object.fromEntries(parsed.searchParams);
    return { pathParts, query };
}

// Handle GET /tickets
function handleGetTickets(res, query) {
    const data = readData();
    let tickets = data.tickets;

    if (query.status) {
        tickets = tickets.filter(t => t.status === query.status);
    }
    if (query.priority) {
        tickets = tickets.filter(t => t.priority === query.priority);
    }

    sendJSON(res, 200, tickets);
}

// Handle POST /tickets
async function handlePostTickets(req, res) {
    try {
        const body = await parseBody(req);
        const errors = validateTicket(body);

        if (errors.length > 0) {
            sendError(res, 400, errors.join(', '));
            return;
        }

        const data = readData();
        const now = new Date().toISOString();

        const ticket = {
            id: data.nextId,
            subject: body.subject.trim(),
            description: body.description.trim(),
            priority: body.priority,
            status: body.status,
            created_at: now,
            updated_at: now
        };

        data.tickets.push(ticket);
        data.nextId++;

        if (!writeData(data)) {
            sendError(res, 500, 'Failed to save data');
            return;
        }

        sendJSON(res, 201, ticket);
    } catch (err) {
        if (err.message === 'Invalid JSON') {
            sendError(res, 400, 'Invalid JSON in request body');
        } else {
            sendError(res, 500, 'Internal server error');
        }
    }
}

// Handle GET /tickets/{id}
function handleGetTicket(res, id) {
    const data = readData();
    const ticket = data.tickets.find(t => t.id === id);

    if (!ticket) {
        sendError(res, 404, 'Ticket not found');
        return;
    }

    sendJSON(res, 200, ticket);
}

// Handle PATCH /tickets/{id}
async function handlePatchTicket(req, res, id) {
    try {
        const body = await parseBody(req);
        const data = readData();
        const index = data.tickets.findIndex(t => t.id === id);

        if (index === -1) {
            sendError(res, 404, 'Ticket not found');
            return;
        }

        const errors = validateTicket(body, true);
        if (errors.length > 0) {
            sendError(res, 400, errors.join(', '));
            return;
        }

        const ticket = data.tickets[index];

        if (body.subject !== undefined) ticket.subject = body.subject.trim();
        if (body.description !== undefined) ticket.description = body.description.trim();
        if (body.priority !== undefined) ticket.priority = body.priority;
        if (body.status !== undefined) ticket.status = body.status;
        ticket.updated_at = new Date().toISOString();

        if (!writeData(data)) {
            sendError(res, 500, 'Failed to save data');
            return;
        }

        sendJSON(res, 200, ticket);
    } catch (err) {
        if (err.message === 'Invalid JSON') {
            sendError(res, 400, 'Invalid JSON in request body');
        } else {
            sendError(res, 500, 'Internal server error');
        }
    }
}

// Handle DELETE /tickets/{id}
function handleDeleteTicket(res, id) {
    const data = readData();
    const index = data.tickets.findIndex(t => t.id === id);

    if (index === -1) {
        sendError(res, 404, 'Ticket not found');
        return;
    }

    data.tickets.splice(index, 1);

    if (!writeData(data)) {
        sendError(res, 500, 'Failed to save data');
        return;
    }

    sendJSON(res, 200, { message: 'Ticket deleted successfully' });
}

// Handle GET /metrics
function handleGetMetrics(res) {
    const data = readData();
    const tickets = data.tickets;
    const now = new Date();

    // Count by status
    const statusCounts = { open: 0, in_progress: 0, resolved: 0 };
    tickets.forEach(t => {
        if (statusCounts[t.status] !== undefined) {
            statusCounts[t.status]++;
        }
    });

    // Count by priority
    const priorityCounts = { low: 0, medium: 0, high: 0 };
    tickets.forEach(t => {
        if (priorityCounts[t.priority] !== undefined) {
            priorityCounts[t.priority]++;
        }
    });

    // Average age of open tickets in seconds
    const openTickets = tickets.filter(t => t.status === 'open');
    let averageAgeSeconds = 0;
    if (openTickets.length > 0) {
        const totalAgeMs = openTickets.reduce((sum, t) => {
            const created = new Date(t.created_at);
            return sum + (now - created);
        }, 0);
        averageAgeSeconds = Math.round(totalAgeMs / openTickets.length / 1000);
    }

    sendJSON(res, 200, {
        byStatus: statusCounts,
        byPriority: priorityCounts,
        averageOpenAgeSeconds: averageAgeSeconds,
        total: tickets.length
    });
}

// Handle OPTIONS request
function handleOptions(res) {
    res.writeHead(204);
    res.end();
}

// Main request handler
function handleRequest(req, res) {
    setCORSHeaders(res);

    if (req.method === 'OPTIONS') {
        handleOptions(res);
        return;
    }

    const { pathParts, query } = parsePath(req.url);

    try {
        // Route: GET /tickets or POST /tickets
        if (pathParts.length === 1 && pathParts[0] === 'tickets') {
            if (req.method === 'GET') {
                handleGetTickets(res, query);
            } else if (req.method === 'POST') {
                handlePostTickets(req, res);
            } else {
                sendError(res, 405, 'Method not allowed');
            }
            return;
        }

        // Route: GET /tickets/{id} or PATCH /tickets/{id} or DELETE /tickets/{id}
        if (pathParts.length === 2 && pathParts[0] === 'tickets') {
            const id = parseInt(pathParts[1]);

            if (isNaN(id)) {
                sendError(res, 400, 'Invalid ticket ID');
                return;
            }

            if (req.method === 'GET') {
                handleGetTicket(res, id);
            } else if (req.method === 'PATCH') {
                handlePatchTicket(req, res, id);
            } else if (req.method === 'DELETE') {
                handleDeleteTicket(res, id);
            } else {
                sendError(res, 405, 'Method not allowed');
            }
            return;
        }

        // Route: GET /metrics
        if (pathParts.length === 1 && pathParts[0] === 'metrics') {
            if (req.method === 'GET') {
                handleGetMetrics(res);
            } else {
                sendError(res, 405, 'Method not allowed');
            }
            return;
        }

        // Unknown route
        sendError(res, 404, 'Route not found');
    } catch (err) {
        sendError(res, 500, 'Internal server error');
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
