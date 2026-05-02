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
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 17.127494
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 318, "total_tokens": 2719, "completion_tokens": 2401, "prompt_tokens_details": null}`
- Prompt tokens: 318
- Completion tokens: 2401
- Total tokens: 2719

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

let tickets = [];
let nextId = 1;
let writeQueue = Promise.resolve();

function loadData() {
    try {
        if (fs.existsSync(DATA_FILE)) {
            const raw = fs.readFileSync(DATA_FILE, 'utf8');
            const data = JSON.parse(raw);
            tickets = data.tickets || [];
            nextId = data.nextId || 1;
        } else {
            tickets = [];
            nextId = 1;
            saveDataSync();
        }
    } catch (err) {
        tickets = [];
        nextId = 1;
    }
}

function saveDataSync() {
    try {
        fs.writeFileSync(DATA_FILE, JSON.stringify({ tickets, nextId }, null, 2), 'utf8');
    } catch (err) {
        console.error('Failed to save data:', err);
    }
}

function saveDataAsync() {
    return new Promise((resolve, reject) => {
        fs.writeFile(DATA_FILE, JSON.stringify({ tickets, nextId }, null, 2), 'utf8', (err) => {
            if (err) reject(err);
            else resolve();
        });
    });
}

function enqueueWrite() {
    writeQueue = writeQueue.then(() => saveDataAsync());
    return writeQueue;
}

function generateId() {
    return nextId++;
}

function getTimestamp() {
    return new Date().toISOString();
}

function parseUrl(url) {
    const [pathPart, queryString] = url.split('?');
    const params = {};
    if (queryString) {
        queryString.split('&').forEach(pair => {
            const [key, value] = pair.split('=');
            params[decodeURIComponent(key)] = decodeURIComponent(value || '');
        });
    }
    return { path: pathPart, params };
}

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

function sendResponse(res, statusCode, data) {
    res.writeHead(statusCode, {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type'
    });
    res.end(JSON.stringify(data));
}

function handleCors(req, res) {
    if (req.method === 'OPTIONS') {
        sendResponse(res, 204, {});
        return true;
    }
    return false;
}

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

function validateUpdate(body) {
    const errors = [];
    const validFields = ['subject', 'description', 'priority', 'status'];
    const updates = Object.keys(body).filter(k => validFields.includes(k));
    if (updates.length === 0) {
        errors.push('No valid fields to update. Valid fields: subject, description, priority, status');
    }
    if (body.subject !== undefined && typeof body.subject !== 'string') {
        errors.push('subject must be a string');
    }
    if (body.description !== undefined && typeof body.description !== 'string') {
        errors.push('description must be a string');
    }
    if (body.priority !== undefined && !['low', 'medium', 'high'].includes(body.priority)) {
        errors.push('priority must be low, medium, or high');
    }
    if (body.status !== undefined && !['open', 'in_progress', 'resolved'].includes(body.status)) {
        errors.push('status must be open, in_progress, or resolved');
    }
    return errors;
}

function handleGetTickets(req, res, params) {
    let filtered = [...tickets];
    if (params.status) {
        filtered = filtered.filter(t => t.status === params.status);
    }
    if (params.priority) {
        filtered = filtered.filter(t => t.priority === params.priority);
    }
    sendResponse(res, 200, filtered);
}

async function handlePostTicket(req, res) {
    try {
        const body = await parseBody(req);
        const errors = validateTicket(body);
        if (errors.length > 0) {
            sendResponse(res, 400, { error: 'Validation failed', details: errors });
            return;
        }
        const now = getTimestamp();
        const ticket = {
            id: generateId(),
            subject: body.subject,
            description: body.description,
            priority: body.priority || 'low',
            status: body.status || 'open',
            created_at: now,
            updated_at: now
        };
        tickets.push(ticket);
        await enqueueWrite();
        sendResponse(res, 201, ticket);
    } catch (err) {
        if (err.message === 'Invalid JSON') {
            sendResponse(res, 400, { error: 'Invalid JSON in request body' });
        } else {
            sendResponse(res, 500, { error: 'Internal server error' });
        }
    }
}

function handleGetTicket(req, res, id) {
    const ticket = tickets.find(t => t.id === id);
    if (!ticket) {
        sendResponse(res, 404, { error: 'Ticket not found' });
        return;
    }
    sendResponse(res, 200, ticket);
}

async function handlePatchTicket(req, res, id) {
    const index = tickets.findIndex(t => t.id === id);
    if (index === -1) {
        sendResponse(res, 404, { error: 'Ticket not found' });
        return;
    }
    try {
        const body = await parseBody(req);
        const errors = validateUpdate(body);
        if (errors.length > 0) {
            sendResponse(res, 400, { error: 'Validation failed', details: errors });
            return;
        }
        const updates = {};
        if (body.subject !== undefined) updates.subject = body.subject;
        if (body.description !== undefined) updates.description = body.description;
        if (body.priority !== undefined) updates.priority = body.priority;
        if (body.status !== undefined) updates.status = body.status;
        updates.updated_at = getTimestamp();
        tickets[index] = { ...tickets[index], ...updates };
        await enqueueWrite();
        sendResponse(res, 200, tickets[index]);
    } catch (err) {
        if (err.message === 'Invalid JSON') {
            sendResponse(res, 400, { error: 'Invalid JSON in request body' });
        } else {
            sendResponse(res, 500, { error: 'Internal server error' });
        }
    }
}

async function handleDeleteTicket(req, res, id) {
    const index = tickets.findIndex(t => t.id === id);
    if (index === -1) {
        sendResponse(res, 404, { error: 'Ticket not found' });
        return;
    }
    const deleted = tickets.splice(index, 1)[0];
    await enqueueWrite();
    sendResponse(res, 200, { message: 'Ticket deleted', ticket: deleted });
}

function handleGetMetrics(req, res) {
    const metrics = {
        by_status: {
            open: 0,
            in_progress: 0,
            resolved: 0
        },
        by_priority: {
            low: 0,
            medium: 0,
            high: 0
        },
        average_open_age_seconds: 0
    };

    const now = new Date();
    let openCount = 0;
    let totalAgeMs = 0;

    tickets.forEach(ticket => {
        if (metrics.by_status[ticket.status] !== undefined) {
            metrics.by_status[ticket.status]++;
        }
        if (metrics.by_priority[ticket.priority] !== undefined) {
            metrics.by_priority[ticket.priority]++;
        }
        if (ticket.status === 'open' || ticket.status === 'in_progress') {
            openCount++;
            const created = new Date(ticket.created_at);
            totalAgeMs += now - created;
        }
    });

    if (openCount > 0) {
        metrics.average_open_age_seconds = Math.round(totalAgeMs / openCount / 1000);
    }

    sendResponse(res, 200, metrics);
}

function routeRequest(req, res) {
    if (handleCors(req, res)) return;

    const { path, params } = parseUrl(req.url);
    const method = req.method;

    try {
        if (path === '/tickets' && method === 'GET') {
            handleGetTickets(req, res, params);
        } else if (path === '/tickets' && method === 'POST') {
            handlePostTicket(req, res);
        } else if (path === '/metrics' && method === 'GET') {
            handleGetMetrics(req, res);
        } else {
            const ticketMatch = path.match(/^\/tickets\/(\d+)$/);
            if (ticketMatch) {
                const id = parseInt(ticketMatch[1]);
                if (isNaN(id)) {
                    sendResponse(res, 400, { error: 'Invalid ticket ID' });
                    return;
                }
                switch (method) {
                    case 'GET':
                        handleGetTicket(req, res, id);
                        break;
                    case 'PATCH':
                        handlePatchTicket(req, res, id);
                        break;
                    case 'DELETE':
                        handleDeleteTicket(req, res, id);
                        break;
                    default:
                        sendResponse(res, 405, { error: 'Method not allowed' });
                }
            } else {
                sendResponse(res, 404, { error: 'Route not found' });
            }
        }
    } catch (err) {
        sendResponse(res, 500, { error: 'Internal server error' });
    }
}

loadData();
const server = http.createServer(routeRequest);
server.listen(PORT, HOST, () => {
    console.log(`Server running at http://${HOST}:${PORT}/`);
});
```
````
