#!/usr/bin/env node
'use strict';

const http = require('http');
const fs = require('fs');
const path = require('path');

// --- Configuration ---
const PORT = process.env.PORT || 8080;
const HOST = process.env.HOST || '127.0.0.1';
const DATA_FILE = path.join(__dirname, 'tickets.json');

// --- In-memory data ---
let tickets = [];

// --- File write queue (serialises modifications) ---
let opQueue = Promise.resolve();

/**
 * Enqueue a mutation operation to ensure sequential file writes.
 * @param {Function} fn - async function that performs the mutation.
 * @returns {Promise} resolves when the operation completes.
 */
function enqueueMutation(fn) {
  const prev = opQueue;
  let resolve;
  opQueue = new Promise(r => { resolve = r; });
  return prev.then(() => fn()).finally(resolve);
}

// --- Persistence helpers ---
async function loadTickets() {
  try {
    const raw = await fs.promises.readFile(DATA_FILE, 'utf8');
    tickets = JSON.parse(raw);
    if (!Array.isArray(tickets)) tickets = [];
  } catch (err) {
    if (err.code === 'ENOENT') {
      tickets = [];
    } else {
      console.error('Failed to load tickets.json:', err.message);
      tickets = [];
    }
  }
}

async function saveTickets() {
  await fs.promises.writeFile(
    DATA_FILE,
    JSON.stringify(tickets, null, 2),
    'utf8'
  );
}

// --- ID generation ---
function nextId() {
  if (tickets.length === 0) return 1;
  const maxId = Math.max(...tickets.map(t => t.id));
  return maxId + 1;
}

// --- Validation helpers ---
const VALID_PRIORITIES = ['low', 'medium', 'high'];
const VALID_STATUSES = ['open', 'in_progress', 'resolved'];

function isValidPriority(p) {
  return VALID_PRIORITIES.includes(p);
}
function isValidStatus(s) {
  return VALID_STATUSES.includes(s);
}

/**
 * Validate fields for creation. Returns an array of error messages (empty if valid).
 */
function validateCreate(body) {
  const errors = [];
  if (!body.subject || typeof body.subject !== 'string' || body.subject.trim() === '') {
    errors.push('subject is required and must be a non-empty string');
  }
  if (!body.description || typeof body.description !== 'string' || body.description.trim() === '') {
    errors.push('description is required and must be a non-empty string');
  }
  if (body.priority !== undefined && !isValidPriority(body.priority)) {
    errors.push(`priority must be one of: ${VALID_PRIORITIES.join(', ')}`);
  }
  if (body.status !== undefined && !isValidStatus(body.status)) {
    errors.push(`status must be one of: ${VALID_STATUSES.join(', ')}`);
  }
  return errors;
}

/**
 * Validate fields for update. Returns an array of error messages (empty if valid).
 */
function validateUpdate(body) {
  const errors = [];
  if (body.subject !== undefined && (typeof body.subject !== 'string' || body.subject.trim() === '')) {
    errors.push('if provided, subject must be a non-empty string');
  }
  if (body.description !== undefined && (typeof body.description !== 'string' || body.description.trim() === '')) {
    errors.push('if provided, description must be a non-empty string');
  }
  if (body.priority !== undefined && !isValidPriority(body.priority)) {
    errors.push(`priority must be one of: ${VALID_PRIORITIES.join(', ')}`);
  }
  if (body.status !== undefined && !isValidStatus(body.status)) {
    errors.push(`status must be one of: ${VALID_STATUSES.join(', ')}`);
  }
  return errors;
}

// --- HTTP helpers ---
function sendJson(res, statusCode, data) {
  res.writeHead(statusCode, {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
  });
  res.end(JSON.stringify(data));
}

function sendError(res, statusCode, message) {
  sendJson(res, statusCode, { error: message });
}

/**
 * Parse the request body as JSON. Returns parsed object or throws.
 */
function parseBody(req) {
  return new Promise((resolve, reject) => {
    let body = '';
    req.on('data', chunk => { body += chunk; });
    req.on('end', () => {
      if (!body) {
        return reject(new Error('Request body is empty'));
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

/**
 * Extract and parse the ID from the URL path /tickets/:id
 * Returns the numeric ID or null if not present or invalid.
 */
function extractId(pathname) {
  const match = pathname.match(/^\/tickets\/(\d+)$/);
  return match ? parseInt(match[1], 10) : null;
}

/**
 * Return a copy of tickets filtered by query params (status, priority)
 */
function filterTickets(query) {
  let result = tickets;
  const status = query.get('status');
  const priority = query.get('priority');
  if (status && isValidStatus(status)) {
    result = result.filter(t => t.status === status);
  }
  if (priority && isValidPriority(priority)) {
    result = result.filter(t => t.priority === priority);
  }
  return result;
}

/**
 * Compute metrics: counts by status, by priority, and average age of open tickets in seconds.
 */
function computeMetrics() {
  const now = Date.now();
  const statusCounts = {};
  const priorityCounts = {};
  let openAgeSum = 0;
  let openCount = 0;

  for (const ticket of tickets) {
    // status counts
    statusCounts[ticket.status] = (statusCounts[ticket.status] || 0) + 1;

    // priority counts
    priorityCounts[ticket.priority] = (priorityCounts[ticket.priority] || 0) + 1;

    // average age for open tickets
    if (ticket.status === 'open') {
      const createdAt = new Date(ticket.created_at).getTime();
      if (!isNaN(createdAt)) {
        openAgeSum += (now - createdAt) / 1000;
        openCount++;
      }
    }
  }

  return {
    statusCounts,
    priorityCounts,
    averageOpenAgeSeconds: openCount > 0 ? openAgeSum / openCount : 0,
  };
}

// --- Request handler ---
async function handleRequest(req, res) {
  // Handle CORS preflight
  if (req.method === 'OPTIONS') {
    res.writeHead(204, {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    });
    return res.end();
  }

  const parsedUrl = new URL(req.url, `http://${req.headers.host || 'localhost'}`);
  const pathname = parsedUrl.pathname;
  const query = parsedUrl.searchParams;

  // --- Routes ---
  try {
    // GET /tickets
    if (pathname === '/tickets' && req.method === 'GET') {
      const filtered = filterTickets(query);
      return sendJson(res, 200, filtered);
    }

    // POST /tickets
    if (pathname === '/tickets' && req.method === 'POST') {
      const body = await parseBody(req);
      const errors = validateCreate(body);
      if (errors.length > 0) {
        return sendError(res, 400, errors.join('; '));
      }

      const ticket = {
        id: nextId(),
        subject: body.subject.trim(),
        description: body.description.trim(),
        priority: body.priority && isValidPriority(body.priority) ? body.priority : 'low',
        status: body.status && isValidStatus(body.status) ? body.status : 'open',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };

      await enqueueMutation(async () => {
        tickets.push(ticket);
        await saveTickets();
      });

      return sendJson(res, 201, ticket);
    }

    // GET /tickets/:id
    const id = extractId(pathname);
    if (pathname.startsWith('/tickets/') && id !== null) {
      const ticket = tickets.find(t => t.id === id);
      if (!ticket) {
        return sendError(res, 404, `Ticket with id ${id} not found`);
      }

      if (req.method === 'GET') {
        return sendJson(res, 200, ticket);
      }

      if (req.method === 'PATCH') {
        const body = await parseBody(req);
        const errors = validateUpdate(body);
        if (errors.length > 0) {
          return sendError(res, 400, errors.join('; '));
        }

        await enqueueMutation(async () => {
          const idx = tickets.findIndex(t => t.id === id);
          if (idx === -1) return; // already handled, but for safety
          const updated = { ...tickets[idx] };
          if (body.subject !== undefined) updated.subject = body.subject.trim();
          if (body.description !== undefined) updated.description = body.description.trim();
          if (body.priority !== undefined) updated.priority = body.priority;
          if (body.status !== undefined) updated.status = body.status;
          updated.updated_at = new Date().toISOString();
          tickets[idx] = updated;
          await saveTickets();
        });

        const updatedTicket = tickets.find(t => t.id === id);
        return sendJson(res, 200, updatedTicket);
      }

      if (req.method === 'DELETE') {
        await enqueueMutation(async () => {
          const idx = tickets.findIndex(t => t.id === id);
          if (idx === -1) return;
          tickets.splice(idx, 1);
          await saveTickets();
        });

        return sendJson(res, 200, { message: `Ticket ${id} deleted` });
      }

      // Method not allowed for this path
      return sendError(res, 405, `Method ${req.method} not allowed on /tickets/${id}`);
    }

    // GET /metrics
    if (pathname === '/metrics' && req.method === 'GET') {
      const metrics = computeMetrics();
      return sendJson(res, 200, metrics);
    }

    // Unknown route
    return sendError(res, 404, `Route ${req.method} ${pathname} not found`);

  } catch (err) {
    if (err.message === 'Invalid JSON' || err.message === 'Request body is empty') {
      return sendError(res, 400, err.message);
    }
    console.error('Unhandled error:', err);
    return sendError(res, 500, 'Internal server error');
  }
}

// --- Server startup ---
async function start() {
  await loadTickets();
  const server = http.createServer(handleRequest);
  server.listen(PORT, HOST, () => {
    console.log(`Server listening on http://${HOST}:${PORT}`);
  });
}

start().catch(err => {
  console.error('Failed to start server:', err);
  process.exit(1);
});
