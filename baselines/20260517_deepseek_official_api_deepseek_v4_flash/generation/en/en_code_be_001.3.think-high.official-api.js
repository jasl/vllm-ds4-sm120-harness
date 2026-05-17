const http = require('http');
const fs = require('fs');
const path = require('path');
const url = require('url');

const DATA_FILE = path.join(__dirname, 'tickets.json');
const HOST = '127.0.0.1';
const PORT = 8080;

// ----------------------------------------------------------------------
// File operations queue (simple mutex to serialise all reads/writes)
// ----------------------------------------------------------------------
let fileQueue = Promise.resolve();

function withFileAccess(fn) {
  fileQueue = fileQueue.then(() => fn());
  return fileQueue;
}

// ----------------------------------------------------------------------
// Read / write tickets.json
// ----------------------------------------------------------------------
async function readTickets() {
  try {
    const raw = await fs.promises.readFile(DATA_FILE, 'utf8');
    return JSON.parse(raw);
  } catch (err) {
    if (err.code === 'ENOENT') return [];
    throw err;
  }
}

async function writeTickets(tickets) {
  const tmpFile = DATA_FILE + '.tmp';
  await fs.promises.writeFile(tmpFile, JSON.stringify(tickets, null, 2), 'utf8');
  await fs.promises.rename(tmpFile, DATA_FILE);
}

// ----------------------------------------------------------------------
// Utility: parse JSON body from request
// ----------------------------------------------------------------------
function parseBody(req) {
  return new Promise((resolve, reject) => {
    let body = '';
    req.on('data', chunk => (body += chunk));
    req.on('end', () => {
      try {
        resolve(body ? JSON.parse(body) : {});
      } catch (e) {
        reject(new Error('Invalid JSON'));
      }
    });
    req.on('error', reject);
  });
}

// ----------------------------------------------------------------------
// Generate a new unique ID (based on existing max id)
// ----------------------------------------------------------------------
function generateId(tickets) {
  if (tickets.length === 0) return 1;
  const maxId = Math.max(...tickets.map(t => t.id));
  return maxId + 1;
}

// ----------------------------------------------------------------------
// Validate ticket fields
// ----------------------------------------------------------------------
const VALID_PRIORITIES = ['low', 'medium', 'high'];
const VALID_STATUSES = ['open', 'in_progress', 'resolved'];

function validateTicket(body, isUpdate = false) {
  const errors = [];
  const { subject, description, priority, status } = body;

  if (!isUpdate) {
    if (!subject || typeof subject !== 'string') errors.push('subject is required and must be a string');
    if (!description || typeof description !== 'string') errors.push('description is required and must be a string');
  } else {
    if (subject !== undefined && typeof subject !== 'string') errors.push('subject must be a string');
    if (description !== undefined && typeof description !== 'string') errors.push('description must be a string');
  }

  if (priority !== undefined && !VALID_PRIORITIES.includes(priority)) {
    errors.push(`priority must be one of: ${VALID_PRIORITIES.join(', ')}`);
  }
  if (status !== undefined && !VALID_STATUSES.includes(status)) {
    errors.push(`status must be one of: ${VALID_STATUSES.join(', ')}`);
  }
  return errors;
}

// ----------------------------------------------------------------------
// Send JSON response
// ----------------------------------------------------------------------
function sendJSON(res, statusCode, data) {
  const headers = {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
  };
  res.writeHead(statusCode, headers);
  res.end(JSON.stringify(data));
}

// ----------------------------------------------------------------------
// Route handlers
// ----------------------------------------------------------------------
async function handleGetTickets(req, res, query) {
  const tickets = await withFileAccess(readTickets);
  const { status: filterStatus, priority: filterPriority } = query;
  let filtered = tickets;
  if (filterStatus) {
    filtered = filtered.filter(t => t.status === filterStatus);
  }
  if (filterPriority) {
    filtered = filtered.filter(t => t.priority === filterPriority);
  }
  sendJSON(res, 200, filtered);
}

async function handlePostTicket(req, res) {
  let body;
  try {
    body = await parseBody(req);
  } catch (err) {
    return sendJSON(res, 400, { error: 'Invalid JSON' });
  }

  const errors = validateTicket(body);
  if (errors.length) {
    return sendJSON(res, 400, { error: errors.join('; ') });
  }

  await withFileAccess(async () => {
    const tickets = await readTickets();
    const now = new Date().toISOString();
    const ticket = {
      id: generateId(tickets),
      subject: body.subject,
      description: body.description,
      priority: body.priority || 'low',
      status: body.status || 'open',
      created_at: now,
      updated_at: now,
    };
    tickets.push(ticket);
    await writeTickets(tickets);
    // Return the created ticket (still inside the mutex)
    sendJSON(res, 201, ticket);
  });
}

async function handleGetTicket(req, res, id) {
  const tickets = await withFileAccess(readTickets);
  const ticket = tickets.find(t => t.id === id);
  if (!ticket) {
    return sendJSON(res, 404, { error: 'Ticket not found' });
  }
  sendJSON(res, 200, ticket);
}

async function handlePatchTicket(req, res, id) {
  let body;
  try {
    body = await parseBody(req);
  } catch (err) {
    return sendJSON(res, 400, { error: 'Invalid JSON' });
  }

  const errors = validateTicket(body, true);
  if (errors.length) {
    return sendJSON(res, 400, { error: errors.join('; ') });
  }

  await withFileAccess(async () => {
    const tickets = await readTickets();
    const index = tickets.findIndex(t => t.id === id);
    if (index === -1) {
      return sendJSON(res, 404, { error: 'Ticket not found' });
    }

    const existing = tickets[index];
    const allowedFields = ['subject', 'description', 'priority', 'status'];
    let changed = false;
    for (const field of allowedFields) {
      if (body[field] !== undefined) {
        existing[field] = body[field];
        changed = true;
      }
    }
    if (changed) {
      existing.updated_at = new Date().toISOString();
    }
    tickets[index] = existing;
    await writeTickets(tickets);
    sendJSON(res, 200, existing);
  });
}

async function handleDeleteTicket(req, res, id) {
  await withFileAccess(async () => {
    const tickets = await readTickets();
    const index = tickets.findIndex(t => t.id === id);
    if (index === -1) {
      return sendJSON(res, 404, { error: 'Ticket not found' });
    }
    const removed = tickets.splice(index, 1)[0];
    await writeTickets(tickets);
    sendJSON(res, 200, removed);
  });
}

async function handleGetMetrics(req, res) {
  const tickets = await withFileAccess(readTickets);
  const now = Date.now();

  const statusCounts = {};
  const priorityCounts = {};
  let totalOpenAgeMs = 0;
  let openCount = 0;

  for (const t of tickets) {
    // status counts
    statusCounts[t.status] = (statusCounts[t.status] || 0) + 1;
    // priority counts
    priorityCounts[t.priority] = (priorityCounts[t.priority] || 0) + 1;
    // average age of open tickets (status === 'open')
    if (t.status === 'open') {
      openCount++;
      totalOpenAgeMs += now - new Date(t.created_at).getTime();
    }
  }

  const metrics = {
    status_counts: statusCounts,
    priority_counts: priorityCounts,
    average_open_age_seconds: openCount > 0 ? Math.round(totalOpenAgeMs / openCount / 1000) : 0,
  };
  sendJSON(res, 200, metrics);
}

// ----------------------------------------------------------------------
// Request dispatcher
// ----------------------------------------------------------------------
const routes = {
  GET: {},
  POST: {},
  PATCH: {},
  DELETE: {},
};

routes.GET['/tickets'] = handleGetTickets;
routes.POST['/tickets'] = handlePostTicket;
routes.GET['/metrics'] = handleGetMetrics;

const server = http.createServer(async (req, res) => {
  // CORS preflight
  if (req.method === 'OPTIONS') {
    res.writeHead(204, {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    });
    res.end();
    return;
  }

  const parsedUrl = url.parse(req.url, true);
  const pathname = parsedUrl.pathname;
  const method = req.method;

  // Try exact match first
  if (routes[method] && routes[method][pathname]) {
    try {
      await routes[method][pathname](req, res, parsedUrl.query);
    } catch (err) {
      console.error(err);
      sendJSON(res, 500, { error: 'Internal server error' });
    }
    return;
  }

  // Try parametric routes: /tickets/:id and /tickets/:id
  const ticketMatch = pathname.match(/^\/tickets\/(\d+)$/);
  if (ticketMatch) {
    const id = parseInt(ticketMatch[1], 10);
    if (isNaN(id)) {
      return sendJSON(res, 400, { error: 'Invalid ticket ID' });
    }
    try {
      switch (method) {
        case 'GET':
          await handleGetTicket(req, res, id);
          break;
        case 'PATCH':
          await handlePatchTicket(req, res, id);
          break;
        case 'DELETE':
          await handleDeleteTicket(req, res, id);
          break;
        default:
          sendJSON(res, 405, { error: 'Method not allowed' });
      }
    } catch (err) {
      console.error(err);
      sendJSON(res, 500, { error: 'Internal server error' });
    }
    return;
  }

  // Unknown route
  sendJSON(res, 404, { error: 'Not found' });
});

server.listen(PORT, HOST, () => {
  console.log(`Server running at http://${HOST}:${PORT}/`);
});
