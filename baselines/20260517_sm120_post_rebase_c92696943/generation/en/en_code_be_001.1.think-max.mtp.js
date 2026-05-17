#!/usr/bin/env node
'use strict';

const http = require('http');
const fs = require('fs').promises;
const path = require('path');
const url = require('url');

const PORT = process.env.PORT || 8080;
const HOST = '127.0.0.1';
const DATA_FILE = path.resolve(__dirname, 'tickets.json');

// In-memory store
let tickets = [];
let nextId = 1;

// ---- File I/O with write serialization ----
let writeQueue = Promise.resolve();

async function loadTickets() {
  try {
    const data = await fs.readFile(DATA_FILE, 'utf8');
    const parsed = JSON.parse(data);
    if (Array.isArray(parsed)) {
      tickets = parsed;
      // Determine the next ID based on existing max id
      const maxId = tickets.reduce((max, t) => Math.max(max, t.id || 0), 0);
      nextId = maxId + 1;
    }
  } catch (err) {
    // File not found or invalid JSON -> start fresh
    tickets = [];
    nextId = 1;
  }
}

function saveTickets() {
  const data = JSON.stringify(tickets, null, 2);
  writeQueue = writeQueue.then(() => fs.writeFile(DATA_FILE, data));
  return writeQueue;
}

// ---- Helpers ----
function sendJSON(res, code, payload) {
  const body = JSON.stringify(payload);
  res.writeHead(code, {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type'
  });
  res.end(body);
}

function sendError(res, code, message) {
  sendJSON(res, code, { error: message });
}

function parseBody(req) {
  return new Promise((resolve, reject) => {
    let raw = '';
    req.on('data', chunk => { raw += chunk; });
    req.on('end', () => {
      if (!raw) return reject(new Error('No body supplied'));
      try {
        resolve(JSON.parse(raw));
      } catch (e) {
        reject(new Error('Invalid JSON'));
      }
    });
    req.on('error', reject);
  });
}

function getTimestamp() {
  return new Date().toISOString();
}

const VALID_STATUSES = ['open', 'in_progress', 'resolved'];
const VALID_PRIORITIES = ['low', 'medium', 'high'];

// ---- Request Handler ----
async function handleRequest(req, res) {
  // CORS preflight
  if (req.method === 'OPTIONS') {
    res.writeHead(204, {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type'
    });
    res.end();
    return;
  }

  const parsedUrl = url.parse(req.url, true);
  const pathname = parsedUrl.pathname;
  const query = parsedUrl.query;
  const method = req.method;

  // Helper for route matching
  const matchRoute = (pattern) => {
    if (typeof pattern === 'string') {
      return pathname === pattern;
    }
    // pattern is a regex
    const match = pathname.match(pattern);
    return match ? match : null;
  };

  try {
    // ---- GET /tickets ----
    if (method === 'GET' && matchRoute('/tickets')) {
      let filtered = tickets;
      if (query.status && VALID_STATUSES.includes(query.status)) {
        filtered = filtered.filter(t => t.status === query.status);
      }
      if (query.priority && VALID_PRIORITIES.includes(query.priority)) {
        filtered = filtered.filter(t => t.priority === query.priority);
      }
      return sendJSON(res, 200, filtered);
    }

    // ---- POST /tickets ----
    if (method === 'POST' && matchRoute('/tickets')) {
      const body = await parseBody(req);
      // Validate required fields
      if (!body.subject || typeof body.subject !== 'string' || body.subject.trim() === '') {
        return sendError(res, 400, 'Missing required field: subject');
      }
      if (!body.description || typeof body.description !== 'string' || body.description.trim() === '') {
        return sendError(res, 400, 'Missing required field: description');
      }
      // Optional fields with defaults
      const priority = body.priority || 'low';
      const status = body.status || 'open';
      if (!VALID_PRIORITIES.includes(priority)) {
        return sendError(res, 400, `Invalid priority. Must be one of: ${VALID_PRIORITIES.join(', ')}`);
      }
      if (!VALID_STATUSES.includes(status)) {
        return sendError(res, 400, `Invalid status. Must be one of: ${VALID_STATUSES.join(', ')}`);
      }

      const ticket = {
        id: nextId++,
        subject: body.subject.trim(),
        description: body.description.trim(),
        priority,
        status,
        created_at: getTimestamp(),
        updated_at: getTimestamp()
      };
      tickets.push(ticket);
      await saveTickets();
      return sendJSON(res, 201, ticket);
    }

    // ---- Routes with ID parameter ----
    const matchSingle = pathname.match(/^\/tickets\/(\d+)$/);
    if (matchSingle) {
      const id = parseInt(matchSingle[1], 10);
      const idx = tickets.findIndex(t => t.id === id);

      // ---- GET /tickets/{id} ----
      if (method === 'GET') {
        if (idx === -1) return sendError(res, 404, 'Ticket not found');
        return sendJSON(res, 200, tickets[idx]);
      }

      // ---- PATCH /tickets/{id} ----
      if (method === 'PATCH') {
        if (idx === -1) return sendError(res, 404, 'Ticket not found');
        const body = await parseBody(req);
        const ticket = tickets[idx];
        // Validate fields if provided
        if (body.subject !== undefined) {
          if (typeof body.subject !== 'string' || body.subject.trim() === '') {
            return sendError(res, 400, 'Invalid subject');
          }
          ticket.subject = body.subject.trim();
        }
        if (body.description !== undefined) {
          if (typeof body.description !== 'string' || body.description.trim() === '') {
            return sendError(res, 400, 'Invalid description');
          }
          ticket.description = body.description.trim();
        }
        if (body.priority !== undefined) {
          if (!VALID_PRIORITIES.includes(body.priority)) {
            return sendError(res, 400, `Invalid priority. Must be one of: ${VALID_PRIORITIES.join(', ')}`);
          }
          ticket.priority = body.priority;
        }
        if (body.status !== undefined) {
          if (!VALID_STATUSES.includes(body.status)) {
            return sendError(res, 400, `Invalid status. Must be one of: ${VALID_STATUSES.join(', ')}`);
          }
          ticket.status = body.status;
        }
        ticket.updated_at = getTimestamp();
        await saveTickets();
        return sendJSON(res, 200, ticket);
      }

      // ---- DELETE /tickets/{id} ----
      if (method === 'DELETE') {
        if (idx === -1) return sendError(res, 404, 'Ticket not found');
        tickets.splice(idx, 1);
        await saveTickets();
        return sendJSON(res, 200, { message: 'Ticket deleted' });
      }

      // Method not allowed on /tickets/{id}
      return sendError(res, 405, 'Method not allowed');
    }

    // ---- GET /metrics ----
    if (method === 'GET' && matchRoute('/metrics')) {
      const statusCounts = { open: 0, in_progress: 0, resolved: 0 };
      const priorityCounts = { low: 0, medium: 0, high: 0 };
      let openAgeSum = 0;
      let openCount = 0;
      const now = Date.now();
      for (const t of tickets) {
        if (statusCounts.hasOwnProperty(t.status)) statusCounts[t.status]++;
        if (priorityCounts.hasOwnProperty(t.priority)) priorityCounts[t.priority]++;
        if (t.status === 'open') {
          const created = new Date(t.created_at).getTime();
          openAgeSum += (now - created) / 1000; // seconds
          openCount++;
        }
      }
      const metrics = {
        statusCounts,
        priorityCounts,
        averageOpenAgeSeconds: openCount > 0 ? +(openAgeSum / openCount).toFixed(2) : 0
      };
      return sendJSON(res, 200, metrics);
    }

    // ---- Fallback: 404 ----
    sendError(res, 404, 'Route not found');
  } catch (err) {
    // Body parsing errors or others
    if (err.message === 'No body supplied' || err.message === 'Invalid JSON') {
      return sendError(res, 400, err.message);
    }
    console.error(err);
    sendError(res, 500, 'Internal server error');
  }
}

// ---- Start Server ----
async function start() {
  await loadTickets();
  const server = http.createServer(handleRequest);
  server.listen(PORT, HOST, () => {
    console.log(`Server running at http://${HOST}:${PORT}/`);
  });
}

start().catch(err => {
  console.error('Failed to start server:', err);
  process.exit(1);
});
