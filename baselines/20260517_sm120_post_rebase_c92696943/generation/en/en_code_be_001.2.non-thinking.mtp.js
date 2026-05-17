const http = require('http');
const fs = require('fs');
const path = require('path');
const url = require('url');

const DATA_FILE = path.join(__dirname, 'tickets.json');
const HOST = '127.0.0.1';
const PORT = 8080;

let ticketStore = [];
let currentId = 1;
let isLoaded = false;

function loadData() {
    try {
        if (fs.existsSync(DATA_FILE)) {
            const data = fs.readFileSync(DATA_FILE, 'utf8');
            if (data.trim()) {
                const parsed = JSON.parse(data);
                ticketStore = parsed.tickets || [];
                currentId = parsed.currentId || 1;
            }
        }
    } catch (err) {
        console.error('Error loading data:', err.message);
        ticketStore = [];
        currentId = 1;
    }
    isLoaded = true;
}

function saveData() {
    try {
        const data = JSON.stringify({ tickets: ticketStore, currentId }, null, 2);
        fs.writeFileSync(DATA_FILE, data, 'utf8');
    } catch (err) {
        console.error('Error saving data:', err.message);
    }
}

function generateId() {
    return currentId++;
}

function addTicket(ticket) {
    ticket.id = generateId();
    const now = new Date().toISOString();
    ticket.created_at = now;
    ticket.updated_at = now;
    ticketStore.push(ticket);
    saveData();
    return ticket;
}

function updateTicket(id, updates) {
    const index = ticketStore.findIndex(t => t.id === id);
    if (index === -1) return null;

    const allowedFields = ['subject', 'description', 'priority', 'status'];
    const ticket = ticketStore[index];

    for (const field of allowedFields) {
        if (updates[field] !== undefined) {
            ticket[field] = updates[field];
        }
    }

    ticket.updated_at = new Date().toISOString();
    ticketStore[index] = ticket;
    saveData();
    return ticket;
}

function deleteTicket(id) {
    const index = ticketStore.findIndex(t => t.id === id);
    if (index === -1) return false;

    ticketStore.splice(index, 1);
    saveData();
    return true;
}

function getTicketById(id) {
    return ticketStore.find(t => t.id === id) || null;
}

function getFilteredTickets(status, priority) {
    let result = [...ticketStore];
    if (status) {
        result = result.filter(t => t.status === status);
    }
    if (priority) {
        result = result.filter(t => t.priority === priority);
    }
    return result;
}

function getMetrics() {
    const statusCounts = { open: 0, in_progress: 0, resolved: 0 };
    const priorityCounts = { low: 0, medium: 0, high: 0 };
    let totalAgeSeconds = 0;
    let openTicketCount = 0;
    const now = new Date();

    for (const ticket of ticketStore) {
        if (statusCounts[ticket.status] !== undefined) {
            statusCounts[ticket.status]++;
        }
        if (priorityCounts[ticket.priority] !== undefined) {
            priorityCounts[ticket.priority]++;
        }

        if (ticket.status === 'open') {
            const created = new Date(ticket.created_at);
            totalAgeSeconds += (now - created) / 1000;
            openTicketCount++;
        }
    }

    return {
        status_counts: statusCounts,
        priority_counts: priorityCounts,
        average_open_age_seconds: openTicketCount > 0 ? (totalAgeSeconds / openTicketCount) : 0
    };
}

function parseRequestBody(req) {
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

function sendJSON(res, statusCode, data) {
    res.writeHead(statusCode, {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type'
    });
    res.end(JSON.stringify(data));
}

function parseTicketId(pathname) {
    const match = pathname.match(/^\/tickets\/(\d+)$/);
    return match ? parseInt(match[1], 10) : null;
}

function isValidTicket(body) {
    const validStatuses = ['open', 'in_progress', 'resolved'];
    const validPriorities = ['low', 'medium', 'high'];

    if (!body.subject || typeof body.subject !== 'string' || body.subject.trim() === '') {
        return 'Subject is required and must be a non-empty string';
    }
    if (!body.description || typeof body.description !== 'string' || body.description.trim() === '') {
        return 'Description is required and must be a non-empty string';
    }
    if (!body.priority || !validPriorities.includes(body.priority)) {
        return 'Priority must be one of: low, medium, high';
    }
    if (!body.status || !validStatuses.includes(body.status)) {
        return 'Status must be one of: open, in_progress, resolved';
    }
    return null;
}

async function handleRequest(req, res) {
    if (!isLoaded) {
        loadData();
    }

    const parsedUrl = url.parse(req.url, true);
    const pathname = parsedUrl.pathname;
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
        // GET /metrics
        if (pathname === '/metrics' && method === 'GET') {
            const metrics = getMetrics();
            sendJSON(res, 200, metrics);
            return;
        }

        // GET /tickets
        if (pathname === '/tickets' && method === 'GET') {
            const status = parsedUrl.query.status || null;
            const priority = parsedUrl.query.priority || null;
            const tickets = getFilteredTickets(status, priority);
            sendJSON(res, 200, tickets);
            return;
        }

        // POST /tickets
        if (pathname === '/tickets' && method === 'POST') {
            const body = await parseRequestBody(req);
            const validationError = isValidTicket(body);
            if (validationError) {
                sendJSON(res, 400, { error: validationError });
                return;
            }

            const ticket = {
                subject: body.subject.trim(),
                description: body.description.trim(),
                priority: body.priority,
                status: body.status
            };

            const newTicket = addTicket(ticket);
            sendJSON(res, 201, newTicket);
            return;
        }

        // Single ticket routes
        const ticketId = parseTicketId(pathname);
        if (ticketId !== null) {
            // GET /tickets/{id}
            if (method === 'GET') {
                const ticket = getTicketById(ticketId);
                if (!ticket) {
                    sendJSON(res, 404, { error: 'Ticket not found' });
                    return;
                }
                sendJSON(res, 200, ticket);
                return;
            }

            // PATCH /tickets/{id}
            if (method === 'PATCH') {
                const ticket = getTicketById(ticketId);
                if (!ticket) {
                    sendJSON(res, 404, { error: 'Ticket not found' });
                    return;
                }

                const body = await parseRequestBody(req);
                const validFields = ['subject', 'description', 'priority', 'status'];
                const hasValidField = Object.keys(body).some(f => validFields.includes(f));

                if (!hasValidField) {
                    sendJSON(res, 400, { error: 'No valid fields to update. Valid fields: subject, description, priority, status' });
                    return;
                }

                // Validate if priority or status provided
                if (body.priority && !['low', 'medium', 'high'].includes(body.priority)) {
                    sendJSON(res, 400, { error: 'Priority must be one of: low, medium, high' });
                    return;
                }
                if (body.status && !['open', 'in_progress', 'resolved'].includes(body.status)) {
                    sendJSON(res, 400, { error: 'Status must be one of: open, in_progress, resolved' });
                    return;
                }
                if (body.subject !== undefined && (typeof body.subject !== 'string' || body.subject.trim() === '')) {
                    sendJSON(res, 400, { error: 'Subject must be a non-empty string' });
                    return;
                }
                if (body.description !== undefined && (typeof body.description !== 'string' || body.description.trim() === '')) {
                    sendJSON(res, 400, { error: 'Description must be a non-empty string' });
                    return;
                }

                // Trim strings
                if (body.subject) body.subject = body.subject.trim();
                if (body.description) body.description = body.description.trim();

                const updatedTicket = updateTicket(ticketId, body);
                sendJSON(res, 200, updatedTicket);
                return;
            }

            // DELETE /tickets/{id}
            if (method === 'DELETE') {
                const deleted = deleteTicket(ticketId);
                if (!deleted) {
                    sendJSON(res, 404, { error: 'Ticket not found' });
                    return;
                }
                sendJSON(res, 200, { message: 'Ticket deleted successfully' });
                return;
            }
        }

        // Unknown route
        sendJSON(res, 404, { error: 'Route not found' });

    } catch (err) {
        if (err.message === 'Invalid JSON') {
            sendJSON(res, 400, { error: 'Invalid JSON in request body' });
        } else {
            console.error('Server error:', err);
            sendJSON(res, 500, { error: 'Internal server error' });
        }
    }
}

const server = http.createServer(handleRequest);

server.listen(PORT, HOST, () => {
    loadData();
    console.log(`Server running at http://${HOST}:${PORT}/`);
});
