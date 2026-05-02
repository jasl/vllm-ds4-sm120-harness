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
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 8.57912
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 318, "total_tokens": 2841, "completion_tokens": 2523, "prompt_tokens_details": null}`
- Prompt tokens: 318
- Completion tokens: 2523
- Total tokens: 2841

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

const HOST = '127.0.0.1';
const PORT = 8080;
const DATA_FILE = path.join(__dirname, 'tickets.json');

// Initialize data file if it doesn't exist
function initDataFile() {
    if (!fs.existsSync(DATA_FILE)) {
        fs.writeFileSync(DATA_FILE, '[]', 'utf8');
    }
}

// Read tickets from file
function readTickets() {
    try {
        const data = fs.readFileSync(DATA_FILE, 'utf8');
        return JSON.parse(data);
    } catch (error) {
        return [];
    }
}

// Write tickets to file
function writeTickets(tickets) {
    fs.writeFileSync(DATA_FILE, JSON.stringify(tickets, null, 2), 'utf8');
}

// Generate unique ID
function generateId() {
    return Date.now().toString(36) + Math.random().toString(36).substr(2, 5);
}

// Validate ticket fields
function validateTicket(body, isUpdate = false) {
    const errors = [];
    const validPriorities = ['low', 'medium', 'high'];
    const validStatuses = ['open', 'in_progress', 'resolved'];

    if (!isUpdate) {
        if (!body.subject || typeof body.subject !== 'string' || body.subject.trim() === '') {
            errors.push('subject is required and must be a non-empty string');
        }
        if (!body.description || typeof body.description !== 'string' || body.description.trim() === '') {
            errors.push('description is required and must be a non-empty string');
        }
        if (!body.priority || !validPriorities.includes(body.priority)) {
            errors.push('priority must be one of: low, medium, high');
        }
        if (body.status && !validStatuses.includes(body.status)) {
            errors.push('status must be one of: open, in_progress, resolved');
        }
    } else {
        if (body.subject !== undefined && (typeof body.subject !== 'string' || body.subject.trim() === '')) {
            errors.push('subject must be a non-empty string');
        }
        if (body.description !== undefined && (typeof body.description !== 'string' || body.description.trim() === '')) {
            errors.push('description must be a non-empty string');
        }
        if (body.priority !== undefined && !validPriorities.includes(body.priority)) {
            errors.push('priority must be one of: low, medium, high');
        }
        if (body.status !== undefined && !validStatuses.includes(body.status)) {
            errors.push('status must be one of: open, in_progress, resolved');
        }
    }

    return errors;
}

// Parse request body
function parseBody(req) {
    return new Promise((resolve, reject) => {
        let body = '';
        req.on('data', chunk => {
            body += chunk.toString();
        });
        req.on('end', () => {
            try {
                resolve(body ? JSON.parse(body) : {});
            } catch (error) {
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

// Parse URL path
function parsePath(url) {
    const parsed = new URL(url, `http://${HOST}:${PORT}`);
    const pathParts = parsed.pathname.split('/').filter(Boolean);
    const queryParams = {};
    parsed.searchParams.forEach((value, key) => {
        queryParams[key] = value;
    });
    return { pathParts, queryParams };
}

// Handle GET /tickets
function handleGetTickets(queryParams, res) {
    const tickets = readTickets();
    let filtered = tickets;

    if (queryParams.status) {
        filtered = filtered.filter(t => t.status === queryParams.status);
    }
    if (queryParams.priority) {
        filtered = filtered.filter(t => t.priority === queryParams.priority);
    }

    sendJson(res, 200, filtered);
}

// Handle POST /tickets
async function handlePostTickets(req, res) {
    try {
        const body = await parseBody(req);
        const errors = validateTicket(body);

        if (errors.length > 0) {
            return sendJson(res, 400, { error: 'Validation failed', details: errors });
        }

        const now = new Date().toISOString();
        const newTicket = {
            id: generateId(),
            subject: body.subject.trim(),
            description: body.description.trim(),
            priority: body.priority,
            status: body.status || 'open',
            created_at: now,
            updated_at: now
        };

        const tickets = readTickets();
        tickets.push(newTicket);
        writeTickets(tickets);

        sendJson(res, 201, newTicket);
    } catch (error) {
        sendJson(res, 400, { error: error.message });
    }
}

// Handle GET /tickets/{id}
function handleGetTicket(id, res) {
    const tickets = readTickets();
    const ticket = tickets.find(t => t.id === id);

    if (!ticket) {
        return sendJson(res, 404, { error: 'Ticket not found' });
    }

    sendJson(res, 200, ticket);
}

// Handle PATCH /tickets/{id}
async function handlePatchTicket(id, req, res) {
    try {
        const body = await parseBody(req);
        const errors = validateTicket(body, true);

        if (errors.length > 0) {
            return sendJson(res, 400, { error: 'Validation failed', details: errors });
        }

        const tickets = readTickets();
        const index = tickets.findIndex(t => t.id === id);

        if (index === -1) {
            return sendJson(res, 404, { error: 'Ticket not found' });
        }

        const now = new Date().toISOString();
        const updatedTicket = { ...tickets[index] };

        if (body.subject !== undefined) updatedTicket.subject = body.subject.trim();
        if (body.description !== undefined) updatedTicket.description = body.description.trim();
        if (body.priority !== undefined) updatedTicket.priority = body.priority;
        if (body.status !== undefined) updatedTicket.status = body.status;
        updatedTicket.updated_at = now;

        tickets[index] = updatedTicket;
        writeTickets(tickets);

        sendJson(res, 200, updatedTicket);
    } catch (error) {
        sendJson(res, 400, { error: error.message });
    }
}

// Handle DELETE /tickets/{id}
function handleDeleteTicket(id, res) {
    const tickets = readTickets();
    const index = tickets.findIndex(t => t.id === id);

    if (index === -1) {
        return sendJson(res, 404, { error: 'Ticket not found' });
    }

    tickets.splice(index, 1);
    writeTickets(tickets);

    sendJson(res, 200, { message: 'Ticket deleted successfully' });
}

// Handle GET /metrics
function handleGetMetrics(res) {
    const tickets = readTickets();
    const now = new Date();

    const statusCounts = { open: 0, in_progress: 0, resolved: 0 };
    const priorityCounts = { low: 0, medium: 0, high: 0 };
    let totalAgeSeconds = 0;
    let openTicketCount = 0;

    tickets.forEach(ticket => {
        // Count by status
        if (statusCounts.hasOwnProperty(ticket.status)) {
            statusCounts[ticket.status]++;
        }

        // Count by priority
        if (priorityCounts.hasOwnProperty(ticket.priority)) {
            priorityCounts[ticket.priority]++;
        }

        // Calculate age for open tickets
        if (ticket.status === 'open') {
            const createdAt = new Date(ticket.created_at);
            const ageSeconds = (now - createdAt) / 1000;
            totalAgeSeconds += ageSeconds;
            openTicketCount++;
        }
    });

    const metrics = {
        status_counts: statusCounts,
        priority_counts: priorityCounts,
        average_open_age_seconds: openTicketCount > 0 ? Math.round(totalAgeSeconds / openTicketCount) : 0
    };

    sendJson(res, 200, metrics);
}

// Handle OPTIONS (CORS preflight)
function handleOptions(res) {
    res.writeHead(204, {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type'
    });
    res.end();
}

// Main request handler
async function handleRequest(req, res) {
    const { pathParts, queryParams } = parsePath(req.url);
    const method = req.method.toUpperCase();

    // Handle CORS preflight
    if (method === 'OPTIONS') {
        return handleOptions(res);
    }

    // Route handling
    try {
        if (pathParts.length === 0) {
            // Root endpoint
            if (method === 'GET') {
                return sendJson(res, 200, { message: 'Help Desk Ticket API', version: '1.0.0' });
            }
            return sendJson(res, 405, { error: 'Method not allowed' });
        }

        const resource = pathParts[0];

        switch (resource) {
            case 'tickets': {
                if (pathParts.length === 1) {
                    // /tickets
                    if (method === 'GET') {
                        return handleGetTickets(queryParams, res);
                    } else if (method === 'POST') {
                        return await handlePostTickets(req, res);
                    }
                    return sendJson(res, 405, { error: 'Method not allowed' });
                } else if (pathParts.length === 2) {
                    // /tickets/{id}
                    const ticketId = pathParts[1];
                    if (method === 'GET') {
                        return handleGetTicket(ticketId, res);
                    } else if (method === 'PATCH') {
                        return await handlePatchTicket(ticketId, req, res);
                    } else if (method === 'DELETE') {
                        return handleDeleteTicket(ticketId, res);
                    }
                    return sendJson(res, 405, { error: 'Method not allowed' });
                }
                return sendJson(res, 404, { error: 'Not found' });
            }

            case 'metrics': {
                if (pathParts.length === 1 && method === 'GET') {
                    return handleGetMetrics(res);
                }
                return sendJson(res, 405, { error: 'Method not allowed' });
            }

            default:
                return sendJson(res, 404, { error: 'Route not found' });
        }
    } catch (error) {
        console.error('Server error:', error);
        return sendJson(res, 500, { error: 'Internal server error' });
    }
}

// Create and start server
initDataFile();

const server = http.createServer(handleRequest);

server.listen(PORT, HOST, () => {
    console.log(`Help Desk API running at http://${HOST}:${PORT}`);
});
```
````
