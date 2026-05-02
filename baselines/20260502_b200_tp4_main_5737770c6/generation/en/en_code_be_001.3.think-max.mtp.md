# Generation Transcript

- Case: `en_code_be_001`
- Language group: `en`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `3`
- Thinking mode: `think-max`
- Thinking strength: `max`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 8.436896
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 318, "total_tokens": 2838, "completion_tokens": 2520, "prompt_tokens_details": null}`
- Prompt tokens: 318
- Completion tokens: 2520
- Total tokens: 2838

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

// Initialize data file if it doesn't exist
function initDataFile() {
    try {
        if (!fs.existsSync(DATA_FILE)) {
            fs.writeFileSync(DATA_FILE, '[]', 'utf8');
        }
    } catch (err) {
        console.error('Failed to initialize data file:', err);
        process.exit(1);
    }
}

// Read tickets from file
function readTickets() {
    try {
        const data = fs.readFileSync(DATA_FILE, 'utf8');
        return JSON.parse(data);
    } catch (err) {
        if (err.code === 'ENOENT') {
            return [];
        }
        throw err;
    }
}

// Write tickets to file atomically
function writeTickets(tickets) {
    const tempFile = DATA_FILE + '.tmp';
    fs.writeFileSync(tempFile, JSON.stringify(tickets, null, 2), 'utf8');
    fs.renameSync(tempFile, DATA_FILE);
}

// Generate unique ID
function generateId(tickets) {
    const maxId = tickets.reduce((max, t) => Math.max(max, parseInt(t.id) || 0), 0);
    return String(maxId + 1);
}

// Validate ticket required fields
function validateTicket(body) {
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
    if (!body.status || !['open', 'in_progress', 'resolved'].includes(body.status)) {
        errors.push('status must be one of: open, in_progress, resolved');
    }
    return errors;
}

// Validate update fields
function validateUpdate(body) {
    const errors = [];
    const allowedFields = ['subject', 'description', 'priority', 'status'];

    for (const key of Object.keys(body)) {
        if (!allowedFields.includes(key)) {
            errors.push(`Cannot update field: ${key}`);
        }
    }

    if (body.subject !== undefined && (typeof body.subject !== 'string' || body.subject.trim() === '')) {
        errors.push('subject must be a non-empty string');
    }
    if (body.description !== undefined && (typeof body.description !== 'string' || body.description.trim() === '')) {
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

// Calculate average age of open tickets in seconds
function calculateAverageAge(tickets) {
    const openTickets = tickets.filter(t => t.status === 'open');
    if (openTickets.length === 0) return 0;

    const now = Date.now();
    const totalAge = openTickets.reduce((sum, t) => {
        const created = new Date(t.created_at).getTime();
        return sum + (now - created);
    }, 0);

    return Math.floor(totalAge / openTickets.length / 1000);
}

// Get metrics
function getMetrics(tickets) {
    const byStatus = { open: 0, in_progress: 0, resolved: 0 };
    const byPriority = { low: 0, medium: 0, high: 0 };

    tickets.forEach(t => {
        if (byStatus.hasOwnProperty(t.status)) byStatus[t.status]++;
        if (byPriority.hasOwnProperty(t.priority)) byPriority[t.priority]++;
    });

    return {
        byStatus,
        byPriority,
        averageOpenAgeSeconds: calculateAverageAge(tickets)
    };
}

// Send JSON response
function sendJSON(res, statusCode, data) {
    res.writeHead(statusCode, {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type'
    });
    res.end(JSON.stringify(data));
}

// Parse request body
function parseBody(req) {
    return new Promise((resolve, reject) => {
        let body = '';
        req.on('data', chunk => {
            body += chunk.toString();
            if (body.length > 1e6) {
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

// Parse URL and extract path and params
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

// Route handler
async function handleRequest(req, res) {
    const { path: urlPath, params } = parseUrl(req.url);
    const method = req.method.toUpperCase();

    // CORS preflight
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
        // Route: GET /metrics
        if (urlPath === '/metrics' && method === 'GET') {
            const tickets = readTickets();
            const metrics = getMetrics(tickets);
            sendJSON(res, 200, metrics);
            return;
        }

        // Route: GET /tickets
        if (urlPath === '/tickets' && method === 'GET') {
            let tickets = readTickets();

            if (params.status) {
                tickets = tickets.filter(t => t.status === params.status);
            }
            if (params.priority) {
                tickets = tickets.filter(t => t.priority === params.priority);
            }

            sendJSON(res, 200, tickets);
            return;
        }

        // Route: POST /tickets
        if (urlPath === '/tickets' && method === 'POST') {
            const body = await parseBody(req);
            const errors = validateTicket(body);

            if (errors.length > 0) {
                sendJSON(res, 400, { error: 'Validation failed', details: errors });
                return;
            }

            const tickets = readTickets();
            const now = new Date().toISOString();

            const ticket = {
                id: generateId(tickets),
                subject: body.subject.trim(),
                description: body.description.trim(),
                priority: body.priority,
                status: body.status,
                created_at: now,
                updated_at: now
            };

            tickets.push(ticket);
            writeTickets(tickets);

            sendJSON(res, 201, ticket);
            return;
        }

        // Routes with ID parameter
        const ticketMatch = urlPath.match(/^\/tickets\/(\d+)$/);
        if (ticketMatch) {
            const id = ticketMatch[1];

            // GET /tickets/{id}
            if (method === 'GET') {
                const tickets = readTickets();
                const ticket = tickets.find(t => t.id === id);

                if (!ticket) {
                    sendJSON(res, 404, { error: 'Ticket not found' });
                    return;
                }

                sendJSON(res, 200, ticket);
                return;
            }

            // PATCH /tickets/{id}
            if (method === 'PATCH') {
                const body = await parseBody(req);
                const errors = validateUpdate(body);

                if (errors.length > 0) {
                    sendJSON(res, 400, { error: 'Validation failed', details: errors });
                    return;
                }

                if (Object.keys(body).length === 0) {
                    sendJSON(res, 400, { error: 'No fields to update' });
                    return;
                }

                const tickets = readTickets();
                const index = tickets.findIndex(t => t.id === id);

                if (index === -1) {
                    sendJSON(res, 404, { error: 'Ticket not found' });
                    return;
                }

                const now = new Date().toISOString();
                const updatedTicket = { ...tickets[index], updated_at: now };

                if (body.subject !== undefined) updatedTicket.subject = body.subject.trim();
                if (body.description !== undefined) updatedTicket.description = body.description.trim();
                if (body.priority !== undefined) updatedTicket.priority = body.priority;
                if (body.status !== undefined) updatedTicket.status = body.status;

                tickets[index] = updatedTicket;
                writeTickets(tickets);

                sendJSON(res, 200, updatedTicket);
                return;
            }

            // DELETE /tickets/{id}
            if (method === 'DELETE') {
                const tickets = readTickets();
                const index = tickets.findIndex(t => t.id === id);

                if (index === -1) {
                    sendJSON(res, 404, { error: 'Ticket not found' });
                    return;
                }

                const deleted = tickets.splice(index, 1)[0];
                writeTickets(tickets);

                sendJSON(res, 200, { message: 'Ticket deleted', ticket: deleted });
                return;
            }

            // Unsupported method on /tickets/{id}
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

// Create and start server
initDataFile();

const server = http.createServer(handleRequest);

server.listen(PORT, HOST, () => {
    console.log(`Help desk API server running at http://${HOST}:${PORT}`);
});
```
````
