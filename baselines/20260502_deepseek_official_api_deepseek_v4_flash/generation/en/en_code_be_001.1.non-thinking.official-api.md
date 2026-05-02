# Generation Transcript

- Case: `en_code_be_001`
- Language group: `en`
- Workload: `coding`
- Model: `deepseek-v4-flash`
- Round: `1`
- Thinking mode: `non-thinking`
- Thinking strength: `disabled`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `official-api`
- OK: `True`
- Status: PASS
- Check: expectation checks skipped
- Detail: `expectation checks skipped`
- Elapsed seconds: 33.984066
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 318, "completion_tokens": 2936, "total_tokens": 3254, "prompt_tokens_details": {"cached_tokens": 0}, "prompt_cache_hit_tokens": 0, "prompt_cache_miss_tokens": 318}`
- Prompt tokens: 318
- Completion tokens: 2936
- Total tokens: 3254

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

let ticketsData = [];
let nextId = 1;
let writeInProgress = false;
let writeQueue = [];

function loadData() {
    try {
        if (fs.existsSync(DATA_FILE)) {
            const raw = fs.readFileSync(DATA_FILE, 'utf8');
            if (raw.trim()) {
                const parsed = JSON.parse(raw);
                ticketsData = Array.isArray(parsed) ? parsed : [];
            } else {
                ticketsData = [];
            }
        } else {
            ticketsData = [];
        }
    } catch (err) {
        ticketsData = [];
    }

    if (ticketsData.length > 0) {
        const maxId = Math.max(...ticketsData.map(t => t.id || 0));
        nextId = maxId + 1;
    } else {
        nextId = 1;
    }
}

function saveData(callback) {
    if (writeInProgress) {
        writeQueue.push(callback);
        return;
    }

    writeInProgress = true;
    const jsonData = JSON.stringify(ticketsData, null, 2);

    fs.writeFile(DATA_FILE, jsonData, 'utf8', (err) => {
        writeInProgress = false;
        if (callback) callback(err);
        if (writeQueue.length > 0) {
            const nextCallback = writeQueue.shift();
            saveData(nextCallback);
        }
    });
}

function generateTimestamp() {
    return new Date().toISOString();
}

function createTicket(subject, description, priority) {
    const now = generateTimestamp();
    const ticket = {
        id: nextId++,
        subject: subject.trim(),
        description: description.trim(),
        priority: priority,
        status: 'open',
        created_at: now,
        updated_at: now
    };
    ticketsData.push(ticket);
    return ticket;
}

function validatePostBody(body) {
    const errors = [];

    if (!body.subject || typeof body.subject !== 'string' || body.subject.trim().length === 0) {
        errors.push('subject is required and must be a non-empty string');
    }

    if (!body.description || typeof body.description !== 'string' || body.description.trim().length === 0) {
        errors.push('description is required and must be a non-empty string');
    }

    const validPriorities = ['low', 'medium', 'high'];
    if (!body.priority || !validPriorities.includes(body.priority)) {
        errors.push('priority must be one of: low, medium, high');
    }

    return errors;
}

function validatePatchBody(body) {
    const errors = [];
    const allowedFields = ['subject', 'description', 'priority', 'status'];

    let hasValidField = false;
    for (const field of allowedFields) {
        if (body[field] !== undefined) {
            hasValidField = true;
            break;
        }
    }

    if (!hasValidField) {
        errors.push('At least one field must be provided: subject, description, priority, status');
    }

    if (body.subject !== undefined && (typeof body.subject !== 'string' || body.subject.trim().length === 0)) {
        errors.push('subject must be a non-empty string');
    }

    if (body.description !== undefined && (typeof body.description !== 'string' || body.description.trim().length === 0)) {
        errors.push('description must be a non-empty string');
    }

    const validPriorities = ['low', 'medium', 'high'];
    if (body.priority !== undefined && !validPriorities.includes(body.priority)) {
        errors.push('priority must be one of: low, medium, high');
    }

    const validStatuses = ['open', 'in_progress', 'resolved'];
    if (body.status !== undefined && !validStatuses.includes(body.status)) {
        errors.push('status must be one of: open, in_progress, resolved');
    }

    return errors;
}

function parseUrlEncoded(data) {
    const result = {};
    if (!data) return result;

    const pairs = data.split('&');
    for (const pair of pairs) {
        const [key, value] = pair.split('=').map(s => decodeURIComponent(s.replace(/\+/g, ' ')));
        if (key) {
            result[key] = value;
        }
    }
    return result;
}

function getRequestBody(req) {
    return new Promise((resolve, reject) => {
        let body = '';
        req.on('data', chunk => {
            body += chunk.toString();
        });
        req.on('end', () => {
            resolve(body);
        });
        req.on('error', reject);
    });
}

function parseJSONBody(body) {
    if (!body || body.trim().length === 0) {
        return null;
    }

    try {
        return JSON.parse(body);
    } catch (e) {
        return null;
    }
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

function parsePathAndQuery(url) {
    const [pathPart, queryString] = url.split('?');
    const queryParams = {};

    if (queryString) {
        const pairs = queryString.split('&');
        for (const pair of pairs) {
            const [key, value] = pair.split('=').map(s => decodeURIComponent(s));
            if (key) {
                queryParams[key] = value;
            }
        }
    }

    return { pathPart, queryParams };
}

function getTicketById(id) {
    return ticketsData.find(t => t.id === id);
}

function deleteTicketById(id) {
    const index = ticketsData.findIndex(t => t.id === id);
    if (index !== -1) {
        ticketsData.splice(index, 1);
        return true;
    }
    return false;
}

function handleMetrics() {
    const statusCounts = { open: 0, in_progress: 0, resolved: 0 };
    const priorityCounts = { low: 0, medium: 0, high: 0 };
    let totalAgeSeconds = 0;
    let openTicketCount = 0;
    const now = new Date();

    for (const ticket of ticketsData) {
        if (statusCounts[ticket.status] !== undefined) {
            statusCounts[ticket.status]++;
        }

        if (priorityCounts[ticket.priority] !== undefined) {
            priorityCounts[ticket.priority]++;
        }

        if (ticket.status === 'open') {
            const created = new Date(ticket.created_at);
            const ageMs = now - created;
            totalAgeSeconds += Math.floor(ageMs / 1000);
            openTicketCount++;
        }
    }

    const averageAge = openTicketCount > 0 ? Math.round(totalAgeSeconds / openTicketCount) : 0;

    return {
        by_status: statusCounts,
        by_priority: priorityCounts,
        average_open_age_seconds: averageAge
    };
}

// Load data on startup
loadData();

const server = http.createServer(async (req, res) => {
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

    const { pathPart, queryParams } = parsePathAndQuery(req.url);
    const pathParts = pathPart.split('/').filter(p => p.length > 0);

    try {
        // Route: GET /tickets
        if (req.method === 'GET' && pathParts.length === 1 && pathParts[0] === 'tickets') {
            let filteredTickets = [...ticketsData];

            if (queryParams.status) {
                filteredTickets = filteredTickets.filter(t => t.status === queryParams.status);
            }

            if (queryParams.priority) {
                filteredTickets = filteredTickets.filter(t => t.priority === queryParams.priority);
            }

            sendJSON(res, 200, filteredTickets);
            return;
        }

        // Route: GET /metrics
        if (req.method === 'GET' && pathParts.length === 1 && pathParts[0] === 'metrics') {
            const metrics = handleMetrics();
            sendJSON(res, 200, metrics);
            return;
        }

        // Route: POST /tickets
        if (req.method === 'POST' && pathParts.length === 1 && pathParts[0] === 'tickets') {
            const bodyString = await getRequestBody(req);
            const body = parseJSONBody(bodyString);

            if (!body) {
                sendJSON(res, 400, { error: 'Invalid JSON in request body' });
                return;
            }

            const errors = validatePostBody(body);
            if (errors.length > 0) {
                sendJSON(res, 400, { error: 'Validation failed', details: errors });
                return;
            }

            const ticket = createTicket(body.subject, body.description, body.priority);

            saveData((err) => {
                if (err) {
                    sendJSON(res, 500, { error: 'Failed to save data' });
                    return;
                }
                sendJSON(res, 201, ticket);
            });
            return;
        }

        // Routes with ID parameter: GET /tickets/{id}, PATCH /tickets/{id}, DELETE /tickets/{id}
        if (pathParts.length === 2 && pathParts[0] === 'tickets') {
            const id = parseInt(pathParts[1], 10);

            if (isNaN(id)) {
                sendJSON(res, 400, { error: 'Invalid ticket ID format' });
                return;
            }

            // GET /tickets/{id}
            if (req.method === 'GET') {
                const ticket = getTicketById(id);
                if (!ticket) {
                    sendJSON(res, 404, { error: 'Ticket not found' });
                    return;
                }
                sendJSON(res, 200, ticket);
                return;
            }

            // PATCH /tickets/{id}
            if (req.method === 'PATCH') {
                const ticket = getTicketById(id);
                if (!ticket) {
                    sendJSON(res, 404, { error: 'Ticket not found' });
                    return;
                }

                const bodyString = await getRequestBody(req);
                const body = parseJSONBody(bodyString);

                if (!body) {
                    sendJSON(res, 400, { error: 'Invalid JSON in request body' });
                    return;
                }

                const errors = validatePatchBody(body);
                if (errors.length > 0) {
                    sendJSON(res, 400, { error: 'Validation failed', details: errors });
                    return;
                }

                if (body.subject !== undefined) ticket.subject = body.subject.trim();
                if (body.description !== undefined) ticket.description = body.description.trim();
                if (body.priority !== undefined) ticket.priority = body.priority;
                if (body.status !== undefined) ticket.status = body.status;
                ticket.updated_at = generateTimestamp();

                saveData((err) => {
                    if (err) {
                        sendJSON(res, 500, { error: 'Failed to save data' });
                        return;
                    }
                    sendJSON(res, 200, ticket);
                });
                return;
            }

            // DELETE /tickets/{id}
            if (req.method === 'DELETE') {
                const deleted = deleteTicketById(id);
                if (!deleted) {
                    sendJSON(res, 404, { error: 'Ticket not found' });
                    return;
                }

                saveData((err) => {
                    if (err) {
                        sendJSON(res, 500, { error: 'Failed to save data' });
                        return;
                    }
                    sendJSON(res, 200, { message: 'Ticket deleted successfully' });
                });
                return;
            }
        }

        // If we reach here, route not found or method not allowed
        if (pathParts.length === 1 && pathParts[0] === 'tickets' && req.method !== 'GET' && req.method !== 'POST') {
            sendJSON(res, 405, { error: 'Method not allowed' });
            return;
        }

        if (pathParts.length === 2 && pathParts[0] === 'tickets' && req.method !== 'GET' && req.method !== 'PATCH' && req.method !== 'DELETE') {
            sendJSON(res, 405, { error: 'Method not allowed' });
            return;
        }

        sendJSON(res, 404, { error: 'Route not found' });

    } catch (err) {
        console.error('Server error:', err);
        sendJSON(res, 500, { error: 'Internal server error' });
    }
});

server.listen(PORT, HOST, () => {
    console.log(`Server running at http://${HOST}:${PORT}/`);
});
```
````
