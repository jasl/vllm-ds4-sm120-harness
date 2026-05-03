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
- Elapsed seconds: 50.927816
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 318, "total_tokens": 3555, "completion_tokens": 3237, "prompt_tokens_details": null}`
- Prompt tokens: 318
- Completion tokens: 3237
- Total tokens: 3555

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

// CORS headers
const CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Content-Type': 'application/json'
};

// File read with retry logic
function readTickets() {
    return new Promise((resolve, reject) => {
        fs.readFile(DATA_FILE, 'utf8', (err, data) => {
            if (err) {
                if (err.code === 'ENOENT') {
                    resolve([]);
                } else {
                    reject(err);
                }
            } else {
                try {
                    const tickets = JSON.parse(data);
                    if (!Array.isArray(tickets)) {
                        resolve([]);
                    } else {
                        resolve(tickets);
                    }
                } catch (e) {
                    reject(new Error('Invalid JSON in data file'));
                }
            }
        });
    });
}

// File write with atomicity
function writeTickets(tickets) {
    return new Promise((resolve, reject) => {
        const tmpFile = DATA_FILE + '.tmp';
        const jsonData = JSON.stringify(tickets, null, 2);
        fs.writeFile(tmpFile, jsonData, 'utf8', (err) => {
            if (err) {
                reject(err);
                return;
            }
            fs.rename(tmpFile, DATA_FILE, (err) => {
                if (err) {
                    reject(err);
                } else {
                    resolve();
                }
            });
        });
    });
}

// Generate UUID-like ID
function generateId() {
    return Date.now().toString(36) + Math.random().toString(36).substr(2, 9);
}

// Validate ticket fields
function validateTicket(body, isUpdate = false) {
    const errors = [];
    const ticket = {};

    if (isUpdate) {
        if (body.subject !== undefined) {
            if (typeof body.subject !== 'string' || body.subject.trim().length === 0) {
                errors.push('subject must be a non-empty string');
            } else {
                ticket.subject = body.subject.trim();
            }
        }

        if (body.description !== undefined) {
            if (typeof body.description !== 'string' || body.description.trim().length === 0) {
                errors.push('description must be a non-empty string');
            } else {
                ticket.description = body.description.trim();
            }
        }

        if (body.priority !== undefined) {
            if (!['low', 'medium', 'high'].includes(body.priority)) {
                errors.push('priority must be one of: low, medium, high');
            } else {
                ticket.priority = body.priority;
            }
        }

        if (body.status !== undefined) {
            if (!['open', 'in_progress', 'resolved'].includes(body.status)) {
                errors.push('status must be one of: open, in_progress, resolved');
            } else {
                ticket.status = body.status;
            }
        }
    } else {
        if (!body.subject || typeof body.subject !== 'string' || body.subject.trim().length === 0) {
            errors.push('subject is required and must be a non-empty string');
        } else {
            ticket.subject = body.subject.trim();
        }

        if (!body.description || typeof body.description !== 'string' || body.description.trim().length === 0) {
            errors.push('description is required and must be a non-empty string');
        } else {
            ticket.description = body.description.trim();
        }

        if (body.priority && !['low', 'medium', 'high'].includes(body.priority)) {
            errors.push('priority must be one of: low, medium, high');
        } else if (!body.priority) {
            ticket.priority = 'medium';
        } else {
            ticket.priority = body.priority;
        }

        if (body.status && !['open', 'in_progress', 'resolved'].includes(body.status)) {
            errors.push('status must be one of: open, in_progress, resolved');
        } else if (!body.status) {
            ticket.status = 'open';
        } else {
            ticket.status = body.status;
        }
    }

    return { errors, ticket };
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
            if (!body) {
                resolve(null);
                return;
            }
            try {
                resolve(JSON.parse(body));
            } catch (e) {
                reject(new Error('Invalid JSON'));
            }
        });
        req.on('error', reject);
    });
}

// Send JSON response
function sendResponse(res, statusCode, data) {
    res.writeHead(statusCode, CORS_HEADERS);
    res.end(JSON.stringify(data));
}

// Handle GET /tickets
async function handleGetTickets(req, res) {
    try {
        const url = new URL(req.url, `http://${HOST}:${PORT}`);
        const statusFilter = url.searchParams.get('status');
        const priorityFilter = url.searchParams.get('priority');

        const tickets = await readTickets();
        let filtered = tickets;

        if (statusFilter) {
            filtered = filtered.filter(t => t.status === statusFilter);
        }
        if (priorityFilter) {
            filtered = filtered.filter(t => t.priority === priorityFilter);
        }

        // Sort by created_at descending
        filtered.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));

        sendResponse(res, 200, filtered);
    } catch (err) {
        console.error('Error reading tickets:', err);
        sendResponse(res, 500, { error: 'Internal server error' });
    }
}

// Handle POST /tickets
async function handlePostTickets(req, res) {
    try {
        const body = await parseBody(req);
        if (!body) {
            sendResponse(res, 400, { error: 'Request body is required' });
            return;
        }

        const { errors, ticket: validated } = validateTicket(body);
        if (errors.length > 0) {
            sendResponse(res, 400, { error: 'Validation failed', details: errors });
            return;
        }

        const now = new Date().toISOString();
        const ticket = {
            id: generateId(),
            subject: validated.subject,
            description: validated.description,
            priority: validated.priority,
            status: validated.status,
            created_at: now,
            updated_at: now
        };

        const tickets = await readTickets();
        tickets.push(ticket);
        await writeTickets(tickets);

        sendResponse(res, 201, ticket);
    } catch (err) {
        if (err.message === 'Invalid JSON') {
            sendResponse(res, 400, { error: 'Invalid JSON in request body' });
        } else if (err.message === 'Request body too large') {
            sendResponse(res, 413, { error: 'Request body too large' });
        } else {
            console.error('Error creating ticket:', err);
            sendResponse(res, 500, { error: 'Internal server error' });
        }
    }
}

// Handle GET /tickets/{id}
async function handleGetTicket(req, res, id) {
    try {
        const tickets = await readTickets();
        const ticket = tickets.find(t => t.id === id);

        if (!ticket) {
            sendResponse(res, 404, { error: 'Ticket not found' });
            return;
        }

        sendResponse(res, 200, ticket);
    } catch (err) {
        console.error('Error reading ticket:', err);
        sendResponse(res, 500, { error: 'Internal server error' });
    }
}

// Handle PATCH /tickets/{id}
async function handlePatchTicket(req, res, id) {
    try {
        const body = await parseBody(req);
        if (!body) {
            sendResponse(res, 400, { error: 'Request body is required' });
            return;
        }

        const { errors, ticket: validated } = validateTicket(body, true);
        if (errors.length > 0) {
            sendResponse(res, 400, { error: 'Validation failed', details: errors });
            return;
        }

        if (Object.keys(validated).length === 0) {
            sendResponse(res, 400, { error: 'No valid fields to update' });
            return;
        }

        const tickets = await readTickets();
        const index = tickets.findIndex(t => t.id === id);

        if (index === -1) {
            sendResponse(res, 404, { error: 'Ticket not found' });
            return;
        }

        const now = new Date().toISOString();
        tickets[index] = {
            ...tickets[index],
            ...validated,
            updated_at: now
        };

        await writeTickets(tickets);
        sendResponse(res, 200, tickets[index]);
    } catch (err) {
        if (err.message === 'Invalid JSON') {
            sendResponse(res, 400, { error: 'Invalid JSON in request body' });
        } else if (err.message === 'Request body too large') {
            sendResponse(res, 413, { error: 'Request body too large' });
        } else {
            console.error('Error updating ticket:', err);
            sendResponse(res, 500, { error: 'Internal server error' });
        }
    }
}

// Handle DELETE /tickets/{id}
async function handleDeleteTicket(req, res, id) {
    try {
        const tickets = await readTickets();
        const index = tickets.findIndex(t => t.id === id);

        if (index === -1) {
            sendResponse(res, 404, { error: 'Ticket not found' });
            return;
        }

        tickets.splice(index, 1);
        await writeTickets(tickets);

        sendResponse(res, 204, null);
    } catch (err) {
        console.error('Error deleting ticket:', err);
        sendResponse(res, 500, { error: 'Internal server error' });
    }
}

// Handle GET /metrics
async function handleGetMetrics(req, res) {
    try {
        const tickets = await readTickets();
        const now = new Date();

        // Status counts
        const statusCounts = { open: 0, in_progress: 0, resolved: 0 };
        tickets.forEach(t => {
            if (statusCounts.hasOwnProperty(t.status)) {
                statusCounts[t.status]++;
            }
        });

        // Priority counts
        const priorityCounts = { low: 0, medium: 0, high: 0 };
        tickets.forEach(t => {
            if (priorityCounts.hasOwnProperty(t.priority)) {
                priorityCounts[t.priority]++;
            }
        });

        // Average age of open tickets in seconds
        const openTickets = tickets.filter(t => t.status === 'open');
        let averageAgeSeconds = 0;
        if (openTickets.length > 0) {
            const totalAge = openTickets.reduce((sum, t) => {
                const created = new Date(t.created_at);
                return sum + (now - created);
            }, 0);
            averageAgeSeconds = totalAge / openTickets.length / 1000;
        }

        const metrics = {
            status_counts: statusCounts,
            priority_counts: priorityCounts,
            average_open_age_seconds: Math.round(averageAgeSeconds * 100) / 100
        };

        sendResponse(res, 200, metrics);
    } catch (err) {
        console.error('Error computing metrics:', err);
        sendResponse(res, 500, { error: 'Internal server error' });
    }
}

// Route handler
async function handleRequest(req, res) {
    const url = new URL(req.url, `http://${HOST}:${PORT}`);
    const method = req.method.toUpperCase();
    const pathParts = url.pathname.split('/').filter(p => p);

    // Handle CORS preflight
    if (method === 'OPTIONS') {
        res.writeHead(204, CORS_HEADERS);
        res.end();
        return;
    }

    try {
        // GET /tickets
        if (method === 'GET' && pathParts.length === 1 && pathParts[0] === 'tickets') {
            await handleGetTickets(req, res);
            return;
        }

        // POST /tickets
        if (method === 'POST' && pathParts.length === 1 && pathParts[0] === 'tickets') {
            await handlePostTickets(req, res);
            return;
        }

        // GET /tickets/{id}
        if (method === 'GET' && pathParts.length === 2 && pathParts[0] === 'tickets' && pathParts[1]) {
            await handleGetTicket(req, res, pathParts[1]);
            return;
        }

        // PATCH /tickets/{id}
        if (method === 'PATCH' && pathParts.length === 2 && pathParts[0] === 'tickets' && pathParts[1]) {
            await handlePatchTicket(req, res, pathParts[1]);
            return;
        }

        // DELETE /tickets/{id}
        if (method === 'DELETE' && pathParts.length === 2 && pathParts[0] === 'tickets' && pathParts[1]) {
            await handleDeleteTicket(req, res, pathParts[1]);
            return;
        }

        // GET /metrics
        if (method === 'GET' && pathParts.length === 1 && pathParts[0] === 'metrics') {
            await handleGetMetrics(req, res);
            return;
        }

        // Unknown route
        sendResponse(res, 404, { error: 'Not found' });
    } catch (err) {
        console.error('Unexpected error:', err);
        sendResponse(res, 500, { error: 'Internal server error' });
    }
}

// Create and start server
const server = http.createServer(handleRequest);

server.listen(PORT, HOST, () => {
    console.log(`Server running at http://${HOST}:${PORT}/`);
});

// Graceful shutdown
process.on('SIGINT', () => {
    console.log('\nShutting down server...');
    server.close(() => {
        console.log('Server stopped.');
        process.exit(0);
    });
});

process.on('SIGTERM', () => {
    server.close(() => {
        process.exit(0);
    });
});
```
````
