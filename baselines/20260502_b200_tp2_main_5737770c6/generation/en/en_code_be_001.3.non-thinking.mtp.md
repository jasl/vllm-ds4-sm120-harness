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
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 10.672211
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 318, "total_tokens": 3397, "completion_tokens": 3079, "prompt_tokens_details": null}`
- Prompt tokens: 318
- Completion tokens: 3079
- Total tokens: 3397

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

const PORT = 8080;
const HOST = '127.0.0.1';
const DATA_FILE = path.join(__dirname, 'tickets.json');

let ticketsData = [];
let nextId = 1;

// Initialize or load data file
function initDataFile() {
    try {
        if (fs.existsSync(DATA_FILE)) {
            const data = fs.readFileSync(DATA_FILE, 'utf8');
            if (data) {
                ticketsData = JSON.parse(data);
                // Find max ID to set nextId
                if (ticketsData.length > 0) {
                    const maxId = Math.max(...ticketsData.map(t => t.id));
                    nextId = maxId + 1;
                }
            }
        } else {
            // Create file with empty array
            fs.writeFileSync(DATA_FILE, '[]', 'utf8');
        }
    } catch (err) {
        console.error('Error initializing data file:', err.message);
        ticketsData = [];
        nextId = 1;
    }
}

// Save data to file safely
function saveData() {
    try {
        fs.writeFileSync(DATA_FILE, JSON.stringify(ticketsData, null, 2), 'utf8');
        return true;
    } catch (err) {
        console.error('Error saving data:', err.message);
        return false;
    }
}

// CORS headers
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

// Parse JSON body
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
            } catch (err) {
                reject(new Error('Invalid JSON'));
            }
        });
        req.on('error', reject);
    });
}

// Validate ticket fields
function validateTicket(ticket) {
    const errors = [];

    if (typeof ticket.subject !== 'string' || ticket.subject.trim().length === 0) {
        errors.push('subject is required and must be a non-empty string');
    }
    if (typeof ticket.description !== 'string' || ticket.description.trim().length === 0) {
        errors.push('description is required and must be a non-empty string');
    }
    if (!['low', 'medium', 'high'].includes(ticket.priority)) {
        errors.push('priority must be one of: low, medium, high');
    }

    return errors;
}

// Generate timestamps
function getTimestamp() {
    return new Date().toISOString();
}

// Parse URL parameters
function parseUrl(url) {
    const [pathname, search] = url.split('?');
    const params = {};

    if (search) {
        search.split('&').forEach(pair => {
            const [key, value] = pair.split('=').map(decodeURIComponent);
            if (key) {
                params[key] = value;
            }
        });
    }

    return { pathname, params };
}

// Find ticket by ID
function findTicket(id) {
    const numericId = parseInt(id, 10);
    return ticketsData.find(t => t.id === numericId);
}

// Handle GET /tickets
function handleGetTickets(res, params) {
    let filtered = [...ticketsData];

    if (params.status) {
        filtered = filtered.filter(t => t.status === params.status);
    }
    if (params.priority) {
        filtered = filtered.filter(t => t.priority === params.priority);
    }

    sendJson(res, 200, { success: true, data: filtered });
}

// Handle POST /tickets
async function handlePostTickets(req, res) {
    let body;
    try {
        body = await parseBody(req);
    } catch (err) {
        sendJson(res, 400, { success: false, error: 'Invalid JSON in request body' });
        return;
    }

    if (!body) {
        sendJson(res, 400, { success: false, error: 'Request body is required' });
        return;
    }

    const ticket = {
        subject: body.subject,
        description: body.description,
        priority: body.priority || 'medium',
        status: 'open',
        created_at: getTimestamp(),
        updated_at: getTimestamp()
    };

    // Validate only required fields for creation
    if (!ticket.subject || !ticket.description) {
        sendJson(res, 400, { success: false, error: 'subject and description are required fields' });
        return;
    }

    if (!['low', 'medium', 'high'].includes(ticket.priority)) {
        ticket.priority = 'medium';
    }

    // Additional validation
    const errors = validateTicket(ticket);
    if (errors.length > 0) {
        sendJson(res, 400, { success: false, error: errors.join('; ') });
        return;
    }

    ticket.id = nextId++;
    ticketsData.push(ticket);

    if (!saveData()) {
        sendJson(res, 500, { success: false, error: 'Internal server error: failed to save data' });
        return;
    }

    sendJson(res, 201, { success: true, data: ticket });
}

// Handle GET /tickets/{id}
function handleGetTicket(res, id) {
    const ticket = findTicket(id);
    if (!ticket) {
        sendJson(res, 404, { success: false, error: `Ticket with id ${id} not found` });
        return;
    }
    sendJson(res, 200, { success: true, data: ticket });
}

// Handle PATCH /tickets/{id}
async function handlePatchTicket(req, res, id) {
    const ticket = findTicket(id);
    if (!ticket) {
        sendJson(res, 404, { success: false, error: `Ticket with id ${id} not found` });
        return;
    }

    let body;
    try {
        body = await parseBody(req);
    } catch (err) {
        sendJson(res, 400, { success: false, error: 'Invalid JSON in request body' });
        return;
    }

    if (!body) {
        sendJson(res, 400, { success: false, error: 'Request body is required' });
        return;
    }

    // Validate fields if provided
    if (body.subject !== undefined && (typeof body.subject !== 'string' || body.subject.trim().length === 0)) {
        sendJson(res, 400, { success: false, error: 'subject must be a non-empty string' });
        return;
    }
    if (body.description !== undefined && (typeof body.description !== 'string' || body.description.trim().length === 0)) {
        sendJson(res, 400, { success: false, error: 'description must be a non-empty string' });
        return;
    }
    if (body.priority !== undefined && !['low', 'medium', 'high'].includes(body.priority)) {
        sendJson(res, 400, { success: false, error: 'priority must be one of: low, medium, high' });
        return;
    }
    if (body.status !== undefined && !['open', 'in_progress', 'resolved'].includes(body.status)) {
        sendJson(res, 400, { success: false, error: 'status must be one of: open, in_progress, resolved' });
        return;
    }

    // Update fields
    if (body.subject !== undefined) ticket.subject = body.subject;
    if (body.description !== undefined) ticket.description = body.description;
    if (body.priority !== undefined) ticket.priority = body.priority;
    if (body.status !== undefined) ticket.status = body.status;
    ticket.updated_at = getTimestamp();

    if (!saveData()) {
        sendJson(res, 500, { success: false, error: 'Internal server error: failed to save data' });
        return;
    }

    sendJson(res, 200, { success: true, data: ticket });
}

// Handle DELETE /tickets/{id}
function handleDeleteTicket(res, id) {
    const index = ticketsData.findIndex(t => t.id === parseInt(id, 10));
    if (index === -1) {
        sendJson(res, 404, { success: false, error: `Ticket with id ${id} not found` });
        return;
    }

    ticketsData.splice(index, 1);

    if (!saveData()) {
        sendJson(res, 500, { success: false, error: 'Internal server error: failed to save data' });
        return;
    }

    sendJson(res, 200, { success: true, message: `Ticket ${id} deleted` });
}

// Handle GET /metrics
function handleGetMetrics(res) {
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
        average_open_age_seconds: 0
    };

    const now = new Date();
    let totalAge = 0;
    let openCount = 0;

    ticketsData.forEach(ticket => {
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
            const created = new Date(ticket.created_at);
            const ageSeconds = (now - created) / 1000;
            totalAge += ageSeconds;
            openCount++;
        }
    });

    if (openCount > 0) {
        metrics.average_open_age_seconds = Math.round(totalAge / openCount);
    }

    sendJson(res, 200, { success: true, data: metrics });
}

// Parse route
function parseRoute(pathname) {
    // Exact match for /tickets
    if (pathname === '/tickets') {
        return { resource: 'tickets', id: null };
    }

    // Match /tickets/{id}
    const ticketsMatch = pathname.match(/^\/tickets\/(\d+)$/);
    if (ticketsMatch) {
        return { resource: 'ticket', id: ticketsMatch[1] };
    }

    // Match /metrics
    if (pathname === '/metrics') {
        return { resource: 'metrics', id: null };
    }

    return { resource: null, id: null };
}

// Handle all routes
async function handleRequest(req, res) {
    setCorsHeaders(res);

    // Handle OPTIONS (preflight)
    if (req.method === 'OPTIONS') {
        res.writeHead(204);
        res.end();
        return;
    }

    const { pathname, params } = parseUrl(req.url);
    const route = parseRoute(pathname);

    try {
        if (route.resource === 'tickets' && !route.id) {
            // /tickets
            if (req.method === 'GET') {
                handleGetTickets(res, params);
            } else if (req.method === 'POST') {
                await handlePostTickets(req, res);
            } else {
                sendJson(res, 405, { success: false, error: `Method ${req.method} not allowed for /tickets` });
            }
        } else if (route.resource === 'ticket' && route.id) {
            // /tickets/{id}
            if (req.method === 'GET') {
                handleGetTicket(res, route.id);
            } else if (req.method === 'PATCH') {
                await handlePatchTicket(req, res, route.id);
            } else if (req.method === 'DELETE') {
                handleDeleteTicket(res, route.id);
            } else {
                sendJson(res, 405, { success: false, error: `Method ${req.method} not allowed for /tickets/{id}` });
            }
        } else if (route.resource === 'metrics') {
            if (req.method === 'GET') {
                handleGetMetrics(res);
            } else {
                sendJson(res, 405, { success: false, error: `Method ${req.method} not allowed for /metrics` });
            }
        } else {
            sendJson(res, 404, { success: false, error: `Route ${pathname} not found` });
        }
    } catch (err) {
        console.error('Unexpected error:', err.message);
        sendJson(res, 500, { success: false, error: 'Internal server error' });
    }
}

// Initialize and start server
initDataFile();

const server = http.createServer(handleRequest);

server.listen(PORT, HOST, () => {
    console.log(`Server running at http://${HOST}:${PORT}/`);
});

// Graceful shutdown
process.on('SIGINT', () => {
    console.log('\nShutting down server...');
    server.close(() => {
        console.log('Server closed.');
        process.exit(0);
    });
});

process.on('SIGTERM', () => {
    console.log('\nShutting down server...');
    server.close(() => {
        console.log('Server closed.');
        process.exit(0);
    });
});
```
````
