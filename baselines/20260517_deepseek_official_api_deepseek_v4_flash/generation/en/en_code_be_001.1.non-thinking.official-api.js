const http = require('http');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const DATA_FILE = path.join(__dirname, 'tickets.json');
const PORT = 8080;
const HOST = '127.0.0.1';

// Simple promise-based mutex to serialize file operations
let _lock = Promise.resolve();
function lock() {
  let release;
  const prev = _lock;
  _lock = new Promise(resolve => { release = resolve; });
  return prev.then(() => release);
}

// Read tickets from file, return array (empty if file missing)
async function readTickets() {
  try {
    const data = await fs.promises.readFile(DATA_FILE, 'utf8');
    return JSON.parse(data);
  } catch (err) {
    if (err.code === 'ENOENT') return [];
    throw err;
  }
}

// Write tickets array to file
async function writeTickets(tickets) {
  await fs.promises.writeFile(DATA_FILE, JSON.stringify(tickets, null, 2), 'utf8');
}

// Generate a unique ID (crypto-based)
function generateId() {
  return crypto.randomUUID();
}

// Validate ticket fields for creation
function validateCreate(body) {
  const errors = [];
  if (!body.subject || typeof body.subject !== 'string' || body.subject.trim() === '') {
    errors.push('subject is required and must be a non-empty string');
  }
  if (!body.description || typeof body.description !== 'string' || body.description.trim() === '') {
    errors.push('description is required and must be a non-empty string');
  }
  if (!body.priority || !['low', 'medium', 'high'].includes(body.priority)) {
    errors.push('priority must be one of: low, medium, high');
  }
  if (body.status && !['open', 'in_progress', 'resolved'].includes(body.status)) {
    errors.push('status must be one of: open, in_progress, resolved');
  }
  return errors;
}

// Validate fields for PATCH (partial update)
function validatePatch(body) {
  const errors = [];
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
  return errors;
}

// Send JSON response
function sendJSON(res, statusCode, data) {
  const json = JSON.stringify(data);
  res.writeHead(statusCode, {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type'
  });
  res.end(json);
}

// Parse JSON body
function parseBody(req) {
  return new Promise((resolve, reject) => {
    let body = '';
    req.on('data', chunk => { body += chunk; });
    req.on('end', () => {
      if (body.length === 0) {
        resolve({});
        return;
      }
      try {
        resolve(JSON.parse(body));
      } catch (e) {
        reject(new Error('Invalid JSON in request body'));
      }
    });
    req.on('error', reject);
  });
}

// Create a new ticket (POST /tickets)
async function handleCreate(req, res) {
  let body;
  try {
    body = await parseBody(req);
  } catch (e) {
    sendJSON(res, 400, { error: e.message });
    return;
  }
  const errors = validateCreate(body);
  if (errors.length > 0) {
    sendJSON(res, 400, { error: 'Validation failed', details: errors });
    return;
  }
  const now = new Date().toISOString();
  const ticket = {
    id: generateId(),
    subject: body.subject.trim(),
    description: body.description.trim(),
    priority: body.priority,
    status: body.status || 'open',
    created_at: now,
    updated_at: now
  };
  const release = await lock();
  try {
    const tickets = await readTickets();
    tickets.push(ticket);
    await writeTickets(tickets);
    sendJSON(res, 201, ticket);
  } catch (err) {
    sendJSON(res, 500, { error: 'Internal server error' });
  } finally {
    release();
  }
}

// List tickets (GET /tickets) with optional filter by status and priority
async function handleList(req, res) {
  const url = new URL(req.url, `http://${req.headers.host}`);
  const statusFilter = url.searchParams.get('status');
  const priorityFilter = url.searchParams.get('priority');
  const release = await lock();
  try {
    let tickets = await readTickets();
    if (statusFilter) {
      tickets = tickets.filter(t => t.status === statusFilter);
    }
    if (priorityFilter) {
      tickets = tickets.filter(t => t.priority === priorityFilter);
    }
    sendJSON(res, 200, tickets);
  } catch (err) {
    sendJSON(res, 500, { error: 'Internal server error' });
  } finally {
    release();
  }
}

// Get single ticket (GET /tickets/:id)
async function handleGetById(req, res, id) {
  const release = await lock();
  try {
    const tickets = await readTickets();
    const ticket = tickets.find(t => t.id === id);
    if (!ticket) {
      sendJSON(res, 404, { error: 'Ticket not found' });
      return;
    }
    sendJSON(res, 200, ticket);
  } catch (err) {
    sendJSON(res, 500, { error: 'Internal server error' });
  } finally {
    release();
  }
}

// Update ticket (PATCH /tickets/:id)
async function handlePatch(req, res, id) {
  let body;
  try {
    body = await parseBody(req);
  } catch (e) {
    sendJSON(res, 400, { error: e.message });
    return;
  }
  const errors = validatePatch(body);
  if (errors.length > 0) {
    sendJSON(res, 400, { error: 'Validation failed', details: errors });
    return;
  }
  const release = await lock();
  try {
    const tickets = await readTickets();
    const index = tickets.findIndex(t => t.id === id);
    if (index === -1) {
      sendJSON(res, 404, { error: 'Ticket not found' });
      return;
    }
    const ticket = tickets[index];
    if (body.subject !== undefined) ticket.subject = body.subject.trim();
    if (body.description !== undefined) ticket.description = body.description.trim();
    if (body.priority !== undefined) ticket.priority = body.priority;
    if (body.status !== undefined) ticket.status = body.status;
    ticket.updated_at = new Date().toISOString();
    tickets[index] = ticket;
    await writeTickets(tickets);
    sendJSON(res, 200, ticket);
  } catch (err) {
    sendJSON(res, 500, { error: 'Internal server error' });
  } finally {
    release();
  }
}

// Delete ticket (DELETE /tickets/:id)
async function handleDelete(req, res, id) {
  const release = await lock();
  try {
    let tickets = await readTickets();
    const index = tickets.findIndex(t => t.id === id);
    if (index === -1) {
      sendJSON(res, 404, { error: 'Ticket not found' });
      return;
    }
    tickets.splice(index, 1);
    await writeTickets(tickets);
    sendJSON(res, 200, { message: 'Ticket deleted' });
  } catch (err) {
    sendJSON(res, 500, { error: 'Internal server error' });
  } finally {
    release();
  }
}

// Metrics (GET /metrics)
async function handleMetrics(req, res) {
  const release = await lock();
  try {
    const tickets = await readTickets();
    const now = Date.now();
    const countsByStatus = { open: 0, in_progress: 0, resolved: 0 };
    const countsByPriority = { low: 0, medium: 0, high: 0 };
    let totalAgeOpen = 0;
    let openCount = 0;
    for (const ticket of tickets) {
      if (countsByStatus.hasOwnProperty(ticket.status)) {
        countsByStatus[ticket.status]++;
      }
      if (countsByPriority.hasOwnProperty(ticket.priority)) {
        countsByPriority[ticket.priority]++;
      }
      if (ticket.status === 'open') {
        const created = new Date(ticket.created_at).getTime();
        totalAgeOpen += (now - created) / 1000; // seconds
        openCount++;
      }
    }
    const avgAgeOpen = openCount > 0 ? totalAgeOpen / openCount : 0;
    const metrics = {
      countsByStatus,
      countsByPriority,
      averageAgeOfOpenTicketsInSeconds: avgAgeOpen
    };
    sendJSON(res, 200, metrics);
  } catch (err) {
    sendJSON(res, 500, { error: 'Internal server error' });
  } finally {
    release();
  }
}

// Route request
async function handleRequest(req, res) {
  // CORS preflight
  if (req.method === 'OPTIONS') {
    res.writeHead(204, {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
      'Access-Control-Max-Age': 86400
    });
    res.end();
    return;
  }

  const url = new URL(req.url, `http://${req.headers.host}`);
  const pathParts = url.pathname.split('/').filter(p => p !== '');

  // Root
  if (pathParts.length === 0) {
    sendJSON(res, 200, { message: 'Help Desk API' });
    return;
  }

  // /tickets routes
  if (pathParts[0] === 'tickets') {
    if (pathParts.length === 1) {
      // /tickets
      if (req.method === 'GET') {
        await handleList(req, res);
      } else if (req.method === 'POST') {
        await handleCreate(req, res);
      } else {
        sendJSON(res, 405, { error: 'Method not allowed' });
      }
      return;
    } else if (pathParts.length === 2) {
      const id = pathParts[1];
      if (req.method === 'GET') {
        await handleGetById(req, res, id);
      } else if (req.method === 'PATCH') {
        await handlePatch(req, res, id);
      } else if (req.method === 'DELETE') {
        await handleDelete(req, res, id);
      } else {
        sendJSON(res, 405, { error: 'Method not allowed' });
      }
      return;
    } else {
      sendJSON(res, 404, { error: 'Not found' });
      return;
    }
  }

  // /metrics
  if (pathParts[0] === 'metrics' && pathParts.length === 1) {
    if (req.method === 'GET') {
      await handleMetrics(req, res);
    } else {
      sendJSON(res, 405, { error: 'Method not allowed' });
    }
    return;
  }

  // Unknown route
  sendJSON(res, 404, { error: 'Not found' });
}

// Create server
const server = http.createServer(handleRequest);

server.listen(PORT, HOST, () => {
  console.log(`Server running at http://${HOST}:${PORT}/`);
});
