const http = require('http');
const fs = require('fs');
const path = require('path');
const { randomUUID } = require('crypto');

const PORT = process.env.PORT || 8080;
const HOST = '127.0.0.1';
const DATA_FILE = path.join(__dirname, 'tickets.json');

// File locking for sequential access
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

// Read tickets from file
async function readTickets() {
    await acquireLock();
    try {
        if (!fs.existsSync(DATA_FILE)) {
            return [];
        }
        const data = fs.readFileSync(DATA_FILE, 'utf8');
        if (!data.trim()) {
            return [];
        }
        return JSON.parse(data);
    } catch (err) {
        return [];
    } finally {
        releaseLock();
    }
}

// Write tickets to file
async function writeTickets(tickets) {
    await acquireLock();
    try {
        fs.writeFileSync(DATA_FILE, JSON.stringify(tickets, null, 2), 'utf8');
        return true;
    } catch (err) {
        return false;
    } finally {
        releaseLock();
    }
}

// Parse URL with query params
function parseURL(url) {
    const [pathname, queryString] = url.split('?');
    const params = {};
    if (queryString) {
        queryString.split('&').forEach(pair => {
            const [key, value] = pair.split('=');
            params[decodeURIComponent(key)] = decodeURIComponent(value || '');
        });
    }
    return { pathname, params };
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

// Send JSON response
function sendJSON(res, statusCode, data) {
    const headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type'
    };
    res.writeHead(statusCode, headers);
    res.end(JSON.stringify(data));
}

// Validate ticket creation data
function validateCreateTicket(body) {
    const errors = [];
    if (!body || typeof body !== 'object') {
        return { valid: false, errors: ['Request body is required'] };
    }
    if (!body.subject || typeof body.subject !== 'string' || body.subject.trim() === '') {
        errors.push('subject is required and must be a non-empty string');
    }
    if (!body.description || typeof body.description !== 'string' || body.description.trim() === '') {
        errors.push('description is required and must be a non-empty string');
    }
    if (body.priority && !['low', 'medium', 'high'].includes(body.priority)) {
        errors.push('priority must be low, medium, or high');
    }
    if (body.status && !['open', 'in_progress', 'resolved'].includes(body.status)) {
        errors.push('status must be open, in_progress, or resolved');
    }
    return { valid: errors.length === 0, errors };
}

// Validate ticket update data
function validateUpdateTicket(body) {
    const errors = [];
    if (!body || typeof body !== 'object') {
        return { valid: false, errors: ['Request body is required'] };
    }
    if (Object.keys(body).length === 0) {
        return { valid: false, errors: ['At least one field to update is required'] };
    }
    if (body.subject !== undefined && (typeof body.subject !== 'string' || body.subject.trim() === '')) {
        errors.push('subject must be a non-empty string');
    }
    if (body.description !== undefined && (typeof body.description !== 'string' || body.description.trim() === '')) {
        errors.push('description must be a non-empty string');
    }
    if (body.priority !== undefined && !['low', 'medium', 'high'].includes(body.priority)) {
        errors.push('priority must be low, medium, or high');
    }
    if (body.status !== undefined && !['open', 'in_progress', 'resolved'].includes(body.status)) {
        errors.push('status must be open, in_progress, or resolved');
    }
    const allowedFields = ['subject', 'description', 'priority', 'status'];
    const invalidFields = Object.keys(body).filter(k => !allowedFields.includes(k));
    if (invalidFields.length > 0) {
        errors.push(`Invalid fields: ${invalidFields.join(', ')}`);
    }
    return { valid: errors.length === 0, errors };
}

// Route handlers
async function handleGetTickets(req, res, params) {
    const tickets = await readTickets();
    let filtered = tickets;

    if (params.status) {
        const statusList = params.status.split(',').map(s => s.trim());
        filtered = filtered.filter(t => statusList.includes(t.status));
    }
    if (params.priority) {
        const priorityList = params.priority.split(',').map(p => p.trim());
        filtered = filtered.filter(t => priorityList.includes(t.priority));
    }

    sendJSON(res, 200, { tickets: filtered });
}

async function handlePostTicket(req, res) {
    let body;
    try {
        body = await parseBody(req);
    } catch (err) {
        return sendJSON(res, 400, { error: 'Invalid JSON in request body' });
    }

    const validation = validateCreateTicket(body);
    if (!validation.valid) {
        return sendJSON(res, 400, { error: 'Validation failed', details: validation.errors });
    }

    const tickets = await readTickets();
    const now = new Date().toISOString();
    const newTicket = {
        id: randomUUID(),
        subject: body.subject.trim(),
        description: body.description.trim(),
        priority: body.priority || 'low',
        status: body.status || 'open',
        created_at: now,
        updated_at: now
    };
    tickets.push(newTicket);
    await writeTickets(tickets);
    sendJSON(res, 201, { ticket: newTicket });
}

async function handleGetTicket(req, res, id) {
    const tickets = await readTickets();
    const ticket = tickets.find(t => t.id === id);
    if (!ticket) {
        return sendJSON(res, 404, { error: 'Ticket not found' });
    }
    sendJSON(res, 200, { ticket });
}

async function handlePatchTicket(req, res, id) {
    let body;
    try {
        body = await parseBody(req);
    } catch (err) {
        return sendJSON(res, 400, { error: 'Invalid JSON in request body' });
    }

    const validation = validateUpdateTicket(body);
    if (!validation.valid) {
        return sendJSON(res, 400, { error: 'Validation failed', details: validation.errors });
    }

    const tickets = await readTickets();
    const index = tickets.findIndex(t => t.id === id);
    if (index === -1) {
        return sendJSON(res, 404, { error: 'Ticket not found' });
    }

    const now = new Date().toISOString();
    const updatedTicket = {
        ...tickets[index],
        ...body,
        id: tickets[index].id,
        created_at: tickets[index].created_at,
        updated_at: now
    };
    tickets[index] = updatedTicket;
    await writeTickets(tickets);
    sendJSON(res, 200, { ticket: updatedTicket });
}

async function handleDeleteTicket(req, res, id) {
    const tickets = await readTickets();
    const index = tickets.findIndex(t => t.id === id);
    if (index === -1) {
        return sendJSON(res, 404, { error: 'Ticket not found' });
    }

    const deleted = tickets.splice(index, 1)[0];
    await writeTickets(tickets);
    sendJSON(res, 200, { ticket: deleted, message: 'Ticket deleted' });
}

async function handleGetMetrics(req, res) {
    const tickets = await readTickets();

    const statusCounts = { open: 0, in_progress: 0, resolved: 0 };
    const priorityCounts = { low: 0, medium: 0, high: 0 };
    let totalAgeSeconds = 0;
    let openCount = 0;
    const now = new Date();

    tickets.forEach(ticket => {
        if (statusCounts.hasOwnProperty(ticket.status)) {
            statusCounts[ticket.status]++;
        }
        if (priorityCounts.hasOwnProperty(ticket.priority)) {
            priorityCounts[ticket.priority]++;
        }
        if (ticket.status === 'open') {
            const created = new Date(ticket.created_at);
            totalAgeSeconds += (now - created) / 1000;
            openCount++;
        }
    });

    const metrics = {
        by_status: statusCounts,
        by_priority: priorityCounts,
        average_open_age_seconds: openCount > 0 ? Math.round(totalAgeSeconds / openCount * 100) / 100 : 0
    };

    sendJSON(res, 200, metrics);
}

// Initialize tickets file if not exists
function initDataFile() {
    if (!fs.existsSync(DATA_FILE)) {
        fs.writeFileSync(DATA_FILE, '[]', 'utf8');
    }
}

// Main request handler
async function handleRequest(req, res) {
    const { pathname, params } = parseURL(req.url);
    const method = req.method.toUpperCase();

    // Handle CORS preflight
    if (method === 'OPTIONS') {
        res.writeHead(204, {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type'
        });
        return res.end();
    }

    // Route matching
    try {
        // GET /tickets
        if (pathname === '/tickets' && method === 'GET') {
            return await handleGetTickets(req, res, params);
        }

        // POST /tickets
        if (pathname === '/tickets' && method === 'POST') {
            return await handlePostTicket(req, res);
        }

        // GET /metrics
        if (pathname === '/metrics' && method === 'GET') {
            return await handleGetMetrics(req, res);
        }

        // /tickets/{id} routes
        const ticketMatch = pathname.match(/^\/tickets\/([a-f0-9-]+)$/);
        if (ticketMatch) {
            const id = ticketMatch[1];
            switch (method) {
                case 'GET':
                    return await handleGetTicket(req, res, id);
                case 'PATCH':
                    return await handlePatchTicket(req, res, id);
                case 'DELETE':
                    return await handleDeleteTicket(req, res, id);
                default:
                    return sendJSON(res, 405, { error: 'Method not allowed' });
            }
        }

        // Unknown route
        sendJSON(res, 404, { error: 'Route not found' });

    } catch (err) {
        console.error('Server error:', err);
        sendJSON(res, 500, { error: 'Internal server error' });
    }
}

// Start server
initDataFile();
const server = http.createServer(handleRequest);
server.listen(PORT, HOST, () => {
    console.log(`Server running at http://${HOST}:${PORT}/`);
});
