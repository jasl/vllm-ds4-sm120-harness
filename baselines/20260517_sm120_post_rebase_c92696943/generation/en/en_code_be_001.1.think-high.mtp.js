const http = require('http');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const HOST = '127.0.0.1';
const PORT = 8080;
const DATA_FILE = path.join(__dirname, 'tickets.json');

// ---------- Simple sequential file access lock ----------
let fileLock = Promise.resolve();

function withFileLock(fn) {
  fileLock = fileLock.then(fn, fn);
  return fileLock;
}

// ---------- File I/O (async, but serialized via lock) ----------
function readTicketsFromFile() {
  return withFileLock(async () => {
    try {
      const data = await fs.promises.readFile(DATA_FILE, 'utf8');
      return JSON.parse(data);
    } catch (err) {
      if (err.code === 'ENOENT') {
        // File doesn't exist yet – start with empty array
        return [];
      }
      throw err;
    }
  });
}

function writeTicketsToFile(tickets) {
  return withFileLock(async () => {
    await fs.promises.writeFile(DATA_FILE, JSON.stringify(tickets, null, 2), 'utf8');
  });
}

// ---------- Helpers ----------
function generateId() {
  return crypto.randomBytes(8).toString('hex');
}

function getTimestamp() {
  return new Date().toISOString();
}

function sendJSON(res, statusCode, data) {
  const body = JSON.stringify(data);
  res.writeHead(statusCode, {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Content-Length': Buffer.byteLength(body)
  });
  res.end(body);
}

function sendError(res, statusCode, message) {
  sendJSON(res, statusCode, { error: message });
}

// Parse JSON body from request
function getBody(req) {
  return new Promise((resolve, reject) => {
    let body = '';
    req.on('data', chunk => { body += chunk.toString(); });
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

// Validate ticket object
function validateTicket(ticket, isCreate) {
  const errors = [];
  if (isCreate) {
    if (!ticket.subject || typeof ticket.subject !== 'string' || ticket.subject.trim() === '') {
      errors.push('subject is required and must be a non-empty string');
    }
    if (!ticket.description || typeof ticket.description !== 'string' || ticket.description.trim() === '') {
      errors.push('description is required and must be a non-empty string');
    }
  }
  if (ticket.priority !== undefined) {
    const validPriorities = ['low', 'medium', 'high'];
    if (!validPriorities.includes(ticket.priority)) {
      errors.push('priority must be one of: low, medium, high');
    }
  }
  if (ticket.status !== undefined) {
    const validStatuses = ['open', 'in_progress', 'resolved'];
    if (!validStatuses.includes(ticket.status)) {
      errors.push('status must be one of: open, in_progress, resolved');
    }
  }
  return errors.length > 0 ? errors.join('; ') : null;
}

// ---------- Route Handlers ----------
async function handleGetTickets(req, res, query) {
  const tickets = await readTicketsFromFile();
  let filtered = tickets;

  // Filter by status
  if (query.status) {
    const status = query.status.toLowerCase();
    filtered = filtered.filter(t => t.status === status);
  }
  // Filter by priority
  if (query.priority) {
    const priority = query.priority.toLowerCase();
    filtered = filtered.filter(t => t.priority === priority);
  }

  sendJSON(res, 200, filtered);
}

async function handlePostTicket(req, res) {
  let body;
  try {
    body = await getBody(req);
  } catch (e) {
    return sendError(res, 400, 'Invalid JSON in request body');
  }

  if (!body) {
    return sendError(res, 400, 'Request body is required');
  }

  const validationError = validateTicket(body, true);
  if (validationError) {
    return sendError(res, 400, validationError);
  }

  const now = getTimestamp();
  const newTicket = {
    id: generateId(),
    subject: body.subject.trim(),
    description: body.description.trim(),
    priority: body.priority || 'low',
    status: body.status || 'open',
    created_at: now,
    updated_at: now
  };

  const tickets = await readTicketsFromFile();
  tickets.push(newTicket);
  await writeTicketsToFile(tickets);

  sendJSON(res, 201, newTicket);
}

async function handleGetTicketById(req, res, id) {
  const tickets = await readTicketsFromFile();
  const ticket = tickets.find(t => t.id === id);
  if (!ticket) {
    return sendError(res, 404, 'Ticket not found');
  }
  sendJSON(res, 200, ticket);
}

async function handlePatchTicketById(req, res, id) {
  let body;
  try {
    body = await getBody(req);
  } catch (e) {
    return sendError(res, 400, 'Invalid JSON in request body');
  }

  if (!body || Object.keys(body).length === 0) {
    return sendError(res, 400, 'Request body must contain at least one field to update');
  }

  // Validate provided fields
  const allowedFields = ['subject', 'description', 'priority', 'status'];
  for (const field of Object.keys(body)) {
    if (!allowedFields.includes(field)) {
      return sendError(res, 400, `Field '${field}' is not allowed for update`);
    }
  }

  // Validate values
  const validationError = validateTicket(body, false);
  if (validationError) {
    return sendError(res, 400, validationError);
  }

  const tickets = await readTicketsFromFile();
  const index = tickets.findIndex(t => t.id === id);
  if (index === -1) {
    return sendError(res, 404, 'Ticket not found');
  }

  const ticket = tickets[index];
  if (body.subject !== undefined) ticket.subject = body.subject.trim();
  if (body.description !== undefined) ticket.description = body.description.trim();
  if (body.priority !== undefined) ticket.priority = body.priority;
  if (body.status !== undefined) ticket.status = body.status;
  ticket.updated_at = getTimestamp();

  tickets[index] = ticket;
  await writeTicketsToFile(tickets);

  sendJSON(res, 200, ticket);
}

async function handleDeleteTicketById(req, res, id) {
  const tickets = await readTicketsFromFile();
  const index = tickets.findIndex(t => t.id === id);
  if (index === -1) {
    return sendError(res, 404, 'Ticket not found');
  }
  const deleted = tickets.splice(index, 1)[0];
  await writeTicketsToFile(tickets);
  sendJSON(res, 200, deleted);
}

async function handleGetMetrics(req, res) {
  const tickets = await readTicketsFromFile();
  const now = Date.now();

  // Counts by status
  const statusCounts = {};
  const priorityCounts = {};
  let openAgeSum = 0;
  let openCount = 0;

  for (const ticket of tickets) {
    // Status counts
    statusCounts[ticket.status] = (statusCounts[ticket.status] || 0) + 1;

    // Priority counts
    priorityCounts[ticket.priority] = (priorityCounts[ticket.priority] || 0) + 1;

    // Open tickets average age
    if (ticket.status === 'open') {
      const created = new Date(ticket.created_at).getTime();
      openAgeSum += (now - created) / 1000; // seconds
      openCount++;
    }
  }

  const metrics = {
    status_counts: statusCounts,
    priority_counts: priorityCounts,
    average_open_age_seconds: openCount > 0 ? openAgeSum / openCount : 0
  };

  sendJSON(res, 200, metrics);
}

// ---------- Server ----------
const server = http.createServer(async (req, res) => {
  // CORS preflight
  if (req.method === 'OPTIONS') {
    res.writeHead(204, {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
      'Access-Control-Max-Age': 86400
    });
    return res.end();
  }

  // Parse URL
  const parsedUrl = new URL(req.url, `http://${HOST}:${PORT}`);
  const pathname = parsedUrl.pathname;
  const query = Object.fromEntries(parsedUrl.searchParams);

  // Simple router
  try {
    // POST /tickets
    if (pathname === '/tickets' && req.method === 'POST') {
      return await handlePostTicket(req, res);
    }

    // GET /tickets
    if (pathname === '/tickets' && req.method === 'GET') {
      return await handleGetTickets(req, res, query);
    }

    // GET /metrics
    if (pathname === '/metrics' && req.method === 'GET') {
      return await handleGetMetrics(req, res);
    }

    // /tickets/{id}
    const ticketMatch = pathname.match(/^\/tickets\/([a-f0-9]+)$/);
    if (ticketMatch) {
      const id = ticketMatch[1];
      if (req.method === 'GET') {
        return await handleGetTicketById(req, res, id);
      }
      if (req.method === 'PATCH') {
        return await handlePatchTicketById(req, res, id);
      }
      if (req.method === 'DELETE') {
        return await handleDeleteTicketById(req, res, id);
      }
      // Method not allowed for this path
      return sendError(res, 405, 'Method not allowed');
    }

    // Unknown route
    sendError(res, 404, 'Not found');
  } catch (err) {
    console.error('Server error:', err);
    sendError(res, 500, 'Internal server error');
  }
});

server.listen(PORT, HOST, () => {
  console.log(`Server running at http://${HOST}:${PORT}/`);
});
