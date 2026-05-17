```javascript
const http = require('http');
const fs = require('fs').promises;
const path = require('path');
const url = require('url');

const HOST = '127.0.0.1';
const PORT = 8080;
const DATA_FILE = path.join(__dirname, 'tickets.json');

// ----------------------------------------------------------------------
// Simple promise-based mutex to serialise write operations on the file
// ----------------------------------------------------------------------
class Mutex {
  constructor() {
    this._locked = false;
    this._queue = [];
  }

  lock() {
    return new Promise((resolve) => {
      if (!this._locked) {
        this._locked = true;
        resolve(this._unlock.bind(this));
      } else {
        this._queue.push(resolve);
      }
    });
  }

  _unlock() {
    if (this._queue.length > 0) {
      const next = this._queue.shift();
      next(this._unlock.bind(this));
    } else {
      this._locked = false;
    }
  }
}

const mutex = new Mutex();

// ----------------------------------------------------------------------
// File read / write helpers (wrapped with mutex for atomicity)
// ----------------------------------------------------------------------
async function readTickets() {
  try {
    const data = await fs.readFile(DATA_FILE, 'utf8');
    return JSON.parse(data);
  } catch (err) {
    if (err.code === 'ENOENT') {
      return [];
    }
    throw err;
  }
}

async function writeTickets(tickets) {
  await fs.writeFile(DATA_FILE, JSON.stringify(tickets, null, 2), 'utf8');
}

async function withMutex(fn) {
  const release = await mutex.lock();
  try {
    return await fn();
  } finally {
    release();
  }
}

// ----------------------------------------------------------------------
// Domain logic
// ----------------------------------------------------------------------
async function getAllTickets(query) {
  const tickets = await readTickets();
  let result = tickets;
  if (query.status) {
    result = result.filter(t => t.status === query.status);
  }
  if (query.priority) {
    result = result.filter(t => t.priority === query.priority);
  }
  return result;
}

async function getTicketById(id) {
  const tickets = await readTickets();
  return tickets.find(t => t.id === id) || null;
}

async function createTicket(data) {
  return withMutex(async () => {
    const tickets = await readTickets();
    const maxId = tickets.reduce((max, t) => Math.max(max, t.id), 0);
    const now = new Date().toISOString();
    const ticket = {
      id: maxId + 1,
      subject: data.subject,
      description: data.description,
      priority: data.priority,
      status: data.status,
      created_at: now,
      updated_at: now,
    };
    tickets.push(ticket);
    await writeTickets(tickets);
    return ticket;
  });
}

async function updateTicket(id, data) {
  return withMutex(async () => {
    const tickets = await readTickets();
    const index = tickets.findIndex(t => t.id === id);
    if (index === -1) return null;
    const ticket = tickets[index];
    if (data.subject !== undefined) ticket.subject = data.subject;
    if (data.description !== undefined) ticket.description = data.description;
    if (data.priority !== undefined) ticket.priority = data.priority;
    if (data.status !== undefined) ticket.status = data.status;
    ticket.updated_at = new Date().toISOString();
    await writeTickets(tickets);
    return ticket;
  });
}

async function deleteTicket(id) {
  return withMutex(async () => {
    const tickets = await readTickets();
    const index = tickets.findIndex(t => t.id === id);
    if (index === -1) return null;
    const [deleted] = tickets.splice(index, 1);
    await writeTickets(tickets);
    return deleted;
  });
}

async function getMetrics() {
  const tickets = await readTickets();
  const statusCounts = { open: 0, in_progress: 0, resolved: 0 };
  const priorityCounts = { low: 0, medium: 0, high: 0 };
  let openAgeSum = 0;
  let openCount = 0;
  const now = Date.now();

  for (const t of tickets) {
    if (statusCounts.hasOwnProperty(t.status)) statusCounts[t.status]++;
    if (priorityCounts.hasOwnProperty(t.priority)) priorityCounts[t.priority]++;
    if (t.status === 'open') {
      const created = new Date(t.created_at).getTime();
      openAgeSum += (now - created) / 1000;
      openCount++;
    }
  }

  return {
    status: statusCounts,
    priority: priorityCounts,
    averageAgeOpenInSeconds: openCount > 0 ? openAgeSum / openCount : 0,
  };
}

// ----------------------------------------------------------------------
// Validation helpers
// ----------------------------------------------------------------------
const VALID_PRIORITIES = ['low', 'medium', 'high'];
const VALID_STATUSES = ['open', 'in_progress', 'resolved'];

function validateTicket(data) {
  const errors = [];
  if (!data.subject || typeof data.subject !== 'string') errors.push('subject is required and must be a string');
  if (!data.description || typeof data.description !== 'string') errors.push('description is required and must be a string');
  if (!data.priority || !VALID_PRIORITIES.includes(data.priority)) errors.push(`priority must be one of ${VALID_PRIORITIES.join(', ')}`);
  if (!data.status || !VALID_STATUSES.includes(data.status)) errors.push(`status must be one of ${VALID_STATUSES.join(', ')}`);
  return errors;
}

function validatePartial(data) {
  const errors = [];
  if (data.subject !== undefined && (typeof data.subject !== 'string' || data.subject.length === 0)) errors.push('subject must be a non-empty string');
  if (data.description !== undefined && (typeof data.description !== 'string' || data.description.length === 0)) errors.push('description must be a non-empty string');
  if (data.priority !== undefined && !VALID_PRIORITIES.includes(data.priority)) errors.push(`priority must be one of ${VALID_PRIORITIES.join(', ')}`);
  if (data.status !== undefined && !VALID_STATUSES.includes(data.status)) errors.push(`status must be one of ${VALID_STATUSES.join(', ')}`);
  return errors;
}

// ----------------------------------------------------------------------
// Request helpers
// ----------------------------------------------------------------------
function sendJSON(res, statusCode, data) {
  const body = JSON.stringify(data);
  res.writeHead(statusCode, {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
  });
  res.end(body);
}

function parseBody(req) {
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

// ----------------------------------------------------------------------
// Route dispatcher
// ----------------------------------------------------------------------
async function handleRequest(req, res) {
  const parsedUrl = new URL(req.url, `http://${req.headers.host || 'localhost'}`);
  const pathname = parsedUrl.pathname;
  const method = req.method.toUpperCase();

  // CORS preflight
  if (method === 'OPTIONS') {
    res.writeHead(204, {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    });
    return res.end();
  }

  // Route matching
  const ticketsMatch = pathname.match(/^\/tickets(?:\/(\d+))?$/);
  const metricsMatch = pathname === '/metrics';

  try {
    if (ticketsMatch) {
      const id = ticketsMatch[1] ? parseInt(ticketsMatch[1], 10) : null;

      // GET /tickets
      if (method === 'GET' && !id) {
        const query = Object.fromEntries(parsedUrl.searchParams);
        const tickets = await getAllTickets(query);
        return sendJSON(res, 200, tickets);
      }

      // POST /tickets
      if (method === 'POST' && !id) {
        const data = await parseBody(req);
        const errors = validateTicket(data);
        if (errors.length > 0) {
          return sendJSON(res, 400, { error: 'Validation failed', details: errors });
        }
        const ticket = await createTicket(data);
        return sendJSON(res, 201, ticket);
      }

      // GET /tickets/:id
      if (method === 'GET' && id) {
        const ticket = await getTicketById(id);
        if (!ticket) return sendJSON(res, 404, { error: 'Ticket not found' });
        return sendJSON(res, 200, ticket);
      }

      // PATCH /tickets/:id
      if (method === 'PATCH' && id) {
        const data = await parseBody(req);
        const errors = validatePartial(data);
        if (errors.length > 0) {
          return sendJSON(res, 400, { error: 'Validation failed', details: errors });
        }
        const ticket = await updateTicket(id, data);
        if (!ticket) return sendJSON(res, 404, { error: 'Ticket not found' });
        return sendJSON(res, 200, ticket);
      }

      // DELETE /tickets/:id
      if (method === 'DELETE' && id) {
        const ticket = await deleteTicket(id);
        if (!ticket) return sendJSON(res, 404, { error: 'Ticket not found' });
        return sendJSON(res, 200, { deleted: ticket });
      }

      // Unsupported method on /tickets
      return sendJSON(res, 405, { error: `Method ${method} not allowed on this
