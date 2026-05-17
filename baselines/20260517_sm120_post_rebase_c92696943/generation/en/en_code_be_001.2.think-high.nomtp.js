const http = require('http');
const url = require('url');
const fs = require('fs');
const path = require('path');

const DATA_FILE = path.join(__dirname, 'tickets.json');
const HOST = '127.0.0.1';
const PORT = 8080;

// Helper: read tickets from file, return array
function readTickets() {
  try {
    const data = fs.readFileSync(DATA_FILE, 'utf8');
    return JSON.parse(data);
  } catch (err) {
    // If file doesn't exist or is invalid, return empty array
    return [];
  }
}

// Helper: write tickets to file
function writeTickets(tickets) {
  fs.writeFileSync(DATA_FILE, JSON.stringify(tickets, null, 2), 'utf8');
}

// Helper: generate next ID
function getNextId(tickets) {
  if (tickets.length === 0) return 1;
  const maxId = Math.max(...tickets.map(t => t.id));
  return maxId + 1;
}

// Helper: validate required fields for ticket creation
function validateCreate(body) {
  const errors = [];
  if (!body.subject || typeof body.subject !== 'string' || body.subject.trim() === '') {
    errors.push('subject is required and must be a non-empty string');
  }
  if (!body.description || typeof body.description !== 'string' || body.description.trim() === '') {
    errors.push('description is required and must be a non-empty string');
  }
  if (body.priority && !['low', 'medium', 'high'].includes(body.priority)) {
    errors.push('priority must be one of: low, medium, high');
  }
  if (body.status && !['open', 'in_progress', 'resolved'].includes(body.status)) {
    errors.push('status must be one of: open, in_progress, resolved');
  }
  return errors;
}

// Helper: validate fields for PATCH
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

// Helper: parse request body
function parseBody(req) {
  return new Promise((resolve, reject) => {
    let body = '';
    req.on('data', chunk => {
      body += chunk;
      // Limit body size to 1MB to prevent abuse
      if (body.length > 1e6) {
        req.destroy();
        reject(new Error('Request body too large'));
      }
    });
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

// Helper: send JSON response
function sendJSON(res, statusCode, data) {
  res.writeHead(statusCode, {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type'
  });
  res.end(JSON.stringify(data));
}

// Helper: send error response
function sendError(res, statusCode, message) {
  sendJSON(res, statusCode, { error: message });
}

// Route handlers
async function handleGetTickets(req, res, query) {
  let tickets = readTickets();
  // Filter by query params
  if (query.status) {
    tickets = tickets.filter(t => t.status === query.status);
  }
  if (query.priority) {
    tickets = tickets.filter(t => t.priority === query.priority);
  }
  sendJSON(res, 200, tickets);
}

async function handlePostTickets(req, res) {
  let body;
  try {
    body = await parseBody(req);
  } catch (err) {
    if (err.message === 'Invalid JSON') {
      return sendError(res, 400, 'Invalid JSON in request body');
    }
    return sendError(res, 400, err.message);
  }

  const errors = validateCreate(body);
  if (errors.length > 0) {
    return sendError(res, 400, errors.join('; '));
  }

  const tickets = readTickets();
  const now = new Date().toISOString();
  const newTicket = {
    id: getNextId(tickets),
    subject: body.subject.trim(),
    description: body.description.trim(),
    priority: body.priority || 'low',
    status: body.status || 'open',
    created_at: now,
    updated_at: now
  };
  tickets.push(newTicket);
  writeTickets(tickets);
  sendJSON(res, 201, newTicket);
}

async function handleGetTicket(req, res, id) {
  const tickets = readTickets();
  const ticket = tickets.find(t => t.id === id);
  if (!ticket) {
    return sendError(res, 404, `Ticket with id ${id} not found`);
  }
  sendJSON(res, 200, ticket);
}

async function handlePatchTicket(req, res, id) {
  let body;
  try {
    body = await parseBody(req);
  } catch (err) {
    if (err.message === 'Invalid JSON') {
      return sendError(res, 400, 'Invalid JSON in request body');
    }
    return sendError(res, 400, err.message);
  }

  const errors = validatePatch(body);
  if (errors.length > 0) {
    return sendError(res, 400, errors.join('; '));
  }

  const tickets = readTickets();
  const index = tickets.findIndex(t => t.id === id);
  if (index === -1) {
    return sendError(res, 404, `Ticket with id ${id} not found`);
  }

  const ticket = tickets[index];
  if (body.subject !== undefined) ticket.subject = body.subject.trim();
  if (body.description !== undefined) ticket.description = body.description.trim();
  if (body.priority !== undefined) ticket.priority = body.priority;
  if (body.status !== undefined) ticket.status = body.status;
  ticket.updated_at = new Date().toISOString();
  tickets[index] = ticket;
  writeTickets(tickets);
  sendJSON(res, 200, ticket);
}

async function handleDeleteTicket(req, res, id) {
  let tickets = readTickets();
  const index = tickets.findIndex(t => t.id === id);
  if (index === -1) {
    return sendError(res, 404, `Ticket with id ${id} not found`);
  }
  tickets.splice(index, 1);
  writeTickets(tickets);
  sendJSON(res, 200, { message: `Ticket ${id} deleted` });
}

async function handleMetrics(req, res) {
  const tickets = readTickets();
  const now = Date.now();

  // Count by status
  const statusCounts = {};
  for (const t of tickets) {
    statusCounts[t.status] = (statusCounts[t.status] || 0) + 1;
  }

  // Count by priority
  const priorityCounts = {};
  for (const t of tickets) {
    priorityCounts[t.priority] = (priorityCounts[t.priority] || 0) + 1;
  }

  // Average age of open tickets in seconds
  const openTickets = tickets.filter(t => t.status === 'open');
  let avgAge = 0;
  if (openTickets.length > 0) {
    const totalAge = openTickets.reduce((sum, t) => {
      const created = new Date(t.created_at).getTime();
      return sum + (now - created);
    }, 0);
    avgAge = (totalAge / openTickets.length) / 1000; // seconds
  }

  sendJSON(res, 200, {
    status_counts: statusCounts,
    priority_counts: priorityCounts,
    average_open_age_seconds: avgAge
  });
}

// Main request handler
async function onRequest(req, res) {
  const parsedUrl = url.parse(req.url, true);
  const pathname = parsedUrl.pathname;
  const method = req.method;

  // CORS preflight
  if (method === 'OPTIONS') {
    res.writeHead(204, {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type'
    });
    return res.end();
  }

  // Parse ID from path
  const match = pathname.match(/^\/tickets\/(\d+)$/);
  const isTicketsRoot = pathname === '/tickets';
  const isMetrics = pathname === '/metrics';

  try {
    if (isMetrics && method === 'GET') {
      await handleMetrics(req, res);
    } else if (isTicketsRoot && method === 'GET') {
      await handleGetTickets(req, res, parsedUrl.query);
    } else if (isTicketsRoot && method === 'POST') {
      await handlePostTickets(req, res);
    } else if (match) {
      const id = parseInt(match[1], 10);
      if (method === 'GET') {
        await handleGetTicket(req, res, id);
      } else if (method === 'PATCH') {
        await handlePatchTicket(req, res, id);
      } else if (method === 'DELETE') {
        await handleDeleteTicket(req, res, id);
      } else {
        sendError(res, 405, `Method ${method} not allowed on /tickets/${id}`);
      }
    } else {
      sendError(res, 404, `Route ${pathname} not found`);
    }
  } catch (err) {
    console.error('Unhandled error:', err);
    sendError(res, 500, 'Internal server error');
  }
}

// Create server
const server = http.createServer(onRequest);
server.listen(PORT, HOST, () => {
  console.log(`Server running at http://${HOST}:${PORT}/`);
});
