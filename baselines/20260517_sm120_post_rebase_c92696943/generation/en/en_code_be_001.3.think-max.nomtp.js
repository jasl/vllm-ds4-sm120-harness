'use strict';

const http = require('http');
const fs = require('fs');
const path = require('path');
const { URL } = require('url');

const HOST = process.env.HOST || '127.0.0.1';
const PORT = process.env.PORT || 8080;
const DATA_FILE = path.join(__dirname, 'tickets.json');

// In-memory ticket store
let tickets = [];
let nextId = 1;

// Simple serial write queue (mutex)
const writeQueue = [];
let writing = false;

function processQueue() {
  if (writing || writeQueue.length === 0) return;
  writing = true;
  const { resolve, reject } = writeQueue.shift();
  fs.writeFile(DATA_FILE, JSON.stringify(tickets, null, 2), 'utf8', (err) => {
    if (err) {
      console.error('Failed to write tickets.json:', err);
      reject(err);
    } else {
      resolve();
    }
    writing = false;
    processQueue();
  });
}

function saveTickets() {
  return new Promise((resolve, reject) => {
    writeQueue.push({ resolve, reject });
    processQueue();
  });
}

// Load data on startup
function loadTickets() {
  try {
    const data = fs.readFileSync(DATA_FILE, 'utf8');
    const parsed = JSON.parse(data);
    if (Array.isArray(parsed)) {
      tickets = parsed;
      const maxId = tickets.reduce((max, t) => Math.max(max, t.id || 0), 0);
      nextId = maxId + 1;
    }
  } catch (err) {
    if (err.code !== 'ENOENT') {
      console.error('Error loading tickets:', err);
    }
    tickets = [];
    nextId = 1;
  }
}
loadTickets();

// ----------------------------------------------------------------------
// Helper functions
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

function sendError(res, statusCode, message) {
  sendJSON(res, statusCode, { error: message });
}

function methodNotAllowed(res, allowed) {
  res.writeHead(405, {
    'Content-Type': 'application/json',
    Allow: allowed,
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': allowed,
    'Access-Control-Allow-Headers': 'Content-Type',
  });
  res.end(JSON.stringify({ error: 'Method Not Allowed' }));
}

function parseURL(req) {
  return new URL(req.url, `http://${req.headers.host || 'localhost'}`);
}

function getTicketId(pathname) {
  const match = pathname.match(/^\/tickets\/(\d+)$/);
  return match ? parseInt(match[1], 10) : null;
}

function getBody(req) {
  return new Promise((resolve, reject) => {
    let raw = '';
    req.on('data', chunk => raw += chunk);
    req.on('end', () => {
      if (raw.length === 0) return resolve({});
      try {
        resolve(JSON.parse(raw));
      } catch (e) {
        reject(new Error('Invalid JSON'));
      }
    });
    req.on('error', reject);
  });
}

function nowISO() {
  return new Date().toISOString();
}

// Validation
function validateCreate(body) {
  const errors = [];
  if (!body.subject || typeof body.subject !== 'string' || body.subject.trim() === '') {
    errors.push('subject is required and must be a non-empty string');
  }
  if (!body.description || typeof body.description !== 'string' || body.description.trim() === '') {
    errors.push('description is required and must be a non-empty string');
  }
  if (body.priority !== undefined && !['low', 'medium', 'high'].includes(body.priority)) {
    errors.push('priority must be one of: low, medium, high');
  }
  if (body.status !== undefined && !['open', 'in_progress', 'resolved'].includes(body.status)) {
    errors.push('status must be one of: open, in_progress, resolved');
  }
  return errors;
}

function validateUpdate(body) {
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

// ----------------------------------------------------------------------
// Route handlers
// ----------------------------------------------------------------------
async function handleGetTickets(req, res) {
  const urlObj = parseURL(req);
  const statusFilter = urlObj.searchParams.get('status');
  const priorityFilter = urlObj.searchParams.get('priority');

  let result = tickets;
  if (statusFilter) {
    if (!['open', 'in_progress', 'resolved'].includes(statusFilter)) {
      return sendError(res, 400, 'Invalid status filter');
    }
    result = result.filter(t => t.status === statusFilter);
  }
  if (priorityFilter) {
    if (!['low', 'medium', 'high'].includes(priorityFilter)) {
      return sendError(res, 400, 'Invalid priority filter');
    }
    result = result.filter(t => t.priority === priorityFilter);
  }
  sendJSON(res, 200, result);
}

async function handlePostTickets(req, res) {
  let body;
  try {
    body = await getBody(req);
  } catch (e) {
    return sendError(res, 400, 'Invalid JSON in request body');
  }

  const errors = validateCreate(body);
  if (errors.length) {
    return sendJSON(res, 400, { errors });
  }

  const ticket = {
    id: nextId++,
    subject: body.subject.trim(),
    description: body.description.trim(),
    priority: body.priority || 'low',
    status: 'open',
    created_at: nowISO(),
    updated_at: nowISO(),
  };
  tickets.push(ticket);

  try {
    await saveTickets();
  } catch (_) {
    return sendError(res, 500, 'Failed to save ticket');
  }
  sendJSON(res, 201, ticket);
}

async function handleGetTicket(req, res, id) {
  const ticket = tickets.find(t => t.id === id);
  if (!ticket) {
    return sendError(res, 404, 'Ticket not found');
  }
  sendJSON(res, 200, ticket);
}

async function handlePatchTicket(req, res, id) {
  const ticket = tickets.find(t => t.id === id);
  if (!ticket) {
    return sendError(res, 404, 'Ticket not found');
  }

  let body;
  try {
    body = await getBody(req);
  } catch (e) {
    return sendError(res, 400, 'Invalid JSON in request body');
  }

  const errors = validateUpdate(body);
  if (errors.length) {
    return sendJSON(res, 400, { errors });
  }

  if (body.subject !== undefined) ticket.subject = body.subject.trim();
  if (body.description !== undefined) ticket.description = body.description.trim();
  if (body.priority !== undefined) ticket.priority = body.priority;
  if (body.status !== undefined) ticket.status = body.status;
  ticket.updated_at = nowISO();

  try {
    await saveTickets();
  } catch (_) {
    return sendError(res, 500, 'Failed to save ticket');
  }
  sendJSON(res, 200, ticket);
}

async function handleDeleteTicket(req, res, id) {
  const index = tickets.findIndex(t => t.id === id);
  if (index === -1) {
    return sendError(res, 404, 'Ticket not found');
  }
  tickets.splice(index, 1);

  try {
    await saveTickets();
  } catch (_) {
    return sendError(res, 500, 'Failed to save ticket');
  }

  res.writeHead(204, {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
  });
  res.end();
}

function handleMetrics(req, res) {
  const statusCounts = { open: 0, in_progress: 0, resolved: 0 };
  const priorityCounts = { low: 0, medium: 0, high: 0 };
  let ageSum = 0;
  let openCount = 0;
  const now = Date.now();

  for (const t of tickets) {
    if (statusCounts.hasOwnProperty(t.status)) statusCounts[t.status]++;
    if (priorityCounts.hasOwnProperty(t.priority)) priorityCounts[t.priority]++;

    if (t.status === 'open') {
      const created = new Date(t.created_at).getTime();
      if (!isNaN(created)) {
        ageSum += (now - created) / 1000;
        openCount++;
      }
    }
  }

  sendJSON(res, 200, {
    statusCounts,
    priorityCounts,
    averageAgeOfOpenTicketsSeconds: openCount > 0 ? ageSum / openCount : 0,
  });
}

// ----------------------------------------------------------------------
// Create HTTP server
// ----------------------------------------------------------------------
const server = http.createServer(async (req, res) => {
  // Preflight handling
  if (req.method === 'OPTIONS') {
    res.writeHead(204, {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    });
    return res.end();
  }

  try {
    const urlObj = parseURL(req);
    const pathname = urlObj.pathname;
    const method = req.method;

    if (pathname === '/tickets') {
      if (method === 'GET') await handleGetTickets(req, res);
      else if (method === 'POST') await handlePostTickets(req, res);
      else methodNotAllowed(res, 'GET, POST');
    } else if (pathname === '/metrics') {
      if (method === 'GET') handleMetrics(req, res);
      else methodNotAllowed(res, 'GET');
    } else {
      const id = getTicketId(pathname);
      if (id !== null) {
        if (method === 'GET') await handleGetTicket(req, res, id);
        else if (method === 'PATCH') await handlePatchTicket(req, res, id);
        else if (method === 'DELETE') await handleDeleteTicket(req, res, id);
        else methodNotAllowed(res, 'GET, PATCH, DELETE');
      } else if (pathname.startsWith('/tickets/')) {
        sendError(res, 400, 'Invalid ticket ID format');
      } else {
        sendError(res, 404, 'Not Found');
      }
    }
  } catch (err) {
    console.error('Unhandled error:', err);
    if (!res.headersSent) {
      sendError(res, 500, 'Internal Server Error');
    }
  }
});

server.listen(PORT, HOST, () => {
  console.log(`Help Desk API listening on http://${HOST}:${PORT}`);
});
