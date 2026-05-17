#!/usr/bin/env node

const http = require('http');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const PORT = 8080;
const HOST = '127.0.0.1';
const DATA_FILE = path.join(process.cwd(), 'tickets.json');

// Simple sequential queue for file operations
class FileQueue {
  constructor(filePath) {
    this.filePath = filePath;
    this.queue = Promise.resolve();
    this.ensureFile();
  }

  ensureFile() {
    if (!fs.existsSync(this.filePath)) {
      fs.writeFileSync(this.filePath, JSON.stringify([]), 'utf8');
    }
  }

  read() {
    return this.enqueue(() => {
      return new Promise((resolve, reject) => {
        fs.readFile(this.filePath, 'utf8', (err, data) => {
          if (err) return reject(err);
          try {
            resolve(JSON.parse(data));
          } catch (e) {
            reject(e);
          }
        });
      });
    });
  }

  write(data) {
    return this.enqueue(() => {
      return new Promise((resolve, reject) => {
        const json = JSON.stringify(data, null, 2);
        fs.writeFile(this.filePath, json, 'utf8', (err) => {
          if (err) return reject(err);
          resolve();
        });
      });
    });
  }

  enqueue(task) {
    this.queue = this.queue.then(task, task);
    return this.queue;
  }
}

const store = new FileQueue(DATA_FILE);

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

function validateTicket(body, strict = true) {
  const errors = [];
  const required = ['subject', 'description', 'priority', 'status'];
  if (strict) {
    for (const field of required) {
      if (!body[field] || typeof body[field] !== 'string') {
        errors.push(`${field} is required and must be a string`);
      }
    }
  }
  const allowedPriority = ['low', 'medium', 'high'];
  if (body.priority && !allowedPriority.includes(body.priority)) {
    errors.push(`priority must be one of ${allowedPriority.join(', ')}`);
  }
  const allowedStatus = ['open', 'in_progress', 'resolved'];
  if (body.status && !allowedStatus.includes(body.status)) {
    errors.push(`status must be one of ${allowedStatus.join(', ')}`);
  }
  return errors.length ? errors : null;
}

function createTicket(body) {
  return {
    id: crypto.randomUUID(),
    subject: body.subject,
    description: body.description,
    priority: body.priority,
    status: body.status,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  };
}

// Route handlers
async function handleGetTickets(req, res, query) {
  try {
    const tickets = await store.read();
    let filtered = tickets;
    if (query.status) {
      filtered = filtered.filter(t => t.status === query.status);
    }
    if (query.priority) {
      filtered = filtered.filter(t => t.priority === query.priority);
    }
    sendJSON(res, 200, filtered);
  } catch (err) {
    sendJSON(res, 500, { error: 'Internal server error' });
  }
}

async function handlePostTicket(req, res) {
  let body;
  try {
    body = await parseBody(req);
  } catch (e) {
    return sendJSON(res, 400, { error: e.message });
  }
  const errors = validateTicket(body, true);
  if (errors) {
    return sendJSON(res, 400, { error: 'Validation failed', details: errors });
  }
  const ticket = createTicket(body);
  try {
    const tickets = await store.read();
    tickets.push(ticket);
    await store.write(tickets);
    sendJSON(res, 201, ticket);
  } catch (err) {
    sendJSON(res, 500, { error: 'Internal server error' });
  }
}

async function handleGetTicket(req, res, id) {
  try {
    const tickets = await store.read();
    const ticket = tickets.find(t => t.id === id);
    if (!ticket) {
      return sendJSON(res, 404, { error: 'Ticket not found' });
    }
    sendJSON(res, 200, ticket);
  } catch (err) {
    sendJSON(res, 500, { error: 'Internal server error' });
  }
}

async function handlePatchTicket(req, res, id) {
  let body;
  try {
    body = await parseBody(req);
  } catch (e) {
    return sendJSON(res, 400, { error: e.message });
  }
  // Validate only provided fields
  const errors = validateTicket(body, false);
  if (errors) {
    return sendJSON(res, 400, { error: 'Validation failed', details: errors });
  }
  try {
    const tickets = await store.read();
    const index = tickets.findIndex(t => t.id === id);
    if (index === -1) {
      return sendJSON(res, 404, { error: 'Ticket not found' });
    }
    const ticket = tickets[index];
    const allowedFields = ['subject', 'description', 'priority', 'status'];
    for (const field of allowedFields) {
      if (body[field] !== undefined) {
        ticket[field] = body[field];
      }
    }
    ticket.updated_at = new Date().toISOString();
    tickets[index] = ticket;
    await store.write(tickets);
    sendJSON(res, 200, ticket);
  } catch (err) {
    sendJSON(res, 500, { error: 'Internal server error' });
  }
}

async function handleDeleteTicket(req, res, id) {
  try {
    const tickets = await store.read();
    const index = tickets.findIndex(t => t.id === id);
    if (index === -1) {
      return sendJSON(res, 404, { error: 'Ticket not found' });
    }
    tickets.splice(index, 1);
    await store.write(tickets);
    sendJSON(res, 204, null);
  } catch (err) {
    sendJSON(res, 500, { error: 'Internal server error' });
  }
}

async function handleMetrics(req, res) {
  try {
    const tickets = await store.read();
    const countsByStatus = { open: 0, in_progress: 0, resolved: 0 };
    const countsByPriority = { low: 0, medium: 0, high: 0 };
    let openAgeSum = 0;
    let openCount = 0;
    const now = Date.now();
    for (const t of tickets) {
      // status counts
      if (countsByStatus.hasOwnProperty(t.status)) {
        countsByStatus[t.status]++;
      }
      // priority counts
      if (countsByPriority.hasOwnProperty(t.priority)) {
        countsByPriority[t.priority]++;
      }
      // average age of open tickets
      if (t.status === 'open') {
        const created = new Date(t.created_at).getTime();
        openAgeSum += (now - created) / 1000;
        openCount++;
      }
    }
    const averageAge = openCount > 0 ? openAgeSum / openCount : 0;
    sendJSON(res, 200, {
      by_status: countsByStatus,
      by_priority: countsByPriority,
      average_age_open_seconds: averageAge,
    });
  } catch (err) {
    sendJSON(res, 500, { error: 'Internal server error' });
  }
}

const server = http.createServer(async (req, res) => {
  const { pathname, searchParams } = new URL(req.url, `http://${req.headers.host || HOST}`);
  const method = req.method.toUpperCase();

  // CORS preflight
  if (method === 'OPTIONS') {
    res.writeHead(204, {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    });
    return res.end();
  }

  // Route matching
  if (pathname === '/tickets' && method === 'GET') {
    return handleGetTickets(req, res, Object.fromEntries(searchParams));
  }
  if (pathname === '/tickets' && method === 'POST') {
    return handlePostTicket(req, res);
  }
  const ticketMatch = pathname.match(/^\/tickets\/([a-f0-9-]+)$/);
  if (ticketMatch) {
    const id = ticketMatch[1];
    if (method === 'GET') {
      return handleGetTicket(req, res, id);
    }
    if (method === 'PATCH') {
      return handlePatchTicket(req, res, id);
    }
    if (method === 'DELETE') {
      return handleDeleteTicket(req, res, id);
    }
    // Method not allowed for this resource
    return sendJSON(res, 405, { error: 'Method not allowed' });
  }
  if (pathname === '/metrics' && method === 'GET') {
    return handleMetrics(req, res);
  }
  // Unknown route
  sendJSON(res, 404, { error: 'Not found' });
});

server.listen(PORT, HOST, () => {
  console.log(`Server running at http://${HOST}:${PORT}/`);
});
