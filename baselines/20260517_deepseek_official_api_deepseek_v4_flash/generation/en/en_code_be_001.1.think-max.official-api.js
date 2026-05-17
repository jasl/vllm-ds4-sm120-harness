```javascript
const http = require('http');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const PORT = process.env.PORT || 8080;
const HOST = '127.0.0.1';
const DATA_FILE = path.join(__dirname, 'tickets.json');

// In-memory store
let tickets = [];

// Simple promise chain mutex for file writes
let fileOperation = Promise.resolve();

function withFileLock(fn) {
  const result = fileOperation.then(fn, fn);
  // Ensure the chain continues even if fn fails
  fileOperation = result.catch(() => {});
  return result;
}

// Load tickets from file (called once on startup)
function loadTickets() {
  try {
    const data = fs.readFileSync(DATA_FILE, 'utf8');
    tickets = JSON.parse(data);
  } catch (err) {
    // If file doesn't exist or is invalid, start with empty array
    tickets = [];
  }
}

// Save tickets to file (mutex ensures sequential writes)
function saveTickets() {
  return withFileLock(() => {
    return new Promise((resolve, reject) => {
      const data = JSON.stringify(tickets, null, 2);
      fs.writeFile(DATA_FILE, data, 'utf8', (err) => {
        if (err) reject(err);
        else resolve();
      });
    });
  });
}

// Generate a unique ID
function generateId() {
  return crypto.randomUUID();
}

// Validate ticket data for creation
function validateCreateTicket(body) {
  const errors = [];
  if (!body.subject || typeof body.subject !== 'string') {
    errors.push('subject is required and must be a string');
  }
  if (!body.description || typeof body.description !== 'string') {
    errors.push('description is required and must be a string');
  }
  if (!body.priority || !['low', 'medium', 'high'].includes(body.priority)) {
    errors.push('priority is required and must be one of: low, medium, high');
  }
  if (body.status !== undefined && !['open', 'in_progress', 'resolved'].includes(body.status)) {
    errors.push('status must be one of: open, in_progress, resolved');
  }
  return errors;
}

// Validate update fields
function validateUpdateTicket(body) {
  const allowedFields = ['subject', 'description', 'priority', 'status'];
  const errors = [];
  for (const key of Object.keys(body)) {
    if (!allowedFields.includes(key)) {
      errors.push(`Field '${key}' is not allowed for update`);
    }
  }
  if (body.subject !== undefined && typeof body.subject !== 'string') {
    errors.push('subject must be a string');
  }
  if (body.description !== undefined && typeof body.description !== 'string') {
    errors.push('description must be a string');
  }
  if (body.priority !== undefined && !['low', 'medium', 'high'].includes(body.priority)) {
    errors.push('priority must be one of: low, medium, high');
  }
  if (body.status !== undefined && !['open', 'in_progress', 'resolved'].includes(body.status)) {
    errors.push('status must be one of: open, in_progress, resolved');
  }
  return errors;
}

// Collect request body
function getBody(req) {
  return new Promise((resolve, reject) => {
    let data = '';
    req.on('data', chunk => {
      data += chunk;
    });
    req.on('end', () => {
      try {
        resolve(data ? JSON.parse(data) : {});
      } catch (e) {
        reject(new Error('Invalid JSON'));
      }
    });
    req.on('error', reject);
  });
}

// Send JSON response
function sendJSON(res, statusCode, data) {
  res.writeHead(statusCode, {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization'
  });
  res.end(JSON.stringify(data));
}

// Route matching
function matchRoute(method, pathname) {
  const parts = pathname.split('/').filter(Boolean);
  // /tickets
  if (parts.length === 1 && parts[0] === 'tickets') {
    if (method === 'GET') return { handler: 'listTickets' };
    if (method === 'POST') return { handler: 'createTicket' };
    return { handler: null, methodNotAllowed: true };
  }
  // /tickets/:id
  if (parts.length === 2 && parts[0] === 'tickets') {
    if (method === 'GET') return { handler: 'getTicket', params: { id: parts[1] } };
    if (method === 'PATCH') return { handler: 'updateTicket', params: { id: parts[1] } };
    if (method === 'DELETE') return { handler: 'deleteTicket', params: { id: parts[1] } };
    return { handler: null, methodNotAllowed: true };
  }
  // /metrics
  if (parts.length === 1 && parts[0] === 'metrics') {
    if (method === 'GET') return { handler: 'getMetrics' };
    return { handler: null, methodNotAllowed: true };
  }
  // unknown route
  return { handler: null, methodNotAllowed: false };
}

// Handlers
async function listTickets(req, res, query) {
  let result = tickets;
  if (query.status) {
    result = result.filter(t => t.status === query.status);
  }
  if (query.priority) {
    result = result.filter(t => t.priority === query.priority);
  }
  sendJSON(res, 200, result);
}

async function createTicket(req, res) {
  let body;
  try {
    body = await getBody(req);
  } catch (e) {
    return sendJSON(res, 400, { error: 'Invalid JSON' });
  }
  const errors = validateCreateTicket(body);
  if (errors.length > 0) {
    return sendJSON(res, 400, { error: 'Validation failed', details: errors });
  }
  const now = new Date().toISOString();
  const ticket = {
    id: generateId(),
    subject: body.subject,
    description: body.description,
    priority: body.priority,
    status: body.status || 'open',
    created_at: now,
    updated_at: now
  };
  tickets.push(ticket);
  try {
    await saveTickets();
    sendJSON(res, 201, ticket);
  } catch (err) {
    // Rollback
    tickets.pop();
    sendJSON(res, 500, { error: 'Failed to save ticket' });
  }
}

async function getTicket(req, res, params) {
  const ticket = tickets.find(t => t.id === params.id);
  if (!ticket) {
    return send
