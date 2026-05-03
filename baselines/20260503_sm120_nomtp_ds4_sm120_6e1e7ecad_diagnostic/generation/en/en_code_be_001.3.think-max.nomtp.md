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
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 41.003586
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 318, "total_tokens": 2930, "completion_tokens": 2612, "prompt_tokens_details": null}`
- Prompt tokens: 318
- Completion tokens: 2612
- Total tokens: 2930

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
const crypto = require('crypto');

const DATA_FILE = path.join(__dirname, 'tickets.json');
const HOST = '127.0.0.1';
const PORT = 8080;

// Initialize data file if it doesn't exist
function initDataFile() {
    if (!fs.existsSync(DATA_FILE)) {
        fs.writeFileSync(DATA_FILE, '[]', 'utf8');
    }
}

// Read tickets with file locking simulation
function readTickets() {
    try {
        const data = fs.readFileSync(DATA_FILE, 'utf8');
        return JSON.parse(data);
    } catch (err) {
        if (err.code === 'ENOENT') {
            initDataFile();
            return [];
        }
        throw err;
    }
}

// Write tickets atomically
function writeTickets(tickets) {
    const tmpFile = DATA_FILE + '.tmp';
    fs.writeFileSync(tmpFile, JSON.stringify(tickets, null, 2), 'utf8');
    fs.renameSync(tmpFile, DATA_FILE);
}

// Generate unique ID
function generateId() {
    return crypto.randomUUID();
}

// Validate ticket fields
function validateTicketFields(body, isUpdate = false) {
    const errors = [];

    if (!isUpdate) {
        if (!body.subject || typeof body.subject !== 'string' || body.subject.trim() === '') {
            errors.push('subject is required and must be a non-empty string');
        }
        if (!body.description || typeof body.description !== 'string' || body.description.trim() === '') {
            errors.push('description is required and must be a non-empty string');
        }
    } else {
        if (body.subject !== undefined && (typeof body.subject !== 'string' || body.subject.trim() === '')) {
            errors.push('subject must be a non-empty string');
        }
        if (body.description !== undefined && (typeof body.description !== 'string' || body.description.trim() === '')) {
            errors.push('description must be a non-empty string');
        }
    }

    const validPriorities = ['low', 'medium', 'high'];
    if (body.priority !== undefined && !validPriorities.includes(body.priority)) {
        errors.push(`priority must be one of: ${validPriorities.join(', ')}`);
    }

    const validStatuses = ['open', 'in_progress', 'resolved'];
    if (body.status !== undefined && !validStatuses.includes(body.status)) {
        errors.push(`status must be one of: ${validStatuses.join(', ')}`);
    }

    if (!isUpdate && !body.priority) {
        errors.push('priority is required');
    }
    if (!isUpdate && !body.status) {
        errors.push('status is required');
    }

    return errors;
}

// Create ticket object
function createTicketObject(body) {
    const now = new Date().toISOString();
    return {
        id: generateId(),
        subject: body.subject.trim(),
        description: body.description.trim(),
        priority: body.priority,
        status: body.status,
        created_at: now,
        updated_at: now
    };
}

// Parse request body
function parseRequestBody(req) {
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
                if (!body) {
                    resolve({});
                } else {
                    resolve(JSON.parse(body));
                }
            } catch (err) {
                reject(new Error('Invalid JSON'));
            }
        });
        req.on('error', reject);
    });
}

// Send JSON response
function sendResponse(res, statusCode, data) {
    const headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type'
    };
    res.writeHead(statusCode, headers);
    res.end(JSON.stringify(data));
}

// Parse URL and extract path and query params
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

// Route: GET /tickets
function getTickets(req, res, urlParsed) {
    const tickets = readTickets();
    let filtered = [...tickets];

    if (urlParsed.params.status) {
        filtered = filtered.filter(t => t.status === urlParsed.params.status);
    }
    if (urlParsed.params.priority) {
        filtered = filtered.filter(t => t.priority === urlParsed.params.priority);
    }

    sendResponse(res, 200, filtered);
}

// Route: POST /tickets
async function postTickets(req, res) {
    try {
        const body = await parseRequestBody(req);
        const errors = validateTicketFields(body);
        if (errors.length > 0) {
            return sendResponse(res, 400, { error: 'Validation failed', details: errors });
        }

        const tickets = readTickets();
        const newTicket = createTicketObject(body);
        tickets.push(newTicket);
        writeTickets(tickets);

        sendResponse(res, 201, newTicket);
    } catch (err) {
        if (err.message === 'Invalid JSON' || err.message === 'Request body too large') {
            sendResponse(res, 400, { error: err.message });
        } else {
            sendResponse(res, 500, { error: 'Internal server error' });
        }
    }
}

// Route: GET /tickets/{id}
function getTicketById(req, res, id) {
    const tickets = readTickets();
    const ticket = tickets.find(t => t.id === id);

    if (!ticket) {
        return sendResponse(res, 404, { error: 'Ticket not found' });
    }

    sendResponse(res, 200, ticket);
}

// Route: PATCH /tickets/{id}
async function patchTicket(req, res, id) {
    try {
        const body = await parseRequestBody(req);
        const errors = validateTicketFields(body, true);
        if (errors.length > 0) {
            return sendResponse(res, 400, { error: 'Validation failed', details: errors });
        }

        const tickets = readTickets();
        const index = tickets.findIndex(t => t.id === id);

        if (index === -1) {
            return sendResponse(res, 404, { error: 'Ticket not found' });
        }

        const updatedTicket = { ...tickets[index] };
        if (body.subject !== undefined) updatedTicket.subject = body.subject.trim();
        if (body.description !== undefined) updatedTicket.description = body.description.trim();
        if (body.priority !== undefined) updatedTicket.priority = body.priority;
        if (body.status !== undefined) updatedTicket.status = body.status;
        updatedTicket.updated_at = new Date().toISOString();

        tickets[index] = updatedTicket;
        writeTickets(tickets);

        sendResponse(res, 200, updatedTicket);
    } catch (err) {
        if (err.message === 'Invalid JSON' || err.message === 'Request body too large') {
            sendResponse(res, 400, { error: err.message });
        } else {
            sendResponse(res, 500, { error: 'Internal server error' });
        }
    }
}

// Route: DELETE /tickets/{id}
function deleteTicket(req, res, id) {
    const tickets = readTickets();
    const index = tickets.findIndex(t => t.id === id);

    if (index === -1) {
        return sendResponse(res, 404, { error: 'Ticket not found' });
    }

    tickets.splice(index, 1);
    writeTickets(tickets);

    sendResponse(res, 200, { message: 'Ticket deleted successfully' });
}

// Route: GET /metrics
function getMetrics(req, res) {
    const tickets = readTickets();
    const now = new Date();

    const statusCounts = { open: 0, in_progress: 0, resolved: 0 };
    const priorityCounts = { low: 0, medium: 0, high: 0 };
    let totalAgeOpen = 0;
    let openTicketCount = 0;

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
            const created = new Date(ticket.created_at);
            const ageInSeconds = (now - created) / 1000;
            totalAgeOpen += ageInSeconds;
            openTicketCount++;
        }
    });

    const averageAgeOpen = openTicketCount > 0 ? totalAgeOpen / openTicketCount : 0;

    sendResponse(res, 200, {
        status_counts: statusCounts,
        priority_counts: priorityCounts,
        average_age_open_seconds: Math.round(averageAgeOpen * 100) / 100
    });
}

// Main request handler
function handleRequest(req, res) {
    const { path: urlPath, params } = parseUrl(req.url);
    const method = req.method.toUpperCase();

    // Handle CORS preflight
    if (method === 'OPTIONS') {
        res.writeHead(204, {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '86400'
        });
        return res.end();
    }

    // Route matching
    try {
        // GET /tickets
        if (urlPath === '/tickets' && method === 'GET') {
            return getTickets(req, res, { params });
        }

        // POST /tickets
        if (urlPath === '/tickets' && method === 'POST') {
            return postTickets(req, res);
        }

        // GET /metrics
        if (urlPath === '/metrics' && method === 'GET') {
            return getMetrics(req, res);
        }

        // Routes with ID parameter
        const ticketMatch = urlPath.match(/^\/tickets\/([a-f0-9-]+)$/);
        if (ticketMatch) {
            const id = ticketMatch[1];
            switch (method) {
                case 'GET':
                    return getTicketById(req, res, id);
                case 'PATCH':
                    return patchTicket(req, res, id);
                case 'DELETE':
                    return deleteTicket(req, res, id);
                default:
                    return sendResponse(res, 405, { error: 'Method not allowed' });
            }
        }

        // Unknown route
        sendResponse(res, 404, { error: 'Route not found' });
    } catch (err) {
        console.error('Server error:', err);
        sendResponse(res, 500, { error: 'Internal server error' });
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
