# Generation Transcript

- Case: `en_code_be_001`
- Language group: `en`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `2`
- Thinking mode: `think-high`
- Thinking strength: `high`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 23.709431
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 318, "total_tokens": 3223, "completion_tokens": 2905, "prompt_tokens_details": null}`
- Prompt tokens: 318
- Completion tokens: 2905
- Total tokens: 3223

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
    try {
        fs.writeFileSync(DATA_FILE, '[]', 'utf8');
    } catch (err) {
        console.error('Failed to create data file:', err);
        process.exit(1);
    }
}

// Read tickets with retry for safety
function readTickets() {
    let retries = 3;
    while (retries > 0) {
        try {
            const data = fs.readFileSync(DATA_FILE, 'utf8');
            return JSON.parse(data);
        } catch (err) {
            if (err.code === 'ENOENT') {
                return [];
            }
            retries--;
            if (retries === 0) {
                throw new Error('Failed to read tickets data');
            }
            // Wait briefly before retry
            require('timers').sleep || (() => {})(); // No-op fallback
        }
    }
    return [];
}

// Write tickets with atomic write
function writeTickets(tickets) {
    const tmpFile = DATA_FILE + '.tmp';
    fs.writeFileSync(tmpFile, JSON.stringify(tickets, null, 2), 'utf8');
    fs.renameSync(tmpFile, DATA_FILE);
}

// Generate unique ID
function generateId() {
    return Date.now().toString(36) + Math.random().toString(36).substr(2, 9);
}

// Validate ticket fields
function validateTicket(body) {
    const errors = [];
    const ticket = {};

    if (!body.subject || typeof body.subject !== 'string' || body.subject.trim() === '') {
        errors.push('subject is required and must be a non-empty string');
    } else {
        ticket.subject = body.subject.trim();
    }

    if (!body.description || typeof body.description !== 'string' || body.description.trim() === '') {
        errors.push('description is required and must be a non-empty string');
    } else {
        ticket.description = body.description.trim();
    }

    if (body.priority) {
        const validPriorities = ['low', 'medium', 'high'];
        if (!validPriorities.includes(body.priority)) {
            errors.push('priority must be one of: low, medium, high');
        } else {
            ticket.priority = body.priority;
        }
    } else {
        ticket.priority = 'low'; // Default
    }

    if (body.status) {
        const validStatuses = ['open', 'in_progress', 'resolved'];
        if (!validStatuses.includes(body.status)) {
            errors.push('status must be one of: open, in_progress, resolved');
        } else {
            ticket.status = body.status;
        }
    } else {
        ticket.status = 'open'; // Default
    }

    return { errors, ticket };
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

// Parse URL path
function parsePath(url) {
    const parsed = new URL(url, `http://${HOST}:${PORT}`);
    const pathParts = parsed.pathname.split('/').filter(Boolean);
    return {
        pathname: parsed.pathname,
        pathParts,
        searchParams: parsed.searchParams
    };
}

// Handle GET /tickets
function handleGetTickets(res, searchParams) {
    try {
        let tickets = readTickets();
        const status = searchParams.get('status');
        const priority = searchParams.get('priority');

        if (status) {
            tickets = tickets.filter(t => t.status === status);
        }
        if (priority) {
            tickets = tickets.filter(t => t.priority === priority);
        }

        sendJson(res, 200, tickets);
    } catch (err) {
        sendJson(res, 500, { error: 'Internal server error' });
    }
}

// Handle POST /tickets
async function handlePostTickets(req, res) {
    try {
        const body = await parseBody(req);
        if (!body) {
            sendJson(res, 400, { error: 'Request body is required' });
            return;
        }

        const { errors, ticket: validatedTicket } = validateTicket(body);
        if (errors.length > 0) {
            sendJson(res, 400, { error: errors.join('; ') });
            return;
        }

        const now = new Date().toISOString();
        const ticket = {
            id: generateId(),
            ...validatedTicket,
            created_at: now,
            updated_at: now
        };

        const tickets = readTickets();
        tickets.push(ticket);
        writeTickets(tickets);

        sendJson(res, 201, ticket);
    } catch (err) {
        if (err.message === 'Invalid JSON') {
            sendJson(res, 400, { error: 'Invalid JSON in request body' });
        } else {
            sendJson(res, 500, { error: 'Internal server error' });
        }
    }
}

// Handle GET /tickets/:id
function handleGetTicket(res, id) {
    try {
        const tickets = readTickets();
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

// Handle PATCH /tickets/:id
async function handlePatchTicket(req, res, id) {
    try {
        const body = await parseBody(req);
        if (!body) {
            sendJson(res, 400, { error: 'Request body is required' });
            return;
        }

        const tickets = readTickets();
        const index = tickets.findIndex(t => t.id === id);
        if (index === -1) {
            sendJson(res, 404, { error: 'Ticket not found' });
            return;
        }

        const allowedFields = ['subject', 'description', 'priority', 'status'];
        const updates = {};
        const errors = [];

        for (const [key, value] of Object.entries(body)) {
            if (!allowedFields.includes(key)) {
                errors.push(`Cannot update field: ${key}`);
                continue;
            }

            if (key === 'subject' || key === 'description') {
                if (typeof value !== 'string' || value.trim() === '') {
                    errors.push(`${key} must be a non-empty string`);
                } else {
                    updates[key] = value.trim();
                }
            } else if (key === 'priority') {
                const validPriorities = ['low', 'medium', 'high'];
                if (!validPriorities.includes(value)) {
                    errors.push('priority must be one of: low, medium, high');
                } else {
                    updates[key] = value;
                }
            } else if (key === 'status') {
                const validStatuses = ['open', 'in_progress', 'resolved'];
                if (!validStatuses.includes(value)) {
                    errors.push('status must be one of: open, in_progress, resolved');
                } else {
                    updates[key] = value;
                }
            }
        }

        if (errors.length > 0) {
            sendJson(res, 400, { error: errors.join('; ') });
            return;
        }

        if (Object.keys(updates).length === 0) {
            sendJson(res, 400, { error: 'No valid fields to update' });
            return;
        }

        tickets[index] = {
            ...tickets[index],
            ...updates,
            updated_at: new Date().toISOString()
        };

        writeTickets(tickets);
        sendJson(res, 200, tickets[index]);
    } catch (err) {
        if (err.message === 'Invalid JSON') {
            sendJson(res, 400, { error: 'Invalid JSON in request body' });
        } else {
            sendJson(res, 500, { error: 'Internal server error' });
        }
    }
}

// Handle DELETE /tickets/:id
function handleDeleteTicket(res, id) {
    try {
        const tickets = readTickets();
        const index = tickets.findIndex(t => t.id === id);
        if (index === -1) {
            sendJson(res, 404, { error: 'Ticket not found' });
            return;
        }

        tickets.splice(index, 1);
        writeTickets(tickets);
        sendJson(res, 204, null);
    } catch (err) {
        sendJson(res, 500, { error: 'Internal server error' });
    }
}

// Handle GET /metrics
function handleGetMetrics(res) {
    try {
        const tickets = readTickets();
        const now = new Date();

        // Count by status
        const statusCounts = { open: 0, in_progress: 0, resolved: 0 };
        // Count by priority
        const priorityCounts = { low: 0, medium: 0, high: 0 };
        // Sum of ages for open tickets in seconds
        let openAgeSum = 0;
        let openCount = 0;

        tickets.forEach(ticket => {
            // Status counts
            if (statusCounts.hasOwnProperty(ticket.status)) {
                statusCounts[ticket.status]++;
            }

            // Priority counts
            if (priorityCounts.hasOwnProperty(ticket.priority)) {
                priorityCounts[ticket.priority]++;
            }

            // Open ticket age
            if (ticket.status === 'open') {
                const created = new Date(ticket.created_at);
                const ageInSeconds = (now - created) / 1000;
                openAgeSum += ageInSeconds;
                openCount++;
            }
        });

        const metrics = {
            by_status: statusCounts,
            by_priority: priorityCounts,
            average_open_age_seconds: openCount > 0 ? (openAgeSum / openCount) : 0
        };

        sendJson(res, 200, metrics);
    } catch (err) {
        sendJson(res, 500, { error: 'Internal server error' });
    }
}

// Create HTTP server
const server = http.createServer(async (req, res) => {
    setCorsHeaders(res);

    // Handle OPTIONS preflight
    if (req.method === 'OPTIONS') {
        res.writeHead(204);
        res.end();
        return;
    }

    const { pathname, pathParts, searchParams } = parsePath(req.url);

    try {
        // Route: GET /tickets
        if (req.method === 'GET' && pathname === '/tickets' && pathParts.length === 1) {
            handleGetTickets(res, searchParams);
            return;
        }

        // Route: POST /tickets
        if (req.method === 'POST' && pathname === '/tickets' && pathParts.length === 1) {
            await handlePostTickets(req, res);
            return;
        }

        // Route: GET /metrics
        if (req.method === 'GET' && pathname === '/metrics' && pathParts.length === 1) {
            handleGetMetrics(res);
            return;
        }

        // Routes with ID parameter: /tickets/:id
        if (pathParts.length === 2 && pathParts[0] === 'tickets') {
            const id = pathParts[1];

            if (req.method === 'GET') {
                handleGetTicket(res, id);
                return;
            }

            if (req.method === 'PATCH') {
                await handlePatchTicket(req, res, id);
                return;
            }

            if (req.method === 'DELETE') {
                handleDeleteTicket(res, id);
                return;
            }

            sendJson(res, 405, { error: 'Method not allowed' });
            return;
        }

        // Unknown route
        sendJson(res, 404, { error: 'Not found' });

    } catch (err) {
        console.error('Server error:', err);
        sendJson(res, 500, { error: 'Internal server error' });
    }
});

server.listen(PORT, HOST, () => {
    console.log(`Server running at http://${HOST}:${PORT}/`);
});
```
````
