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
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 17.129004
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 318, "total_tokens": 2714, "completion_tokens": 2396, "prompt_tokens_details": null}`
- Prompt tokens: 318
- Completion tokens: 2396
- Total tokens: 2714

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
let fileWritePending = false;
let fileWriteQueue = [];

// Initialize or load tickets.json
if (!fs.existsSync(DATA_FILE)) {
    fs.writeFileSync(DATA_FILE, JSON.stringify([]), 'utf8');
} else {
    try {
        const data = fs.readFileSync(DATA_FILE, 'utf8');
        tickets = JSON.parse(data);
        if (tickets.length > 0) {
            nextId = Math.max(...tickets.map(t => t.id)) + 1;
        }
    } catch (err) {
        tickets = [];
        nextId = 1;
        fs.writeFileSync(DATA_FILE, JSON.stringify([]), 'utf8');
    }
}

function safeWriteFile(callback) {
    fileWriteQueue.push(callback);
    if (!fileWritePending) {
        processWriteQueue();
    }
}

function processWriteQueue() {
    if (fileWriteQueue.length === 0) {
        fileWritePending = false;
        return;
    }
    fileWritePending = true;
    const callback = fileWriteQueue.shift();
    fs.writeFile(DATA_FILE, JSON.stringify(tickets, null, 2), 'utf8', (err) => {
        if (err) {
            console.error('Error writing file:', err);
        }
        processWriteQueue();
        if (callback) callback(err);
    });
}

function getTimestamp() {
    return new Date().toISOString();
}

function parseUrl(url) {
    const parts = url.split('?');
    const pathname = parts[0].replace(/\/+$/, '') || '/';
    const query = {};
    if (parts[1]) {
        parts[1].split('&').forEach(pair => {
            const [key, value] = pair.split('=').map(decodeURIComponent);
            if (key) query[key] = value;
        });
    }
    return { pathname, query };
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

function getBody(req) {
    return new Promise((resolve, reject) => {
        let body = '';
        req.on('data', chunk => {
            body += chunk;
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

function validateTicket(body) {
    const errors = [];
    if (!body.subject || typeof body.subject !== 'string' || body.subject.trim() === '') {
        errors.push('subject is required and must be a non-empty string');
    }
    if (!body.description || typeof body.description !== 'string' || body.description.trim() === '') {
        errors.push('description is required and must be a non-empty string');
    }
    if (body.priority && !['low', 'medium', 'high'].includes(body.priority)) {
        errors.push('priority must be low, medium, or high');
    }
    if (body.status && !['open', 'in_progress', 'resolved'].includes(body.status)) {
        errors.push('status must be open, in_progress, or resolved');
    }
    return errors;
}

function findTicketIndex(id) {
    const numId = parseInt(id, 10);
    if (isNaN(numId)) return -1;
    return tickets.findIndex(t => t.id === numId);
}

const server = http.createServer(async (req, res) => {
    const { pathname, query } = parseUrl(req.url);
    const method = req.method.toUpperCase();

    // Handle CORS preflight
    if (method === 'OPTIONS') {
        res.writeHead(204, {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type'
        });
        res.end();
        return;
    }

    try {
        // Route handling
        if (pathname === '/tickets' && method === 'GET') {
            // GET /tickets
            let filteredTickets = [...tickets];
            if (query.status) {
                filteredTickets = filteredTickets.filter(t => t.status === query.status);
            }
            if (query.priority) {
                filteredTickets = filteredTickets.filter(t => t.priority === query.priority);
            }
            sendJSON(res, 200, filteredTickets);

        } else if (pathname === '/tickets' && method === 'POST') {
            // POST /tickets
            const body = await getBody(req);
            const errors = validateTicket(body);
            if (errors.length > 0) {
                sendJSON(res, 400, { error: 'Validation failed', details: errors });
                return;
            }
            const now = getTimestamp();
            const ticket = {
                id: nextId++,
                subject: body.subject.trim(),
                description: body.description.trim(),
                priority: body.priority || 'low',
                status: body.status || 'open',
                created_at: now,
                updated_at: now
            };
            tickets.push(ticket);
            safeWriteFile((err) => {
                if (err) {
                    sendJSON(res, 500, { error: 'Failed to save ticket' });
                } else {
                    sendJSON(res, 201, ticket);
                }
            });

        } else if (pathname.startsWith('/tickets/') && method === 'GET') {
            // GET /tickets/{id}
            const id = pathname.split('/')[2];
            const index = findTicketIndex(id);
            if (index === -1) {
                sendJSON(res, 404, { error: 'Ticket not found' });
                return;
            }
            sendJSON(res, 200, tickets[index]);

        } else if (pathname.startsWith('/tickets/') && method === 'PATCH') {
            // PATCH /tickets/{id}
            const id = pathname.split('/')[2];
            const index = findTicketIndex(id);
            if (index === -1) {
                sendJSON(res, 404, { error: 'Ticket not found' });
                return;
            }
            const body = await getBody(req);
            const ticket = tickets[index];
            const allowedFields = ['subject', 'description', 'priority', 'status'];
            let hasUpdates = false;
            for (const field of allowedFields) {
                if (body[field] !== undefined) {
                    if (field === 'priority' && !['low', 'medium', 'high'].includes(body[field])) {
                        sendJSON(res, 400, { error: `Invalid priority: ${body[field]}. Must be low, medium, or high` });
                        return;
                    }
                    if (field === 'status' && !['open', 'in_progress', 'resolved'].includes(body[field])) {
                        sendJSON(res, 400, { error: `Invalid status: ${body[field]}. Must be open, in_progress, or resolved` });
                        return;
                    }
                    if (field === 'subject' || field === 'description') {
                        if (typeof body[field] !== 'string' || body[field].trim() === '') {
                            sendJSON(res, 400, { error: `${field} must be a non-empty string` });
                            return;
                        }
                        ticket[field] = body[field].trim();
                    } else {
                        ticket[field] = body[field];
                    }
                    hasUpdates = true;
                }
            }
            if (!hasUpdates) {
                sendJSON(res, 400, { error: 'No valid fields to update' });
                return;
            }
            ticket.updated_at = getTimestamp();
            safeWriteFile((err) => {
                if (err) {
                    sendJSON(res, 500, { error: 'Failed to update ticket' });
                } else {
                    sendJSON(res, 200, ticket);
                }
            });

        } else if (pathname.startsWith('/tickets/') && method === 'DELETE') {
            // DELETE /tickets/{id}
            const id = pathname.split('/')[2];
            const index = findTicketIndex(id);
            if (index === -1) {
                sendJSON(res, 404, { error: 'Ticket not found' });
                return;
            }
            const deletedTicket = tickets.splice(index, 1)[0];
            safeWriteFile((err) => {
                if (err) {
                    sendJSON(res, 500, { error: 'Failed to delete ticket' });
                } else {
                    sendJSON(res, 200, deletedTicket);
                }
            });

        } else if (pathname === '/metrics' && method === 'GET') {
            // GET /metrics
            const now = new Date();
            const statusCounts = { open: 0, in_progress: 0, resolved: 0 };
            const priorityCounts = { low: 0, medium: 0, high: 0 };
            let totalOpenAgeSeconds = 0;
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
                    const ageSeconds = (now - created) / 1000;
                    totalOpenAgeSeconds += ageSeconds;
                    openTicketCount++;
                }
            });

            const metrics = {
                by_status: statusCounts,
                by_priority: priorityCounts,
                average_open_age_seconds: openTicketCount > 0 ? totalOpenAgeSeconds / openTicketCount : 0
            };
            sendJSON(res, 200, metrics);

        } else {
            // Not found
            sendJSON(res, 404, { error: 'Not found' });
        }
    } catch (err) {
        if (err.message === 'Invalid JSON') {
            sendJSON(res, 400, { error: 'Invalid JSON body' });
        } else {
            console.error(err);
            sendJSON(res, 500, { error: 'Internal server error' });
        }
    }
});

server.listen(PORT, HOST, () => {
    console.log(`Server running at http://${HOST}:${PORT}/`);
});
```
````
