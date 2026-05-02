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
- Elapsed seconds: 24.879357
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 318, "total_tokens": 3147, "completion_tokens": 2829, "prompt_tokens_details": null}`
- Prompt tokens: 318
- Completion tokens: 2829
- Total tokens: 3147

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

// Initialize data file if it doesn't exist
if (!fs.existsSync(DATA_FILE)) {
    fs.writeFileSync(DATA_FILE, JSON.stringify({ tickets: [], counter: 0 }), 'utf8');
}

// Safe file read with retry
function readData() {
    return new Promise((resolve, reject) => {
        let retries = 0;
        const maxRetries = 3;

        function tryRead() {
            fs.readFile(DATA_FILE, 'utf8', (err, data) => {
                if (err) {
                    if (retries < maxRetries) {
                        retries++;
                        setTimeout(tryRead, 50);
                    } else {
                        reject(err);
                    }
                    return;
                }
                try {
                    resolve(JSON.parse(data));
                } catch (parseErr) {
                    reject(parseErr);
                }
            });
        }
        tryRead();
    });
}

// Safe file write with retry
function writeData(data) {
    return new Promise((resolve, reject) => {
        let retries = 0;
        const maxRetries = 3;

        function tryWrite() {
            fs.writeFile(DATA_FILE, JSON.stringify(data, null, 2), 'utf8', (err) => {
                if (err) {
                    if (retries < maxRetries) {
                        retries++;
                        setTimeout(tryWrite, 50);
                    } else {
                        reject(err);
                    }
                    return;
                }
                resolve();
            });
        }
        tryWrite();
    });
}

// Parse JSON body
function parseBody(req) {
    return new Promise((resolve, reject) => {
        let body = '';
        req.on('data', chunk => {
            body += chunk.toString();
            // Limit body size to 1MB
            if (body.length > 1048576) {
                reject(new Error('Request body too large'));
            }
        });
        req.on('end', () => {
            if (!body) {
                resolve({});
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

// Parse URL and query parameters
function parseUrl(url) {
    const [pathname, queryString] = url.split('?');
    const params = {};
    if (queryString) {
        queryString.split('&').forEach(pair => {
            const [key, value] = pair.split('=').map(decodeURIComponent);
            params[key] = value;
        });
    }
    return { pathname, params };
}

// Generate response
function sendResponse(res, statusCode, data) {
    const headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization'
    };
    res.writeHead(statusCode, headers);
    res.end(JSON.stringify(data));
}

// Validate ticket fields
function validateTicket(body, isUpdate = false) {
    const errors = [];

    if (!isUpdate) {
        if (!body.subject || typeof body.subject !== 'string' || body.subject.trim().length === 0) {
            errors.push('subject is required and must be a non-empty string');
        }
        if (!body.description || typeof body.description !== 'string' || body.description.trim().length === 0) {
            errors.push('description is required and must be a non-empty string');
        }
    }

    if (body.subject !== undefined && (typeof body.subject !== 'string' || body.subject.trim().length === 0)) {
        errors.push('subject must be a non-empty string');
    }

    if (body.description !== undefined && (typeof body.description !== 'string' || body.description.trim().length === 0)) {
        errors.push('description must be a non-empty string');
    }

    if (body.priority !== undefined && !['low', 'medium', 'high'].includes(body.priority)) {
        errors.push('priority must be one of: low, medium, high');
    }

    if (body.status !== undefined && !['open', 'in_progress', 'resolved'].includes(body.status)) {
        errors.push('status must be one of: open, in_progress, resolved');
    }

    return errors;
}

// Route handlers
async function handleGetTickets(req, res, params) {
    try {
        const data = await readData();
        let tickets = data.tickets;

        if (params.status) {
            tickets = tickets.filter(t => t.status === params.status);
        }
        if (params.priority) {
            tickets = tickets.filter(t => t.priority === params.priority);
        }

        sendResponse(res, 200, { tickets });
    } catch (err) {
        sendResponse(res, 500, { error: 'Internal server error' });
    }
}

async function handlePostTicket(req, res) {
    try {
        const body = await parseBody(req);
        const errors = validateTicket(body);

        if (errors.length > 0) {
            sendResponse(res, 400, { error: 'Validation failed', details: errors });
            return;
        }

        const data = await readData();
        data.counter++;
        const now = new Date().toISOString();

        const ticket = {
            id: data.counter,
            subject: body.subject.trim(),
            description: body.description.trim(),
            priority: body.priority || 'medium',
            status: 'open',
            created_at: now,
            updated_at: now
        };

        data.tickets.push(ticket);
        await writeData(data);

        sendResponse(res, 201, { ticket });
    } catch (err) {
        if (err.message === 'Invalid JSON' || err.message === 'Request body too large') {
            sendResponse(res, 400, { error: err.message });
        } else {
            sendResponse(res, 500, { error: 'Internal server error' });
        }
    }
}

async function handleGetTicket(req, res, id) {
    try {
        const data = await readData();
        const ticket = data.tickets.find(t => t.id === id);

        if (!ticket) {
            sendResponse(res, 404, { error: 'Ticket not found' });
            return;
        }

        sendResponse(res, 200, { ticket });
    } catch (err) {
        sendResponse(res, 500, { error: 'Internal server error' });
    }
}

async function handlePatchTicket(req, res, id) {
    try {
        const data = await readData();
        const index = data.tickets.findIndex(t => t.id === id);

        if (index === -1) {
            sendResponse(res, 404, { error: 'Ticket not found' });
            return;
        }

        const body = await parseBody(req);
        const errors = validateTicket(body, true);

        if (errors.length > 0) {
            sendResponse(res, 400, { error: 'Validation failed', details: errors });
            return;
        }

        // Check if there's anything to update
        const allowedFields = ['subject', 'description', 'priority', 'status'];
        const hasUpdates = allowedFields.some(field => body[field] !== undefined);

        if (!hasUpdates) {
            sendResponse(res, 400, { error: 'No valid fields to update' });
            return;
        }

        const now = new Date().toISOString();
        const ticket = data.tickets[index];

        if (body.subject !== undefined) ticket.subject = body.subject.trim();
        if (body.description !== undefined) ticket.description = body.description.trim();
        if (body.priority !== undefined) ticket.priority = body.priority;
        if (body.status !== undefined) ticket.status = body.status;
        ticket.updated_at = now;

        data.tickets[index] = ticket;
        await writeData(data);

        sendResponse(res, 200, { ticket });
    } catch (err) {
        if (err.message === 'Invalid JSON' || err.message === 'Request body too large') {
            sendResponse(res, 400, { error: err.message });
        } else {
            sendResponse(res, 500, { error: 'Internal server error' });
        }
    }
}

async function handleDeleteTicket(req, res, id) {
    try {
        const data = await readData();
        const index = data.tickets.findIndex(t => t.id === id);

        if (index === -1) {
            sendResponse(res, 404, { error: 'Ticket not found' });
            return;
        }

        data.tickets.splice(index, 1);
        await writeData(data);

        sendResponse(res, 200, { message: 'Ticket deleted successfully' });
    } catch (err) {
        sendResponse(res, 500, { error: 'Internal server error' });
    }
}

async function handleMetrics(req, res) {
    try {
        const data = await readData();
        const tickets = data.tickets;
        const now = new Date();

        // Counts by status
        const byStatus = { open: 0, in_progress: 0, resolved: 0 };
        // Counts by priority
        const byPriority = { low: 0, medium: 0, high: 0 };

        let totalAgeSeconds = 0;
        let openCount = 0;

        tickets.forEach(ticket => {
            // Count by status
            if (byStatus[ticket.status] !== undefined) {
                byStatus[ticket.status]++;
            }

            // Count by priority
            if (byPriority[ticket.priority] !== undefined) {
                byPriority[ticket.priority]++;
            }

            // Calculate age for open tickets
            if (ticket.status === 'open') {
                const created = new Date(ticket.created_at);
                const ageSeconds = (now - created) / 1000;
                totalAgeSeconds += ageSeconds;
                openCount++;
            }
        });

        const averageAgeSeconds = openCount > 0 ? Math.round(totalAgeSeconds / openCount) : 0;

        sendResponse(res, 200, {
            by_status: byStatus,
            by_priority: byPriority,
            average_open_age_seconds: averageAgeSeconds,
            total_tickets: tickets.length
        });
    } catch (err) {
        sendResponse(res, 500, { error: 'Internal server error' });
    }
}

// Main request handler
async function handleRequest(req, res) {
    const { pathname, params } = parseUrl(req.url);
    const method = req.method.toUpperCase();

    // Handle CORS preflight
    if (method === 'OPTIONS') {
        res.writeHead(204, {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
            'Access-Control-Max-Age': '86400'
        });
        res.end();
        return;
    }

    // Route matching
    const getTicketMatch = pathname.match(/^\/tickets\/(\d+)$/);
    const isMetrics = pathname === '/metrics';
    const isTickets = pathname === '/tickets';

    try {
        if (isTickets && method === 'GET') {
            await handleGetTickets(req, res, params);
        } else if (isTickets && method === 'POST') {
            await handlePostTicket(req, res);
        } else if (getTicketMatch && method === 'GET') {
            await handleGetTicket(req, res, parseInt(getTicketMatch[1]));
        } else if (getTicketMatch && method === 'PATCH') {
            await handlePatchTicket(req, res, parseInt(getTicketMatch[1]));
        } else if (getTicketMatch && method === 'DELETE') {
            await handleDeleteTicket(req, res, parseInt(getTicketMatch[1]));
        } else if (isMetrics && method === 'GET') {
            await handleMetrics(req, res);
        } else if (isMetrics) {
            sendResponse(res, 405, { error: 'Method not allowed' });
        } else {
            sendResponse(res, 404, { error: 'Route not found' });
        }
    } catch (err) {
        sendResponse(res, 500, { error: 'Internal server error' });
    }
}

// Create and start server
const server = http.createServer(handleRequest);

server.listen(PORT, HOST, () => {
    console.log(`Server running at http://${HOST}:${PORT}/`);
});
```
````
