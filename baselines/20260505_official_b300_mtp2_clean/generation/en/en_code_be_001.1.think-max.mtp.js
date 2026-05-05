const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = 8080;
const HOST = '127.0.0.1';
const DATA_FILE = path.join(__dirname, 'tickets.json');

// File locking mechanism for sequential access
let fileLock = false;
const lockQueue = [];

function acquireLock() {
    return new Promise((resolve) => {
        if (!fileLock) {
            fileLock = true;
            resolve();
        } else {
            lockQueue.push(resolve);
        }
    });
}

function releaseLock() {
    if (lockQueue.length > 0) {
        const next = lockQueue.shift();
        next();
    } else {
        fileLock = false;
    }
}

// Initialize data file if it doesn't exist
function initDataFile() {
    if (!fs.existsSync(DATA_FILE)) {
        fs.writeFileSync(DATA_FILE, '[]', 'utf8');
    }
}

// Read tickets from file
async function readTickets() {
    await acquireLock();
    try {
        const data = fs.readFileSync(DATA_FILE, 'utf8');
        return JSON.parse(data);
    } finally {
        releaseLock();
    }
}

// Write tickets to file
async function writeTickets(tickets) {
    await acquireLock();
    try {
        fs.writeFileSync(DATA_FILE, JSON.stringify(tickets, null, 2), 'utf8');
    } finally {
        releaseLock();
    }
}

// Generate unique ID
function generateId() {
    return Date.now().toString(36) + Math.random().toString(36).substr(2, 9);
}

// Validate ticket fields
function validateTicket(body) {
    const errors = [];
    const required = ['subject', 'description', 'priority', 'status'];

    for (const field of required) {
        if (!body[field] || typeof body[field] !== 'string' || body[field].trim() === '') {
            errors.push(`${field} is required and must be a non-empty string`);
        }
    }

    if (body.priority && !['low', 'medium', 'high'].includes(body.priority)) {
        errors.push('priority must be one of: low, medium, high');
    }

    if (body.status && !['open', 'in_progress', 'resolved'].includes(body.status)) {
        errors.push('status must be one of: open, in_progress, resolved');
    }

    return errors;
}

// Parse JSON body
function parseBody(req) {
    return new Promise((resolve, reject) => {
        let body = '';
        req.on('data', chunk => {
            body += chunk.toString();
        });
        req.on('end', () => {
            try {
                resolve(body ? JSON.parse(body) : {});
            } catch (e) {
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

// Handle GET /tickets
async function handleGetTickets(req, res) {
    const url = new URL(req.url, `http://${HOST}:${PORT}`);
    const statusFilter = url.searchParams.get('status');
    const priorityFilter = url.searchParams.get('priority');

    try {
        let tickets = await readTickets();

        if (statusFilter) {
            tickets = tickets.filter(t => t.status === statusFilter);
        }
        if (priorityFilter) {
            tickets = tickets.filter(t => t.priority === priorityFilter);
        }

        sendJson(res, 200, tickets);
    } catch (error) {
        sendJson(res, 500, { error: 'Internal server error' });
    }
}

// Handle POST /tickets
async function handlePostTickets(req, res) {
    try {
        const body = await parseBody(req);
        const errors = validateTicket(body);

        if (errors.length > 0) {
            return sendJson(res, 400, { error: 'Validation failed', details: errors });
        }

        const now = new Date().toISOString();
        const ticket = {
            id: generateId(),
            subject: body.subject.trim(),
            description: body.description.trim(),
            priority: body.priority,
            status: body.status,
            created_at: now,
            updated_at: now
        };

        const tickets = await readTickets();
        tickets.push(ticket);
        await writeTickets(tickets);

        sendJson(res, 201, ticket);
    } catch (error) {
        if (error.message === 'Invalid JSON') {
            return sendJson(res, 400, { error: 'Invalid JSON in request body' });
        }
        sendJson(res, 500, { error: 'Internal server error' });
    }
}

// Handle GET /tickets/{id}
async function handleGetTicket(req, res, id) {
    try {
        const tickets = await readTickets();
        const ticket = tickets.find(t => t.id === id);

        if (!ticket) {
            return sendJson(res, 404, { error: 'Ticket not found' });
        }

        sendJson(res, 200, ticket);
    } catch (error) {
        sendJson(res, 500, { error: 'Internal server error' });
    }
}

// Handle PATCH /tickets/{id}
async function handlePatchTicket(req, res, id) {
    try {
        const body = await parseBody(req);
        const allowedFields = ['subject', 'description', 'priority', 'status'];
        const updates = {};

        for (const field of allowedFields) {
            if (body[field] !== undefined) {
                if (field === 'priority' && !['low', 'medium', 'high'].includes(body[field])) {
                    return sendJson(res, 400, { error: 'priority must be one of: low, medium, high' });
                }
                if (field === 'status' && !['open', 'in_progress', 'resolved'].includes(body[field])) {
                    return sendJson(res, 400, { error: 'status must be one of: open, in_progress, resolved' });
                }
                updates[field] = typeof body[field] === 'string' ? body[field].trim() : body[field];
            }
        }

        if (Object.keys(updates).length === 0) {
            return sendJson(res, 400, { error: 'No valid fields to update' });
        }

        const tickets = await readTickets();
        const index = tickets.findIndex(t => t.id === id);

        if (index === -1) {
            return sendJson(res, 404, { error: 'Ticket not found' });
        }

        tickets[index] = {
            ...tickets[index],
            ...updates,
            updated_at: new Date().toISOString()
        };

        await writeTickets(tickets);
        sendJson(res, 200, tickets[index]);
    } catch (error) {
        if (error.message === 'Invalid JSON') {
            return sendJson(res, 400, { error: 'Invalid JSON in request body' });
        }
        sendJson(res, 500, { error: 'Internal server error' });
    }
}

// Handle DELETE /tickets/{id}
async function handleDeleteTicket(req, res, id) {
    try {
        const tickets = await readTickets();
        const index = tickets.findIndex(t => t.id === id);

        if (index === -1) {
            return sendJson(res, 404, { error: 'Ticket not found' });
        }

        tickets.splice(index, 1);
        await writeTickets(tickets);

        sendJson(res, 200, { message: 'Ticket deleted successfully' });
    } catch (error) {
        sendJson(res, 500, { error: 'Internal server error' });
    }
}

// Handle GET /metrics
async function handleGetMetrics(req, res) {
    try {
        const tickets = await readTickets();
        const now = new Date();

        const metrics = {
            by_status: {
                open: tickets.filter(t => t.status === 'open').length,
                in_progress: tickets.filter(t => t.status === 'in_progress').length,
                resolved: tickets.filter(t => t.status === 'resolved').length
            },
            by_priority: {
                low: tickets.filter(t => t.priority === 'low').length,
                medium: tickets.filter(t => t.priority === 'medium').length,
                high: tickets.filter(t => t.priority === 'high').length
            },
            average_open_age_seconds: 0
        };

        const openTickets = tickets.filter(t => t.status === 'open');
        if (openTickets.length > 0) {
            const totalAge = openTickets.reduce((sum, ticket) => {
                const created = new Date(ticket.created_at);
                return sum + (now - created);
            }, 0);
            metrics.average_open_age_seconds = Math.round(totalAge / openTickets.length / 1000);
        }

        sendJson(res, 200, metrics);
    } catch (error) {
        sendJson(res, 500, { error: 'Internal server error' });
    }
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

    const url = new URL(req.url, `http://${HOST}:${PORT}`);
    const pathParts = url.pathname.split('/').filter(p => p);

    // Route matching
    try {
        // GET /tickets or GET /tickets?status=...&priority=...
        if (req.method === 'GET' && pathParts.length === 1 && pathParts[0] === 'tickets') {
            return await handleGetTickets(req, res);
        }

        // POST /tickets
        if (req.method === 'POST' && pathParts.length === 1 && pathParts[0] === 'tickets') {
            return await handlePostTickets(req, res);
        }

        // GET /tickets/{id}
        if (req.method === 'GET' && pathParts.length === 2 && pathParts[0] === 'tickets') {
            return await handleGetTicket(req, res, pathParts[1]);
        }

        // PATCH /tickets/{id}
        if (req.method === 'PATCH' && pathParts.length === 2 && pathParts[0] === 'tickets') {
            return await handlePatchTicket(req, res, pathParts[1]);
        }

        // DELETE /tickets/{id}
        if (req.method === 'DELETE' && pathParts.length === 2 && pathParts[0] === 'tickets') {
            return await handleDeleteTicket(req, res, pathParts[1]);
        }

        // GET /metrics
        if (req.method === 'GET' && pathParts.length === 1 && pathParts[0] === 'metrics') {
            return await handleGetMetrics(req, res);
        }

        // Unknown route
        if (pathParts.length === 0 || (pathParts[0] !== 'tickets' && pathParts[0] !== 'metrics')) {
            return sendJson(res, 404, { error: 'Route not found' });
        }

        // Method not allowed
        sendJson(res, 405, { error: 'Method not allowed' });
    } catch (error) {
        sendJson(res, 500, { error: 'Internal server error' });
    }
}

// Start server
initDataFile();

const server = http.createServer(handleRequest);

server.listen(PORT, HOST, () => {
    console.log(`Server running at http://${HOST}:${PORT}/`);
});
