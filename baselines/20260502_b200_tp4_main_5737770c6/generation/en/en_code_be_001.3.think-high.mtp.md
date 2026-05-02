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
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 7.88941
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 318, "total_tokens": 2716, "completion_tokens": 2398, "prompt_tokens_details": null}`
- Prompt tokens: 318
- Completion tokens: 2398
- Total tokens: 2716

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
if (!fs.existsSync(DATA_FILE)) {
    fs.writeFileSync(DATA_FILE, JSON.stringify([]), 'utf8');
}

// Helper to read tickets from file
function readTickets() {
    try {
        const data = fs.readFileSync(DATA_FILE, 'utf8');
        return JSON.parse(data);
    } catch (err) {
        return [];
    }
}

// Helper to write tickets to file
function writeTickets(tickets) {
    fs.writeFileSync(DATA_FILE, JSON.stringify(tickets, null, 2), 'utf8');
}

// Generate unique ID
function generateId() {
    return Date.now().toString(36) + Math.random().toString(36).substr(2, 9);
}

// Validate ticket fields
function validateTicket(body) {
    const errors = [];
    if (!body.subject || typeof body.subject !== 'string') {
        errors.push('subject is required and must be a string');
    }
    if (!body.description || typeof body.description !== 'string') {
        errors.push('description is required and must be a string');
    }
    if (body.priority && !['low', 'medium', 'high'].includes(body.priority)) {
        errors.push('priority must be low, medium, or high');
    }
    if (body.status && !['open', 'in_progress', 'resolved'].includes(body.status)) {
        errors.push('status must be open, in_progress, or resolved');
    }
    return errors;
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

// Parse request body
function parseBody(req) {
    return new Promise((resolve, reject) => {
        let body = '';
        req.on('data', chunk => {
            body += chunk.toString();
            if (body.length > 1e6) {
                reject(new Error('Request body too large'));
            }
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

// Parse URL parameters
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

// Handle GET /tickets
function handleGetTickets(res, params) {
    let tickets = readTickets();

    if (params.status) {
        tickets = tickets.filter(t => t.status === params.status);
    }
    if (params.priority) {
        tickets = tickets.filter(t => t.priority === params.priority);
    }

    sendJson(res, 200, tickets);
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

        const tickets = readTickets();
        const now = new Date().toISOString();

        const ticket = {
            id: generateId(),
            subject: body.subject,
            description: body.description,
            priority: body.priority || 'medium',
            status: 'open',
            created_at: now,
            updated_at: now
        };

        tickets.push(ticket);
        writeTickets(tickets);
        sendJson(res, 201, ticket);
    } catch (err) {
        if (err.message === 'Invalid JSON') {
            sendJson(res, 400, { error: 'Invalid JSON in request body' });
        } else {
            sendJson(res, 500, { error: 'Internal server error' });
        }
    }
}

// Handle GET /tickets/{id}
function handleGetTicket(res, id) {
    const tickets = readTickets();
    const ticket = tickets.find(t => t.id === id);

    if (!ticket) {
        sendJson(res, 404, { error: 'Ticket not found' });
        return;
    }

    sendJson(res, 200, ticket);
}

// Handle PATCH /tickets/{id}
async function handlePatchTicket(req, res, id) {
    try {
        const body = await parseBody(req);
        const tickets = readTickets();
        const index = tickets.findIndex(t => t.id === id);

        if (index === -1) {
            sendJson(res, 404, { error: 'Ticket not found' });
            return;
        }

        const allowedFields = ['subject', 'description', 'priority', 'status'];
        const updates = {};

        for (const field of allowedFields) {
            if (body[field] !== undefined) {
                if (field === 'priority' && !['low', 'medium', 'high'].includes(body[field])) {
                    sendJson(res, 400, { error: 'priority must be low, medium, or high' });
                    return;
                }
                if (field === 'status' && !['open', 'in_progress', 'resolved'].includes(body[field])) {
                    sendJson(res, 400, { error: 'status must be open, in_progress, or resolved' });
                    return;
                }
                updates[field] = body[field];
            }
        }

        if (Object.keys(updates).length === 0) {
            sendJson(res, 400, { error: 'No valid fields to update' });
            return;
        }

        updates.updated_at = new Date().toISOString();
        tickets[index] = { ...tickets[index], ...updates };
        writeTickets(tickets);
        sendJson(res, 200, tickets[index]);
    } catch (err) {
        if (err.message === 'Invalid JSON') {
            sendJson(res, 400, { error: 'Invalid JSON in request body' });
        } else {
            sendJson(res, 500, { error: 'Internal server error' });
        }
    }
}

// Handle DELETE /tickets/{id}
function handleDeleteTicket(res, id) {
    const tickets = readTickets();
    const index = tickets.findIndex(t => t.id === id);

    if (index === -1) {
        sendJson(res, 404, { error: 'Ticket not found' });
        return;
    }

    const deleted = tickets.splice(index, 1)[0];
    writeTickets(tickets);
    sendJson(res, 200, { message: 'Ticket deleted', ticket: deleted });
}

// Handle GET /metrics
function handleMetrics(res) {
    const tickets = readTickets();

    // Count by status
    const statusCounts = {
        open: 0,
        in_progress: 0,
        resolved: 0
    };

    // Count by priority
    const priorityCounts = {
        low: 0,
        medium: 0,
        high: 0
    };

    let totalAge = 0;
    let openTicketCount = 0;
    const now = new Date();

    tickets.forEach(ticket => {
        if (statusCounts.hasOwnProperty(ticket.status)) {
            statusCounts[ticket.status]++;
        }
        if (priorityCounts.hasOwnProperty(ticket.priority)) {
            priorityCounts[ticket.priority]++;
        }

        if (ticket.status === 'open') {
            const created = new Date(ticket.created_at);
            totalAge += (now - created) / 1000;
            openTicketCount++;
        }
    });

    const averageAge = openTicketCount > 0 ? totalAge / openTicketCount : 0;

    sendJson(res, 200, {
        status_counts: statusCounts,
        priority_counts: priorityCounts,
        average_open_ticket_age_seconds: Math.round(averageAge * 100) / 100
    });
}

// Main request handler
const server = http.createServer(async (req, res) => {
    // Handle CORS preflight
    if (req.method === 'OPTIONS') {
        res.writeHead(204, {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': 86400
        });
        res.end();
        return;
    }

    const { pathname, params } = parseUrl(req.url);

    // Route matching
    const getTicketMatch = pathname.match(/^\/tickets\/([a-zA-Z0-9]+)$/);
    const metricsMatch = pathname === '/metrics';
    const ticketsMatch = pathname === '/tickets';

    try {
        if (ticketsMatch) {
            if (req.method === 'GET') {
                handleGetTickets(res, params);
            } else if (req.method === 'POST') {
                await handlePostTickets(req, res);
            } else {
                sendJson(res, 405, { error: 'Method not allowed' });
            }
        } else if (getTicketMatch) {
            const id = getTicketMatch[1];
            if (req.method === 'GET') {
                handleGetTicket(res, id);
            } else if (req.method === 'PATCH') {
                await handlePatchTicket(req, res, id);
            } else if (req.method === 'DELETE') {
                handleDeleteTicket(res, id);
            } else {
                sendJson(res, 405, { error: 'Method not allowed' });
            }
        } else if (metricsMatch) {
            if (req.method === 'GET') {
                handleMetrics(res);
            } else {
                sendJson(res, 405, { error: 'Method not allowed' });
            }
        } else {
            sendJson(res, 404, { error: 'Route not found' });
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
