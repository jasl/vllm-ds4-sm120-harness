# Generation Transcript

- Case: `en_code_be_001`
- Language group: `en`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `2`
- Thinking mode: `non-thinking`
- Thinking strength: `disabled`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 8.319351
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 318, "total_tokens": 2770, "completion_tokens": 2452, "prompt_tokens_details": null}`
- Prompt tokens: 318
- Completion tokens: 2452
- Total tokens: 2770

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

const PORT = process.env.PORT || 8080;
const HOST = process.env.HOST || '127.0.0.1';
const DATA_FILE = path.join(__dirname, 'tickets.json');

// Helper functions
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

function writeTickets(tickets) {
    fs.writeFileSync(DATA_FILE, JSON.stringify(tickets, null, 2), 'utf8');
}

function generateId() {
    return Date.now().toString(36) + Math.random().toString(36).substr(2, 9);
}

function getCurrentTimestamp() {
    return new Date().toISOString();
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
    const body = JSON.stringify(data);
    res.writeHead(statusCode, {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Content-Length': Buffer.byteLength(body)
    });
    res.end(body);
}

function sendError(res, statusCode, message) {
    sendResponse(res, statusCode, { error: message });
}

function parsePath(reqUrl) {
    const parsed = url.parse(reqUrl, true);
    const pathParts = parsed.pathname.split('/').filter(Boolean);
    return { pathParts, query: parsed.query };
}

// Route handlers
async function handleGetTickets(req, res, query) {
    try {
        let tickets = readTickets();

        if (query.status) {
            tickets = tickets.filter(t => t.status === query.status);
        }
        if (query.priority) {
            tickets = tickets.filter(t => t.priority === query.priority);
        }

        sendResponse(res, 200, tickets);
    } catch (err) {
        sendError(res, 500, 'Internal server error');
    }
}

async function handlePostTickets(req, res) {
    try {
        const body = await parseBody(req);

        // Validate required fields
        if (!body.subject || typeof body.subject !== 'string') {
            return sendError(res, 400, 'Subject is required and must be a string');
        }
        if (!body.description || typeof body.description !== 'string') {
            return sendError(res, 400, 'Description is required and must be a string');
        }

        const validPriorities = ['low', 'medium', 'high'];
        const validStatuses = ['open', 'in_progress', 'resolved'];

        let priority = body.priority || 'low';
        let status = body.status || 'open';

        if (!validPriorities.includes(priority)) {
            return sendError(res, 400, 'Priority must be one of: low, medium, high');
        }
        if (!validStatuses.includes(status)) {
            return sendError(res, 400, 'Status must be one of: open, in_progress, resolved');
        }

        const now = getCurrentTimestamp();
        const ticket = {
            id: generateId(),
            subject: body.subject,
            description: body.description,
            priority: priority,
            status: status,
            created_at: now,
            updated_at: now
        };

        const tickets = readTickets();
        tickets.push(ticket);
        writeTickets(tickets);

        sendResponse(res, 201, ticket);
    } catch (err) {
        if (err.message === 'Invalid JSON') {
            return sendError(res, 400, 'Invalid JSON in request body');
        }
        sendError(res, 500, 'Internal server error');
    }
}

async function handleGetTicketById(req, res, id) {
    try {
        const tickets = readTickets();
        const ticket = tickets.find(t => t.id === id);

        if (!ticket) {
            return sendError(res, 404, 'Ticket not found');
        }

        sendResponse(res, 200, ticket);
    } catch (err) {
        sendError(res, 500, 'Internal server error');
    }
}

async function handlePatchTicket(req, res, id) {
    try {
        const body = await parseBody(req);
        const tickets = readTickets();
        const index = tickets.findIndex(t => t.id === id);

        if (index === -1) {
            return sendError(res, 404, 'Ticket not found');
        }

        const validPriorities = ['low', 'medium', 'high'];
        const validStatuses = ['open', 'in_progress', 'resolved'];

        // Validate update fields
        if (body.subject !== undefined && typeof body.subject !== 'string') {
            return sendError(res, 400, 'Subject must be a string');
        }
        if (body.description !== undefined && typeof body.description !== 'string') {
            return sendError(res, 400, 'Description must be a string');
        }
        if (body.priority !== undefined && !validPriorities.includes(body.priority)) {
            return sendError(res, 400, 'Priority must be one of: low, medium, high');
        }
        if (body.status !== undefined && !validStatuses.includes(body.status)) {
            return sendError(res, 400, 'Status must be one of: open, in_progress, resolved');
        }

        const ticket = tickets[index];

        if (body.subject !== undefined) ticket.subject = body.subject;
        if (body.description !== undefined) ticket.description = body.description;
        if (body.priority !== undefined) ticket.priority = body.priority;
        if (body.status !== undefined) ticket.status = body.status;
        ticket.updated_at = getCurrentTimestamp();

        tickets[index] = ticket;
        writeTickets(tickets);

        sendResponse(res, 200, ticket);
    } catch (err) {
        if (err.message === 'Invalid JSON') {
            return sendError(res, 400, 'Invalid JSON in request body');
        }
        sendError(res, 500, 'Internal server error');
    }
}

async function handleDeleteTicket(req, res, id) {
    try {
        let tickets = readTickets();
        const index = tickets.findIndex(t => t.id === id);

        if (index === -1) {
            return sendError(res, 404, 'Ticket not found');
        }

        tickets.splice(index, 1);
        writeTickets(tickets);

        sendResponse(res, 200, { message: 'Ticket deleted successfully' });
    } catch (err) {
        sendError(res, 500, 'Internal server error');
    }
}

function handleMetrics(req, res) {
    try {
        const tickets = readTickets();

        // Count by status
        const statusCounts = {
            open: 0,
            in_progress: 0,
            resolved: 0
        };

        // Count by priority
        const priorityCounts = {
            low: 0,
            medium: 0,
            high: 0
        };

        let totalAgeSeconds = 0;
        let openTicketCount = 0;

        tickets.forEach(ticket => {
            // Status counts
            if (statusCounts.hasOwnProperty(ticket.status)) {
                statusCounts[ticket.status]++;
            }

            // Priority counts
            if (priorityCounts.hasOwnProperty(ticket.priority)) {
                priorityCounts[ticket.priority]++;
            }

            // Average age for open tickets
            if (ticket.status === 'open' || ticket.status === 'in_progress') {
                const created = new Date(ticket.created_at);
                const now = new Date();
                const ageSeconds = Math.floor((now - created) / 1000);
                totalAgeSeconds += ageSeconds;
                openTicketCount++;
            }
        });

        const averageAgeSeconds = openTicketCount > 0 ? Math.floor(totalAgeSeconds / openTicketCount) : 0;

        const metrics = {
            by_status: statusCounts,
            by_priority: priorityCounts,
            average_age_seconds: averageAgeSeconds
        };

        sendResponse(res, 200, metrics);
    } catch (err) {
        sendError(res, 500, 'Internal server error');
    }
}

// Request handler
async function handleRequest(req, res) {
    // CORS preflight
    if (req.method === 'OPTIONS') {
        res.writeHead(204, {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '86400'
        });
        return res.end();
    }

    const { pathParts, query } = parsePath(req.url);

    try {
        // Route matching
        if (pathParts.length === 1 && pathParts[0] === 'tickets') {
            if (req.method === 'GET') {
                return await handleGetTickets(req, res, query);
            } else if (req.method === 'POST') {
                return await handlePostTickets(req, res);
            } else {
                return sendError(res, 405, 'Method not allowed');
            }
        }

        if (pathParts.length === 2 && pathParts[0] === 'tickets') {
            const id = pathParts[1];

            if (req.method === 'GET') {
                return await handleGetTicketById(req, res, id);
            } else if (req.method === 'PATCH') {
                return await handlePatchTicket(req, res, id);
            } else if (req.method === 'DELETE') {
                return await handleDeleteTicket(req, res, id);
            } else {
                return sendError(res, 405, 'Method not allowed');
            }
        }

        if (pathParts.length === 1 && pathParts[0] === 'metrics') {
            if (req.method === 'GET') {
                return handleMetrics(req, res);
            } else {
                return sendError(res, 405, 'Method not allowed');
            }
        }

        // Unknown route
        sendError(res, 404, 'Route not found');
    } catch (err) {
        sendError(res, 500, 'Internal server error');
    }
}

// Create and start server
const server = http.createServer(handleRequest);

server.listen(PORT, HOST, () => {
    console.log(`Server running at http://${HOST}:${PORT}/`);
});
```
````
