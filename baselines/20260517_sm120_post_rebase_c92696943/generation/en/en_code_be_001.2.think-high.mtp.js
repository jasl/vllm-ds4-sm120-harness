const http = require('http');
const fs = require('fs');
const path = require('path');

const DATA_FILE = path.join(__dirname, 'tickets.json');
const HOST = '127.0.0.1';
const PORT = process.env.PORT || 8080;

// ---------------------------------------------------------------------------
// Simple sequential lock for file operations
// ---------------------------------------------------------------------------
let lockQueue = [];
let lockInProgress = false;

function acquireLock() {
  return new Promise((resolve) => {
    lockQueue.push(resolve);
    if (!lockInProgress) {
      lockInProgress = true;
      processNextLock();
    }
  });
}

function releaseLock() {
  if (lockQueue.length > 0) {
    const next = lockQueue.shift();
    next();
  } else {
    lockInProgress = false;
  }
}

// ---------------------------------------------------------------------------
// File helpers
// ---------------------------------------------------------------------------
async function readTickets() {
  try {
    const raw = await fs.promises.readFile(DATA_FILE, 'utf-8');
    return JSON.parse(raw);
  } catch {
    return [];
  }
}

async function writeTickets(tickets) {
  await fs.promises.writeFile(DATA_FILE, JSON.stringify(tickets, null, 2));
}

// Acquire lock, read, call modifier, write result, release lock
async function modifyTickets(modifier) {
  await acquireLock();
  try {
    const tickets = await readTickets();
    const result = await modifier(tickets);
    await writeTickets(tickets);
    return result;
  } finally {
    releaseLock();
  }
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
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
    req.on('data', (chunk) => (body += chunk));
    req.on('end', () => {
      try {
        resolve(JSON.parse(body));
      } catch {
        reject(new Error('Invalid JSON'));
      }
    });
    req.on('error', reject);
  });
}

function getNextId(tickets) {
  if (tickets.length === 0) return 1;
  return Math.max(...tickets.map((t) => t.id)) + 1;
}

const PRIORITIES = ['low', 'medium', 'high'];
const STATUSES = ['open', 'in_progress', 'resolved'];

function isValidPriority(p) {
  return PRIORITIES.includes(p);
}
function isValidStatus(s) {
  return STATUSES.includes(s);
}

function toEpoch() {
  return Math.floor(Date.now() / 1000);
}

// ---------------------------------------------------------------------------
// Route handlers
// ---------------------------------------------------------------------------
async function handleGetTickets(req, res, parsedUrl) {
  const status = parsedUrl.searchParams.get('status');
  const priority = parsedUrl.searchParams.get('priority');

  const result = await modifyTickets(async (tickets) => {
    let filtered = tickets;
    if (status) {
      if (!isValidStatus(status)) {
        throw { status: 400, message: `Invalid status: ${status}` };
      }
      filtered = filtered.filter((t) => t.status === status);
    }
    if (priority) {
      if (!isValidPriority(priority)) {
        throw { status: 400, message: `Invalid priority: ${priority}` };
      }
      filtered = filtered.filter((t) => t.priority === priority);
    }
    return filtered;
  });

  sendJSON(res, 200, result);
}

async function handlePostTickets(req, res) {
  const body = await parseBody(req).catch(() => {
    throw { status: 400, message: 'Invalid JSON in request body' };
  });

  const { subject, description, priority } = body;
  if (!subject || !description || !priority) {
    throw { status: 400, message: 'Missing required fields: subject, description, priority' };
  }
  if (!isValidPriority(priority)) {
    throw { status: 400, message: 'Priority must be one of: low, medium, high' };
  }

  const ticket = await modifyTickets(async (tickets) => {
    const now = toEpoch();
    const newTicket = {
      id: getNextId(tickets),
      subject,
      description,
      priority,
      status: 'open',
      created_at: now,
      updated_at: now,
    };
    tickets.push(newTicket);
    return newTicket;
  });

  sendJSON(res, 201, ticket);
}

async function handleGetTicket(req, res, id) {
  const numId = Number(id);
  const ticket = await modifyTickets(async (tickets) => {
    const found = tickets.find((t) => t.id === numId);
    if (!found) throw { status: 404, message: `Ticket with id ${numId} not found` };
    return found;
  });

  sendJSON(res, 200, ticket);
}

async function handlePatchTicket(req, res, id) {
  const numId = Number(id);
  const body = await parseBody(req).catch(() => {
    throw { status: 400, message: 'Invalid JSON in request body' };
  });

  const allowedFields = ['subject', 'description', 'priority', 'status'];
  const update = {};
  for (const field of allowedFields) {
    if (body[field] !== undefined) update[field] = body[field];
  }

  if (update.priority !== undefined && !isValidPriority(update.priority)) {
    throw { status: 400, message: 'Priority must be one of: low, medium, high' };
  }
  if (update.status !== undefined && !isValidStatus(update.status)) {
    throw { status: 400, message: 'Status must be one of: open, in_progress, resolved' };
  }

  const updatedTicket = await modifyTickets(async (tickets) => {
    const idx = tickets.findIndex((t) => t.id === numId);
    if (idx === -1) throw { status: 404, message: `Ticket with id ${numId} not found` };

    const ticket = tickets[idx];
    for (const [key, val] of Object.entries(update)) {
      ticket[key] = val;
    }
    ticket.updated_at = toEpoch();
    return ticket;
  });

  sendJSON(res, 200, updatedTicket);
}

async function handleDeleteTicket(req, res, id) {
  const numId = Number(id);
  await modifyTickets(async (tickets) => {
    const idx = tickets.findIndex((t) => t.id === numId);
    if (idx === -1) throw { status: 404, message: `Ticket with id ${numId} not found` };
    tickets.splice(idx, 1);
  });

  sendJSON(res, 200, { message: 'Ticket deleted' });
}

async function handleGetMetrics(req, res) {
  const metrics = await modifyTickets(async (tickets) => {
    const now = toEpoch();
    const statusCounts = {};
    const priorityCounts = {};

    for (const s of STATUSES) statusCounts[s] = 0;
    for (const p of PRIORITIES) priorityCounts[p] = 0;

    let totalAgeOpen = 0;
    let openCount = 0;

    for (const t of tickets) {
      if (statusCounts[t.status] !== undefined) statusCounts[t.status]++;
      if (priorityCounts[t.priority] !== undefined) priorityCounts[t.priority]++;

      if (t.status === 'open') {
        totalAgeOpen += now - t.created_at;
        openCount++;
      }
    }

    return {
      by_status: statusCounts,
      by_priority: priorityCounts,
      average_open_age_seconds: openCount > 0 ? Math.round(totalAgeOpen / openCount) : 0,
    };
  });

  sendJSON(res, 200, metrics);
}

// ---------------------------------------------------------------------------
// Server
// ---------------------------------------------------------------------------
const server = http.createServer(async (req, res) => {
  // Handle CORS preflight
  if (req.method === 'OPTIONS') {
    res.writeHead(204, {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    });
    res.end();
    return;
  }

  try {
    const parsedUrl = new URL(req.url, 'http://localhost');
    const pathname = parsedUrl.pathname;

    // Route matching
    const matchTickets = pathname === '/tickets';
    const matchTicketId = pathname.match(/^\/tickets\/(\d+)$/);
    const matchMetrics = pathname === '/metrics';

    if (req.method === 'GET' && matchTickets) {
      await handleGetTickets(req, res, parsedUrl);
    } else if (req.method === 'POST' && matchTickets) {
      await handlePostTickets(req, res);
    } else if (req.method === 'GET' && matchTicketId) {
      await handleGetTicket(req, res, matchTicketId[1]);
    } else if (req.method === 'PATCH' && matchTicketId) {
      await handlePatchTicket(req, res, matchTicketId[1]);
    } else if (req.method === 'DELETE' && matchTicketId) {
      await handleDeleteTicket(req, res, matchTicketId[1]);
    } else if (req.method === 'GET' && matchMetrics) {
      await handleGetMetrics(req, res);
    } else if (req.method === 'POST' && matchMetrics) {
      // Metrics only supports GET
      sendJSON(res, 405, { error: 'Method not allowed' });
    } else {
      sendJSON(res, 404, { error: 'Not found' });
    }
  } catch (err) {
    if (err.status && err.message) {
      sendJSON(res, err.status, { error: err.message });
    } else {
      console.error('Unhandled error:', err);
      sendJSON(res, 500, { error: 'Internal server error' });
    }
  }
});

server.listen(PORT, HOST, () => {
  console.log(`Server running at http://${HOST}:${PORT}/`);
});
