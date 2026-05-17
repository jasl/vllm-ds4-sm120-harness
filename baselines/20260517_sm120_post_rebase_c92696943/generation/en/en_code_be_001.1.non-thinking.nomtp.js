const http = require('http');
const fs = require('fs');
const path = require('path');

const HOST = '127.0.0.1';
const PORT = 8080;
const DATA_FILE = path.join(__dirname, 'tickets.json');
let tickets = [];
let nextId = 1;

// Initialize data file if it doesn't exist
function initDataFile() {
    try {
        if (!fs.existsSync(DATA_FILE)) {
            tickets = [];
            nextId = 1;
            saveTickets();
        } else {
            const data = fs.readFileSync(DATA_FILE, 'utf8');
            if (data) {
                const parsed = JSON.parse(data);
                tickets = parsed.tickets || [];
                nextId = parsed.nextId || 1;
            } else {
                tickets = [];
                nextId = 1;
            }
        }
    } catch (err) {
        tickets = [];
        nextId = 1;
    }
}

function saveTickets() {
    const data = JSON.stringify({ tickets, nextId }, null, 2);
    fs.writeFileSync(DATA_FILE, data, 'utf8');
}

function getCurrentTimestamp() {
    return new Date().toISOString();
}

function parseUrl(url) {
    const parsed = new URL(url, `http://${HOST}:${PORT}`);
    const pathParts = parsed.pathname.split('/').filter(Boolean);
    return { pathParts, query: parsed.searchParams };
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
        errors.push('priority must be one of: low, medium, high');
    }

    if (body.status && !['open', 'in_progress', 'resolved'].includes(body.status)) {
        errors.push('status must be one of: open, in_progress, resolved');
    }

    return errors;
}

function handleGetTickets(res, query) {
    let filtered = [...tickets];

    const status = query.get('status');
    const priority = query.get('priority');

    if (status) {
        filtered = filtered.filter(t => t.status === status);
    }

    if (priority) {
        filtered = filtered.filter(t => t.priority === priority);
    }

    sendJSON(res, 200, filtered);
}

function handlePostTicket(req, res) {
    let body = '';

    req.on('data', chunk => {
        body += chunk;
    });

    req.on('end', () => {
        try {
            if (!body) {
                sendJSON(res, 400, { error: 'Request body is required' });
                return;
            }

            const parsed = JSON.parse(body);
            const errors = validateTicket(parsed);

            if (errors.length > 0) {
                sendJSON(res, 400, { error: 'Validation failed', details: errors });
                return;
            }

            const now = getCurrentTimestamp();
            const newTicket = {
                id: nextId++,
                subject: parsed.subject.trim(),
                description: parsed.description.trim(),
                priority: parsed.priority || 'low',
                status: 'open',
                created_at: now,
                updated_at: now
            };

            tickets.push(newTicket);
            saveTickets();

            sendJSON(res, 201, newTicket);
        } catch (err) {
            sendJSON(res, 400, { error: 'Invalid JSON in request body' });
        }
    });
}

function handleGetTicket(res, id) {
    const ticket = tickets.find(t => t.id === id);

    if (!ticket) {
        sendJSON(res, 404, { error: `Ticket with id ${id} not found` });
        return;
    }

    sendJSON(res, 200, ticket);
}

function handlePatchTicket(req, res, id) {
    const ticketIndex = tickets.findIndex(t => t.id === id);

    if (ticketIndex === -1) {
        sendJSON(res, 404, { error: `Ticket with id ${id} not found` });
        return;
    }

    let body = '';

    req.on('data', chunk => {
        body += chunk;
    });

    req.on('end', () => {
        try {
            if (!body) {
                sendJSON(res, 400, { error: 'Request body is required' });
                return;
            }

            const parsed = JSON.parse(body);
            const validFields = ['subject', 'description', 'priority', 'status'];
            const updates = {};

            for (const field of validFields) {
                if (parsed[field] !== undefined) {
                    updates[field] = parsed[field];
                }
            }

            if (Object.keys(updates).length === 0) {
                sendJSON(res, 400, { error: 'No valid fields to update. Valid fields: subject, description, priority, status' });
                return;
            }

            // Validate updated fields
            const validationBody = { ...tickets[ticketIndex], ...updates };
            const errors = [];

            if (updates.subject !== undefined) {
                if (typeof updates.subject !== 'string' || updates.subject.trim() === '') {
                    errors.push('subject must be a non-empty string');
                }
                updates.subject = updates.subject.trim();
            }

            if (updates.description !== undefined) {
                if (typeof updates.description !== 'string' || updates.description.trim() === '') {
                    errors.push('description must be a non-empty string');
                }
                updates.description = updates.description.trim();
            }

            if (updates.priority !== undefined && !['low', 'medium', 'high'].includes(updates.priority)) {
                errors.push('priority must be one of: low, medium, high');
            }

            if (updates.status !== undefined && !['open', 'in_progress', 'resolved'].includes(updates.status)) {
                errors.push('status must be one of: open, in_progress, resolved');
            }

            if (errors.length > 0) {
                sendJSON(res, 400, { error: 'Validation failed', details: errors });
                return;
            }

            tickets[ticketIndex] = {
                ...tickets[ticketIndex],
                ...updates,
                updated_at: getCurrentTimestamp()
            };

            saveTickets();
            sendJSON(res, 200, tickets[ticketIndex]);
        } catch (err) {
            sendJSON(res, 400, { error: 'Invalid JSON in request body' });
        }
    });
}

function handleDeleteTicket(res, id) {
    const ticketIndex = tickets.findIndex(t => t.id === id);

    if (ticketIndex === -1) {
        sendJSON(res, 404, { error: `Ticket with id ${id} not found` });
        return;
    }

    const deletedTicket = tickets.splice(ticketIndex, 1)[0];
    saveTickets();

    sendJSON(res, 200, { message: `Ticket ${id} deleted`, ticket: deletedTicket });
}

function handleGetMetrics(res) {
    const statusCounts = {
        open: 0,
        in_progress: 0,
        resolved: 0
    };

    const priorityCounts = {
        low: 0,
        medium: 0,
        high: 0
    };

    let totalAgeSeconds = 0;
    let openTicketCount = 0;
    const now = new Date();

    for (const ticket of tickets) {
        statusCounts[ticket.status] = (statusCounts[ticket.status] || 0) + 1;
        priorityCounts[ticket.priority] = (priorityCounts[ticket.priority] || 0) + 1;

        if (ticket.status === 'open') {
            const createdDate = new Date(ticket.created_at);
            const ageSeconds = Math.floor((now - createdDate) / 1000);
            totalAgeSeconds += ageSeconds;
            openTicketCount++;
        }
    }

    const metrics = {
        status_counts: statusCounts,
        priority_counts: priorityCounts,
        average_open_age_seconds: openTicketCount > 0 ? Math.round(totalAgeSeconds / openTicketCount) : 0
    };

    sendJSON(res, 200, metrics);
}

const server = http.createServer((req, res) => {
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

    const { pathParts, query } = parseUrl(req.url);

    try {
        // GET /tickets
        if (pathParts.length === 1 && pathParts[0] === 'tickets' && req.method === 'GET') {
            handleGetTickets(res, query);
            return;
        }

        // POST /tickets
        if (pathParts.length === 1 && pathParts[0] === 'tickets' && req.method === 'POST') {
            handlePostTicket(req, res);
            return;
        }

        // GET /metrics
        if (pathParts.length === 1 && pathParts[0] === 'metrics' && req.method === 'GET') {
            handleGetMetrics(res);
            return;
        }

        // GET /tickets/{id}
        if (pathParts.length === 2 && pathParts[0] === 'tickets' && req.method === 'GET') {
            const id = parseInt(pathParts[1], 10);
            if (isNaN(id)) {
                sendJSON(res, 400, { error: 'Invalid ticket ID format' });
                return;
            }
            handleGetTicket(res, id);
            return;
        }

        // PATCH /tickets/{id}
        if (pathParts.length === 2 && pathParts[0] === 'tickets' && req.method === 'PATCH') {
            const id = parseInt(pathParts[1], 10);
            if (isNaN(id)) {
                sendJSON(res, 400, { error: 'Invalid ticket ID format' });
                return;
            }
            handlePatchTicket(req, res, id);
            return;
        }

        // DELETE /tickets/{id}
        if (pathParts.length === 2 && pathParts[0] === 'tickets' && req.method === 'DELETE') {
            const id = parseInt(pathParts[1], 10);
            if (isNaN(id)) {
                sendJSON(res, 400, { error: 'Invalid ticket ID format' });
                return;
            }
            handleDeleteTicket(res, id);
            return;
        }

        // Handle unknown routes
        sendJSON(res, 404, { error: `Route not found: ${req.method} ${req.url}` });
    } catch (err) {
        sendJSON(res, 500, { error: 'Internal server error' });
    }
});

// Initialize data and start server
initDataFile();

server.listen(PORT, HOST, () => {
    console.log(`Server running at http://${HOST}:${PORT}/`);
});
