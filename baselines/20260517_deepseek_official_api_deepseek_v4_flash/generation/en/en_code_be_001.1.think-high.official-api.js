const http = require('http');
const fs = require('fs');
const path = require('path');
const url = require('url');

const DATA_FILE = path.join(__dirname, 'tickets.json');
const DEFAULT_PORT = 8080;
const HOST = '127.0.0.1';

// ---------- File lock for sequential access ----------
let fileLock = Promise.resolve();

function withFileLock(fn) {
  return fileLock = fileLock.then(fn);
}

// ---------- File I/O helpers ----------
function readTickets() {
  return new Promise((resolve, reject) => {
    fs.readFile(DATA_FILE, 'utf8', (err, data) => {
      if (err) {
        if (err.code === 'ENOENT') {
          // File does not exist, return empty array
          resolve([]);
        } else {
          reject(err);
        }
      } else {
        try {
          const tickets = JSON.parse(data);
          if (!Array.isArray(tickets)) {
            reject(new Error('Invalid tickets file format'));
          } else {
            resolve(tickets);
          }
        } catch (parseError) {
          reject(parseError);
        }
      }
    });
  });
}

function writeTickets(tickets) {
  return new Promise((resolve, reject) => {
    const json = JSON.stringify(tickets, null, 2);
    fs.writeFile(DATA_FILE, json, 'utf8', (err) => {
      if (err) reject(err);
      else resolve();
    });
  });
}

// ---------- Validation helpers ----------
const VALID_PRIORITIES = ['low', 'medium', 'high'];
const VALID_STATUSES = ['open', 'in_progress', 'resolved'];

function validateTicket(body, requireFields = true) {
  const errors = [];
  if (requireFields) {
    if (!body.subject || typeof body.subject !== 'string') errors.push('subject is required and must be a string');
    if (!body.description || typeof body.description !== 'string') errors.push('description is required and must be a string');
  } else {
    if (body.subject !== undefined && typeof body.subject !== 'string') errors.push('subject must be a string');
    if (body.description !== undefined && typeof body.description !== 'string') errors.push('description must be a string');
  }

  if (body.priority !== undefined && !VALID_PRIORITIES.includes(body.priority)) {
    errors.push(`priority must be one of: ${VALID_PRIORITIES.join(', ')}`);
  }
  if (body.status !== undefined && !VALID_STATUSES.includes(body.status)) {
    errors.push(`status must be one of: ${VALID_STATUSES.join(', ')}`);
  }
  return errors;
}

function getMaxId(tickets) {
  if (tickets.length === 0) return 0;
  return Math.max(...tickets.map(t => t.id));
}

// ---------- Route handlers ----------
async function handleTickets(req, res, parsedUrl) {
  const method = req.method.toUpperCase();
  const query = parsedUrl.query || {};

  if (method === 'GET') {
    // GET /tickets with optional filters
    const tickets = await withFileLock(async () => {
      return await readTickets();
    });
    const { status, priority } = query;
    let filtered = tickets;
    if (status) {
      if (VALID_STATUSES.includes(status)) {
        filtered = filtered.filter(t => t.status === status);
      } else {
        sendJSON(res, 400, { error: `Invalid status filter. Valid: ${VALID_STATUSES.join(', ')}` });
        return;
      }
    }
    if (priority) {
      if (VALID_PRIORITIES.includes(priority)) {
        filtered = filtered.filter(t => t.priority === priority);
      } else {
        sendJSON(res, 400, { error: `Invalid priority filter. Valid: ${VALID_PRIORITIES.join(', ')}` });
        return;
      }
    }
    sendJSON(res, 200, filtered);
  } else if (method === 'POST') {
    // POST /tickets
    const body = await getRequestBody(req);
    const errors = validateTicket(body, true);
    if (errors.length > 0) {
      sendJSON(res, 400, { error: errors.join('; ') });
      return;
    }

    const result = await withFileLock(async () => {
      const tickets = await readTickets();
      const newId = getMaxId(tickets) + 1;
      const now = new Date().toISOString();
      const ticket = {
        id: newId,
        subject: body.subject,
        description: body.description,
        priority: body.priority || 'low',
        status: body.status || 'open',
        created_at: now,
        updated_at: now
      };
      // Ensure status and priority are valid (already validated but default)
      if (!VALID_PRIORITIES.includes(ticket.priority)) ticket.priority = 'low';
      if (!VALID_STATUSES.includes(ticket.status)) ticket.status = 'open';
      tickets.push(ticket);
      await writeTickets(tickets);
      return ticket;
    });
    sendJSON(res, 201, result);
  } else {
    sendJSON(res, 405, { error: 'Method not allowed' });
  }
}

async function handleTicketById(req, res, id) {
  const method = req.method.toUpperCase();
  if (!id || isNaN(parseInt(id))) {
    sendJSON(res, 400, { error: 'Invalid ticket ID' });
    return;
  }
  const ticketId = parseInt(id);

  if (method === 'GET') {
    const tickets = await withFileLock(async () => {
      return await readTickets();
    });
    const ticket = tickets.find(t => t.id === ticketId);
    if (!ticket) {
      sendJSON(res, 404, { error: 'Ticket not found' });
      return;
    }
    sendJSON(res, 200, ticket);
  } else if (method === 'PATCH') {
    const body = await getRequestBody(req);
    const errors = validateTicket(body, false);
    if (errors.length > 0) {
      sendJSON(res, 400, { error: errors.join('; ') });
      return;
    }

    const result = await withFileLock(async () => {
      const tickets = await readTickets();
      const index = tickets.findIndex(t => t.id === ticketId);
      if (index === -1) {
        return null;
      }
      const ticket = tickets[index];
      // Update only provided fields
      if (body.subject !== undefined) ticket.subject = body.subject;
      if (body.description !== undefined) ticket.description = body.description;
      if (body.priority !== undefined) ticket.priority = body.priority;
      if (body.status !== undefined) ticket.status = body.status;
      ticket.updated_at = new Date().toISOString();
      tickets[index] = ticket;
      await writeTickets(tickets);
      return ticket;
    });
    if (result === null) {
      sendJSON(res, 404, { error: 'Ticket not found' });
    } else {
      sendJSON(res, 200, result);
    }
  } else if (method === 'DELETE') {
    const result = await withFileLock(async () => {
      const tickets = await readTickets();
      const index = tickets.findIndex(t => t.id === ticketId);
      if (index === -1) {
        return false;
      }
      tickets.splice(index, 1);
      await writeTickets(tickets);
      return true;
    });
    if (result) {
      sendJSON(res, 200, { message: 'Ticket deleted' });
    } else {
      sendJSON(res, 404, { error: 'Ticket not found' });
    }
  } else {
    sendJSON(res, 405, { error: 'Method not allowed' });
  }
}

async function handleMetrics(req, res) {
  const tickets = await withFileLock(async () => {
    return await readTickets();
  });

  // Counts by status
  const statusCounts = { open: 0, in_progress: 0, resolved: 0 };
  // Counts by priority
  const priorityCounts = { low: 0, medium: 0, high: 0 };
  let openAgeSum = 0;
  let openCount = 0;
  const now = new Date();

  for (const ticket of tickets) {
    // Status counts
    if (statusCounts.hasOwnProperty(ticket.status)) {
      statusCounts[ticket.status]++;
    }
    // Priority counts
    if (priorityCounts.hasOwnProperty(ticket.priority)) {
      priorityCounts[ticket.priority]++;
    }
    // Average age for open tickets
    if (ticket.status === 'open') {
      const createdAt = new Date(ticket.created_at);
      if (!isNaN(createdAt.getTime())) {
        const ageSeconds = (now - createdAt) / 1000;
        openAgeSum += ageSeconds;
        openCount++;
      }
    }
  }

  const averageAgeOpen = openCount > 0 ? (openAgeSum / openCount) : 0;

  const metrics = {
    status_counts: statusCounts,
    priority_counts: priorityCounts,
    average_age_open_seconds: averageAgeOpen
  };

  sendJSON(res, 200, metrics);
}

// ---------- Utility functions ----------
function sendJSON(res, statusCode, data) {
  const body = JSON.stringify(data) + '\n';
  res.writeHead(statusCode, {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type'
  });
  res.end(body);
}

function getRequestBody(req) {
  return new Promise((resolve, reject) => {
    let body = '';
    req.on('data', chunk => { body += chunk; });
    req.on('end', () => {
      if (!body) {
        resolve({});
        return;
      }
      try {
        const parsed = JSON.parse(body);
        resolve(parsed);
      } catch (e) {
        reject(new Error('Invalid JSON'));
      }
    });
    req.on('error', reject);
  });
}

// ---------- Request router ----------
async function onRequest(req, res) {
  // Handle CORS preflight
  if (req.method.toUpperCase() === 'OPTIONS') {
    sendJSON(res, 204, {});
    return;
  }

  const parsedUrl = url.parse(req.url, true);
  const pathname = parsedUrl.pathname.replace(/\/+$/, '') || '/';

  try {
    if (pathname === '/tickets') {
      await handleTickets(req, res, parsedUrl);
    } else if (pathname.startsWith('/tickets/')) {
      const id = pathname.split('/')[2];
      await handleTicketById(req, res, id);
    } else if (pathname === '/metrics') {
      if (req.method.toUpperCase() !== 'GET') {
        sendJSON(res, 405, { error: 'Method not allowed' });
        return;
      }
      await handleMetrics(req, res);
    } else {
      sendJSON(res, 404, { error: 'Not found' });
    }
  } catch (err) {
    if (err.message === 'Invalid JSON') {
      sendJSON(res, 400, { error: 'Invalid JSON in request body' });
    } else {
      console.error('Server error:', err);
      sendJSON(res, 500, { error: 'Internal server error' });
    }
  }
}

// ---------- Server start ----------
const server = http.createServer(onRequest);
const port = parseInt(process.argv[2], 10) || DEFAULT_PORT;
server.listen(port, HOST, () => {
  console.log(`Server running at http://${HOST}:${port}/`);
});
