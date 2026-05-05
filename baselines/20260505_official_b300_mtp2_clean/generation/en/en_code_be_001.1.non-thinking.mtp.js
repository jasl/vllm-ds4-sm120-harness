const http = require('http');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const PORT = process.env.PORT || 8080;
const HOST = '127.0.0.1';
const DATA_FILE = path.join(__dirname, 'tickets.json');

// Initialize data file if it doesn't exist
function initDataFile() {
    try {
        if (!fs.existsSync(DATA_FILE)) {
            fs.writeFileSync(DATA_FILE, JSON.stringify({ tickets: [], nextId: 1 }), 'utf8');
        }
    } catch (err) {
        console.error('Failed to initialize data file:', err);
        process.exit(1);
    }
}

// Read data from file with lock mechanism
let fileLock = false;
const fileQueue = [];

function acquireLock(callback) {
    if (!fileLock) {
        fileLock = true;
        callback();
    } else {
        fileQueue.push(callback);
    }
}

function releaseLock() {
    if (fileQueue.length > 0) {
        const next = fileQueue.shift();
        next();
    } else {
        fileLock = false;
    }
}

function readData() {
    return new Promise((resolve, reject) => {
        acquireLock(() => {
            fs.readFile(DATA_FILE, 'utf8', (err, data) => {
                try {
                    if (err) {
                        releaseLock();
                        reject(err);
                        return;
                    }
                    const parsed = JSON.parse(data);
                    releaseLock();
                    resolve(parsed);
                } catch (parseErr) {
                    releaseLock();
                    reject(parseErr);
                }
            });
        });
    });
}

function writeData(data) {
    return new Promise((resolve, reject) => {
        acquireLock(() => {
            const tempFile = DATA_FILE + '.tmp';
            fs.writeFile(tempFile, JSON.stringify(data, null, 2), 'utf8', (err) => {
                if (err) {
                    releaseLock();
                    reject(err);
                    return;
                }
                fs.rename(tempFile, DATA_FILE, (renameErr) => {
                    if (renameErr) {
                        releaseLock();
                        reject(renameErr);
                        return;
                    }
                    releaseLock();
                    resolve();
                });
            });
        });
    });
}

// Helper functions
function generateId() {
    return crypto.randomBytes(16).toString('hex');
}

function getCurrentTime() {
    return new Date().toISOString();
}

function validateTicketBody(body, isUpdate = false) {
    const errors = [];

    if (!isUpdate) {
        if (!body.subject || typeof body.subject !== 'string' || body.subject.trim() === '') {
            errors.push('subject is required and must be a non-empty string');
        }
        if (!body.description || typeof body.description !== 'string' || body.description.trim() === '') {
            errors.push('description is required and must be a non-empty string');
        }
        if (!body.priority || !['low', 'medium', 'high'].includes(body.priority)) {
            errors.push('priority is required and must be one of: low, medium, high');
        }
    } else {
        if (body.subject !== undefined && (typeof body.subject !== 'string' || body.subject.trim() === '')) {
            errors.push('subject must be a non-empty string');
        }
        if (body.description !== undefined && (typeof body.description !== 'string' || body.description.trim() === '')) {
            errors.push('description must be a non-empty string');
        }
        if (body.priority !== undefined && !['low', 'medium', 'high'].includes(body.priority)) {
            errors.push('priority must be one of: low, medium, high');
        }
        if (body.status !== undefined && !['open', 'in_progress', 'resolved'].includes(body.status)) {
            errors.push('status must be one of: open, in_progress, resolved');
        }
    }

    return errors;
}

function sendJSON(res, statusCode, data) {
    const body = JSON.stringify(data);
    res.writeHead(statusCode, {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(body),
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type'
    });
    res.end(body);
}

function parseBody(req) {
    return new Promise((resolve, reject) => {
        let body = '';
        req.on('data', chunk => {
            body += chunk.toString();
            if (body.length > 1048576) { // 1MB limit
                reject(new Error('Request body too large'));
            }
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

function getPathSegments(url) {
    const parsed = new URL(url, `http://${HOST}:${PORT}`);
    const pathname = parsed.pathname.replace(/\/+$/, '') || '/';
    const segments = pathname.split('/').filter(Boolean);
    const query = Object.fromEntries(parsed.searchParams);
    return { segments, query };
}

// Route handlers
async function handleGetTickets(res, query) {
    try {
        const data = await readData();
        let tickets = data.tickets;

        if (query.status) {
            tickets = tickets.filter(t => t.status === query.status);
        }
        if (query.priority) {
            tickets = tickets.filter(t => t.priority === query.priority);
        }

        sendJSON(res, 200, { tickets });
    } catch (err) {
        sendJSON(res, 500, { error: 'Internal server error' });
    }
}

async function handleCreateTicket(req, res) {
    try {
        const body = await parseBody(req);
        if (!body) {
            sendJSON(res, 400, { error: 'Request body is required' });
            return;
        }

        const errors = validateTicketBody(body);
        if (errors.length > 0) {
            sendJSON(res, 400, { error: 'Validation failed', details: errors });
            return;
        }

        const data = await readData();
        const now = getCurrentTime();

        const ticket = {
            id: generateId(),
            subject: body.subject.trim(),
            description: body.description.trim(),
            priority: body.priority,
            status: 'open',
            created_at: now,
            updated_at: now
        };

        data.tickets.push(ticket);
        data.nextId = (parseInt(data.nextId) || 0) + 1;

        await writeData(data);
        sendJSON(res, 201, { ticket });
    } catch (err) {
        if (err.message === 'Invalid JSON' || err.message === 'Request body too large') {
            sendJSON(res, 400, { error: err.message });
        } else {
            sendJSON(res, 500, { error: 'Internal server error' });
        }
    }
}

async function handleGetTicket(res, id) {
    try {
        const data = await readData();
        const ticket = data.tickets.find(t => t.id === id);

        if (!ticket) {
            sendJSON(res, 404, { error: 'Ticket not found' });
            return;
        }

        sendJSON(res, 200, { ticket });
    } catch (err) {
        sendJSON(res, 500, { error: 'Internal server error' });
    }
}

async function handleUpdateTicket(req, res, id) {
    try {
        const body = await parseBody(req);
        if (!body) {
            sendJSON(res, 400, { error: 'Request body is required' });
            return;
        }

        const errors = validateTicketBody(body, true);
        if (errors.length > 0) {
            sendJSON(res, 400, { error: 'Validation failed', details: errors });
            return;
        }

        const data = await readData();
        const ticketIndex = data.tickets.findIndex(t => t.id === id);

        if (ticketIndex === -1) {
            sendJSON(res, 404, { error: 'Ticket not found' });
            return;
        }

        const now = getCurrentTime();
        const updates = {};

        if (body.subject !== undefined) updates.subject = body.subject.trim();
        if (body.description !== undefined) updates.description = body.description.trim();
        if (body.priority !== undefined) updates.priority = body.priority;
        if (body.status !== undefined) updates.status = body.status;
        updates.updated_at = now;

        data.tickets[ticketIndex] = { ...data.tickets[ticketIndex], ...updates };

        await writeData(data);
        sendJSON(res, 200, { ticket: data.tickets[ticketIndex] });
    } catch (err) {
        if (err.message === 'Invalid JSON' || err.message === 'Request body too large') {
            sendJSON(res, 400, { error: err.message });
        } else {
            sendJSON(res, 500, { error: 'Internal server error' });
        }
    }
}

async function handleDeleteTicket(res, id) {
    try {
        const data = await readData();
        const ticketIndex = data.tickets.findIndex(t => t.id === id);

        if (ticketIndex === -1) {
            sendJSON(res, 404, { error: 'Ticket not found' });
            return;
        }

        data.tickets.splice(ticketIndex, 1);

        await writeData(data);
        sendJSON(res, 200, { message: 'Ticket deleted successfully' });
    } catch (err) {
        sendJSON(res, 500, { error: 'Internal server error' });
    }
}

async function handleMetrics(res) {
    try {
        const data = await readData();
        const tickets = data.tickets;

        // Counts by status
        const statusCounts = { open: 0, in_progress: 0, resolved: 0 };
        // Counts by priority
        const priorityCounts = { low: 0, medium: 0, high: 0 };

        let totalOpenAge = 0;
        let openTicketCount = 0;
        const now = new Date();

        tickets.forEach(ticket => {
            // Status counts
            if (statusCounts.hasOwnProperty(ticket.status)) {
                statusCounts[ticket.status]++;
            }

            // Priority counts
            if (priorityCounts.hasOwnProperty(ticket.priority)) {
                priorityCounts[ticket.priority]++;
            }

            // Average age of open tickets
            if (ticket.status === 'open') {
                const created = new Date(ticket.created_at);
                const ageInSeconds = (now - created) / 1000;
                totalOpenAge += ageInSeconds;
                openTicketCount++;
            }
        });

        const averageAgeInSeconds = openTicketCount > 0 ? totalOpenAge / openTicketCount : 0;

        sendJSON(res, 200, {
            counts_by_status: statusCounts,
            counts_by_priority: priorityCounts,
            average_age_of_open_tickets_seconds: Math.round(averageAgeInSeconds * 100) / 100
        });
    } catch (err) {
        sendJSON(res, 500, { error: 'Internal server error' });
    }
}

// Main request handler
async function handleRequest(req, res) {
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

    const { segments, query } = getPathSegments(req.url);

    try {
        // Route matching
        if (segments.length === 0 && req.url === '/') {
            sendJSON(res, 200, { message: 'Help Desk Ticket API', version: '1.0.0' });
            return;
        }

        if (segments[0] === 'tickets' && segments.length === 1) {
            if (req.method === 'GET') {
                await handleGetTickets(res, query);
            } else if (req.method === 'POST') {
                await handleCreateTicket(req, res);
            } else {
                sendJSON(res, 405, { error: 'Method not allowed' });
            }
            return;
        }

        if (segments[0] === 'tickets' && segments.length === 2) {
            const id = segments[1];
            if (req.method === 'GET') {
                await handleGetTicket(res, id);
            } else if (req.method === 'PATCH') {
                await handleUpdateTicket(req, res, id);
            } else if (req.method === 'DELETE') {
                await handleDeleteTicket(res, id);
            } else {
                sendJSON(res, 405, { error: 'Method not allowed' });
            }
            return;
        }

        if (segments[0] === 'metrics' && segments.length === 1 && req.method === 'GET') {
            await handleMetrics(res);
            return;
        }

        // Unknown route
        sendJSON(res, 404, { error: 'Route not found' });
    } catch (err) {
        console.error('Request handler error:', err);
        sendJSON(res, 500, { error: 'Internal server error' });
    }
}

// Start server
initDataFile();

const server = http.createServer(handleRequest);

server.listen(PORT, HOST, () => {
    console.log(`Server running at http://${HOST}:${PORT}/`);
});
