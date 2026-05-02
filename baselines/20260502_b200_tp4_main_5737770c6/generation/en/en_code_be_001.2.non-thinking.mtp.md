# Generation Transcript

- Case: `en_code_be_001`
- Language group: `en`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `2`
- Thinking mode: `non-thinking`
- Thinking strength: `disabled`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 8.491752
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 318, "total_tokens": 2779, "completion_tokens": 2461, "prompt_tokens_details": null}`
- Prompt tokens: 318
- Completion tokens: 2461
- Total tokens: 2779

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

let tickets = [];
let nextId = 1;
let fileOperationInProgress = false;
let pendingOperations = [];

// Initialize data file
function initDataFile() {
    try {
        if (fs.existsSync(DATA_FILE)) {
            const data = fs.readFileSync(DATA_FILE, 'utf8');
            if (data) {
                const parsed = JSON.parse(data);
                tickets = parsed.tickets || [];
                nextId = parsed.nextId || 1;
            }
        } else {
            saveDataSync();
        }
    } catch (err) {
        console.error('Error initializing data file:', err);
        tickets = [];
        nextId = 1;
        saveDataSync();
    }
}

function saveDataSync() {
    const data = JSON.stringify({ tickets, nextId }, null, 2);
    fs.writeFileSync(DATA_FILE, data, 'utf8');
}

async function saveDataAsync() {
    return new Promise((resolve, reject) => {
        if (fileOperationInProgress) {
            pendingOperations.push({ resolve, reject });
            return;
        }
        fileOperationInProgress = true;
        const data = JSON.stringify({ tickets, nextId }, null, 2);
        fs.writeFile(DATA_FILE, data, 'utf8', (err) => {
            fileOperationInProgress = false;
            if (err) {
                reject(err);
                while (pendingOperations.length > 0) {
                    const op = pendingOperations.shift();
                    op.reject(err);
                }
                return;
            }
            resolve(data);
            const ops = pendingOperations.slice();
            pendingOperations = [];
            ops.forEach(op => op.resolve());
        });
    });
}

function generateId() {
    return nextId++;
}

function now() {
    return new Date().toISOString();
}

function createTicket({ subject, description, priority }) {
    const id = generateId();
    const timestamp = now();
    return {
        id,
        subject,
        description,
        priority,
        status: 'open',
        created_at: timestamp,
        updated_at: timestamp
    };
}

function validateTicketBody(body) {
    const errors = [];
    if (!body.subject || typeof body.subject !== 'string' || body.subject.trim() === '') {
        errors.push('subject is required and must be a non-empty string');
    }
    if (!body.description || typeof body.description !== 'string' || body.description.trim() === '') {
        errors.push('description is required and must be a non-empty string');
    }
    if (!body.priority || !['low', 'medium', 'high'].includes(body.priority)) {
        errors.push('priority must be one of: low, medium, high');
    }
    return errors;
}

function validatePatchBody(body) {
    const errors = [];
    const allowedFields = ['subject', 'description', 'priority', 'status'];
    const updates = {};

    for (const field of allowedFields) {
        if (body[field] !== undefined) {
            updates[field] = body[field];
        }
    }

    if (Object.keys(updates).length === 0) {
        errors.push('At least one field must be provided for update');
        return { errors, updates: null };
    }

    if (updates.subject !== undefined && (typeof updates.subject !== 'string' || updates.subject.trim() === '')) {
        errors.push('subject must be a non-empty string');
    }
    if (updates.description !== undefined && (typeof updates.description !== 'string' || updates.description.trim() === '')) {
        errors.push('description must be a non-empty string');
    }
    if (updates.priority !== undefined && !['low', 'medium', 'high'].includes(updates.priority)) {
        errors.push('priority must be one of: low, medium, high');
    }
    if (updates.status !== undefined && !['open', 'in_progress', 'resolved'].includes(updates.status)) {
        errors.push('status must be one of: open, in_progress, resolved');
    }

    return { errors, updates: errors.length === 0 ? updates : null };
}

function parseBody(req) {
    return new Promise((resolve, reject) => {
        let body = '';
        req.on('data', chunk => body += chunk);
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

function sendJSON(res, statusCode, data) {
    res.writeHead(statusCode, {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type'
    });
    res.end(JSON.stringify(data));
}

function getMetrics() {
    const statusCounts = { open: 0, in_progress: 0, resolved: 0 };
    const priorityCounts = { low: 0, medium: 0, high: 0 };
    let totalAgeSeconds = 0;
    let openTicketCount = 0;
    const nowTime = Date.now();

    tickets.forEach(ticket => {
        statusCounts[ticket.status]++;
        priorityCounts[ticket.priority]++;

        if (ticket.status === 'open' || ticket.status === 'in_progress') {
            const created = new Date(ticket.created_at).getTime();
            totalAgeSeconds += (nowTime - created) / 1000;
            openTicketCount++;
        }
    });

    return {
        status_counts: statusCounts,
        priority_counts: priorityCounts,
        average_open_ticket_age_seconds: openTicketCount > 0 ? (totalAgeSeconds / openTicketCount) : 0
    };
}

function parseURL(reqUrl) {
    const url = new URL(reqUrl, `http://${HOST}:${PORT}`);
    const pathParts = url.pathname.split('/').filter(p => p);
    return { url, pathParts, query: url.searchParams };
}

const server = http.createServer(async (req, res) => {
    try {
        const { url, pathParts, query } = parseURL(req.url);

        // Handle CORS preflight
        if (req.method === 'OPTIONS') {
            res.writeHead(204, {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Max-Age': '86400'
            });
            res.end();
            return;
        }

        // Route handling
        if (pathParts.length === 0 || pathParts[0] === '') {
            sendJSON(res, 200, { message: 'Help Desk Ticket API', version: '1.0.0' });
            return;
        }

        if (pathParts[0] === 'tickets') {
            if (pathParts.length === 1) {
                // GET /tickets or POST /tickets
                if (req.method === 'GET') {
                    let filtered = [...tickets];
                    const statusFilter = query.get('status');
                    const priorityFilter = query.get('priority');

                    if (statusFilter && ['open', 'in_progress', 'resolved'].includes(statusFilter)) {
                        filtered = filtered.filter(t => t.status === statusFilter);
                    }
                    if (priorityFilter && ['low', 'medium', 'high'].includes(priorityFilter)) {
                        filtered = filtered.filter(t => t.priority === priorityFilter);
                    }

                    sendJSON(res, 200, filtered);
                } else if (req.method === 'POST') {
                    const body = await parseBody(req);
                    const errors = validateTicketBody(body);
                    if (errors.length > 0) {
                        sendJSON(res, 400, { error: 'Validation failed', details: errors });
                        return;
                    }

                    const ticket = createTicket(body);
                    tickets.push(ticket);
                    await saveDataAsync();
                    sendJSON(res, 201, ticket);
                } else {
                    sendJSON(res, 405, { error: 'Method not allowed' });
                }
            } else if (pathParts.length === 2) {
                const ticketId = parseInt(pathParts[1], 10);
                if (isNaN(ticketId)) {
                    sendJSON(res, 400, { error: 'Invalid ticket ID' });
                    return;
                }

                const ticketIndex = tickets.findIndex(t => t.id === ticketId);
                if (ticketIndex === -1) {
                    sendJSON(res, 404, { error: 'Ticket not found' });
                    return;
                }

                if (req.method === 'GET') {
                    sendJSON(res, 200, tickets[ticketIndex]);
                } else if (req.method === 'PATCH') {
                    const body = await parseBody(req);
                    const { errors, updates } = validatePatchBody(body);
                    if (errors.length > 0) {
                        sendJSON(res, 400, { error: 'Validation failed', details: errors });
                        return;
                    }

                    const ticket = tickets[ticketIndex];
                    Object.keys(updates).forEach(key => {
                        if (key === 'subject' || key === 'description') {
                            ticket[key] = updates[key].trim();
                        } else {
                            ticket[key] = updates[key];
                        }
                    });
                    ticket.updated_at = now();
                    await saveDataAsync();
                    sendJSON(res, 200, ticket);
                } else if (req.method === 'DELETE') {
                    tickets.splice(ticketIndex, 1);
                    await saveDataAsync();
                    sendJSON(res, 200, { message: 'Ticket deleted' });
                } else {
                    sendJSON(res, 405, { error: 'Method not allowed' });
                }
            } else {
                sendJSON(res, 404, { error: 'Not found' });
            }
        } else if (pathParts[0] === 'metrics') {
            if (req.method === 'GET') {
                sendJSON(res, 200, getMetrics());
            } else {
                sendJSON(res, 405, { error: 'Method not allowed' });
            }
        } else {
            sendJSON(res, 404, { error: 'Route not found' });
        }
    } catch (err) {
        if (err.message === 'Invalid JSON') {
            sendJSON(res, 400, { error: 'Invalid JSON in request body' });
        } else {
            console.error('Server error:', err);
            sendJSON(res, 500, { error: 'Internal server error' });
        }
    }
});

initDataFile();

server.listen(PORT, HOST, () => {
    console.log(`Server running at http://${HOST}:${PORT}/`);
});

process.on('SIGINT', () => {
    console.log('\nShutting down server...');
    saveDataSync();
    process.exit(0);
});

process.on('SIGTERM', () => {
    saveDataSync();
    process.exit(0);
});
```
````
