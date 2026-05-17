#!/usr/bin/env node

const http = require('http');
const fs = require('fs').promises;
const path = require('path');
const crypto = require('crypto');
const url = require('url');

const PORT = process.env.PORT || 8080;
const HOST = '127.0.0.1';
const DATA_FILE = path.join(__dirname, 'tickets.json');

/* Simple mutex for serialising write operations */
class Mutex {
  constructor() {
    this._lock = Promise.resolve();
  }

  exec(fn) {
    let releaseNext;
    const nextPromise = new Promise(resolve => { releaseNext = resolve; });
    const prev = this._lock;
    this._lock = prev.then(() => nextPromise);
    return prev.then(async () => {
      try {
        return await fn();
      } finally {
        releaseNext();
      }
    });
  }
}

const dataMutex = new Mutex();
let tickets = [];

/* ---------- Initialise data file ---------- */
async function initData() {
  try {
    const raw = await fs.readFile(DATA_FILE, 'utf8');
    tickets = JSON.parse(raw);
    if (!Array.isArray(tickets)) {
      console.warn('tickets.json is not an array – resetting');
      tickets = [];
    }
  } catch (err) {
    if (err.code === 'ENOENT') {
      console.log('Creating empty tickets.json');
      await fs.writeFile(DATA_FILE, '[]', 'utf8');
      tickets = [];
    } else {
      console.error('Failed to load tickets.json:', err);
      process.exit(1);
    }
  }
}

/* ---------- Helpers ---------- */
function sendJSON(res, status, data) {
  const body = JSON.stringify(data);
  res.writeHead(status, {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
  });
  res.end(body);
}

function sendError(res, status, message) {
  sendJSON(res, status, { error: message });
}

function readBody(req) {
  return new Promise((resolve, reject) => {
    let body = '';
    req.on('data', chunk => { body += chunk; });
    req.on('end', () => resolve(body));
    req.on('error', reject);
  });
}

function parsePath(reqUrl) {
  return url.parse(reqUrl).pathname.split('/').filter(Boolean);
}

function parseQuery(reqUrl) {
  return url.parse(reqUrl, true).query;
}

/* ---------- Route handlers ---------- */
async function handleGetTickets(req, res, query) {
  let result = tickets;

  if (query.status) {
    const s = query.status.toLowerCase();
    if (!['open', 'in_progress', 'resolved'].includes(s)) {
      sendError(res, 400, `Invalid status: ${s}`);
      return;
    }
    result = result.filter(t => t.status === s);
  }

  if (query.priority) {
    const p = query.priority.toLowerCase();
    if (!['low', 'medium', 'high'].includes(p)) {
      sendError(res, 400, `Invalid priority: ${p}`);
      return;
    }
    result = result.filter(t => t.priority === p);
  }

  sendJSON(res, 200, result);
}

async function handlePostTicket(req, res) {
  let body;
  try {
    body = JSON.parse(await readBody(req));
  } catch (_) {
    sendError(res, 400, 'Invalid JSON body');
    return;
  }

  // Required fields: subject, description, priority
  for (const field of ['subject', 'description', 'priority']) {
    if (!body[field] || typeof body[field] !== 'string' || body[field].trim() === '') {
      sendError(res, 400, `Missing or invalid required field: ${field}`);
      return;
    }
  }

  const subject = body.subject.trim();
  const description = body.description.trim();

  const priority = body.priority.toLowerCase();
  if (!['low', 'medium', 'high'].includes(priority)) {
    sendError(res, 400, 'Priority must be low, medium, or high');
    return;
  }

  let status = 'open';
  if (body.status !== undefined) {
    if (typeof body.status !== 'string' || body.status.trim() === '') {
      sendError(res, 400, 'Status must be a non-empty string');
      return;
    }
    status = body.status.trim().toLowerCase();
    if (!['open', 'in_progress', 'resolved'].includes(status)) {
      sendError(res, 400, 'Status must be open, in_progress, or resolved');
      return;
    }
  }

  const now = new Date().toISOString();
  const ticket = {
    id: crypto.randomUUID(),
    subject,
    description,
    priority,
    status,
    created_at: now,
    updated_at: now,
  };

  await dataMutex.exec(async () => {
    tickets.push(ticket);
    await fs.writeFile(DATA_FILE, JSON.stringify(tickets, null, 2), 'utf8');
  });

  sendJSON(res, 201, ticket);
}

async function handleGetTicket(req, res, id) {
  const ticket = tickets.find(t => t.id === id);
  if (!ticket) {
    sendError(res, 404, 'Ticket not found');
    return;
  }
  sendJSON(res, 200, ticket);
}

async function handlePatchTicket(req, res, id) {
  let body;
  try {
    body = JSON.parse(await readBody(req));
  } catch (_) {
    sendError(res, 400, 'Invalid JSON body');
    return;
  }

  // Validate supplied fields
  const allowed = ['subject', 'description', 'priority', 'status'];
  const updates = {};
  for (const field of allowed) {
    if (body[field] !== undefined) {
      if (typeof body[field] !== 'string' || body[field].trim() === '') {
        sendError(res, 400, `Invalid value for ${field}`);
        return;
      }
      let val = body[field].trim().toLowerCase();
      if (field === 'priority' && !['low', 'medium', 'high'].includes(val)) {
        sendError(res, 400, 'Priority must be low, medium, or high');
        return;
      }
      if (field === 'status' && !['open', 'in_progress', 'resolved'].includes(val)) {
        sendError(res, 400, 'Status must be open, in_progress, or resolved');
        return;
      }
      updates[field] = val;
    }
  }

  if (Object.keys(updates).length === 0) {
    sendError(res, 400, 'No valid fields provided to update');
    return;
  }

  const updatedTicket = await dataMutex.exec(async () => {
    const idx = tickets.findIndex(t => t.id === id);
    if (idx === -1) return null;

    const ticket = tickets[idx];
    for (const [field, value] of Object.entries(updates)) {
      ticket[field] = value;
    }
    ticket.updated_at = new Date().toISOString();
    tickets[idx] = ticket;

    await fs.writeFile(DATA_FILE, JSON.stringify(tickets, null, 2), 'utf8');
    return { ...ticket };
  });

  if (!updatedTicket) {
    sendError(res, 404, 'Ticket not found');
    return;
  }
  sendJSON(res, 200, updatedTicket);
}

async function handleDeleteTicket(req, res, id) {
  const deleted = await dataMutex.exec(async () => {
    const idx = tickets.findIndex(t => t.id === id);
    if (idx === -1) return false;
    tickets.splice(idx, 1);
    await fs.writeFile(DATA_FILE, JSON.stringify(tickets, null, 2), 'utf8');
    return true;
  });

  if (!deleted) {
    sendError(res, 404, 'Ticket not found');
    return;
  }
  sendJSON(res, 200, { message: 'Ticket deleted' });
}

async function handleGetMetrics(req, res) {
  const byStatus = { open: 0, in_progress: 0, resolved: 0 };
  const byPriority = { low: 0, medium: 0, high: 0 };
  let totalAge = 0;
  let openCount = 0;
  const now = Date.now();

  for (const t of tickets) {
    if (byStatus.hasOwnProperty(t.status)) byStatus[t.status]++;
    if (byPriority.hasOwnProperty(t.priority)) byPriority[t.priority]++;

    if (t.status === 'open') {
      openCount++;
      totalAge += (now - new Date(t.created_at).getTime()) / 1000;
    }
  }

  const averageAgeOfOpenTicketsInSeconds = openCount > 0 ? totalAge / openCount : 0;

  sendJSON(res, 200, { byStatus, byPriority, averageAgeOfOpenTicketsInSeconds });
}

/* ---------- Request dispatcher ---------- */
async function handleRequest(req, res) {
  // CORS preflight
  if (req.method === 'OPTIONS') {
    res.writeHead(204, {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
      'Access-Control-Max-Age': 86400,
    });
    res.end();
    return;
  }

  const segments = parsePath(req.url);
  const query = parseQuery(req.url);
  const method = req.method;

  try {
    if (segments.length === 1 && segments[0] === 'tickets') {
      // /tickets
      if (method === 'GET') await handleGetTickets(req, res, query);
      else if (method === 'POST') await handlePostTicket(req, res);
      else sendError(res, 405, `Method ${method} not allowed on /tickets`);
    } else if (segments.length === 2 && segments[0] === 'tickets') {
      // /tickets/:id
      const id = segments[1];
      if (method === 'GET') await handleGetTicket(req, res, id);
      else if (method === 'PATCH') await handlePatchTicket(req, res, id);
      else if (method === 'DELETE') await handleDeleteTicket(req, res, id);
      else sendError(res, 405, `Method ${method} not allowed on /tickets/${id}`);
    } else if (segments.length === 1 && segments[0] === 'metrics') {
      // /metrics
      if (method === 'GET') await handleGetMetrics(req, res);
      else sendError(res, 405, `Method ${method} not allowed on /metrics`);
    } else {
      sendError(res, 404, 'Not Found');
    }
  } catch (err) {
    console.error('Internal error:', err);
    sendError(res, 500, 'Internal Server Error');
  }
}

/* ---------- Start server ---------- */
async function main() {
  await initData();
  const server = http.createServer(handleRequest);
  server.listen(PORT, HOST, () => {
    console.log(`Ticket server running at http://${HOST}:${PORT}/`);
  });
}

main();
