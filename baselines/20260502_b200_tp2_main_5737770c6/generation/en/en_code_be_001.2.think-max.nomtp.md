# Generation Transcript

- Case: `en_code_be_001`
- Language group: `en`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `2`
- Thinking mode: `think-max`
- Thinking strength: `max`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 25.235663
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 318, "total_tokens": 3378, "completion_tokens": 3060, "prompt_tokens_details": null}`
- Prompt tokens: 318
- Completion tokens: 3060
- Total tokens: 3378

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
if (!fs.existsSync(DATA_FILE)) {
    fs.writeFileSync(DATA_FILE, '[]', 'utf8');
}

// Utility functions for file operations with locking
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

function readTickets() {
    return new Promise((resolve, reject) => {
        fs.readFile(DATA_FILE, 'utf8', (err, data) => {
            if (err) {
                reject(err);
            } else {
                try {
                    resolve(JSON.parse(data));
                } catch (e) {
                    reject(e);
                }
            }
        });
    });
}

function writeTickets(tickets) {
    return new Promise((resolve, reject) => {
        fs.writeFile(DATA_FILE, JSON.stringify(tickets, null, 2), 'utf8', (err) => {
            if (err) {
                reject(err);
            } else {
                resolve();
            }
        });
    });
}

// Validation helper
function validateTicketData(body) {
    const errors = [];

    if (!body.subject || typeof body.subject !== 'string' || body.subject.trim().length === 0) {
        errors.push('subject is required and must be a non-empty string');
    }

    if (!body.description || typeof body.description !== 'string' || body.description.trim().length === 0) {
        errors.push('description is required and must be a non-empty string');
    }

    if (body.priority && !['low', 'medium', 'high'].includes(body.priority)) {
        errors.push('priority must be one of: low, medium, high');
    }

    if (body.status && !['open', 'in_progress', 'resolved'].includes(body.status)) {
        errors.push('status must be one of: open, in_progress, resolved');
    }

    return errors;
}

// Generate unique ID
function generateId() {
    return Date.now().toString(36) + Math.random().toString(36).substr(2, 9);
}

// Server
const server = http.createServer((req, res) => {
    // CORS headers
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

    if (req.method === 'OPTIONS') {
        res.writeHead(204);
        res.end();
        return;
    }

    const parsedUrl = url.parse(req.url, true);
    const pathname = parsedUrl.pathname;
    const query = parsedUrl.query;

    // Route handling
    if (pathname === '/tickets' && req.method === 'GET') {
        handleGetTickets(req, res, query);
    } else if (pathname === '/tickets' && req.method === 'POST') {
        handlePostTicket(req, res);
    } else if (pathname.match(/^\/tickets\/([a-zA-Z0-9]+)$/) && req.method === 'GET') {
        const id = pathname.split('/')[2];
        handleGetTicket(req, res, id);
    } else if (pathname.match(/^\/tickets\/([a-zA-Z0-9]+)$/) && req.method === 'PATCH') {
        const id = pathname.split('/')[2];
        handlePatchTicket(req, res, id);
    } else if (pathname.match(/^\/tickets\/([a-zA-Z0-9]+)$/) && req.method === 'DELETE') {
        const id = pathname.split('/')[2];
        handleDeleteTicket(req, res, id);
    } else if (pathname === '/metrics' && req.method === 'GET') {
        handleGetMetrics(req, res);
    } else {
        res.writeHead(404, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: 'Route not found' }));
    }
});

// GET /tickets
async function handleGetTickets(req, res, query) {
    try {
        await acquireLock();
        const tickets = await readTickets();
        releaseLock();

        let filtered = [...tickets];

        if (query.status) {
            filtered = filtered.filter(t => t.status === query.status);
        }

        if (query.priority) {
            filtered = filtered.filter(t => t.priority === query.priority);
        }

        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify(filtered));
    } catch (err) {
        releaseLock();
        res.writeHead(500, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: 'Internal server error' }));
    }
}

// POST /tickets
async function handlePostTicket(req, res) {
    let body = '';

    req.on('data', chunk => {
        body += chunk.toString();
    });

    req.on('end', async () => {
        try {
            const data = JSON.parse(body);
            const errors = validateTicketData(data);

            if (errors.length > 0) {
                res.writeHead(400, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ error: 'Validation failed', details: errors }));
                return;
            }

            const now = new Date().toISOString();
            const ticket = {
                id: generateId(),
                subject: data.subject.trim(),
                description: data.description.trim(),
                priority: data.priority || 'low',
                status: data.status || 'open',
                created_at: now,
                updated_at: now
            };

            await acquireLock();
            const tickets = await readTickets();
            tickets.push(ticket);
            await writeTickets(tickets);
            releaseLock();

            res.writeHead(201, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify(ticket));
        } catch (err) {
            if (err instanceof SyntaxError) {
                res.writeHead(400, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ error: 'Invalid JSON' }));
            } else {
                releaseLock();
                res.writeHead(500, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ error: 'Internal server error' }));
            }
        }
    });
}

// GET /tickets/{id}
async function handleGetTicket(req, res, id) {
    try {
        await acquireLock();
        const tickets = await readTickets();
        releaseLock();

        const ticket = tickets.find(t => t.id === id);

        if (!ticket) {
            res.writeHead(404, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ error: 'Ticket not found' }));
            return;
        }

        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify(ticket));
    } catch (err) {
        releaseLock();
        res.writeHead(500, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: 'Internal server error' }));
    }
}

// PATCH /tickets/{id}
async function handlePatchTicket(req, res, id) {
    let body = '';

    req.on('data', chunk => {
        body += chunk.toString();
    });

    req.on('end', async () => {
        try {
            const data = JSON.parse(body);

            if (Object.keys(data).length === 0) {
                res.writeHead(400, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ error: 'No fields to update provided' }));
                return;
            }

            const allowedFields = ['subject', 'description', 'priority', 'status'];
            const updates = {};

            for (const field of allowedFields) {
                if (data[field] !== undefined) {
                    updates[field] = data[field];
                }
            }

            if (updates.subject !== undefined && (typeof updates.subject !== 'string' || updates.subject.trim().length === 0)) {
                res.writeHead(400, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ error: 'subject must be a non-empty string' }));
                return;
            }

            if (updates.description !== undefined && (typeof updates.description !== 'string' || updates.description.trim().length === 0)) {
                res.writeHead(400, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ error: 'description must be a non-empty string' }));
                return;
            }

            if (updates.priority && !['low', 'medium', 'high'].includes(updates.priority)) {
                res.writeHead(400, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ error: 'priority must be one of: low, medium, high' }));
                return;
            }

            if (updates.status && !['open', 'in_progress', 'resolved'].includes(updates.status)) {
                res.writeHead(400, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ error: 'status must be one of: open, in_progress, resolved' }));
                return;
            }

            await acquireLock();
            const tickets = await readTickets();
            const index = tickets.findIndex(t => t.id === id);

            if (index === -1) {
                releaseLock();
                res.writeHead(404, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ error: 'Ticket not found' }));
                return;
            }

            const now = new Date().toISOString();
            tickets[index] = {
                ...tickets[index],
                ...updates,
                updated_at: now
            };

            await writeTickets(tickets);
            releaseLock();

            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify(tickets[index]));
        } catch (err) {
            if (err instanceof SyntaxError) {
                res.writeHead(400, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ error: 'Invalid JSON' }));
            } else {
                releaseLock();
                res.writeHead(500, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ error: 'Internal server error' }));
            }
        }
    });
}

// DELETE /tickets/{id}
async function handleDeleteTicket(req, res, id) {
    try {
        await acquireLock();
        const tickets = await readTickets();
        const index = tickets.findIndex(t => t.id === id);

        if (index === -1) {
            releaseLock();
            res.writeHead(404, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ error: 'Ticket not found' }));
            return;
        }

        const deleted = tickets.splice(index, 1)[0];
        await writeTickets(tickets);
        releaseLock();

        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify(deleted));
    } catch (err) {
        releaseLock();
        res.writeHead(500, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: 'Internal server error' }));
    }
}

// GET /metrics
async function handleGetMetrics(req, res) {
    try {
        await acquireLock();
        const tickets = await readTickets();
        releaseLock();

        const now = new Date();

        // Count by status
        const statusCounts = { open: 0, in_progress: 0, resolved: 0 };
        for (const ticket of tickets) {
            if (statusCounts[ticket.status] !== undefined) {
                statusCounts[ticket.status]++;
            }
        }

        // Count by priority
        const priorityCounts = { low: 0, medium: 0, high: 0 };
        for (const ticket of tickets) {
            if (priorityCounts[ticket.priority] !== undefined) {
                priorityCounts[ticket.priority]++;
            }
        }

        // Average age of open tickets in seconds
        const openTickets = tickets.filter(t => t.status === 'open');
        let averageAge = 0;

        if (openTickets.length > 0) {
            let totalAge = 0;
            for (const ticket of openTickets) {
                const createdAt = new Date(ticket.created_at);
                totalAge += (now - createdAt) / 1000; // Convert to seconds
            }
            averageAge = totalAge / openTickets.length;
        }

        const metrics = {
            by_status: statusCounts,
            by_priority: priorityCounts,
            average_age_seconds: Math.round(averageAge * 100) / 100
        };

        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify(metrics));
    } catch (err) {
        releaseLock();
        res.writeHead(500, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: 'Internal server error' }));
    }
}

server.listen(PORT, HOST, () => {
    console.log(`Server running at http://${HOST}:${PORT}/`);
});
```
````
