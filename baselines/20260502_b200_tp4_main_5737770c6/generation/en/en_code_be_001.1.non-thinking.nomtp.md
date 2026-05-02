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
- Elapsed seconds: 18.905526
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 318, "total_tokens": 2959, "completion_tokens": 2641, "prompt_tokens_details": null}`
- Prompt tokens: 318
- Completion tokens: 2641
- Total tokens: 2959

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

const HOST = '127.0.0.1';
const PORT = 8080;
const DATA_FILE = path.join(__dirname, 'tickets.json');

// Initialize data file if it doesn't exist
function initDataFile() {
    if (!fs.existsSync(DATA_FILE)) {
        fs.writeFileSync(DATA_FILE, '[]', 'utf8');
    }
}

// Read tickets from file with retry logic
function readTickets() {
    let retries = 3;
    while (retries > 0) {
        try {
            const data = fs.readFileSync(DATA_FILE, 'utf8');
            return JSON.parse(data);
        } catch (err) {
            if (err.code === 'ENOENT') {
                initDataFile();
                return [];
            }
            retries--;
            if (retries === 0) throw err;
            // Wait a bit before retrying
            require('util').promisify(setTimeout)(100);
        }
    }
}

// Write tickets to file with safe write
function writeTickets(tickets) {
    const tmpFile = DATA_FILE + '.tmp';
    fs.writeFileSync(tmpFile, JSON.stringify(tickets, null, 2), 'utf8');
    fs.renameSync(tmpFile, DATA_FILE);
}

// Generate unique ID
function generateId() {
    return Date.now().toString(36) + Math.random().toString(36).substr(2, 9);
}

// Validate ticket data
function validateTicket(data) {
    const errors = [];

    if (!data.subject || typeof data.subject !== 'string' || data.subject.trim() === '') {
        errors.push('subject is required and must be a non-empty string');
    }

    if (!data.description || typeof data.description !== 'string' || data.description.trim() === '') {
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

// Set CORS headers
function setCorsHeaders(res) {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, PATCH, DELETE, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
    res.setHeader('Access-Control-Max-Age', '86400');
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
            try {
                resolve(body ? JSON.parse(body) : {});
            } catch (err) {
                reject(new Error('Invalid JSON'));
            }
        });
        req.on('error', reject);
    });
}

// GET /tickets
function handleGetTickets(req, res, queryParams) {
    try {
        let tickets = readTickets();

        if (queryParams.status) {
            tickets = tickets.filter(t => t.status === queryParams.status);
        }

        if (queryParams.priority) {
            tickets = tickets.filter(t => t.priority === queryParams.priority);
        }

        sendJson(res, 200, tickets);
    } catch (err) {
        sendJson(res, 500, { error: 'Internal server error' });
    }
}

// POST /tickets
async function handlePostTickets(req, res) {
    try {
        const data = await parseBody(req);

        // Set defaults
        if (!data.priority) data.priority = 'medium';
        if (!data.status) data.status = 'open';

        const errors = validateTicket(data);
        if (errors.length > 0) {
            sendJson(res, 400, { error: 'Validation failed', details: errors });
            return;
        }

        const now = new Date().toISOString();
        const ticket = {
            id: generateId(),
            subject: data.subject.trim(),
            description: data.description.trim(),
            priority: data.priority,
            status: data.status,
            created_at: now,
            updated_at: now
        };

        const tickets = readTickets();
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

// GET /tickets/:id
function handleGetTicket(req, res, id) {
    try {
        const tickets = readTickets();
        const ticket = tickets.find(t => t.id === id);

        if (!ticket) {
            sendJson(res, 404, { error: 'Ticket not found' });
            return;
        }

        sendJson(res, 200, ticket);
    } catch (err) {
        sendJson(res, 500, { error: 'Internal server error' });
    }
}

// PATCH /tickets/:id
async function handlePatchTicket(req, res, id) {
    try {
        const data = await parseBody(req);

        const allowedFields = ['subject', 'description', 'priority', 'status'];
        const updates = {};

        for (const field of allowedFields) {
            if (data[field] !== undefined) {
                updates[field] = data[field];
            }
        }

        if (Object.keys(updates).length === 0) {
            sendJson(res, 400, { error: 'No valid fields to update. Allowed: subject, description, priority, status' });
            return;
        }

        // Validate updated fields
        const testTicket = { subject: 'test', description: 'test', ...updates };
        const errors = validateTicket(testTicket);
        if (errors.length > 0) {
            sendJson(res, 400, { error: 'Validation failed', details: errors });
            return;
        }

        const tickets = readTickets();
        const index = tickets.findIndex(t => t.id === id);

        if (index === -1) {
            sendJson(res, 404, { error: 'Ticket not found' });
            return;
        }

        const ticket = tickets[index];
        if (updates.subject) ticket.subject = updates.subject.trim();
        if (updates.description) ticket.description = updates.description.trim();
        if (updates.priority) ticket.priority = updates.priority;
        if (updates.status) ticket.status = updates.status;
        ticket.updated_at = new Date().toISOString();

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

// DELETE /tickets/:id
function handleDeleteTicket(req, res, id) {
    try {
        const tickets = readTickets();
        const index = tickets.findIndex(t => t.id === id);

        if (index === -1) {
            sendJson(res, 404, { error: 'Ticket not found' });
            return;
        }

        tickets.splice(index, 1);
        writeTickets(tickets);

        sendJson(res, 200, { message: 'Ticket deleted successfully' });
    } catch (err) {
        sendJson(res, 500, { error: 'Internal server error' });
    }
}

// GET /metrics
function handleGetMetrics(req, res) {
    try {
        const tickets = readTickets();
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

        // Calculate average age of open tickets
        let totalAgeSeconds = 0;
        let openTicketCount = 0;

        for (const ticket of tickets) {
            // Status counts
            if (statusCounts[ticket.status] !== undefined) {
                statusCounts[ticket.status]++;
            }

            // Priority counts
            if (priorityCounts[ticket.priority] !== undefined) {
                priorityCounts[ticket.priority]++;
            }

            // Age calculation for open and in_progress tickets
            if (ticket.status === 'open' || ticket.status === 'in_progress') {
                const createdAt = new Date(ticket.created_at);
                const ageSeconds = Math.floor((now - createdAt) / 1000);
                totalAgeSeconds += ageSeconds;
                openTicketCount++;
            }
        }

        const averageAgeSeconds = openTicketCount > 0
            ? Math.floor(totalAgeSeconds / openTicketCount)
            : 0;

        sendJson(res, 200, {
            status_counts: statusCounts,
            priority_counts: priorityCounts,
            average_open_age_seconds: averageAgeSeconds,
            total_tickets: tickets.length
        });
    } catch (err) {
        sendJson(res, 500, { error: 'Internal server error' });
    }
}

// Route handler
async function handleRequest(req, res) {
    setCorsHeaders(res);

    // Handle CORS preflight
    if (req.method === 'OPTIONS') {
        res.writeHead(204);
        res.end();
        return;
    }

    const parsedUrl = url.parse(req.url, true);
    const pathname = parsedUrl.pathname;
    const queryParams = parsedUrl.query;

    try {
        // Route matching
        if (pathname === '/tickets' && req.method === 'GET') {
            handleGetTickets(req, res, queryParams);
        } else if (pathname === '/tickets' && req.method === 'POST') {
            await handlePostTickets(req, res);
        } else if (pathname === '/metrics' && req.method === 'GET') {
            handleGetMetrics(req, res);
        } else if (pathname.startsWith('/tickets/')) {
            const id = pathname.split('/')[2];

            if (!id) {
                sendJson(res, 400, { error: 'Ticket ID is required' });
                return;
            }

            if (req.method === 'GET') {
                handleGetTicket(req, res, id);
            } else if (req.method === 'PATCH') {
                await handlePatchTicket(req, res, id);
            } else if (req.method === 'DELETE') {
                handleDeleteTicket(req, res, id);
            } else {
                sendJson(res, 405, { error: 'Method not allowed' });
            }
        } else {
            sendJson(res, 404, { error: 'Route not found' });
        }
    } catch (err) {
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
