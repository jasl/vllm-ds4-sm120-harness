# Generation Transcript

- Case: `en_code_be_001`
- Language group: `en`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `3`
- Thinking mode: `think-max`
- Thinking strength: `max`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 22.540346
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 318, "total_tokens": 3463, "completion_tokens": 3145, "prompt_tokens_details": null}`
- Prompt tokens: 318
- Completion tokens: 3145
- Total tokens: 3463

## Prompt

```markdown
Write a single-file Node.js HTTP server named `server.js`. Use only built-in Node.js modules; no Express, no npm packages. Keep the code under 1,000 lines.

Task: implement a small JSON API for a help-desk ticket queue stored in a local JSON file.

Data model:
- Ticket: `id`, `subject`, `description`, `priority` (`low`, `medium`, `high`), `status` (`open`, `in_progress`, `resolved`), `created_at`, `updated_at`.

API requirements:
1. `GET /tickets` with optional query params `status` and `priority`.
2. `POST /tickets` to create a ticket. Validate required fields.
3. `GET /tickets/{id}` to fetch one ticket.
4. `PATCH /tickets/{id}` to update `subject`, `description`, `priority`, or `status`.
5. `DELETE /tickets/{id}` to delete a ticket.
6. `GET /metrics` returning counts by status and priority plus average age of open tickets in seconds.

Engineering requirements:
- Read/write a `tickets.json` file safely enough for sequential requests.
- Return JSON for all responses, including errors.
- Include CORS headers for local browser testing.
- Handle invalid JSON, unknown routes, unsupported methods, and missing IDs.
- Start on `127.0.0.1:8080` by default.

Output only the complete JavaScript code. Do not include explanations.
```

## Assistant

````markdown
```javascript
const http = require('http');
const fs = require('fs');
const path = require('path');

const HOST = process.env.HOST || '127.0.0.1';
const PORT = process.env.PORT || 8080;
const DATA_FILE = path.join(__dirname, 'tickets.json');

// CORS headers
const CORS_HEADERS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
  'Content-Type': 'application/json'
};

// Initialize data file if it doesn't exist
function initDataFile() {
  try {
    if (!fs.existsSync(DATA_FILE)) {
      fs.writeFileSync(DATA_FILE, JSON.stringify([]), 'utf8');
    }
  } catch (err) {
    console.error('Failed to initialize data file:', err.message);
    process.exit(1);
  }
}

// Read tickets with file locking simulation
function readTickets() {
  try {
    const raw = fs.readFileSync(DATA_FILE, 'utf8');
    const data = JSON.parse(raw);
    if (!Array.isArray(data)) return [];
    return data;
  } catch (err) {
    if (err.code === 'ENOENT') return [];
    throw err;
  }
}

// Write tickets atomically
function writeTickets(tickets) {
  const tempFile = DATA_FILE + '.tmp';
  fs.writeFileSync(tempFile, JSON.stringify(tickets, null, 2), 'utf8');
  fs.renameSync(tempFile, DATA_FILE);
}

// Generate unique ID
let idCounter = 0;
function generateId(tickets) {
  const maxId = tickets.reduce((max, t) => (t.id > max ? t.id : max), 0);
  return Math.max(maxId + 1, Date.now());
}

// Validation helpers
const VALID_PRIORITIES = ['low', 'medium', 'high'];
const VALID_STATUSES = ['open', 'in_progress', 'resolved'];
const REQUIRED_FIELDS = ['subject', 'description', 'priority'];

function validateTicketInput(body, isUpdate = false) {
  const errors = [];

  if (!isUpdate) {
    for (const field of REQUIRED_FIELDS) {
      if (!body[field] || (typeof body[field] === 'string' && body[field].trim() === '')) {
        errors.push(`${field} is required`);
      }
    }
  }

  if (body.subject !== undefined && (typeof body.subject !== 'string' || body.subject.trim() === '')) {
    errors.push('subject must be a non-empty string');
  }

  if (body.description !== undefined && (typeof body.description !== 'string' || body.description.trim() === '')) {
    errors.push('description must be a non-empty string');
  }

  if (body.priority !== undefined && !VALID_PRIORITIES.includes(body.priority)) {
    errors.push(`priority must be one of: ${VALID_PRIORITIES.join(', ')}`);
  }

  if (body.status !== undefined && !VALID_STATUSES.includes(body.status)) {
    errors.push(`status must be one of: ${VALID_STATUSES.join(', ')}`);
  }

  return errors;
}

// Metrics calculation
function calculateMetrics(tickets) {
  const now = Date.now();
  const metrics = {
    statuses: {},
    priorities: {},
    average_open_age_seconds: 0
  };

  // Initialize counts
  for (const status of VALID_STATUSES) {
    metrics.statuses[status] = 0;
  }
  for (const priority of VALID_PRIORITIES) {
    metrics.priorities[priority] = 0;
  }

  let openTicketsCount = 0;
  let totalOpenAge = 0;

  for (const ticket of tickets) {
    // Count by status
    if (metrics.statuses[ticket.status] !== undefined) {
      metrics.statuses[ticket.status]++;
    }

    // Count by priority
    if (metrics.priorities[ticket.priority] !== undefined) {
      metrics.priorities[ticket.priority]++;
    }

    // Calculate age for open tickets
    if (ticket.status === 'open') {
      const createdAt = new Date(ticket.created_at).getTime();
      if (!isNaN(createdAt)) {
        const ageMs = now - createdAt;
        totalOpenAge += ageMs / 1000; // Convert to seconds
        openTicketsCount++;
      }
    }
  }

  if (openTicketsCount > 0) {
    metrics.average_open_age_seconds = Math.round(totalOpenAge / openTicketsCount);
  }

  return metrics;
}

// Parse URL and extract path and query params
function parseRequest(url) {
  const queryStart = url.indexOf('?');
  let pathname = url;
  const queryParams = {};

  if (queryStart !== -1) {
    pathname = url.substring(0, queryStart);
    const queryString = url.substring(queryStart + 1);
    const params = queryString.split('&');
    for (const param of params) {
      const [key, value] = param.split('=');
      if (key) {
        queryParams[decodeURIComponent(key)] = decodeURIComponent(value || '');
      }
    }
  }

  // Remove trailing slash if present
  if (pathname.endsWith('/') && pathname.length > 1) {
    pathname = pathname.slice(0, -1);
  }

  return { pathname, queryParams };
}

// Route matching and ID extraction
function matchRoute(method, parsedUrl) {
  const { pathname, queryParams } = parsedUrl;

  // GET /tickets
  if (method === 'GET' && pathname === '/tickets') {
    return { handler: 'getTickets', params: { queryParams } };
  }

  // POST /tickets
  if (method === 'POST' && pathname === '/tickets') {
    return { handler: 'createTicket', params: {} };
  }

  // GET /metrics
  if (method === 'GET' && pathname === '/metrics') {
    return { handler: 'getMetrics', params: {} };
  }

  // GET /tickets/{id}
  const getMatch = pathname.match(/^\/tickets\/(\d+)$/);
  if (method === 'GET' && getMatch) {
    return { handler: 'getTicket', params: { id: parseInt(getMatch[1], 10) } };
  }

  // PATCH /tickets/{id}
  const patchMatch = pathname.match(/^\/tickets\/(\d+)$/);
  if (method === 'PATCH' && patchMatch) {
    return { handler: 'updateTicket', params: { id: parseInt(patchMatch[1], 10) } };
  }

  // DELETE /tickets/{id}
  const deleteMatch = pathname.match(/^\/tickets\/(\d+)$/);
  if (method === 'DELETE' && deleteMatch) {
    return { handler: 'deleteTicket', params: { id: parseInt(deleteMatch[1], 10) } };
  }

  return null;
}

// Request handlers
function getTickets(queryParams) {
  const tickets = readTickets();
  let filtered = tickets;

  if (queryParams.status) {
    filtered = filtered.filter(t => t.status === queryParams.status);
  }

  if (queryParams.priority) {
    filtered = filtered.filter(t => t.priority === queryParams.priority);
  }

  return {
    statusCode: 200,
    body: filtered
  };
}

function createTicket(body) {
  const errors = validateTicketInput(body);
  if (errors.length > 0) {
    return {
      statusCode: 400,
      body: { error: 'Validation failed', details: errors }
    };
  }

  const tickets = readTickets();
  const now = new Date().toISOString();

  const newTicket = {
    id: generateId(tickets),
    subject: body.subject.trim(),
    description: body.description.trim(),
    priority: body.priority,
    status: body.status || 'open',
    created_at: now,
    updated_at: now
  };

  tickets.push(newTicket);
  writeTickets(tickets);

  return {
    statusCode: 201,
    body: newTicket
  };
}

function getTicket(id) {
  const tickets = readTickets();
  const ticket = tickets.find(t => t.id === id);

  if (!ticket) {
    return {
      statusCode: 404,
      body: { error: 'Ticket not found', id }
    };
  }

  return {
    statusCode: 200,
    body: ticket
  };
}

function updateTicket(id, body) {
  if (Object.keys(body).length === 0) {
    return {
      statusCode: 400,
      body: { error: 'No fields to update' }
    };
  }

  const errors = validateTicketInput(body, true);
  if (errors.length > 0) {
    return {
      statusCode: 400,
      body: { error: 'Validation failed', details: errors }
    };
  }

  const tickets = readTickets();
  const index = tickets.findIndex(t => t.id === id);

  if (index === -1) {
    return {
      statusCode: 404,
      body: { error: 'Ticket not found', id }
    };
  }

  const updatedTicket = { ...tickets[index] };

  if (body.subject !== undefined) updatedTicket.subject = body.subject.trim();
  if (body.description !== undefined) updatedTicket.description = body.description.trim();
  if (body.priority !== undefined) updatedTicket.priority = body.priority;
  if (body.status !== undefined) updatedTicket.status = body.status;

  updatedTicket.updated_at = new Date().toISOString();

  tickets[index] = updatedTicket;
  writeTickets(tickets);

  return {
    statusCode: 200,
    body: updatedTicket
  };
}

function deleteTicket(id) {
  const tickets = readTickets();
  const index = tickets.findIndex(t => t.id === id);

  if (index === -1) {
    return {
      statusCode: 404,
      body: { error: 'Ticket not found', id }
    };
  }

  const deletedTicket = tickets.splice(index, 1)[0];
  writeTickets(tickets);

  return {
    statusCode: 200,
    body: deletedTicket
  };
}

function getMetrics() {
  const tickets = readTickets();
  const metrics = calculateMetrics(tickets);

  return {
    statusCode: 200,
    body: metrics
  };
}

// Server creation
function createServer() {
  initDataFile();

  const server = http.createServer((req, res) => {
    const parsedUrl = parseRequest(req.url);

    // Handle CORS preflight
    if (req.method === 'OPTIONS') {
      res.writeHead(204, CORS_HEADERS);
      res.end();
      return;
    }

    // Parse body for POST and PATCH
    let body = '';
    req.on('data', chunk => {
      body += chunk;
    });

    req.on('end', () => {
      // Parse JSON body if present
      let parsedBody = {};
      if (body) {
        try {
          parsedBody = JSON.parse(body);
        } catch (err) {
          const response = { error: 'Invalid JSON in request body' };
          res.writeHead(400, CORS_HEADERS);
          res.end(JSON.stringify(response));
          return;
        }
      }

      // Route the request
      const route = matchRoute(req.method, parsedUrl);

      if (!route) {
        // Check if route exists but method not allowed
        const allowedMethods = [];
        if (parsedUrl.pathname === '/tickets') {
          allowedMethods.push('GET', 'POST');
        } else if (parsedUrl.pathname === '/metrics') {
          allowedMethods.push('GET');
        } else if (parsedUrl.pathname.match(/^\/tickets\/\d+$/)) {
          allowedMethods.push('GET', 'PATCH', 'DELETE');
        }

        if (allowedMethods.length > 0) {
          const response = {
            error: `Method ${req.method} not allowed for ${parsedUrl.pathname}`,
            allowed_methods: allowedMethods
          };
          res.writeHead(405, {
            ...CORS_HEADERS,
            'Allow': allowedMethods.join(', ')
          });
          res.end(JSON.stringify(response));
        } else {
          const response = { error: `Route ${parsedUrl.pathname} not found` };
          res.writeHead(404, CORS_HEADERS);
          res.end(JSON.stringify(response));
        }
        return;
      }

      // Execute handler
      let result;
      try {
        switch (route.handler) {
          case 'getTickets':
            result = getTickets(route.params.queryParams);
            break;
          case 'createTicket':
            result = createTicket(parsedBody);
            break;
          case 'getTicket':
            result = getTicket(route.params.id);
            break;
          case 'updateTicket':
            result = updateTicket(route.params.id, parsedBody);
            break;
          case 'deleteTicket':
            result = deleteTicket(route.params.id);
            break;
          case 'getMetrics':
            result = getMetrics();
            break;
          default:
            result = {
              statusCode: 500,
              body: { error: 'Internal server error' }
            };
        }
      } catch (err) {
        console.error('Handler error:', err);
        result = {
          statusCode: 500,
          body: { error: 'Internal server error' }
        };
      }

      res.writeHead(result.statusCode, CORS_HEADERS);
      res.end(JSON.stringify(result.body));
    });

    req.on('error', (err) => {
      console.error('Request error:', err);
      const response = { error: 'Internal server error' };
      res.writeHead(500, CORS_HEADERS);
      res.end(JSON.stringify(response));
    });
  });

  return server;
}

// Start server
const server = createServer();
server.listen(PORT, HOST, () => {
  console.log(`Server running at http://${HOST}:${PORT}/`);
});
```
````
