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
- Elapsed seconds: 44.491021
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 318, "total_tokens": 3150, "completion_tokens": 2832, "prompt_tokens_details": null}`
- Prompt tokens: 318
- Completion tokens: 2832
- Total tokens: 3150

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
function initDataFile() {
    if (!fs.existsSync(DATA_FILE)) {
        fs.writeFileSync(DATA_FILE, '[]', 'utf8');
    }
}

// Read tickets from file
function readTickets() {
    try {
        const data = fs.readFileSync(DATA_FILE, 'utf8');
        return JSON.parse(data);
    } catch (error) {
        return [];
    }
}

// Write tickets to file
function writeTickets(tickets) {
    fs.writeFileSync(DATA_FILE, JSON.stringify(tickets, null, 2), 'utf8');
}

// Generate unique ID
function generateId() {
    return 'ticket_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

// Validate ticket data
function validateTicket(data) {
    const errors = [];

    if (!data.subject || typeof data.subject !== 'string' || data.subject.trim().length === 0) {
        errors.push('subject is required and must be a non-empty string');
    }

    if (!data.description || typeof data.description !== 'string' || data.description.trim().length === 0) {
        errors.push('description is required and must be a non-empty string');
    }

    const validPriorities = ['low', 'medium', 'high'];
    if (!data.priority || !validPriorities.includes(data.priority)) {
        errors.push('priority must be one of: low, medium, high');
    }

    if (errors.length > 0) {
        return { valid: false, errors };
    }

    return { valid: true, errors: [] };
}

// Parse URL and extract path and query parameters
function parseUrl(url) {
    const urlParts = url.split('?');
    const pathname = urlParts[0].replace(/\/+$/, '') || '/';
    const query = {};

    if (urlParts[1]) {
        urlParts[1].split('&').forEach(param => {
            const [key, value] = param.split('=');
            if (key) {
                query[decodeURIComponent(key)] = decodeURIComponent(value || '');
            }
        });
    }

    return { pathname, query };
}

// Set CORS headers
function setCorsHeaders(res) {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
}

// Send JSON response
function sendJson(res, statusCode, data) {
    res.writeHead(statusCode, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(data));
}

// Handle GET /tickets
function handleGetTickets(res, query) {
    try {
        let tickets = readTickets();

        if (query.status) {
            tickets = tickets.filter(t => t.status === query.status);
        }

        if (query.priority) {
            tickets = tickets.filter(t => t.priority === query.priority);
        }

        sendJson(res, 200, { success: true, data: tickets });
    } catch (error) {
        sendJson(res, 500, { success: false, error: 'Internal server error' });
    }
}

// Handle POST /tickets
function handlePostTickets(res, body) {
    try {
        const validation = validateTicket(body);
        if (!validation.valid) {
            sendJson(res, 400, { success: false, errors: validation.errors });
            return;
        }

        const tickets = readTickets();
        const now = new Date().toISOString();

        const newTicket = {
            id: generateId(),
            subject: body.subject.trim(),
            description: body.description.trim(),
            priority: body.priority,
            status: 'open',
            created_at: now,
            updated_at: now
        };

        tickets.push(newTicket);
        writeTickets(tickets);

        sendJson(res, 201, { success: true, data: newTicket });
    } catch (error) {
        sendJson(res, 500, { success: false, error: 'Internal server error' });
    }
}

// Handle GET /tickets/{id}
function handleGetTicket(res, id) {
    try {
        const tickets = readTickets();
        const ticket = tickets.find(t => t.id === id);

        if (!ticket) {
            sendJson(res, 404, { success: false, error: 'Ticket not found' });
            return;
        }

        sendJson(res, 200, { success: true, data: ticket });
    } catch (error) {
        sendJson(res, 500, { success: false, error: 'Internal server error' });
    }
}

// Handle PATCH /tickets/{id}
function handlePatchTicket(res, id, body) {
    try {
        const tickets = readTickets();
        const index = tickets.findIndex(t => t.id === id);

        if (index === -1) {
            sendJson(res, 404, { success: false, error: 'Ticket not found' });
            return;
        }

        const validFields = ['subject', 'description', 'priority', 'status'];
        const updateFields = {};

        for (const field of validFields) {
            if (body[field] !== undefined) {
                if (field === 'priority') {
                    const validPriorities = ['low', 'medium', 'high'];
                    if (!validPriorities.includes(body[field])) {
                        sendJson(res, 400, { success: false, error: 'priority must be one of: low, medium, high' });
                        return;
                    }
                } else if (field === 'status') {
                    const validStatuses = ['open', 'in_progress', 'resolved'];
                    if (!validStatuses.includes(body[field])) {
                        sendJson(res, 400, { success: false, error: 'status must be one of: open, in_progress, resolved' });
                        return;
                    }
                }
                updateFields[field] = typeof body[field] === 'string' ? body[field].trim() : body[field];
            }
        }

        if (Object.keys(updateFields).length === 0) {
            sendJson(res, 400, { success: false, error: 'No valid fields to update' });
            return;
        }

        tickets[index] = {
            ...tickets[index],
            ...updateFields,
            updated_at: new Date().toISOString()
        };

        writeTickets(tickets);

        sendJson(res, 200, { success: true, data: tickets[index] });
    } catch (error) {
        sendJson(res, 500, { success: false, error: 'Internal server error' });
    }
}

// Handle DELETE /tickets/{id}
function handleDeleteTicket(res, id) {
    try {
        const tickets = readTickets();
        const index = tickets.findIndex(t => t.id === id);

        if (index === -1) {
            sendJson(res, 404, { success: false, error: 'Ticket not found' });
            return;
        }

        tickets.splice(index, 1);
        writeTickets(tickets);

        sendJson(res, 200, { success: true, message: 'Ticket deleted successfully' });
    } catch (error) {
        sendJson(res, 500, { success: false, error: 'Internal server error' });
    }
}

// Handle GET /metrics
function handleGetMetrics(res) {
    try {
        const tickets = readTickets();

        const statusCounts = { open: 0, in_progress: 0, resolved: 0 };
        const priorityCounts = { low: 0, medium: 0, high: 0 };
        let totalOpenAgeSeconds = 0;
        let openTicketCount = 0;

        const now = new Date();

        tickets.forEach(ticket => {
            // Count by status
            if (statusCounts.hasOwnProperty(ticket.status)) {
                statusCounts[ticket.status]++;
            }

            // Count by priority
            if (priorityCounts.hasOwnProperty(ticket.priority)) {
                priorityCounts[ticket.priority]++;
            }

            // Calculate age for open tickets
            if (ticket.status === 'open') {
                const createdAt = new Date(ticket.created_at);
                const ageInSeconds = (now - createdAt) / 1000;
                totalOpenAgeSeconds += ageInSeconds;
                openTicketCount++;
            }
        });

        const metrics = {
            status_counts: statusCounts,
            priority_counts: priorityCounts,
            average_open_ticket_age_seconds: openTicketCount > 0 ? totalOpenAgeSeconds / openTicketCount : 0,
            total_tickets: tickets.length,
            open_ticket_count: openTicketCount
        };

        sendJson(res, 200, { success: true, data: metrics });
    } catch (error) {
        sendJson(res, 500, { success: false, error: 'Internal server error' });
    }
}

// Parse JSON body from request
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
            } catch (error) {
                reject(new Error('Invalid JSON'));
            }
        });

        req.on('error', reject);
    });
}

// Main request handler
async function handleRequest(req, res) {
    setCorsHeaders(res);

    // Handle preflight
    if (req.method === 'OPTIONS') {
        res.writeHead(204);
        res.end();
        return;
    }

    const { pathname, query } = parseUrl(req.url);
    const pathParts = pathname.split('/').filter(part => part.length > 0);

    try {
        // Route: GET /tickets
        if (pathname === '/' || pathname === '/tickets') {
            if (req.method === 'GET') {
                handleGetTickets(res, query);
            } else if (req.method === 'POST') {
                let body;
                try {
                    body = await parseBody(req);
                    if (!body) {
                        sendJson(res, 400, { success: false, error: 'Request body is required' });
                        return;
                    }
                } catch (error) {
                    sendJson(res, 400, { success: false, error: 'Invalid JSON in request body' });
                    return;
                }
                handlePostTickets(res, body);
            } else {
                sendJson(res, 405, { success: false, error: 'Method not allowed' });
            }
            return;
        }

        // Route: GET /metrics
        if (pathname === '/metrics') {
            if (req.method === 'GET') {
                handleGetMetrics(res);
            } else {
                sendJson(res, 405, { success: false, error: 'Method not allowed' });
            }
            return;
        }

        // Route: /tickets/{id}
        if (pathParts.length === 2 && pathParts[0] === 'tickets') {
            const id = pathParts[1];

            switch (req.method) {
                case 'GET':
                    handleGetTicket(res, id);
                    break;

                case 'PATCH':
                    let body;
                    try {
                        body = await parseBody(req);
                        if (!body) {
                            sendJson(res, 400, { success: false, error: 'Request body is required' });
                            return;
                        }
                    } catch (error) {
                        sendJson(res, 400, { success: false, error: 'Invalid JSON in request body' });
                        return;
                    }
                    handlePatchTicket(res, id, body);
                    break;

                case 'DELETE':
                    handleDeleteTicket(res, id);
                    break;

                default:
                    sendJson(res, 405, { success: false, error: 'Method not allowed' });
            }
            return;
        }

        // Unknown route
        sendJson(res, 404, { success: false, error: 'Route not found' });
    } catch (error) {
        sendJson(res, 500, { success: false, error: 'Internal server error' });
    }
}

// Start server
initDataFile();

const server = http.createServer(handleRequest);

server.listen(PORT, HOST, () => {
    console.log(`Server running at http://${HOST}:${PORT}/`);
});
```
````
