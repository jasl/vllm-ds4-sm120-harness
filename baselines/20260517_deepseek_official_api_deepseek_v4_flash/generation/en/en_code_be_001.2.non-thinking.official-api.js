const http = require('http');
const fs = require('fs');
const path = require('path');
const { URL } = require('url');

const DATA_FILE = path.join(__dirname, 'tickets.json');
const HOST = '127.0.0.1';
const PORT = 8080;

// Simple mutex for file operations (promise-based queue)
class FileLock {
  constructor() {
    this._queue = [];
    this._locked = false;
  }

  acquire() {
    return new Promise(resolve => {
      if (!this._locked) {
        this._locked = true;
        resolve();
      } else {
        this._queue.push(resolve);
      }
    });
  }

  release() {
    if (this._queue.length > 0) {
      const next = this._queue.shift();
      next();
    } else {
      this._locked = false;
    }
  }
}

const fileLock = new FileLock();

// File I/O helpers with locking
async function readTickets() {
  await fileLock.acquire();
  try {
    if (!fs.existsSync(DATA_FILE)) {
      return [];
    }
    const data = fs.readFileSync(DATA_FILE, 'utf8');
    return JSON.parse(data);
  } catch (err) {
    console.error('Error reading tickets:', err);
    return [];
  } finally {
    fileLock.release();
  }
}

async function writeTickets(tickets) {
  await fileLock.acquire();
  try {
    fs.writeFileSync(DATA_FILE, JSON.stringify(tickets, null, 2), 'utf8');
  } catch (err) {
    console.error('Error writing tickets:', err);
    throw err;
  } finally {
    fileLock.release();
  }
}

// UUID/ID generation (simple)
function generateId() {
  return Date.now().toString(36) + Math.random().toString(36).substr(2, 5);
}

function currentTime() {
  return new Date().toISOString();
}

// Parse URL and query params
function parseUrl(reqUrl) {
  const parsed = new URL(reqUrl, `http://${HOST}:${PORT}`);
  const pathname = parsed.pathname;
  const params = {};
  parsed.searchParams.forEach((value, key) => {
    params[key] = value;
  });
  return { pathname, params };
}

// Parse request body (JSON)
function parseBody(req) {
  return new Promise((resolve, reject) => {
    let body = '';
    req.on('data', chunk => {
      body += chunk;
    });
    req.on('end', () => {
      if (!body) {
        resolve(null);
        return;
      }
      try {
        resolve(JSON.parse(body));
      } catch (e) {
        reject(new Error('Invalid JSON'));
      }
    });
    req.on('error', reject);
  });
}

// Send JSON response
function sendJson(res, statusCode, data) {
  const body = JSON.stringify(data);
  res.writeHead(statusCode, {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Accept',
  });
  res.end(body);
}

// Validate ticket fields
function validateTicket(body, isCreate = true) {
  const errors = [];
  const validPriorities = ['low', 'medium', 'high'];
  const validStatuses = ['open', 'in_progress', 'resolved'];

  if (isCreate) {
    if (!body.subject || typeof body.subject !== 'string' || body.subject.trim() === '') {
      errors.push('subject is required and must be a non-empty string');
    }
    if (!body.description || typeof body.description !== 'string' || body.description.trim() === '') {
      errors.push('description is required and must be a non-empty string');
    }
    if (!body.priority || !validPriorities.includes(body.priority)) {
      errors.push('priority is required and must be one of: low, medium, high');
    }
  } else {
    // For updates, only validate provided fields
    if (body.subject !== undefined && (typeof body.subject !== 'string' || body.subject.trim() === '')) {
      errors.push('subject must be a non-empty string');
    }
    if (body.description !== undefined && (typeof body.description !== 'string' || body.description.trim() === '')) {
      errors.push('description must be a non-empty string');
    }
    if (body.priority !== undefined && !validPriorities.includes(body.priority)) {
      errors.push('priority must be one of: low, medium, high');
    }
    if (body.status !== undefined && !validStatuses.includes(body.status)) {
      errors.push('status must be one of: open, in_progress, resolved');
    }
  }
  return errors;
}

// Route handler
async function handleRequest(req, res) {
  // Handle CORS preflight
  if (req.method === 'OPTIONS') {
    res.writeHead(204, {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Accept',
    });
    res.end();
    return;
  }

  const { pathname, params } = parseUrl(req.url);
  const method = req.method;

  let body = null;
  if (method === 'POST' || method === 'PATCH') {
    try {
      body = await parseBody(req);
    } catch (e) {
      sendJson(res, 400, { error: 'Invalid JSON in request body' });
      return;
    }
  }

  try {
    // Routing
    if (pathname === '/tickets' && method === 'GET') {
      await handleGetTickets(res, params);
    } else if (pathname === '/tickets' && method === 'POST') {
      await handleCreateTicket(res, body);
    } else if (pathname.startsWith('/tickets/') && method === 'GET') {
      const id = pathname.split('/')[2];
      await handleGetTicketById(res, id);
    } else if (pathname.startsWith('/tickets/') && method === 'PATCH') {
      const id = pathname.split('/')[2];
      await handleUpdateTicket(res, id, body);
    } else if (pathname.startsWith('/tickets/') && method === 'DELETE') {
      const id = pathname.split('/')[2];
      await handleDeleteTicket(res, id);
    } else if (pathname === '/metrics' && method === 'GET') {
      await handleMetrics(res);
    } else {
      sendJson(res, 404, { error: 'Route not found' });
    }
  } catch (err) {
    console.error('Server error:', err);
    sendJson(res, 500, { error: 'Internal server error' });
  }
}

// --- Handlers ---

async function handleGetTickets(res, query) {
  const tickets = await readTickets();
  let filtered = tickets;

  if (query.status) {
    filtered = filtered.filter(t => t.status === query.status);
  }
  if (query.priority) {
    filtered = filtered.filter(t => t.priority === query.priority);
  }

  sendJson(res, 200, filtered);
}

async function handleCreateTicket(res, body) {
  if (!body) {
    sendJson(res, 400, { error: 'Request body is required' });
    return;
  }

  const errors = validateTicket(body, true);
  if (errors.length > 0) {
    sendJson(res, 400, { error: 'Validation failed', details: errors });
    return;
  }

  const tickets = await readTickets();
  const newTicket = {
    id: generateId(),
    subject: body.subject.trim(),
    description: body.description.trim(),
    priority: body.priority,
    status: body.status || 'open',
    created_at: currentTime(),
    updated_at: currentTime(),
  };
  tickets.push(newTicket);
  await writeTickets(tickets);

  sendJson(res, 201, newTicket);
}

async function handleGetTicketById(res, id) {
  const tickets = await readTickets();
  const ticket = tickets.find(t => t.id === id);
  if (!ticket) {
    sendJson(res, 404, { error: 'Ticket not found' });
    return;
  }
  sendJson(res, 200, ticket);
}

async function handleUpdateTicket(res, id, body) {
  if (!body) {
    sendJson(res, 400, { error: 'Request body is required' });
    return;
  }

  const errors = validateTicket(body, false);
  if (errors.length > 0) {
    sendJson(res, 400, { error: 'Validation failed', details: errors });
    return;
  }

  const tickets = await readTickets();
  const index = tickets.findIndex(t => t.id === id);
  if (index === -1) {
    sendJson(res, 404, { error: 'Ticket not found' });
    return;
  }

  const updated = { ...tickets[index] };
  if (body.subject !== undefined) updated.subject = body.subject.trim();
  if (body.description !== undefined) updated.description = body.description.trim();
  if (body.priority !== undefined) updated.priority = body.priority;
  if (body.status !== undefined) updated.status = body.status;
  updated.updated_at = currentTime();

  tickets[index] = updated;
  await writeTickets(tickets);

  sendJson(res, 200, updated);
}

async function handleDeleteTicket(res, id) {
  const tickets = await readTickets();
  const index = tickets.findIndex(t => t.id === id);
  if (index === -1) {
    sendJson(res, 404, { error: 'Ticket not found' });
    return;
  }

  const deleted = tickets.splice(index, 1)[0];
  await writeTickets(tickets);

  sendJson(res, 200, { message: 'Ticket deleted', ticket: deleted });
}

async function handleMetrics(res) {
  const tickets = await readTickets();

  // Counts by status
  const statusCounts = { open: 0, in_progress: 0, resolved: 0 };
  // Counts by priority
  const priorityCounts = { low: 0, medium: 0, high: 0 };

  let totalOpenAgeSeconds = 0;
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
      const ageSeconds = (now - created) / 1000;
      totalOpenAgeSeconds += ageSeconds;
      openCount++;
    }
  });

  const averageAge = openCount > 0 ? totalOpenAgeSeconds / openCount : 0;

  sendJson(res, 200, {
    statusCounts,
    priorityCounts,
    averageAgeSeconds: Math.round(averageAge * 100) / 100, // round to 2 decimals
  });
}

// Create server
const server = http.createServer(handleRequest);

server.listen(PORT, HOST, () => {
  console.log(`Server running at http://${HOST}:${PORT}/`);
});
