// server.js - Help Desk Ticket API Server
import http from 'http';
import fs from 'fs';
import path from 'path';
import crypto from 'crypto';

const HOST = '127.0.0.1';
const PORT = 8080;
const DATA_FILE = path.join(process.cwd(), 'tickets.json');

// ---------- Helper functions ----------

function readTickets() {
  try {
    const data = fs.readFileSync(DATA_FILE, 'utf8');
    return JSON.parse(data);
  } catch (err) {
    if (err.code === 'ENOENT') return [];
    throw err;
  }
}

function saveTickets(tickets) {
  fs.writeFileSync(DATA_FILE, JSON.stringify(tickets, null, 2), 'utf8');
}

function sendJSON(res, statusCode, data) {
  res.writeHead(statusCode, {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
  });
  res.end(JSON.stringify(data));
}

function getBody(req) {
  return new Promise((resolve, reject) => {
    let body = '';
    req.on('data', chunk => (body += chunk));
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

function generateId() {
  return crypto.randomUUID();
}

function nowISO() {
  return new Date().toISOString();
}

const VALID_PRIORITIES = ['low', 'medium', 'high'];
const VALID_STATUSES = ['open', 'in_progress', 'resolved'];

function validateTicket(body, requireAll) {
  const errors = [];
  if (requireAll) {
    if (!body.subject || typeof body.subject !== 'string') errors.push('subject is required and must be a string');
    if (!body.description || typeof body.description !== 'string') errors.push('description is required and must be a string');
    if (!body.priority || !VALID_PRIORITIES.includes(body.priority)) errors.push('priority must be one of: low, medium, high');
    if (!body.status || !VALID_STATUSES.includes(body.status)) errors.push('status must be one of: open, in_progress, resolved');
  } else {
    if (body.subject !== undefined && typeof body.subject !== 'string') errors.push('subject must be a string');
    if (body.description !== undefined && typeof body.description !== 'string') errors.push('description must be a string');
    if (body.priority !== undefined && !VALID_PRIORITIES.includes(body.priority)) errors.push('priority must be one of: low, medium, high');
    if (body.status !== undefined && !VALID_STATUSES.includes(body.status)) errors.push('status must be one of: open, in_progress, resolved');
  }
  return errors;
}

// ---------- Route handlers ----------

function getTickets(req, res) {
  const url = new URL(req.url, `http://${req.headers.host}`);
  const statusFilter = url.searchParams.get('status');
  const priorityFilter = url.searchParams.get('priority');

  let tickets = readTickets();

  if (statusFilter) {
    tickets = tickets.filter(t => t.status === statusFilter);
  }
  if (priorityFilter) {
    tickets = tickets.filter(t => t.priority === priorityFilter);
  }

  sendJSON(res, 200, tickets);
}

async function createTicket(req, res) {
  let body;
  try {
    body = await getBody(req);
  } catch {
    sendJSON(res, 400, { error: 'Invalid JSON in request body' });
    return;
  }

  const errors = validateTicket(body, true);
  if (errors.length > 0) {
    sendJSON(res, 400, { error: 'Validation error', details: errors });
    return;
  }

  const ticket = {
    id: generateId(),
    subject: body.subject,
    description: body.description,
    priority: body.priority,
    status: body.status,
    created_at: nowISO(),
    updated_at: nowISO(),
  };

  const tickets = readTickets();
  tickets.push(ticket);
  saveTickets(tickets);

  sendJSON(res, 201, ticket);
}

function getTicket(req, res, id) {
  const tickets = readTickets();
  const ticket = tickets.find(t => t.id === id);
  if (!ticket) {
    sendJSON(res, 404, { error: 'Ticket not found' });
    return;
  }
  sendJSON(res, 200, ticket);
}

async function updateTicket(req, res, id) {
  let body;
  try {
    body = await getBody(req);
  } catch {
    sendJSON(res, 400, { error: 'Invalid JSON in request body' });
    return;
  }

  // Only allow known fields
  const allowedFields = ['subject', 'description', 'priority', 'status'];
  const updateData = {};
  for (const key of allowedFields) {
    if (body[key] !== undefined) {
      updateData[key] = body[key];
    }
  }

  if (Object.keys(updateData).length === 0) {
    sendJSON(res, 400, { error: 'No valid fields provided for update' });
    return;
  }

  const errors = validateTicket(updateData, false);
  if (errors.length > 0) {
    sendJSON(res, 400, { error: 'Validation error', details: errors });
    return;
  }

  const tickets = readTickets();
  const index = tickets.findIndex(t => t.id === id);
  if (index === -1) {
    sendJSON(res, 404, { error: 'Ticket not found' });
    return;
  }

  const ticket = tickets[index];
  for (const key of Object.keys(updateData)) {
    ticket[key] = updateData[key];
  }
  ticket.updated_at = nowISO();
  tickets[index] = ticket;
  saveTickets(tickets);

  sendJSON(res, 200, ticket);
}

function deleteTicket(req, res, id) {
  const tickets = readTickets();
  const index = tickets.findIndex(t => t.id === id);
  if (index === -1) {
    sendJSON(res, 404, { error: 'Ticket not found' });
    return;
  }

  tickets.splice(index, 1);
  saveTickets(tickets);
  res.writeHead(204, {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
  });
  res.end();
}

function getMetrics(req, res) {
  const tickets = readTickets();
  const statusCounts = { open: 0, in_progress: 0, resolved: 0 };
  const priorityCounts = { low: 0, medium: 0, high: 0 };

  let openAgeSum = 0;
  let openCount = 0;
  const now = Date.now();

  for (const ticket of tickets) {
    if (statusCounts.hasOwnProperty(ticket.status)) {
      statusCounts[ticket.status]++;
    }
    if (priorityCounts.hasOwnProperty(ticket.priority)) {
      priorityCounts[ticket.priority]++;
    }
    if (ticket.status === 'open') {
      const created = new Date(ticket.created_at).getTime();
      if (!isNaN(created)) {
        openAgeSum += (now - created) / 1000;
        openCount++;
      }
    }
  }

  const averageAgeOpenTickets = openCount > 0 ? openAgeSum / openCount : 0;

  sendJSON(res, 200, { statusCounts, priorityCounts, averageAgeOpenTickets });
}

// ---------- Server ----------

const server = http.createServer((req, res) => {
  // Handle CORS preflight (OPTIONS)
  if (req.method === 'OPTIONS') {
    res.writeHead(204, {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    });
    res.end();
    return;
  }

  // Parse URL
  const url = new URL(req.url, `http://${req.headers.host}`);
  const pathname = url.pathname;

  // Routing
  const ticketDetailMatch = pathname.match(/^\/tickets\/([^\/]+)$/);

  try {
    if (req.method === 'GET' && pathname === '/tickets') {
      getTickets(req, res);
    } else if (req.method === 'POST' && pathname === '/tickets') {
      createTicket(req, res);
    } else if (req.method === 'GET' && ticketDetailMatch) {
      getTicket(req, res, ticketDetailMatch[1]);
    } else if (req.method === 'PATCH' && ticketDetailMatch) {
      updateTicket(req, res, ticketDetailMatch[1]);
    } else if (req.method === 'DELETE' && ticketDetailMatch) {
      deleteTicket(req, res, ticketDetailMatch[1]);
    } else if (req.method === 'GET' && pathname === '/metrics') {
      getMetrics(req, res);
    } else if (req.method === 'GET' && pathname === '/') {
      sendJSON(res, 200, { message: 'Help Desk Ticket API' });
    } else {
      sendJSON(res, 404, { error: 'Route not found' });
    }
  } catch (err) {
    console.error('Unexpected error:', err);
    sendJSON(res, 500, { error: 'Internal server error' });
  }
});

server.listen(PORT, HOST, () => {
  console.log(`Server running at http://${HOST}:${PORT}/`);
});
