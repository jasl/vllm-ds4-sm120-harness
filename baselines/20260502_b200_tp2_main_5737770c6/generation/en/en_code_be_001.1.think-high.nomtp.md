# Generation Transcript

- Case: `en_code_be_001`
- Language group: `en`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `1`
- Thinking mode: `think-high`
- Thinking strength: `high`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 21.120792
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 318, "total_tokens": 2901, "completion_tokens": 2583, "prompt_tokens_details": null}`
- Prompt tokens: 318
- Completion tokens: 2583
- Total tokens: 2901

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

const PORT = 8080;
const HOST = '127.0.0.1';
const DATA_FILE = path.join(__dirname, 'tickets.json');

// CORS headers
const CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    'Content-Type': 'application/json'
};

// Initialize data file if it doesn't exist
function initDataFile() {
    if (!fs.existsSync(DATA_FILE)) {
        fs.writeFileSync(DATA_FILE, JSON.stringify({ tickets: [], counter: 0 }), 'utf8');
    }
}

// Read tickets from file
function readData() {
    try {
        const raw = fs.readFileSync(DATA_FILE, 'utf8');
        return JSON.parse(raw);
    } catch (err) {
        throw new Error('Failed to read data file');
    }
}

// Write tickets to file
function writeData(data) {
    try {
        fs.writeFileSync(DATA_FILE, JSON.stringify(data, null, 2), 'utf8');
    } catch (err) {
        throw new Error('Failed to write data file');
    }
}

// Validate ticket fields
function validateTicket(body, isUpdate = false) {
    const errors = [];
    const allowedPriority = ['low', 'medium', 'high'];
    const allowedStatus = ['open', 'in_progress', 'resolved'];

    if (!isUpdate) {
        if (!body.subject || typeof body.subject !== 'string' || body.subject.trim() === '') {
            errors.push('subject is required and must be a non-empty string');
        }
        if (!body.description || typeof body.description !== 'string' || body.description.trim() === '') {
            errors.push('description is required and must be a non-empty string');
        }
    }

    if (body.subject !== undefined && (typeof body.subject !== 'string' || body.subject.trim() === '')) {
        errors.push('subject must be a non-empty string');
    }

    if (body.description !== undefined && (typeof body.description !== 'string' || body.description.trim() === '')) {
        errors.push('description must be a non-empty string');
    }

    if (body.priority !== undefined) {
        if (!allowedPriority.includes(body.priority)) {
            errors.push(`priority must be one of: ${allowedPriority.join(', ')}`);
        }
    } else if (!isUpdate) {
        errors.push('priority is required');
    }

    if (body.status !== undefined) {
        if (!allowedStatus.includes(body.status)) {
            errors.push(`status must be one of: ${allowedStatus.join(', ')}`);
        }
    } else if (!isUpdate) {
        errors.push('status is required');
    }

    return errors;
}

// Parse and validate JSON body
function parseBody(req) {
    return new Promise((resolve, reject) => {
        let body = '';
        req.on('data', chunk => {
            body += chunk.toString();
        });
        req.on('end', () => {
            if (!body) {
                reject(new Error('Request body is empty'));
                return;
            }
            try {
                resolve(JSON.parse(body));
            } catch (err) {
                reject(new Error('Invalid JSON in request body'));
            }
        });
        req.on('error', err => {
            reject(err);
        });
    });
}

// Send JSON response
function sendJSON(res, statusCode, data) {
    res.writeHead(statusCode, CORS_HEADERS);
    res.end(JSON.stringify(data));
}

// Handle GET /tickets
function getTickets(req, res) {
    const query = url.parse(req.url, true).query;
    const data = readData();
    let tickets = data.tickets;

    if (query.status) {
        tickets = tickets.filter(t => t.status === query.status);
    }
    if (query.priority) {
        tickets = tickets.filter(t => t.priority === query.priority);
    }

    sendJSON(res, 200, { success: true, data: tickets });
}

// Handle POST /tickets
async function postTickets(req, res) {
    try {
        const body = await parseBody(req);
        const errors = validateTicket(body);
        if (errors.length > 0) {
            sendJSON(res, 400, { success: false, errors });
            return;
        }

        const data = readData();
        data.counter += 1;
        const now = new Date().toISOString();
        const ticket = {
            id: data.counter,
            subject: body.subject.trim(),
            description: body.description.trim(),
            priority: body.priority,
            status: body.status,
            created_at: now,
            updated_at: now
        };

        data.tickets.push(ticket);
        writeData(data);
        sendJSON(res, 201, { success: true, data: ticket });
    } catch (err) {
        sendJSON(res, 400, { success: false, error: err.message });
    }
}

// Handle GET /tickets/{id}
function getTicketById(req, res, id) {
    const data = readData();
    const ticket = data.tickets.find(t => t.id === parseInt(id));
    if (!ticket) {
        sendJSON(res, 404, { success: false, error: 'Ticket not found' });
        return;
    }
    sendJSON(res, 200, { success: true, data: ticket });
}

// Handle PATCH /tickets/{id}
async function patchTicket(req, res, id) {
    try {
        const body = await parseBody(req);
        const data = readData();
        const ticketIndex = data.tickets.findIndex(t => t.id === parseInt(id));

        if (ticketIndex === -1) {
            sendJSON(res, 404, { success: false, error: 'Ticket not found' });
            return;
        }

        const errors = validateTicket(body, true);
        if (errors.length > 0) {
            sendJSON(res, 400, { success: false, errors });
            return;
        }

        const ticket = data.tickets[ticketIndex];
        if (body.subject !== undefined) ticket.subject = body.subject.trim();
        if (body.description !== undefined) ticket.description = body.description.trim();
        if (body.priority !== undefined) ticket.priority = body.priority;
        if (body.status !== undefined) ticket.status = body.status;
        ticket.updated_at = new Date().toISOString();

        data.tickets[ticketIndex] = ticket;
        writeData(data);
        sendJSON(res, 200, { success: true, data: ticket });
    } catch (err) {
        sendJSON(res, 400, { success: false, error: err.message });
    }
}

// Handle DELETE /tickets/{id}
function deleteTicket(req, res, id) {
    const data = readData();
    const ticketIndex = data.tickets.findIndex(t => t.id === parseInt(id));

    if (ticketIndex === -1) {
        sendJSON(res, 404, { success: false, error: 'Ticket not found' });
        return;
    }

    const deletedTicket = data.tickets.splice(ticketIndex, 1)[0];
    writeData(data);
    sendJSON(res, 200, { success: true, data: deletedTicket });
}

// Handle GET /metrics
function getMetrics(req, res) {
    const data = readData();
    const tickets = data.tickets;

    // Counts by status
    const statusCounts = { open: 0, in_progress: 0, resolved: 0 };
    tickets.forEach(t => {
        if (statusCounts[t.status] !== undefined) {
            statusCounts[t.status]++;
        }
    });

    // Counts by priority
    const priorityCounts = { low: 0, medium: 0, high: 0 };
    tickets.forEach(t => {
        if (priorityCounts[t.priority] !== undefined) {
            priorityCounts[t.priority]++;
        }
    });

    // Average age of open tickets in seconds
    const now = new Date();
    const openTickets = tickets.filter(t => t.status === 'open');
    let averageAge = 0;
    if (openTickets.length > 0) {
        const totalAge = openTickets.reduce((sum, t) => {
            const created = new Date(t.created_at);
            return sum + (now - created) / 1000;
        }, 0);
        averageAge = totalAge / openTickets.length;
    }

    sendJSON(res, 200, {
        success: true,
        data: {
            status_counts: statusCounts,
            priority_counts: priorityCounts,
            average_open_age_seconds: Math.round(averageAge * 100) / 100
        }
    });
}

// Handle OPTIONS preflight
function handleOptions(req, res) {
    res.writeHead(204, CORS_HEADERS);
    res.end();
}

// Parse URL to get path segments and query
function parseUrl(reqUrl) {
    const parsed = url.parse(reqUrl, true);
    const pathParts = parsed.pathname.split('/').filter(p => p);
    return { pathParts, query: parsed.query };
}

// Main request handler
function handleRequest(req, res) {
    try {
        const { pathParts } = parseUrl(req.url);
        const method = req.method.toUpperCase();

        // Handle preflight
        if (method === 'OPTIONS') {
            handleOptions(req, res);
            return;
        }

        // Route matching
        if (pathParts.length === 0 || pathParts[0] === '') {
            // Root route - not implemented
            sendJSON(res, 404, { success: false, error: 'Route not found' });
            return;
        }

        const resource = pathParts[0];

        if (resource === 'tickets' && pathParts.length === 1) {
            switch (method) {
                case 'GET':
                    getTickets(req, res);
                    break;
                case 'POST':
                    postTickets(req, res);
                    break;
                default:
                    sendJSON(res, 405, { success: false, error: `Method ${method} not allowed` });
            }
        } else if (resource === 'tickets' && pathParts.length === 2) {
            const id = pathParts[1];
            if (!/^\d+$/.test(id)) {
                sendJSON(res, 400, { success: false, error: 'Invalid ticket ID format' });
                return;
            }
            switch (method) {
                case 'GET':
                    getTicketById(req, res, id);
                    break;
                case 'PATCH':
                    patchTicket(req, res, id);
                    break;
                case 'DELETE':
                    deleteTicket(req, res, id);
                    break;
                default:
                    sendJSON(res, 405, { success: false, error: `Method ${method} not allowed` });
            }
        } else if (resource === 'metrics' && pathParts.length === 1) {
            if (method === 'GET') {
                getMetrics(req, res);
            } else {
                sendJSON(res, 405, { success: false, error: `Method ${method} not allowed` });
            }
        } else {
            sendJSON(res, 404, { success: false, error: 'Route not found' });
        }
    } catch (err) {
        sendJSON(res, 500, { success: false, error: 'Internal server error' });
    }
}

// Initialize and start server
initDataFile();
const server = http.createServer(handleRequest);

server.listen(PORT, HOST, () => {
    console.log(`Server running at http://${HOST}:${PORT}/`);
});
```
````
