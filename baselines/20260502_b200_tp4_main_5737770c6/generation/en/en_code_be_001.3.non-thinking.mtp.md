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
- Elapsed seconds: 7.229226
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 318, "total_tokens": 2429, "completion_tokens": 2111, "prompt_tokens_details": null}`
- Prompt tokens: 318
- Completion tokens: 2111
- Total tokens: 2429

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

let ticketIdCounter = 1;
let tickets = [];

function loadData() {
    try {
        if (fs.existsSync(DATA_FILE)) {
            const raw = fs.readFileSync(DATA_FILE, 'utf8');
            tickets = JSON.parse(raw);
            if (tickets.length > 0) {
                ticketIdCounter = Math.max(...tickets.map(t => t.id)) + 1;
            }
        } else {
            tickets = [];
            saveDataSync();
        }
    } catch (err) {
        tickets = [];
        saveDataSync();
    }
}

function saveDataSync() {
    try {
        fs.writeFileSync(DATA_FILE, JSON.stringify(tickets, null, 2), 'utf8');
    } catch (err) {
        console.error('Error saving data:', err);
    }
}

function saveDataAsync() {
    return new Promise((resolve, reject) => {
        fs.writeFile(DATA_FILE, JSON.stringify(tickets, null, 2), 'utf8', (err) => {
            if (err) reject(err);
            else resolve();
        });
    });
}

function getBody(req) {
    return new Promise((resolve, reject) => {
        let body = '';
        req.on('data', chunk => {
            body += chunk;
            if (body.length > 1e6) {
                req.destroy();
                reject(new Error('Request body too large'));
            }
        });
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

function validateUpdate(body) {
    const errors = [];
    if (body.subject !== undefined && (typeof body.subject !== 'string' || body.subject.trim() === '')) {
        errors.push('subject must be a non-empty string');
    }
    if (body.description !== undefined && (typeof body.description !== 'string' || body.description.trim() === '')) {
        errors.push('description must be a non-empty string');
    }
    if (body.priority !== undefined && !['low', 'medium', 'high'].includes(body.priority)) {
        errors.push('priority must be low, medium, or high');
    }
    if (body.status !== undefined && !['open', 'in_progress', 'resolved'].includes(body.status)) {
        errors.push('status must be open, in_progress, or resolved');
    }
    return errors;
}

function parseId(pathname) {
    const match = pathname.match(/^\/tickets\/(\d+)$/);
    return match ? parseInt(match[1], 10) : null;
}

async function handleRequest(req, res) {
    const url = new URL(req.url, `http://${HOST}:${PORT}`);
    const pathname = url.pathname;
    const method = req.method.toUpperCase();

    // CORS preflight
    if (method === 'OPTIONS') {
        sendJSON(res, 204, '');
        return;
    }

    try {
        // GET /metrics
        if (pathname === '/metrics' && method === 'GET') {
            const statusCounts = { open: 0, in_progress: 0, resolved: 0 };
            const priorityCounts = { low: 0, medium: 0, high: 0 };
            let totalAge = 0;
            let openCount = 0;
            const now = Date.now();

            for (const ticket of tickets) {
                if (statusCounts.hasOwnProperty(ticket.status)) {
                    statusCounts[ticket.status]++;
                }
                if (priorityCounts.hasOwnProperty(ticket.priority)) {
                    priorityCounts[ticket.priority]++;
                }
                if (ticket.status === 'open') {
                    const createdAt = new Date(ticket.created_at).getTime();
                    totalAge += (now - createdAt) / 1000;
                    openCount++;
                }
            }

            const metrics = {
                status_counts: statusCounts,
                priority_counts: priorityCounts,
                average_open_age_seconds: openCount > 0 ? totalAge / openCount : 0
            };
            sendJSON(res, 200, metrics);
            return;
        }

        // GET /tickets
        if (pathname === '/tickets' && method === 'GET') {
            let filtered = [...tickets];
            const statusFilter = url.searchParams.get('status');
            const priorityFilter = url.searchParams.get('priority');

            if (statusFilter && ['open', 'in_progress', 'resolved'].includes(statusFilter)) {
                filtered = filtered.filter(t => t.status === statusFilter);
            }
            if (priorityFilter && ['low', 'medium', 'high'].includes(priorityFilter)) {
                filtered = filtered.filter(t => t.priority === priorityFilter);
            }

            sendJSON(res, 200, filtered);
            return;
        }

        // POST /tickets
        if (pathname === '/tickets' && method === 'POST') {
            const body = await getBody(req);
            const errors = validateTicket(body);
            if (errors.length > 0) {
                sendJSON(res, 400, { error: 'Validation failed', details: errors });
                return;
            }

            const now = new Date().toISOString();
            const newTicket = {
                id: ticketIdCounter++,
                subject: body.subject.trim(),
                description: body.description.trim(),
                priority: body.priority || 'low',
                status: 'open',
                created_at: now,
                updated_at: now
            };

            tickets.push(newTicket);
            await saveDataAsync();
            sendJSON(res, 201, newTicket);
            return;
        }

        // Single ticket operations: GET, PATCH, DELETE
        const ticketId = parseId(pathname);
        if (ticketId !== null) {
            const index = tickets.findIndex(t => t.id === ticketId);

            if (index === -1) {
                sendJSON(res, 404, { error: 'Ticket not found' });
                return;
            }

            // GET /tickets/{id}
            if (method === 'GET') {
                sendJSON(res, 200, tickets[index]);
                return;
            }

            // PATCH /tickets/{id}
            if (method === 'PATCH') {
                const body = await getBody(req);
                const errors = validateUpdate(body);
                if (errors.length > 0) {
                    sendJSON(res, 400, { error: 'Validation failed', details: errors });
                    return;
                }

                const updated = tickets[index];
                if (body.subject !== undefined) updated.subject = body.subject.trim();
                if (body.description !== undefined) updated.description = body.description.trim();
                if (body.priority !== undefined) updated.priority = body.priority;
                if (body.status !== undefined) updated.status = body.status;
                updated.updated_at = new Date().toISOString();

                tickets[index] = updated;
                await saveDataAsync();
                sendJSON(res, 200, updated);
                return;
            }

            // DELETE /tickets/{id}
            if (method === 'DELETE') {
                const deleted = tickets.splice(index, 1)[0];
                await saveDataAsync();
                sendJSON(res, 200, { message: 'Ticket deleted', ticket: deleted });
                return;
            }

            // Method not allowed on /tickets/{id}
            sendJSON(res, 405, { error: 'Method not allowed' });
            return;
        }

        // Unknown route
        sendJSON(res, 404, { error: 'Route not found' });

    } catch (err) {
        if (err.message === 'Invalid JSON') {
            sendJSON(res, 400, { error: 'Invalid JSON in request body' });
        } else if (err.message === 'Request body too large') {
            sendJSON(res, 413, { error: 'Request body too large' });
        } else {
            console.error('Server error:', err);
            sendJSON(res, 500, { error: 'Internal server error' });
        }
    }
}

loadData();

const server = http.createServer(handleRequest);

server.listen(PORT, HOST, () => {
    console.log(`Server running at http://${HOST}:${PORT}/`);
});
```
````
