const http = require('http');
const fs = require('fs').promises;
const path = require('path');
const { URL } = require('url');

const DATA_FILE = path.join(__dirname, 'tickets.json');
const PORT = process.env.PORT || 8080;
const HOST = '127.0.0.1';

// --- Async mutex for safe file access ---
class Mutex {
  constructor() {
    this._locked = false;
    this._queue = [];
  }

  lock() {
    return new Promise(resolve => {
      if (!this._locked) {
        this._locked = true;
        resolve();
      } else {
        this._queue.push(resolve);
      }
    });
  }

  unlock() {
    if (this._queue.length > 0) {
      const next = this._queue.shift();
      next();
    } else {
      this._locked = false;
    }
  }
}

const fileMutex = new Mutex();

// --- File operations (always acquire mutex) ---
async function readData() {
  await fileMutex.lock();
  try {
    const raw = await fs.readFile(DATA_FILE, 'utf8');
    return JSON.parse(raw);
  } catch (e) {
    // File doesn't exist or invalid JSON -> return default structure
    return { nextId: 1, tickets: [] };
  } finally {
    fileMutex.unlock();
  }
}

async function writeData(data) {
  await fileMutex.lock();
  try {
    await fs.writeFile(DATA_FILE, JSON.stringify(data, null, 2));
  } finally {
    fileMutex.unlock();
  }
}

// --- Helper to send JSON response ---
function sendJSON(res, statusCode, body) {
  res.writeHead(statusCode, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify(body));
}

// --- Parse request body as JSON ---
function getBody(req) {
  return new Promise((resolve, reject) => {
    let body = '';
    req.on('data', chunk => (body += chunk));
    req.on('end', () => {
      try {
        resolve(JSON.parse(body));
      } catch (e) {
        reject(new Error('Invalid JSON'));
      }
    });
    req.on('error', reject);
  });
}

// --- Calculate average age of open tickets in seconds ---
function averageOpenAge(tickets) {
  const openTickets = tickets.filter(t => t.status === 'open');
  if (openTickets.length === 0) return 0;
  const now = Date.now();
  const totalAge = openTickets.reduce((sum, t) => {
    const created = new Date(t.created_at).getTime();
    return sum + (now - created);
  }, 0);
  return Math.round(totalAge / openTickets.length / 1000); // seconds
}

// --- Handlers ---
async function handleGetTickets(req, res, searchParams) {
  const data = await readData();
  let tickets = data.tickets;

  const statusFilter = searchParams.get('status');
  const priorityFilter = searchParams.get('priority');

  if (statusFilter) {
    tickets = tickets.filter(t => t.status === statusFilter);
  }
  if (priorityFilter) {
    tickets = tickets.filter(t => t.priority === priorityFilter);
  }

  sendJSON(res, 200, tickets);
}

async function handlePostTicket(req, res) {
  let body;
  try {
    body = await getBody(req);
  } catch (e) {
    return sendJSON(res, 400, { error: 'Invalid JSON' });
  }

  const { subject, description, priority, status } = body;

  if (!subject || typeof subject !== 'string' || subject.trim() === '') {
    return sendJSON(res, 400, { error: 'Subject is required and must be a non-empty string' });
  }
  if (!description || typeof description !== 'string') {
    return sendJSON(res, 400, { error: 'Description is required and must be a string' });
  }
  if (!priority || !['low', 'medium', 'high'].includes(priority)) {
    return sendJSON(res, 400, { error: 'Priority must be one of: low, medium, high' });
  }
  const finalStatus = status || 'open';
  if (!['open', 'in_progress', 'resolved'].includes(finalStatus)) {
    return sendJSON(res, 400, { error: 'Status must be one of: open, in_progress, resolved' });
  }

  const now = new Date().toISOString();

  // Read, modify, write under a single lock via writeData (which locks internally)
  // But we need to atomically read-modify-write. Let's write a helper for that.
  // To avoid extra lock overhead, we'll read then write with the same mutex via explicit lock.
  await fileMutex.lock();
  try {
    const raw = await fs.readFile(DATA_FILE, 'utf8');
    const data = JSON.parse(raw);
    const newTicket = {
      id: data.nextId,
      subject,
      description,
      priority,
      status: finalStatus,
      created_at: now,
      updated_at: now,
    };
    data.tickets.push(newTicket);
    data.nextId++;
    await fs.writeFile(DATA_FILE, JSON.stringify(data, null, 2));
    sendJSON(res, 201, newTicket);
  } catch (e) {
    // If file doesn't exist, create new data structure
    const data = { nextId: 1, tickets: [] };
    const newTicket = {
      id: data.nextId,
      subject,
      description,
      priority,
      status: finalStatus,
      created_at: now,
      updated_at: now,
    };
    data.tickets.push(newTicket);
    data.nextId++;
    await fs.writeFile(DATA_FILE, JSON.stringify(data, null, 2));
    sendJSON(res, 201, newTicket);
  } finally {
    fileMutex.unlock();
  }
}

async function handleGetTicketById(req, res, id) {
  const data = await readData();
  const ticket = data.tickets.find(t => t.id === id);
  if (!ticket) {
    return sendJSON(res, 404, { error: 'Ticket not found' });
  }
  sendJSON(res, 200, ticket);
}

async function handlePatchTicket(req, res, id) {
  let body;
  try {
    body = await getBody(req);
  } catch (e) {
    return sendJSON(res, 400, { error: 'Invalid JSON' });
  }

  const allowedFields = ['subject', 'description', 'priority', 'status'];
  const updates = {};
  for (const field of allowedFields) {
    if (body[field] !== undefined) {
      updates[field] = body[field];
    }
  }

  if (updates.subject !== undefined && (typeof updates.subject !== 'string' || updates.subject.trim() === '')) {
    return sendJSON(res, 400, { error: 'Subject must be a non-empty string' });
  }
  if (updates.description !== undefined && typeof updates.description !== 'string') {
    return sendJSON(res, 400, { error: 'Description must be a string' });
  }
  if (updates.priority !== undefined && !['low', 'medium', 'high'].includes(updates.priority)) {
    return sendJSON(res, 400, { error: 'Priority must be one of: low, medium, high' });
  }
  if (updates.status !== undefined && !['open', 'in_progress', 'resolved'].includes(updates.status)) {
    return sendJSON(res, 400, { error: 'Status must be one of: open, in_progress, resolved' });
  }

  if (Object.keys(updates).length === 0) {
    return sendJSON(res, 400, { error: 'No valid fields to update' });
  }

  await fileMutex.lock();
  try {
    const raw = await fs.readFile(DATA_FILE, 'utf8');
    const data = JSON.parse(raw);
    const ticket = data.tickets.find(t => t.id === id);
    if (!ticket) {
      return sendJSON(res, 404, { error: 'Ticket not found' });
    }
    for (const key of Object.keys(updates)) {
      ticket[key] = updates[key];
    }
    ticket.updated_at = new Date().toISOString();
    await fs.writeFile(DATA_FILE, JSON.stringify(data, null, 2));
    sendJSON(res, 200, ticket);
  } catch (e) {
    sendJSON(res, 500, { error: 'Internal server error' });
  } finally {
    fileMutex.unlock();
  }
}

async function handleDeleteTicket(req, res, id) {
  await fileMutex.lock();
  try {
    const raw = await fs.readFile(DATA_FILE, 'utf8');
    const data = JSON.parse(raw);
    const index = data.tickets.findIndex(t => t.id === id);
    if (index === -1) {
      return sendJSON(res, 404, { error: 'Ticket not found' });
    }
    data.tickets.splice(index, 1);
    await fs.writeFile(DATA_FILE, JSON.stringify(data, null, 2));
    sendJSON(res, 200, { message: 'Ticket deleted' });
  } catch (e) {
    sendJSON(res, 500, { error: 'Internal server error' });
  } finally {
    fileMutex.unlock();
  }
}

async function handleMetrics(req, res) {
  const data = await readData();
  const tickets = data.tickets;

  const statusCounts = tickets.reduce((acc, t) => {
    acc[t.status] = (acc[t.status] || 0) + 1;
    return acc;
  }, {});
  const priorityCounts = tickets.reduce((acc, t) => {
    acc[t.priority] = (acc[t.priority] || 0) + 1;
    return acc;
  }, {});
  const avgAge = averageOpenAge(tickets);

  sendJSON(res, 200, {
    statusCounts,
    priorityCounts,
    averageAgeOpenTicketsSeconds: avgAge,
  });
}

// --- Server creation ---
async function startServer() {
  // Ensure data file exists with default structure
  try {
    await fs.access(DATA_FILE);
  } catch {
    await fs.writeFile(DATA_FILE, JSON.stringify({ nextId: 1, tickets: [] }, null, 2));
  }

  const server = http.createServer(async (req, res) => {
    // CORS headers
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

    if (req.method === 'OPTIONS') {
      res.writeHead(200);
      res.end();
      return;
    }

    const parsedUrl = new URL(req.url, `http://${req.headers.host || 'localhost'}`);
    const pathname = parsedUrl.pathname;

    // Route definitions
    const routes = [
      { pattern: /^\/tickets$/, methods: ['GET', 'POST'] },
      { pattern: /^\/tickets\/(\d+)$/, methods: ['GET', 'PATCH', 'DELETE'] },
      { pattern: /^\/metrics$/, methods: ['GET'] },
    ];

    let match = null;
    for (const route of routes) {
      const m = pathname.match(route.pattern);
      if (m) {
        match = { params: m.slice(1), methods: route.methods };
        break;
      }
    }

    if (!match) {
      return sendJSON(res, 404, { error: 'Not found' });
    }

    if (!match.methods.includes(req.method)) {
      return sendJSON(res, 405, { error: 'Method not allowed' });
    }

    try {
      if (pathname === '/tickets' && req.method === 'GET') {
        await handleGetTickets(req, res, parsedUrl.searchParams);
      } else if (pathname === '/tickets' && req.method === 'POST') {
        await handlePostTicket(req, res);
      } else if (match.params && pathname.startsWith('/tickets/') && match.params.length === 1) {
        const id = parseInt(match.params[0], 10);
        if (isNaN(id)) {
          return sendJSON(res, 400, { error: 'Invalid ticket ID' });
        }
        if (req.method === 'GET') {
          await handleGetTicketById(req, res, id);
        } else if (req.method === 'PATCH') {
          await handlePatchTicket(req, res, id);
        } else if (req.method === 'DELETE') {
          await handleDeleteTicket(req, res, id);
        }
      } else if (pathname === '/metrics' && req.method === 'GET') {
        await handleMetrics(req, res);
      } else {
        // Should not happen due to route matching
        sendJSON(res, 404, { error: 'Not found' });
      }
    } catch (err) {
      console.error(err);
      sendJSON(res, 500, { error: 'Internal server error' });
    }
  });

  server.listen(PORT, HOST, () => {
    console.log(`Server running at http://${HOST}:${PORT}`);
  });
}

startServer();
