# Generation Transcript

- Case: `en_code_be_001`
- Language group: `en`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `1`
- Thinking mode: `think-max`
- Thinking strength: `max`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 8.816238
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

const HOST = '127.0.0.1';
const PORT = 8080;
const DATA_FILE = path.join(__dirname, 'tickets.json');

// Initialize empty tickets array if file doesn't exist
function initializeDataFile() {
    if (!fs.existsSync(DATA_FILE)) {
        fs.writeFileSync(DATA_FILE, JSON.stringify([]));
    }
}

// Read tickets from file
function readTickets() {
    try {
        const data = fs.readFileSync(DATA_FILE, 'utf8');
        return JSON.parse(data);
    } catch (err) {
        return [];
    }
}

// Write tickets to file
function writeTickets(tickets) {
    fs.writeFileSync(DATA_FILE, JSON.stringify(tickets, null, 2));
}

// Generate unique ID
function generateId() {
    return Date.now().toString(36) + Math.random().toString(36).substr(2, 9);
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
        if (!body.priority || !['low', 'medium', 'high'].includes(body.priority)) {
            errors.push('priority must be one of: low, medium, high');
        }
        if (!body.status || !['open', 'in_progress', 'resolved'].includes(body.status)) {
            errors.push('status must be one of: open, in_progress, resolved');
        }
    } else {
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
    }

    return errors;
}

// Parse request body
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
                const parsed = body ? JSON.parse(body) : {};
                resolve(parsed);
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

// Handle GET /tickets
function handleGetTickets(req, res) {
    const url = new URL(req.url, `http://${HOST}:${PORT}`);
    const statusFilter = url.searchParams.get('status');
    const priorityFilter = url.searchParams.get('priority');

    let tickets = readTickets();

    if (statusFilter) {
        tickets = tickets.filter(t => t.status === statusFilter);
    }
    if (priorityFilter) {
        tickets = tickets.filter(t => t.priority === priorityFilter);
    }

    sendJson(res, 200, tickets);
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
        const ticket = {
            id: generateId(),
            subject: body.subject.trim(),
            description: body.description.trim(),
            priority: body.priority,
            status: body.status,
            created_at: now,
            updated_at: now
        };

        const tickets = readTickets();
        tickets.push(ticket);
        writeTickets(tickets);

        sendJson(res, 201, ticket);
    } catch (err) {
        if (err.message === 'Invalid JSON') {
            return sendJson(res, 400, { error: 'Invalid JSON in request body' });
        }
        sendJson(res, 500, { error: 'Internal server error' });
    }
}

// Handle GET /tickets/{id}
function handleGetTicket(req, res, id) {
    const tickets = readTickets();
    const ticket = tickets.find(t => t.id === id);

    if (!ticket) {
        return sendJson(res, 404, { error: 'Ticket not found' });
    }

    sendJson(res, 200, ticket);
}

// Handle PATCH /tickets/{id}
async function handlePatchTicket(req, res, id) {
    try {
        const body = await parseBody(req);

        if (Object.keys(body).length === 0) {
            return sendJson(res, 400, { error: 'No fields provided for update' });
        }

        const allowedFields = ['subject', 'description', 'priority', 'status'];
        const hasValidField = Object.keys(body).some(key => allowedFields.includes(key));

        if (!hasValidField) {
            return sendJson(res, 400, { error: 'Only subject, description, priority, and status can be updated' });
        }

        const errors = validateTicket(body, true);
        if (errors.length > 0) {
            return sendJson(res, 400, { error: 'Validation failed', details: errors });
        }

        const tickets = readTickets();
        const index = tickets.findIndex(t => t.id === id);

        if (index === -1) {
            return sendJson(res, 404, { error: 'Ticket not found' });
        }

        if (body.subject !== undefined) tickets[index].subject = body.subject.trim();
        if (body.description !== undefined) tickets[index].description = body.description.trim();
        if (body.priority !== undefined) tickets[index].priority = body.priority;
        if (body.status !== undefined) tickets[index].status = body.status;

        tickets[index].updated_at = new Date().toISOString();
        writeTickets(tickets);

        sendJson(res, 200, tickets[index]);
    } catch (err) {
        if (err.message === 'Invalid JSON') {
            return sendJson(res, 400, { error: 'Invalid JSON in request body' });
        }
        sendJson(res, 500, { error: 'Internal server error' });
    }
}

// Handle DELETE /tickets/{id}
function handleDeleteTicket(req, res, id) {
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
function handleGetMetrics(req, res) {
    const tickets = readTickets();
    const now = new Date();

    const statusCounts = { open: 0, in_progress: 0, resolved: 0 };
    const priorityCounts = { low: 0, medium: 0, high: 0 };
    let totalAge = 0;
    let openTicketsCount = 0;

    tickets.forEach(ticket => {
        // Count by status
        if (statusCounts[ticket.status] !== undefined) {
            statusCounts[ticket.status]++;
        }

        // Count by priority
        if (priorityCounts[ticket.priority] !== undefined) {
            priorityCounts[ticket.priority]++;
        }

        // Calculate age for open tickets
        if (ticket.status === 'open') {
            const created = new Date(ticket.created_at);
            const ageInSeconds = Math.floor((now - created) / 1000);
            totalAge += ageInSeconds;
            openTicketsCount++;
        }
    });

    const metrics = {
        by_status: statusCounts,
        by_priority: priorityCounts,
        average_open_age_seconds: openTicketsCount > 0 ? Math.round(totalAge / openTicketsCount) : 0
    };

    sendJson(res, 200, metrics);
}

// Route handler
async function handleRequest(req, res) {
    const url = new URL(req.url, `http://${HOST}:${PORT}`);
    const pathParts = url.pathname.split('/').filter(p => p);
    const method = req.method.toUpperCase();

    // Handle CORS preflight
    if (method === 'OPTIONS') {
        res.writeHead(204, {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type'
        });
        return res.end();
    }

    try {
        // GET /tickets
        if (method === 'GET' && pathParts.length === 1 && pathParts[0] === 'tickets') {
            return handleGetTickets(req, res);
        }

        // GET /metrics
        if (method === 'GET' && pathParts.length === 1 && pathParts[0] === 'metrics') {
            return handleGetMetrics(req, res);
        }

        // POST /tickets
        if (method === 'POST' && pathParts.length === 1 && pathParts[0] === 'tickets') {
            return await handlePostTickets(req, res);
        }

        // GET /tickets/{id}
        if (method === 'GET' && pathParts.length === 2 && pathParts[0] === 'tickets') {
            return handleGetTicket(req, res, pathParts[1]);
        }

        // PATCH /tickets/{id}
        if (method === 'PATCH' && pathParts.length === 2 && pathParts[0] === 'tickets') {
            return await handlePatchTicket(req, res, pathParts[1]);
        }

        // DELETE /tickets/{id}
        if (method === 'DELETE' && pathParts.length === 2 && pathParts[0] === 'tickets') {
            return handleDeleteTicket(req, res, pathParts[1]);
        }

        // Unknown route
        sendJson(res, 404, { error: 'Route not found' });

    } catch (err) {
        sendJson(res, 500, { error: 'Internal server error' });
    }
}

// Create and start server
initializeDataFile();

const server = http.createServer(handleRequest);

server.listen(PORT, HOST, () => {
    console.log(`Server running at http://${HOST}:${PORT}/`);
});
```
````
