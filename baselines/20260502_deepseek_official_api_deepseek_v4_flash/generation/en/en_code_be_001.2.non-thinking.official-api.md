# Generation Transcript

- Case: `en_code_be_001`
- Language group: `en`
- Workload: `coding`
- Model: `deepseek-v4-flash`
- Round: `2`
- Thinking mode: `non-thinking`
- Thinking strength: `disabled`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `official-api`
- OK: `True`
- Status: PASS
- Check: expectation checks skipped
- Detail: `expectation checks skipped`
- Elapsed seconds: 32.829305
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 318, "completion_tokens": 2735, "total_tokens": 3053, "prompt_tokens_details": {"cached_tokens": 256}, "prompt_cache_hit_tokens": 256, "prompt_cache_miss_tokens": 62}`
- Prompt tokens: 318
- Completion tokens: 2735
- Total tokens: 3053

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

// File locking mechanism for sequential access
let fileLock = false;
const lockQueue = [];

function acquireLock() {
    return new Promise((resolve) => {
        if (!fileLock) {
            fileLock = true;
            resolve();
        } else {
            lockQueue.push(resolve);
        }
    });
}

function releaseLock() {
    if (lockQueue.length > 0) {
        const next = lockQueue.shift();
        next();
    } else {
        fileLock = false;
    }
}

// Read tickets from file
async function readTickets() {
    await acquireLock();
    try {
        if (!fs.existsSync(DATA_FILE)) {
            fs.writeFileSync(DATA_FILE, JSON.stringify([]), 'utf8');
            return [];
        }
        const data = fs.readFileSync(DATA_FILE, 'utf8');
        return JSON.parse(data);
    } catch (err) {
        throw new Error('Failed to read tickets');
    } finally {
        releaseLock();
    }
}

// Write tickets to file
async function writeTickets(tickets) {
    await acquireLock();
    try {
        fs.writeFileSync(DATA_FILE, JSON.stringify(tickets, null, 2), 'utf8');
    } catch (err) {
        throw new Error('Failed to write tickets');
    } finally {
        releaseLock();
    }
}

// Generate ID
function generateId(tickets) {
    if (tickets.length === 0) return 1;
    return Math.max(...tickets.map(t => t.id)) + 1;
}

// Validate ticket creation fields
function validateCreateBody(body) {
    const errors = [];
    if (!body.subject || typeof body.subject !== 'string' || body.subject.trim() === '') {
        errors.push('subject is required and must be a non-empty string');
    }
    if (!body.description || typeof body.description !== 'string' || body.description.trim() === '') {
        errors.push('description is required and must be a non-empty string');
    }
    if (body.priority && !['low', 'medium', 'high'].includes(body.priority)) {
        errors.push('priority must be one of: low, medium, high');
    }
    if (!body.priority) {
        errors.push('priority is required');
    }
    return errors;
}

// Validate ticket update fields
function validateUpdateBody(body) {
    const errors = [];
    const validStatuses = ['open', 'in_progress', 'resolved'];
    const validPriorities = ['low', 'medium', 'high'];

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
    return errors;
}

// Set CORS headers
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

// Parse body
function parseBody(req) {
    return new Promise((resolve, reject) => {
        let body = '';
        req.on('data', chunk => {
            body += chunk.toString();
        });
        req.on('end', () => {
            try {
                if (body) {
                    resolve(JSON.parse(body));
                } else {
                    resolve({});
                }
            } catch (err) {
                reject(new Error('Invalid JSON'));
            }
        });
        req.on('error', reject);
    });
}

// Parse URL and query params
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

// Extract ID from path
function extractId(pathname) {
    const match = pathname.match(/^\/tickets\/(\d+)$/);
    return match ? parseInt(match[1]) : null;
}

// GET /tickets
async function getTickets(req, res) {
    try {
        const { params } = parseUrl(req.url);
        let tickets = await readTickets();

        if (params.status) {
            tickets = tickets.filter(t => t.status === params.status);
        }
        if (params.priority) {
            tickets = tickets.filter(t => t.priority === params.priority);
        }

        sendJson(res, 200, tickets);
    } catch (err) {
        sendJson(res, 500, { error: 'Internal server error' });
    }
}

// POST /tickets
async function createTicket(req, res) {
    try {
        const body = await parseBody(req);
        const errors = validateCreateBody(body);
        if (errors.length > 0) {
            sendJson(res, 400, { error: 'Validation failed', details: errors });
            return;
        }

        const tickets = await readTickets();
        const now = new Date().toISOString();
        const ticket = {
            id: generateId(tickets),
            subject: body.subject.trim(),
            description: body.description.trim(),
            priority: body.priority,
            status: 'open',
            created_at: now,
            updated_at: now
        };

        tickets.push(ticket);
        await writeTickets(tickets);
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
async function getTicket(req, res, id) {
    try {
        const tickets = await readTickets();
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
async function updateTicket(req, res, id) {
    try {
        const body = await parseBody(req);
        const errors = validateUpdateBody(body);
        if (errors.length > 0) {
            sendJson(res, 400, { error: 'Validation failed', details: errors });
            return;
        }

        if (Object.keys(body).length === 0) {
            sendJson(res, 400, { error: 'No fields to update' });
            return;
        }

        const tickets = await readTickets();
        const index = tickets.findIndex(t => t.id === id);

        if (index === -1) {
            sendJson(res, 404, { error: 'Ticket not found' });
            return;
        }

        const allowedFields = ['subject', 'description', 'priority', 'status'];
        const updates = {};
        for (const field of allowedFields) {
            if (body[field] !== undefined) {
                updates[field] = typeof body[field] === 'string' ? body[field].trim() : body[field];
            }
        }

        tickets[index] = {
            ...tickets[index],
            ...updates,
            updated_at: new Date().toISOString()
        };

        await writeTickets(tickets);
        sendJson(res, 200, tickets[index]);
    } catch (err) {
        if (err.message === 'Invalid JSON') {
            sendJson(res, 400, { error: 'Invalid JSON in request body' });
        } else {
            sendJson(res, 500, { error: 'Internal server error' });
        }
    }
}

// DELETE /tickets/:id
async function deleteTicket(req, res, id) {
    try {
        const tickets = await readTickets();
        const index = tickets.findIndex(t => t.id === id);

        if (index === -1) {
            sendJson(res, 404, { error: 'Ticket not found' });
            return;
        }

        const deleted = tickets.splice(index, 1)[0];
        await writeTickets(tickets);
        sendJson(res, 200, { deleted: deleted });
    } catch (err) {
        sendJson(res, 500, { error: 'Internal server error' });
    }
}

// GET /metrics
async function getMetrics(req, res) {
    try {
        const tickets = await readTickets();
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

        tickets.forEach(ticket => {
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
                const ageInSeconds = (now - created) / 1000;
                totalAge += ageInSeconds;
                openCount++;
            }
        });

        if (openCount > 0) {
            metrics.average_open_age_seconds = Math.round(totalAge / openCount);
        }

        sendJson(res, 200, metrics);
    } catch (err) {
        sendJson(res, 500, { error: 'Internal server error' });
    }
}

// Router
async function handleRequest(req, res) {
    setCorsHeaders(res);

    // Handle preflight
    if (req.method === 'OPTIONS') {
        sendJson(res, 200, {});
        return;
    }

    const { pathname } = parseUrl(req.url);

    try {
        // Route matching
        if (pathname === '/tickets' && req.method === 'GET') {
            await getTickets(req, res);
        } else if (pathname === '/tickets' && req.method === 'POST') {
            await createTicket(req, res);
        } else if (pathname === '/metrics' && req.method === 'GET') {
            await getMetrics(req, res);
        } else {
            const id = extractId(pathname);
            if (id !== null) {
                if (req.method === 'GET') {
                    await getTicket(req, res, id);
                } else if (req.method === 'PATCH') {
                    await updateTicket(req, res, id);
                } else if (req.method === 'DELETE') {
                    await deleteTicket(req, res, id);
                } else {
                    sendJson(res, 405, { error: 'Method not allowed' });
                }
            } else {
                sendJson(res, 404, { error: 'Route not found' });
            }
        }
    } catch (err) {
        sendJson(res, 500, { error: 'Internal server error' });
    }
}

// Create and start server
const server = http.createServer(handleRequest);

server.listen(PORT, HOST, () => {
    console.log(`Server running at http://${HOST}:${PORT}/`);
});
```
````
