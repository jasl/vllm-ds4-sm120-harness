# Generation Transcript

- Case: `en_code_be_001`
- Language group: `en`
- Workload: `coding`
- Model: `deepseek-v4-flash`
- Round: `3`
- Thinking mode: `non-thinking`
- Thinking strength: `disabled`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `official-api`
- OK: `True`
- Status: PASS
- Check: expectation checks skipped
- Detail: `expectation checks skipped`
- Elapsed seconds: 31.742574
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 318, "completion_tokens": 2585, "total_tokens": 2903, "prompt_tokens_details": {"cached_tokens": 256}, "prompt_cache_hit_tokens": 256, "prompt_cache_miss_tokens": 62}`
- Prompt tokens: 318
- Completion tokens: 2585
- Total tokens: 2903

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
const PORT = 8080;
const HOST = '127.0.0.1';

// Initialize tickets file if it doesn't exist
function initDataFile() {
    if (!fs.existsSync(DATA_FILE)) {
        fs.writeFileSync(DATA_FILE, JSON.stringify([]), 'utf8');
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
    try {
        fs.writeFileSync(DATA_FILE, JSON.stringify(tickets, null, 2), 'utf8');
        return true;
    } catch (err) {
        return false;
    }
}

// Generate unique ID
function generateId(tickets) {
    if (tickets.length === 0) return 1;
    const maxId = Math.max(...tickets.map(t => t.id));
    return maxId + 1;
}

// Validate ticket fields
function validateTicket(data) {
    const errors = [];

    if (!data.subject || typeof data.subject !== 'string' || data.subject.trim() === '') {
        errors.push('subject is required and must be a non-empty string');
    }

    if (!data.description || typeof data.description !== 'string' || data.description.trim() === '') {
        errors.push('description is required and must be a non-empty string');
    }

    const validPriorities = ['low', 'medium', 'high'];
    if (!data.priority || !validPriorities.includes(data.priority)) {
        errors.push('priority must be one of: low, medium, high');
    }

    const validStatuses = ['open', 'in_progress', 'resolved'];
    if (data.status && !validStatuses.includes(data.status)) {
        errors.push('status must be one of: open, in_progress, resolved');
    }

    return errors;
}

// Parse URL
function parseUrl(url) {
    const [pathname, queryString] = url.split('?');
    const query = {};

    if (queryString) {
        queryString.split('&').forEach(pair => {
            const [key, value] = pair.split('=');
            query[decodeURIComponent(key)] = decodeURIComponent(value || '');
        });
    }

    return { pathname, query };
}

// Extract ID from path
function extractId(pathname) {
    const match = pathname.match(/^\/tickets\/(\d+)$/);
    return match ? parseInt(match[1]) : null;
}

// Set CORS headers
function setCorsHeaders(res) {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
}

// Send JSON response
function sendJson(res, statusCode, data) {
    res.writeHead(statusCode, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(data));
}

// Handle GET /tickets
function handleGetTickets(res, query) {
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

// Handle POST /tickets
function handlePostTickets(res, body) {
    const tickets = readTickets();
    const errors = validateTicket(body);

    if (errors.length > 0) {
        sendJson(res, 400, { error: 'Validation failed', details: errors });
        return;
    }

    const now = new Date().toISOString();
    const newTicket = {
        id: generateId(tickets),
        subject: body.subject.trim(),
        description: body.description.trim(),
        priority: body.priority,
        status: body.status || 'open',
        created_at: now,
        updated_at: now
    };

    tickets.push(newTicket);

    if (!writeTickets(tickets)) {
        sendJson(res, 500, { error: 'Failed to save ticket' });
        return;
    }

    sendJson(res, 201, newTicket);
}

// Handle GET /tickets/:id
function handleGetTicket(res, id) {
    const tickets = readTickets();
    const ticket = tickets.find(t => t.id === id);

    if (!ticket) {
        sendJson(res, 404, { error: 'Ticket not found' });
        return;
    }

    sendJson(res, 200, ticket);
}

// Handle PATCH /tickets/:id
function handlePatchTicket(res, id, body) {
    const tickets = readTickets();
    const index = tickets.findIndex(t => t.id === id);

    if (index === -1) {
        sendJson(res, 404, { error: 'Ticket not found' });
        return;
    }

    const validFields = ['subject', 'description', 'priority', 'status'];
    const updates = {};

    for (const field of validFields) {
        if (body[field] !== undefined) {
            if (field === 'subject' || field === 'description') {
                if (typeof body[field] !== 'string' || body[field].trim() === '') {
                    sendJson(res, 400, { error: `${field} must be a non-empty string` });
                    return;
                }
                updates[field] = body[field].trim();
            } else if (field === 'priority') {
                const validPriorities = ['low', 'medium', 'high'];
                if (!validPriorities.includes(body[field])) {
                    sendJson(res, 400, { error: `priority must be one of: low, medium, high` });
                    return;
                }
                updates[field] = body[field];
            } else if (field === 'status') {
                const validStatuses = ['open', 'in_progress', 'resolved'];
                if (!validStatuses.includes(body[field])) {
                    sendJson(res, 400, { error: `status must be one of: open, in_progress, resolved` });
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

    updates.updated_at = new Date().toISOString();
    tickets[index] = { ...tickets[index], ...updates };

    if (!writeTickets(tickets)) {
        sendJson(res, 500, { error: 'Failed to update ticket' });
        return;
    }

    sendJson(res, 200, tickets[index]);
}

// Handle DELETE /tickets/:id
function handleDeleteTicket(res, id) {
    const tickets = readTickets();
    const index = tickets.findIndex(t => t.id === id);

    if (index === -1) {
        sendJson(res, 404, { error: 'Ticket not found' });
        return;
    }

    tickets.splice(index, 1);

    if (!writeTickets(tickets)) {
        sendJson(res, 500, { error: 'Failed to delete ticket' });
        return;
    }

    sendJson(res, 200, { message: 'Ticket deleted successfully' });
}

// Handle GET /metrics
function handleGetMetrics(res) {
    const tickets = readTickets();

    const statusCounts = {
        open: 0,
        in_progress: 0,
        resolved: 0
    };

    const priorityCounts = {
        low: 0,
        medium: 0,
        high: 0
    };

    let totalAgeSeconds = 0;
    let openTicketCount = 0;

    tickets.forEach(ticket => {
        if (statusCounts[ticket.status] !== undefined) {
            statusCounts[ticket.status]++;
        }

        if (priorityCounts[ticket.priority] !== undefined) {
            priorityCounts[ticket.priority]++;
        }

        if (ticket.status === 'open') {
            const created = new Date(ticket.created_at);
            const now = new Date();
            const ageSeconds = Math.floor((now - created) / 1000);
            totalAgeSeconds += ageSeconds;
            openTicketCount++;
        }
    });

    const metrics = {
        status_counts: statusCounts,
        priority_counts: priorityCounts,
        average_open_ticket_age_seconds: openTicketCount > 0 ? Math.round(totalAgeSeconds / openTicketCount) : 0
    };

    sendJson(res, 200, metrics);
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

// Create server
const server = http.createServer(async (req, res) => {
    setCorsHeaders(res);

    // Handle OPTIONS preflight
    if (req.method === 'OPTIONS') {
        res.writeHead(204);
        res.end();
        return;
    }

    const { pathname, query } = parseUrl(req.url);
    const id = extractId(pathname);

    try {
        // Routes
        if (pathname === '/tickets' && req.method === 'GET') {
            handleGetTickets(res, query);
        } else if (pathname === '/tickets' && req.method === 'POST') {
            const body = await parseBody(req);
            handlePostTickets(res, body);
        } else if (pathname === '/metrics' && req.method === 'GET') {
            handleGetMetrics(res);
        } else if (id !== null && req.method === 'GET') {
            handleGetTicket(res, id);
        } else if (id !== null && req.method === 'PATCH') {
            const body = await parseBody(req);
            handlePatchTicket(res, id, body);
        } else if (id !== null && req.method === 'DELETE') {
            handleDeleteTicket(res, id);
        } else if (pathname.startsWith('/tickets') && !pathname.match(/^\/tickets(?:\/\d+)?$/)) {
            sendJson(res, 400, { error: 'Invalid ticket ID format' });
        } else if (pathname === '/tickets' || pathname.match(/^\/tickets\/\d+$/) || pathname === '/metrics') {
            sendJson(res, 405, { error: 'Method not allowed' });
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
});

// Initialize and start
initDataFile();
server.listen(PORT, HOST, () => {
    console.log(`Server running at http://${HOST}:${PORT}/`);
});
```
````
