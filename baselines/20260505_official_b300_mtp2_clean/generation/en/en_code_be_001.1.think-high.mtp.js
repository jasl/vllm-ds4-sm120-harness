const http = require('http');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const HOST = '127.0.0.1';
const PORT = 8080;
const DATA_FILE = path.join(__dirname, 'tickets.json');

// File locking mechanism for safe concurrent access
class FileLock {
    constructor() {
        this.locked = false;
        this.queue = [];
    }

    acquire() {
        return new Promise((resolve) => {
            if (!this.locked) {
                this.locked = true;
                resolve();
            } else {
                this.queue.push(resolve);
            }
        });
    }

    release() {
        if (this.queue.length > 0) {
            const next = this.queue.shift();
            next();
        } else {
            this.locked = false;
        }
    }
}

const lock = new FileLock();

// Load tickets from file
function loadTickets() {
    try {
        if (!fs.existsSync(DATA_FILE)) {
            return [];
        }
        const data = fs.readFileSync(DATA_FILE, 'utf8');
        return JSON.parse(data);
    } catch (error) {
        return [];
    }
}

// Save tickets to file
function saveTickets(tickets) {
    fs.writeFileSync(DATA_FILE, JSON.stringify(tickets, null, 2), 'utf8');
}

// Generate unique ID
function generateId() {
    return crypto.randomUUID();
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
                if (!body) {
                    resolve({});
                    return;
                }
                resolve(JSON.parse(body));
            } catch (error) {
                reject(new Error('Invalid JSON'));
            }
        });
        req.on('error', reject);
    });
}

// Send JSON response
function sendJSON(res, statusCode, data) {
    res.writeHead(statusCode, {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type'
    });
    res.end(JSON.stringify(data));
}

// Parse URL query parameters
function parseQuery(url) {
    const query = {};
    const queryString = url.split('?')[1];
    if (queryString) {
        const pairs = queryString.split('&');
        for (const pair of pairs) {
            const [key, value] = pair.split('=');
            query[decodeURIComponent(key)] = decodeURIComponent(value);
        }
    }
    return query;
}

// Parse URL path
function parsePath(url) {
    return url.split('?')[0].split('/').filter(Boolean);
}

// Calculate average age of open tickets in seconds
function calculateAverageAge(tickets) {
    const openTickets = tickets.filter(t => t.status === 'open');
    if (openTickets.length === 0) return 0;

    const now = Date.now();
    const totalAge = openTickets.reduce((sum, ticket) => {
        const created = new Date(ticket.created_at).getTime();
        return sum + (now - created);
    }, 0);

    return Math.floor(totalAge / openTickets.length / 1000);
}

// Routes handling
async function handleRoutes(req, res) {
    const { method, url } = req;
    const pathParts = parsePath(url);
    const query = parseQuery(url);

    // CORS preflight
    if (method === 'OPTIONS') {
        sendJSON(res, 200, {});
        return;
    }

    // Route: GET /tickets
    if (method === 'GET' && pathParts.length === 1 && pathParts[0] === 'tickets') {
        await lock.acquire();
        try {
            let tickets = loadTickets();

            if (query.status) {
                tickets = tickets.filter(t => t.status === query.status);
            }
            if (query.priority) {
                tickets = tickets.filter(t => t.priority === query.priority);
            }

            sendJSON(res, 200, tickets);
        } finally {
            lock.release();
        }
        return;
    }

    // Route: POST /tickets
    if (method === 'POST' && pathParts.length === 1 && pathParts[0] === 'tickets') {
        let body;
        try {
            body = await parseBody(req);
        } catch (error) {
            sendJSON(res, 400, { error: 'Invalid JSON in request body' });
            return;
        }

        const errors = validateTicket(body);
        if (errors.length > 0) {
            sendJSON(res, 400, { error: 'Validation failed', details: errors });
            return;
        }

        await lock.acquire();
        try {
            const tickets = loadTickets();
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
            tickets.push(ticket);
            saveTickets(tickets);
            sendJSON(res, 201, ticket);
        } finally {
            lock.release();
        }
        return;
    }

    // Route: GET /metrics
    if (method === 'GET' && pathParts.length === 1 && pathParts[0] === 'metrics') {
        await lock.acquire();
        try {
            const tickets = loadTickets();

            // Count by status
            const statusCounts = { open: 0, in_progress: 0, resolved: 0 };
            tickets.forEach(t => {
                if (statusCounts.hasOwnProperty(t.status)) {
                    statusCounts[t.status]++;
                }
            });

            // Count by priority
            const priorityCounts = { low: 0, medium: 0, high: 0 };
            tickets.forEach(t => {
                if (priorityCounts.hasOwnProperty(t.priority)) {
                    priorityCounts[t.priority]++;
                }
            });

            const metrics = {
                status_counts: statusCounts,
                priority_counts: priorityCounts,
                average_age_open_seconds: calculateAverageAge(tickets)
            };

            sendJSON(res, 200, metrics);
        } finally {
            lock.release();
        }
        return;
    }

    // Route: GET /tickets/{id}
    if (method === 'GET' && pathParts.length === 2 && pathParts[0] === 'tickets') {
        const id = pathParts[1];
        await lock.acquire();
        try {
            const tickets = loadTickets();
            const ticket = tickets.find(t => t.id === id);
            if (!ticket) {
                sendJSON(res, 404, { error: 'Ticket not found' });
                return;
            }
            sendJSON(res, 200, ticket);
        } finally {
            lock.release();
        }
        return;
    }

    // Route: PATCH /tickets/{id}
    if (method === 'PATCH' && pathParts.length === 2 && pathParts[0] === 'tickets') {
        const id = pathParts[1];
        let body;
        try {
            body = await parseBody(req);
        } catch (error) {
            sendJSON(res, 400, { error: 'Invalid JSON in request body' });
            return;
        }

        // Validate if any fields provided
        const allowedFields = ['subject', 'description', 'priority', 'status'];
        const hasValidField = Object.keys(body).some(key => allowedFields.includes(key));
        if (!hasValidField) {
            sendJSON(res, 400, { error: 'No valid fields to update. Allowed fields: subject, description, priority, status' });
            return;
        }

        // Validate individual fields
        if (body.subject !== undefined && (typeof body.subject !== 'string' || body.subject.trim() === '')) {
            sendJSON(res, 400, { error: 'subject must be a non-empty string' });
            return;
        }
        if (body.description !== undefined && (typeof body.description !== 'string' || body.description.trim() === '')) {
            sendJSON(res, 400, { error: 'description must be a non-empty string' });
            return;
        }
        if (body.priority !== undefined && !['low', 'medium', 'high'].includes(body.priority)) {
            sendJSON(res, 400, { error: 'priority must be one of: low, medium, high' });
            return;
        }
        if (body.status !== undefined && !['open', 'in_progress', 'resolved'].includes(body.status)) {
            sendJSON(res, 400, { error: 'status must be one of: open, in_progress, resolved' });
            return;
        }

        await lock.acquire();
        try {
            const tickets = loadTickets();
            const index = tickets.findIndex(t => t.id === id);
            if (index === -1) {
                sendJSON(res, 404, { error: 'Ticket not found' });
                return;
            }

            // Update fields
            if (body.subject) tickets[index].subject = body.subject.trim();
            if (body.description) tickets[index].description = body.description.trim();
            if (body.priority) tickets[index].priority = body.priority;
            if (body.status) tickets[index].status = body.status;
            tickets[index].updated_at = new Date().toISOString();

            saveTickets(tickets);
            sendJSON(res, 200, tickets[index]);
        } finally {
            lock.release();
        }
        return;
    }

    // Route: DELETE /tickets/{id}
    if (method === 'DELETE' && pathParts.length === 2 && pathParts[0] === 'tickets') {
        const id = pathParts[1];
        await lock.acquire();
        try {
            const tickets = loadTickets();
            const index = tickets.findIndex(t => t.id === id);
            if (index === -1) {
                sendJSON(res, 404, { error: 'Ticket not found' });
                return;
            }
            tickets.splice(index, 1);
            saveTickets(tickets);
            sendJSON(res, 200, { message: 'Ticket deleted successfully' });
        } finally {
            lock.release();
        }
        return;
    }

    // 404 for unknown routes
    sendJSON(res, 404, { error: 'Route not found' });
}

// Create and start server
const server = http.createServer((req, res) => {
    handleRoutes(req, res).catch(error => {
        console.error('Server error:', error);
        sendJSON(res, 500, { error: 'Internal server error' });
    });
});

server.listen(PORT, HOST, () => {
    console.log(`Server running at http://${HOST}:${PORT}/`);
});
