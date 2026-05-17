const http = require('http');
const fs = require('fs');
const path = require('path');
const { promisify } = require('util');

const DATA_FILE = path.join(__dirname, 'tickets.json');
const HOST = '127.0.0.1';
const PORT = 8080;

const readFileAsync = promisify(fs.readFile);
const writeFileAsync = promisify(fs.writeFile);

let ticketData = [];
let nextId = 1;
let fileLock = false;
const requestQueue = [];

function loadData() {
    try {
        if (fs.existsSync(DATA_FILE)) {
            const content = fs.readFileSync(DATA_FILE, 'utf8');
            if (content.trim()) {
                const parsed = JSON.parse(content);
                ticketData = parsed.tickets || [];
                nextId = parsed.nextId || 1;
            } else {
                ticketData = [];
                nextId = 1;
            }
        } else {
            ticketData = [];
            nextId = 1;
            saveDataSync();
        }
    } catch (err) {
        console.error('Error loading data:', err);
        ticketData = [];
        nextId = 1;
    }
}

function saveDataSync() {
    const data = JSON.stringify({ tickets: ticketData, nextId }, null, 2);
    fs.writeFileSync(DATA_FILE, data, 'utf8');
}

async function acquireLock() {
    return new Promise((resolve) => {
        if (!fileLock) {
            fileLock = true;
            resolve();
        } else {
            requestQueue.push(resolve);
        }
    });
}

function releaseLock() {
    if (requestQueue.length > 0) {
        const next = requestQueue.shift();
        next();
    } else {
        fileLock = false;
    }
}

function saveData() {
    return new Promise((resolve, reject) => {
        try {
            const data = JSON.stringify({ tickets: ticketData, nextId }, null, 2);
            fs.writeFile(DATA_FILE, data, 'utf8', (err) => {
                if (err) reject(err);
                else resolve();
            });
        } catch (err) {
            reject(err);
        }
    });
}

function validateTicket(body) {
    const errors = [];

    if (!body.subject || typeof body.subject !== 'string' || !body.subject.trim()) {
        errors.push('subject is required and must be a non-empty string');
    }

    if (!body.description || typeof body.description !== 'string' || !body.description.trim()) {
        errors.push('description is required and must be a non-empty string');
    }

    const validPriority = ['low', 'medium', 'high'];
    if (body.priority && !validPriority.includes(body.priority)) {
        errors.push('priority must be one of: low, medium, high');
    }

    const validStatus = ['open', 'in_progress', 'resolved'];
    if (body.status && !validStatus.includes(body.status)) {
        errors.push('status must be one of: open, in_progress, resolved');
    }

    return errors;
}

function setCorsHeaders(res) {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
}

function sendJson(res, statusCode, data) {
    res.writeHead(statusCode, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(data));
}

function parseUrl(url) {
    const parsedUrl = new URL(url, `http://${HOST}:${PORT}`);
    const pathname = parsedUrl.pathname;
    const searchParams = parsedUrl.searchParams;
    return { pathname, searchParams };
}

function getTicketById(id) {
    return ticketData.find(t => t.id === id);
}

function generateId() {
    return nextId++;
}

function averageAgeOfOpenTickets() {
    const now = Date.now();
    const openTickets = ticketData.filter(t => t.status === 'open' || t.status === 'in_progress');

    if (openTickets.length === 0) return 0;

    const totalAge = openTickets.reduce((sum, ticket) => {
        const created = new Date(ticket.created_at).getTime();
        return sum + (now - created);
    }, 0);

    return Math.floor(totalAge / openTickets.length / 1000);
}

async function handleGetTickets(req, res, searchParams) {
    let result = [...ticketData];

    const statusFilter = searchParams.get('status');
    const priorityFilter = searchParams.get('priority');

    if (statusFilter) {
        result = result.filter(t => t.status === statusFilter);
    }

    if (priorityFilter) {
        result = result.filter(t => t.priority === priorityFilter);
    }

    sendJson(res, 200, result);
}

async function handlePostTicket(req, res) {
    let body = '';

    req.on('data', chunk => {
        body += chunk.toString();
    });

    req.on('end', async () => {
        try {
            const parsed = JSON.parse(body);
            const errors = validateTicket(parsed);

            if (errors.length > 0) {
                sendJson(res, 400, { error: 'Validation failed', details: errors });
                return;
            }

            await acquireLock();

            const now = new Date().toISOString();
            const ticket = {
                id: generateId(),
                subject: parsed.subject.trim(),
                description: parsed.description.trim(),
                priority: parsed.priority || 'medium',
                status: parsed.status || 'open',
                created_at: now,
                updated_at: now
            };

            ticketData.push(ticket);
            await saveData();
            releaseLock();

            sendJson(res, 201, ticket);
        } catch (err) {
            sendJson(res, 400, { error: 'Invalid JSON in request body' });
        }
    });
}

async function handleGetTicket(req, res, id) {
    const ticket = getTicketById(id);

    if (!ticket) {
        sendJson(res, 404, { error: 'Ticket not found' });
        return;
    }

    sendJson(res, 200, ticket);
}

async function handlePatchTicket(req, res, id) {
    let body = '';

    req.on('data', chunk => {
        body += chunk.toString();
    });

    req.on('end', async () => {
        try {
            const parsed = JSON.parse(body);

            await acquireLock();

            const ticket = getTicketById(id);

            if (!ticket) {
                releaseLock();
                sendJson(res, 404, { error: 'Ticket not found' });
                return;
            }

            if (parsed.subject !== undefined) {
                if (typeof parsed.subject !== 'string' || !parsed.subject.trim()) {
                    releaseLock();
                    sendJson(res, 400, { error: 'subject must be a non-empty string' });
                    return;
                }
                ticket.subject = parsed.subject.trim();
            }

            if (parsed.description !== undefined) {
                if (typeof parsed.description !== 'string' || !parsed.description.trim()) {
                    releaseLock();
                    sendJson(res, 400, { error: 'description must be a non-empty string' });
                    return;
                }
                ticket.description = parsed.description.trim();
            }

            if (parsed.priority !== undefined) {
                const validPriority = ['low', 'medium', 'high'];
                if (!validPriority.includes(parsed.priority)) {
                    releaseLock();
                    sendJson(res, 400, { error: 'priority must be one of: low, medium, high' });
                    return;
                }
                ticket.priority = parsed.priority;
            }

            if (parsed.status !== undefined) {
                const validStatus = ['open', 'in_progress', 'resolved'];
                if (!validStatus.includes(parsed.status)) {
                    releaseLock();
                    sendJson(res, 400, { error: 'status must be one of: open, in_progress, resolved' });
                    return;
                }
                ticket.status = parsed.status;
            }

            ticket.updated_at = new Date().toISOString();
            await saveData();
            releaseLock();

            sendJson(res, 200, ticket);
        } catch (err) {
            sendJson(res, 400, { error: 'Invalid JSON in request body' });
        }
    });
}

async function handleDeleteTicket(req, res, id) {
    await acquireLock();

    const index = ticketData.findIndex(t => t.id === id);

    if (index === -1) {
        releaseLock();
        sendJson(res, 404, { error: 'Ticket not found' });
        return;
    }

    ticketData.splice(index, 1);
    await saveData();
    releaseLock();

    sendJson(res, 204, null);
}

async function handleMetrics(req, res) {
    const metrics = {
        byStatus: {
            open: ticketData.filter(t => t.status === 'open').length,
            in_progress: ticketData.filter(t => t.status === 'in_progress').length,
            resolved: ticketData.filter(t => t.status === 'resolved').length
        },
        byPriority: {
            low: ticketData.filter(t => t.priority === 'low').length,
            medium: ticketData.filter(t => t.priority === 'medium').length,
            high: ticketData.filter(t => t.priority === 'high').length
        },
        averageOpenTicketAgeSeconds: averageAgeOfOpenTickets()
    };

    sendJson(res, 200, metrics);
}

function parsePathId(pathname) {
    const parts = pathname.split('/').filter(p => p);

    if (parts.length === 2 && parts[0] === 'tickets') {
        const id = parseInt(parts[1], 10);
        if (!isNaN(id)) return id;
    }

    return null;
}

const server = http.createServer(async (req, res) => {
    setCorsHeaders(res);

    if (req.method === 'OPTIONS') {
        res.writeHead(204);
        res.end();
        return;
    }

    const { pathname, searchParams } = parseUrl(req.url);

    try {
        if (pathname === '/tickets' && req.method === 'GET') {
            await handleGetTickets(req, res, searchParams);
        } else if (pathname === '/tickets' && req.method === 'POST') {
            await handlePostTicket(req, res);
        } else if (pathname === '/metrics' && req.method === 'GET') {
            await handleMetrics(req, res);
        } else if (pathname.startsWith('/tickets/')) {
            const id = parsePathId(pathname);

            if (id === null) {
                sendJson(res, 400, { error: 'Invalid ticket ID' });
                return;
            }

            if (req.method === 'GET') {
                await handleGetTicket(req, res, id);
            } else if (req.method === 'PATCH') {
                await handlePatchTicket(req, res, id);
            } else if (req.method === 'DELETE') {
                await handleDeleteTicket(req, res, id);
            } else {
                sendJson(res, 405, { error: 'Method not allowed' });
            }
        } else {
            sendJson(res, 404, { error: 'Route not found' });
        }
    } catch (err) {
        console.error('Server error:', err);
        sendJson(res, 500, { error: 'Internal server error' });
    }
});

loadData();
server.listen(PORT, HOST, () => {
    console.log(`Server running at http://${HOST}:${PORT}/`);
});
