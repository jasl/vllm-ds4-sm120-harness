const http = require('http');
const fs = require('fs');
const path = require('path');
const url = require('url');

const PORT = process.env.PORT || 8080;
const HOST = '127.0.0.1';
const DATA_FILE = path.join(__dirname, 'tickets.json');

// Ensure data file exists
if (!fs.existsSync(DATA_FILE)) {
    fs.writeFileSync(DATA_FILE, '[]', 'utf8');
}

// CORS headers
const corsHeaders = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
};

// Utility: read data synchronously (safe for sequential use)
function readData() {
    try {
        const raw = fs.readFileSync(DATA_FILE, 'utf8');
        return JSON.parse(raw);
    } catch (err) {
        console.error('Error reading data file:', err);
        return [];
    }
}

// Utility: write data synchronously
function writeData(data) {
    try {
        fs.writeFileSync(DATA_FILE, JSON.stringify(data, null, 2), 'utf8');
    } catch (err) {
        console.error('Error writing data file:', err);
        throw err;
    }
}

// Generate new ID
function generateId(tickets) {
    if (tickets.length === 0) return 1;
    const maxId = Math.max(...tickets.map(t => t.id));
    return maxId + 1;
}

// Validate ticket fields for creation
function validateCreate(body) {
    const errors = [];
    if (!body.subject || typeof body.subject !== 'string') errors.push('subject is required and must be a string');
    if (!body.description || typeof body.description !== 'string') errors.push('description is required and must be a string');
    if (!body.priority || !['low', 'medium', 'high'].includes(body.priority)) errors.push('priority must be one of low, medium, high');
    if (body.status && !['open', 'in_progress', 'resolved'].includes(body.status)) errors.push('status must be one of open, in_progress, resolved');
    return errors;
}

// Validate update fields
function validateUpdate(body) {
    const allowed = ['subject', 'description', 'priority', 'status'];
    const errors = [];
    for (const key of Object.keys(body)) {
        if (!allowed.includes(key)) continue;
        if (key === 'priority' && !['low', 'medium', 'high'].includes(body[key])) {
            errors.push('priority must be one of low, medium, high');
        }
        if (key === 'status' && !['open', 'in_progress', 'resolved'].includes(body[key])) {
            errors.push('status must be one of open, in_progress, resolved');
        }
        if (key === 'subject' && typeof body[key] !== 'string') errors.push('subject must be a string');
        if (key === 'description' && typeof body[key] !== 'string') errors.push('description must be a string');
    }
    return errors;
}

// Parse JSON body
function parseBody(req) {
    return new Promise((resolve, reject) => {
        let body = '';
        req.on('data', chunk => { body += chunk; });
        req.on('end', () => {
            try {
                if (!body) reject(new Error('Invalid JSON'));
                else resolve(JSON.parse(body));
            } catch (e) {
                reject(new Error('Invalid JSON'));
            }
        });
        req.on('error', reject);
    });
}

// Send JSON response
function sendJson(res, statusCode, data) {
    res.writeHead(statusCode, {
        'Content-Type': 'application/json',
        ...corsHeaders
    });
    res.end(JSON.stringify(data));
}

// Handle OPTIONS (preflight)
function handleOptions(req, res) {
    res.writeHead(204, corsHeaders);
    res.end();
}

// Routes
async function handleRequest(req, res) {
    const parsedUrl = url.parse(req.url, true);
    const pathname = parsedUrl.pathname;
    const method = req.method;

    // CORS preflight
    if (method === 'OPTIONS') {
        return handleOptions(req, res);
    }

    try {
        // GET /tickets
        if (pathname === '/tickets' && method === 'GET') {
            const tickets = readData();
            const { status, priority } = parsedUrl.query;
            let filtered = tickets;
            if (status) {
                filtered = filtered.filter(t => t.status === status);
            }
            if (priority) {
                filtered = filtered.filter(t => t.priority === priority);
            }
            return sendJson(res, 200, filtered);
        }

        // POST /tickets
        if (pathname === '/tickets' && method === 'POST') {
            const body = await parseBody(req);
            const errors = validateCreate(body);
            if (errors.length > 0) {
                return sendJson(res, 400, { error: 'Validation failed', details: errors });
            }
            const tickets = readData();
            const now = new Date().toISOString();
            const newTicket = {
                id: generateId(tickets),
                subject: body.subject,
                description: body.description,
                priority: body.priority,
                status: body.status || 'open',
                created_at: now,
                updated_at: now
            };
            tickets.push(newTicket);
            writeData(tickets);
            return sendJson(res, 201, newTicket);
        }

        // GET /tickets/{id}
        const ticketMatch = pathname.match(/^\/tickets\/(\d+)$/);
        if (ticketMatch && method === 'GET') {
            const id = parseInt(ticketMatch[1], 10);
            const tickets = readData();
            const ticket = tickets.find(t => t.id === id);
            if (!ticket) {
                return sendJson(res, 404, { error: 'Ticket not found' });
            }
            return sendJson(res, 200, ticket);
        }

        // PATCH /tickets/{id}
        if (ticketMatch && method === 'PATCH') {
            const id = parseInt(ticketMatch[1], 10);
            const body = await parseBody(req);
            const errors = validateUpdate(body);
            if (errors.length > 0) {
                return sendJson(res, 400, { error: 'Validation failed', details: errors });
            }
            const tickets = readData();
            const index = tickets.findIndex(t => t.id === id);
            if (index === -1) {
                return sendJson(res, 404, { error: 'Ticket not found' });
            }
            const updated = { ...tickets[index] };
            const allowed = ['subject', 'description', 'priority', 'status'];
            for (const key of allowed) {
                if (body[key] !== undefined) {
                    updated[key] = body[key];
                }
            }
            updated.updated_at = new Date().toISOString();
            tickets[index] = updated;
            writeData(tickets);
            return sendJson(res, 200, updated);
        }

        // DELETE /tickets/{id}
        if (ticketMatch && method === 'DELETE') {
            const id = parseInt(ticketMatch[1], 10);
            const tickets = readData();
            const index = tickets.findIndex(t => t.id === id);
            if (index === -1) {
                return sendJson(res, 404, { error: 'Ticket not found' });
            }
            tickets.splice(index, 1);
            writeData(tickets);
            return sendJson(res, 200, { message: 'Ticket deleted' });
        }

        // GET /metrics
        if (pathname === '/metrics' && method === 'GET') {
            const tickets = readData();
            const metrics = {
                by_status: { open: 0, in_progress: 0, resolved: 0 },
                by_priority: { low: 0, medium: 0, high: 0 },
                average_open_age_seconds: 0
            };
            let openTickets = [];
            const now = new Date();
            for (const ticket of tickets) {
                // Count status
                if (metrics.by_status[ticket.status] !== undefined) {
                    metrics.by_status[ticket.status]++;
                }
                // Count priority
                if (metrics.by_priority[ticket.priority] !== undefined) {
                    metrics.by_priority[ticket.priority]++;
                }
                // Open tickets for age
                if (ticket.status === 'open') {
                    openTickets.push(ticket);
                }
            }
            if (openTickets.length > 0) {
                let totalAge = 0;
                for (const ticket of openTickets) {
                    const created = new Date(ticket.created_at);
                    const ageMs = now - created;
                    totalAge += ageMs / 1000; // seconds
                }
                metrics.average_open_age_seconds = totalAge / openTickets.length;
            }
            return sendJson(res, 200, metrics);
        }

        // 404 for unknown routes
        return sendJson(res, 404, { error: 'Not found' });

    } catch (err) {
        if (err.message === 'Invalid JSON') {
            return sendJson(res, 400, { error: 'Invalid JSON' });
        }
        console.error(err);
        return sendJson(res, 500, { error: 'Internal server error' });
    }
}

// Create server
const server = http.createServer(handleRequest);

server.listen(PORT, HOST, () => {
    console.log(`Server running at http://${HOST}:${PORT}/`);
});
