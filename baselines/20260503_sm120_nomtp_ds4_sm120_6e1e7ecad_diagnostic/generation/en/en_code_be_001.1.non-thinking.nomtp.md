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
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 41.902075
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 318, "total_tokens": 2987, "completion_tokens": 2669, "prompt_tokens_details": null}`
- Prompt tokens: 318
- Completion tokens: 2669
- Total tokens: 2987

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
        fs.writeFileSync(DATA_FILE, JSON.stringify({ tickets: [], nextId: 1 }), 'utf8');
    }
}

// Read data from file with retry
function readData() {
    try {
        const data = fs.readFileSync(DATA_FILE, 'utf8');
        return JSON.parse(data);
    } catch (error) {
        if (error.code === 'ENOENT') {
            initDataFile();
            return { tickets: [], nextId: 1 };
        }
        throw error;
    }
}

// Write data to file atomically
function writeData(data) {
    const tmpFile = DATA_FILE + '.tmp';
    fs.writeFileSync(tmpFile, JSON.stringify(data, null, 2), 'utf8');
    fs.renameSync(tmpFile, DATA_FILE);
}

// Generate timestamp in ISO format
function getTimestamp() {
    return new Date().toISOString();
}

// CORS headers
function setCorsHeaders(res) {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
}

// Send JSON response
function sendJson(res, statusCode, data) {
    res.writeHead(statusCode, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(data));
}

// Parse request body
function parseBody(req) {
    return new Promise((resolve, reject) => {
        let body = '';
        req.on('data', chunk => {
            body += chunk.toString();
        });
        req.on('end', () => {
            if (!body) {
                resolve(null);
                return;
            }
            try {
                resolve(JSON.parse(body));
            } catch (error) {
                reject(new Error('Invalid JSON'));
            }
        });
        req.on('error', reject);
    });
}

// Validate ticket creation fields
function validateCreateTicket(body) {
    const errors = [];
    if (!body || typeof body !== 'object') {
        return { valid: false, errors: ['Request body is required'] };
    }
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
    return {
        valid: errors.length === 0,
        errors: errors
    };
}

// Validate ticket update fields
function validateUpdateTicket(body) {
    const errors = [];
    if (!body || typeof body !== 'object') {
        return { valid: false, errors: ['Request body is required'] };
    }
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
    if (Object.keys(body).length === 0) {
        errors.push('At least one field to update is required');
    }
    return {
        valid: errors.length === 0,
        errors: errors
    };
}

// Route handlers
function getTickets(req, res) {
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

    sendJson(res, 200, tickets);
}

function createTicket(req, res) {
    parseBody(req).then(body => {
        const validation = validateCreateTicket(body);
        if (!validation.valid) {
            sendJson(res, 400, { error: 'Validation failed', details: validation.errors });
            return;
        }

        const data = readData();

        const now = getTimestamp();
        const ticket = {
            id: data.nextId,
            subject: body.subject.trim(),
            description: body.description.trim(),
            priority: body.priority || 'medium',
            status: body.status || 'open',
            created_at: now,
            updated_at: now
        };

        data.tickets.push(ticket);
        data.nextId++;
        writeData(data);

        sendJson(res, 201, ticket);
    }).catch(error => {
        sendJson(res, 400, { error: error.message });
    });
}

function getTicket(req, res, id) {
    const data = readData();
    const ticket = data.tickets.find(t => t.id === id);

    if (!ticket) {
        sendJson(res, 404, { error: 'Ticket not found' });
        return;
    }

    sendJson(res, 200, ticket);
}

function updateTicket(req, res, id) {
    parseBody(req).then(body => {
        const validation = validateUpdateTicket(body);
        if (!validation.valid) {
            sendJson(res, 400, { error: 'Validation failed', details: validation.errors });
            return;
        }

        const data = readData();
        const ticketIndex = data.tickets.findIndex(t => t.id === id);

        if (ticketIndex === -1) {
            sendJson(res, 404, { error: 'Ticket not found' });
            return;
        }

        const ticket = data.tickets[ticketIndex];
        const now = getTimestamp();

        if (body.subject !== undefined) ticket.subject = body.subject.trim();
        if (body.description !== undefined) ticket.description = body.description.trim();
        if (body.priority !== undefined) ticket.priority = body.priority;
        if (body.status !== undefined) ticket.status = body.status;
        ticket.updated_at = now;

        data.tickets[ticketIndex] = ticket;
        writeData(data);

        sendJson(res, 200, ticket);
    }).catch(error => {
        sendJson(res, 400, { error: error.message });
    });
}

function deleteTicket(req, res, id) {
    const data = readData();
    const ticketIndex = data.tickets.findIndex(t => t.id === id);

    if (ticketIndex === -1) {
        sendJson(res, 404, { error: 'Ticket not found' });
        return;
    }

    const deletedTicket = data.tickets.splice(ticketIndex, 1)[0];
    writeData(data);

    sendJson(res, 200, { message: 'Ticket deleted', ticket: deletedTicket });
}

function getMetrics(req, res) {
    const data = readData();
    const tickets = data.tickets;
    const now = new Date();

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

    let totalOpenAge = 0;
    let openTicketCount = 0;

    tickets.forEach(ticket => {
        // Status counts
        if (statusCounts[ticket.status] !== undefined) {
            statusCounts[ticket.status]++;
        }

        // Priority counts
        if (priorityCounts[ticket.priority] !== undefined) {
            priorityCounts[ticket.priority]++;
        }

        // Average age of open tickets
        if (ticket.status === 'open') {
            const created = new Date(ticket.created_at);
            const ageInSeconds = (now - created) / 1000;
            totalOpenAge += ageInSeconds;
            openTicketCount++;
        }
    });

    const averageAge = openTicketCount > 0 ? totalOpenAge / openTicketCount : 0;

    const metrics = {
        status_counts: statusCounts,
        priority_counts: priorityCounts,
        average_open_ticket_age_seconds: Math.round(averageAge * 100) / 100
    };

    sendJson(res, 200, metrics);
}

// Parse ticket ID from URL
function parseTicketId(url) {
    const match = url.pathname.match(/^\/tickets\/(\d+)$/);
    return match ? parseInt(match[1]) : null;
}

// Create HTTP server
const server = http.createServer((req, res) => {
    setCorsHeaders(res);
    const url = new URL(req.url, `http://${HOST}:${PORT}`);

    // Handle CORS preflight
    if (req.method === 'OPTIONS') {
        res.writeHead(204);
        res.end();
        return;
    }

    // Route handling
    try {
        if (req.method === 'GET' && url.pathname === '/tickets') {
            getTickets(req, res);
        } else if (req.method === 'POST' && url.pathname === '/tickets') {
            createTicket(req, res);
        } else if (req.method === 'GET' && url.pathname === '/metrics') {
            getMetrics(req, res);
        } else if (req.method === 'GET' && url.pathname.startsWith('/tickets/')) {
            const id = parseTicketId(url);
            if (id !== null) {
                getTicket(req, res, id);
            } else {
                sendJson(res, 404, { error: 'Route not found' });
            }
        } else if (req.method === 'PATCH' && url.pathname.startsWith('/tickets/')) {
            const id = parseTicketId(url);
            if (id !== null) {
                updateTicket(req, res, id);
            } else {
                sendJson(res, 404, { error: 'Route not found' });
            }
        } else if (req.method === 'DELETE' && url.pathname.startsWith('/tickets/')) {
            const id = parseTicketId(url);
            if (id !== null) {
                deleteTicket(req, res, id);
            } else {
                sendJson(res, 404, { error: 'Route not found' });
            }
        } else if (url.pathname === '/tickets') {
            // Handle unsupported methods on /tickets
            sendJson(res, 405, { error: 'Method not allowed' });
        } else {
            sendJson(res, 404, { error: 'Route not found' });
        }
    } catch (error) {
        console.error('Server error:', error);
        sendJson(res, 500, { error: 'Internal server error' });
    }
});

// Start server
initDataFile();
server.listen(PORT, HOST, () => {
    console.log(`Server running at http://${HOST}:${PORT}/`);
});
```
````
