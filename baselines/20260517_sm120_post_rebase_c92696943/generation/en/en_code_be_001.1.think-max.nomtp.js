const http = require('http');
const fs = require('fs');
const path = require('path');

const DATA_FILE = path.join(__dirname, 'tickets.json');
const PORT = process.env.PORT || 8080;
const HOST = '127.0.0.1';

// Ensure data file exists
if (!fs.existsSync(DATA_FILE)) {
    fs.writeFileSync(DATA_FILE, '[]', 'utf-8');
}

// Synchronous file helpers
function readTickets() {
    const data = fs.readFileSync(DATA_FILE, 'utf-8');
    return JSON.parse(data);
}

function writeTickets(tickets) {
    fs.writeFileSync(DATA_FILE, JSON.stringify(tickets, null, 2), 'utf-8');
}

// Body parser
function parseBody(req) {
    return new Promise((resolve, reject) => {
        let body = '';
        req.on('data', chunk => { body += chunk; });
        req.on('end', () => {
            if (!body) return resolve({});
            try {
                resolve(JSON.parse(body));
            } catch (e) {
                reject(new Error('Invalid JSON'));
            }
        });
        req.on('error', reject);
    });
}

// Generate new ID
function generateId(tickets) {
    if (tickets.length === 0) return 1;
    const maxId = Math.max(...tickets.map(t => t.id));
    return maxId + 1;
}

// Validate priority
function isValidPriority(p) {
    return ['low', 'medium', 'high'].includes(p);
}

// Validate status
function isValidStatus(s) {
    return ['open', 'in_progress', 'resolved'].includes(s);
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

// Handle routes
async function handleRequest(req, res) {
    const { method, url } = req;
    const parsedUrl = new URL(url, `http://${HOST}:${PORT}`);
    const pathname = parsedUrl.pathname;
    const query = parsedUrl.searchParams;

    // CORS preflight
    if (method === 'OPTIONS') {
        res.writeHead(204, {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type'
        });
        return res.end();
    }

    try {
        // Routes
        if (method === 'GET' && pathname === '/tickets') {
            // GET /tickets
            const statusFilter = query.get('status');
            const priorityFilter = query.get('priority');
            let tickets = readTickets();

            if (statusFilter) {
                if (!isValidStatus(statusFilter)) {
                    return sendJSON(res, 400, { error: `Invalid status: ${statusFilter}` });
                }
                tickets = tickets.filter(t => t.status === statusFilter);
            }
            if (priorityFilter) {
                if (!isValidPriority(priorityFilter)) {
                    return sendJSON(res, 400, { error: `Invalid priority: ${priorityFilter}` });
                }
                tickets = tickets.filter(t => t.priority === priorityFilter);
            }
            return sendJSON(res, 200, tickets);
        }

        if (method === 'POST' && pathname === '/tickets') {
            // POST /tickets
            const body = await parseBody(req);
            const { subject, description, priority, status } = body;

            // Validate required
            if (!subject || typeof subject !== 'string' || subject.trim() === '') {
                return sendJSON(res, 400, { error: 'Subject is required' });
            }
            if (!description || typeof description !== 'string' || description.trim() === '') {
                return sendJSON(res, 400, { error: 'Description is required' });
            }

            const newPriority = priority && isValidPriority(priority) ? priority : 'low';
            const newStatus = status && isValidStatus(status) ? status : 'open';

            const tickets = readTickets();
            const newTicket = {
                id: generateId(tickets),
                subject: subject.trim(),
                description: description.trim(),
                priority: newPriority,
                status: newStatus,
                created_at: new Date().toISOString(),
                updated_at: new Date().toISOString()
            };
            tickets.push(newTicket);
            writeTickets(tickets);
            return sendJSON(res, 201, newTicket);
        }

        // Match /tickets/{id}
        const ticketsMatch = pathname.match(/^\/tickets\/(\d+)$/);
        if (ticketsMatch) {
            const id = parseInt(ticketsMatch[1], 10);
            const tickets = readTickets();
            const index = tickets.findIndex(t => t.id === id);

            if (index === -1) {
                return sendJSON(res, 404, { error: 'Ticket not found' });
            }

            if (method === 'GET') {
                return sendJSON(res, 200, tickets[index]);
            }

            if (method === 'PATCH') {
                const body = await parseBody(req);
                const allowedFields = ['subject', 'description', 'priority', 'status'];
                const updates = {};

                for (const field of allowedFields) {
                    if (body[field] !== undefined) {
                        if (field === 'priority' && !isValidPriority(body[field])) {
                            return sendJSON(res, 400, { error: `Invalid priority: ${body[field]}` });
                        }
                        if (field === 'status' && !isValidStatus(body[field])) {
                            return sendJSON(res, 400, { error: `Invalid status: ${body[field]}` });
                        }
                        if (field === 'subject' && (typeof body[field] !== 'string' || body[field].trim() === '')) {
                            return sendJSON(res, 400, { error: 'Subject cannot be empty' });
                        }
                        if (field === 'description' && (typeof body[field] !== 'string' || body[field].trim() === '')) {
                            return sendJSON(res, 400, { error: 'Description cannot be empty' });
                        }
                        updates[field] = body[field].trim();
                    }
                }

                if (Object.keys(updates).length === 0) {
                    return sendJSON(res, 400, { error: 'No valid fields to update' });
                }

                const ticket = tickets[index];
                for (const key of Object.keys(updates)) {
                    ticket[key] = updates[key];
                }
                ticket.updated_at = new Date().toISOString();
                writeTickets(tickets);
                return sendJSON(res, 200, ticket);
            }

            if (method === 'DELETE') {
                tickets.splice(index, 1);
                writeTickets(tickets);
                return sendJSON(res, 200, { message: 'Ticket deleted' });
            }

            // Method not allowed for this path
            return sendJSON(res, 405, { error: 'Method not allowed' });
        }

        if (method === 'GET' && pathname === '/metrics') {
            const tickets = readTickets();
            const now = new Date();

            // Counts by status
            const statusCounts = { open: 0, in_progress: 0, resolved: 0 };
            // Counts by priority
            const priorityCounts = { low: 0, medium: 0, high: 0 };
            let totalAgeOpenMs = 0;
            let openCount = 0;

            for (const ticket of tickets) {
                if (statusCounts.hasOwnProperty(ticket.status)) {
                    statusCounts[ticket.status]++;
                }
                if (priorityCounts.hasOwnProperty(ticket.priority)) {
                    priorityCounts[ticket.priority]++;
                }
                if (ticket.status === 'open') {
                    const created = new Date(ticket.created_at);
                    totalAgeOpenMs += now - created;
                    openCount++;
                }
            }

            const averageAgeSeconds = openCount > 0 ? (totalAgeOpenMs / openCount / 1000) : 0;

            return sendJSON(res, 200, {
                statusCounts,
                priorityCounts,
                averageOpenAgeSeconds: Math.round(averageAgeSeconds * 100) / 100
            });
        }

        // Unknown route
        return sendJSON(res, 404, { error: 'Not found' });

    } catch (err) {
        if (err.message === 'Invalid JSON') {
            return sendJSON(res, 400, { error: 'Invalid JSON' });
        }
        console.error(err);
        return sendJSON(res, 500, { error: 'Internal server error' });
    }
}

// Create server
const server = http.createServer(handleRequest);

server.listen(PORT, HOST, () => {
    console.log(`Server running at http://${HOST}:${PORT}/`);
});
