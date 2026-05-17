# Generation Transcript

- Case: `en_code_be_001`
- Language group: `en`
- Workload: `coding`
- Model: `deepseek-v4-flash`
- Round: `3`
- Thinking mode: `think-high`
- Thinking strength: `high`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `official-api`
- OK: `True`
- Status: PASS
- Check: expectation checks skipped
- Detail: `expectation checks skipped`
- Elapsed seconds: 28.387366
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 318, "completion_tokens": 3958, "total_tokens": 4276, "prompt_tokens_details": {"cached_tokens": 256}, "completion_tokens_details": {"reasoning_tokens": 1595}, "prompt_cache_hit_tokens": 256, "prompt_cache_miss_tokens": 62}`
- Prompt tokens: 318
- Completion tokens: 3958
- Total tokens: 4276

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

## Reasoning Content

```text
We need to write a single-file Node.js HTTP server using only built-in modules. Must be server.js. Use http, fs, path, url, etc. Read/write tickets.json. Implement CRUD and metrics. Ensure sequential requests handled safely: file locking? Since node is single-threaded and we are using read/write synchronously or with callbacks, we need to ensure no race conditions. There are no external libraries so we can use readFile/writeFile with callbacks, but multiple requests could interleave. For safety, we can use a simple mutex or queue. Since it's sequential requests (one after another) but async, we can use a promise-based queue. But we can also read/write synchronously? That would block the event loop, not ideal but for small loads it's okay. The requirement says "safe enough for sequential requests" - maybe they mean no concurrent writes? We can use a flag to serialize writes. I'll implement a simple lock: a promise chain that ensures only one write at a time. Use async/await.

We need to parse URL, method, body. Use JSON.parse for request body. Validate required fields for POST: subject, description, priority (should be low/medium/high), status default 'open'. Also created_at/updated_at set to now.

For PATCH, only allow updating subject, description, priority, status. Validate enum values.

Generate unique IDs: use incremental numbers? Could use uuid-like but simple: use timestamp + random. Or just maintain a counter in the file. Simpler: find max ID and increment. But if file empty, start at 1. Could use crypto.randomUUID? That's built-in in Node 19+ but not in older? The requirement says built-in modules; crypto is built-in. But we want simplicity. I'll use a simple counter based on existing IDs: Math.max(...ids)+1. That's fine.

Metrics: GET /metrics - count tickets by status, by priority, and average age of open tickets in seconds. Age = now - created_at in ms, convert to seconds. For open tickets: status='open'? Or also 'in_progress'? The description says "average age of open tickets". Usually open tickets are those with status 'open'. We'll assume only 'open'. But we can clarify; "open" tickets likely means status 'open'. So compute average age in seconds from created_at.

CORS headers: Access-Control-Allow-Origin: *, Allow-Methods, etc.

Error handling: 400 for bad request, 404 for not found, 405 for method not allowed, 500 for internal.

We need to parse path parameters: /tickets/{id} and /tickets, /metrics.

Also handle unknown routes: 404.

Output only code.

Let's write server.js with all above. Use async functions with try/catch. For file operations, use fs.promises for async.

Implement a simple request handler that dispatches based on method and path.

We'll create a helper function to read tickets file, if not exists return empty array. Write back.

For sequential writes, we can use a promise variable that chains writes: let writePromise = Promise.resolve(). Then each write operation: writePromise = writePromise.then(() => writeFile). That way writes are serial. Reads can be concurrent but if we need to read before write we need to ensure read is also serial? Actually if we read then modify then write, we need to ensure no other write happens between read and write. So we need a lock for the whole read-modify-write cycle. Use a queue: a promise chain that ensures only one operation at a time. We'll implement a simple mutex: an array of functions that are executed sequentially. Or use a single promise that resolves after each operation. We'll define a `lock` function that returns a promise and a release. But to keep simple, we'll use a global promise variable `fileLock` that we chain each read-modify-write operation onto. That is: let fileLock = Promise.resolve(); then for each operation, we do:

fileLock = fileLock.then(async () => {
  // read, modify, write
});

This ensures sequential execution. Because each operation waits for previous to complete. However, we also have reads for GET /tickets that don't need a lock if they only read and no write. But we need to ensure that while a write is in progress, a read might read stale data? That's fine because we want consistency? Actually we want to avoid reading during a write? If we read while a write is in progress, we might get the old file content because the write hasn't completed. That's okay if we don't require strict consistency. But to avoid reading partially written data, we should also serialize reads? Since fs promises are atomic for file read? Actually when you read a file, it reads the entire content at that moment. If a write is in progress, the file might be partially written, leading to corruption. So we need to serialize all file operations (read and write) to avoid reading a partially written file. Therefore, we should use a single queue for all file operations, not just writes. So use a promise chain for all file accesses. We'll create a function `accessFile` that returns a promise that resolves with the data after performing a read, and also allows a write operation. But better: we can implement a simple mutex using a promise that each operation awaits and then updates.

Simpler: Use a module-level Promise-based mutex. We'll have a single `fileLock` promise that we chain all operations onto. For read-only operations, we still need to wait for any pending writes to finish, but we can read concurrently after that? Actually if we chain reads they will happen one after another. That's fine for simplicity.

We'll implement:

let fileOperationQueue = Promise.resolve();

async function withFileAccess(fn) {
  fileOperationQueue = fileOperationQueue.then(async () => {
    // fn is a function that returns a promise (e.g., read, modify, write)
    return await fn();
  });
  return fileOperationQueue;
}

Then every endpoint that reads/writes should call withFileAccess.

But careful: withFileAccess returns the promise that resolves when the operation is done. For endpoints that need to respond after operation, they should await it.

But if we have multiple endpoints, they all push onto queue. Since we use await in the handler, it will wait for the previous operation to complete.

We need to be careful that the queue itself is not a problem: if a request comes and we push a new operation, it returns a promise that resolves when that operation completes. Since we are awaiting it, the request handler will wait. That's correct.

However, we must be careful not to have unhandled rejections if an operation fails. We'll catch errors inside the handler and respond with 500.

Now, implement the server.

We'll parse request body for POST and PATCH using a function that collects chunks.

We'll use `url.parse` (or URL constructor) to parse query params.

Let's code.

We'll handle:

- GET /tickets?status=...&priority=...
- POST /tickets
- GET /tickets/:id
- PATCH /tickets/:id
- DELETE /tickets/:id
- GET /metrics

Other routes return 404.

Methods not allowed return 405.

Also handle OPTIONS for CORS preflight.

We'll add CORS headers to all responses.

Now write the code.

We'll keep under 1000 lines, it will be fine.

Let's start writing.
```

## Assistant

````markdown
```javascript
const http = require('http');
const fs = require('fs');
const path = require('path');
const url = require('url');

const DATA_FILE = path.join(__dirname, 'tickets.json');
const HOST = '127.0.0.1';
const PORT = 8080;

// ----------------------------------------------------------------------
// File operations queue (simple mutex to serialise all reads/writes)
// ----------------------------------------------------------------------
let fileQueue = Promise.resolve();

function withFileAccess(fn) {
  fileQueue = fileQueue.then(() => fn());
  return fileQueue;
}

// ----------------------------------------------------------------------
// Read / write tickets.json
// ----------------------------------------------------------------------
async function readTickets() {
  try {
    const raw = await fs.promises.readFile(DATA_FILE, 'utf8');
    return JSON.parse(raw);
  } catch (err) {
    if (err.code === 'ENOENT') return [];
    throw err;
  }
}

async function writeTickets(tickets) {
  const tmpFile = DATA_FILE + '.tmp';
  await fs.promises.writeFile(tmpFile, JSON.stringify(tickets, null, 2), 'utf8');
  await fs.promises.rename(tmpFile, DATA_FILE);
}

// ----------------------------------------------------------------------
// Utility: parse JSON body from request
// ----------------------------------------------------------------------
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

// ----------------------------------------------------------------------
// Generate a new unique ID (based on existing max id)
// ----------------------------------------------------------------------
function generateId(tickets) {
  if (tickets.length === 0) return 1;
  const maxId = Math.max(...tickets.map(t => t.id));
  return maxId + 1;
}

// ----------------------------------------------------------------------
// Validate ticket fields
// ----------------------------------------------------------------------
const VALID_PRIORITIES = ['low', 'medium', 'high'];
const VALID_STATUSES = ['open', 'in_progress', 'resolved'];

function validateTicket(body, isUpdate = false) {
  const errors = [];
  const { subject, description, priority, status } = body;

  if (!isUpdate) {
    if (!subject || typeof subject !== 'string') errors.push('subject is required and must be a string');
    if (!description || typeof description !== 'string') errors.push('description is required and must be a string');
  } else {
    if (subject !== undefined && typeof subject !== 'string') errors.push('subject must be a string');
    if (description !== undefined && typeof description !== 'string') errors.push('description must be a string');
  }

  if (priority !== undefined && !VALID_PRIORITIES.includes(priority)) {
    errors.push(`priority must be one of: ${VALID_PRIORITIES.join(', ')}`);
  }
  if (status !== undefined && !VALID_STATUSES.includes(status)) {
    errors.push(`status must be one of: ${VALID_STATUSES.join(', ')}`);
  }
  return errors;
}

// ----------------------------------------------------------------------
// Send JSON response
// ----------------------------------------------------------------------
function sendJSON(res, statusCode, data) {
  const headers = {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
  };
  res.writeHead(statusCode, headers);
  res.end(JSON.stringify(data));
}

// ----------------------------------------------------------------------
// Route handlers
// ----------------------------------------------------------------------
async function handleGetTickets(req, res, query) {
  const tickets = await withFileAccess(readTickets);
  const { status: filterStatus, priority: filterPriority } = query;
  let filtered = tickets;
  if (filterStatus) {
    filtered = filtered.filter(t => t.status === filterStatus);
  }
  if (filterPriority) {
    filtered = filtered.filter(t => t.priority === filterPriority);
  }
  sendJSON(res, 200, filtered);
}

async function handlePostTicket(req, res) {
  let body;
  try {
    body = await parseBody(req);
  } catch (err) {
    return sendJSON(res, 400, { error: 'Invalid JSON' });
  }

  const errors = validateTicket(body);
  if (errors.length) {
    return sendJSON(res, 400, { error: errors.join('; ') });
  }

  await withFileAccess(async () => {
    const tickets = await readTickets();
    const now = new Date().toISOString();
    const ticket = {
      id: generateId(tickets),
      subject: body.subject,
      description: body.description,
      priority: body.priority || 'low',
      status: body.status || 'open',
      created_at: now,
      updated_at: now,
    };
    tickets.push(ticket);
    await writeTickets(tickets);
    // Return the created ticket (still inside the mutex)
    sendJSON(res, 201, ticket);
  });
}

async function handleGetTicket(req, res, id) {
  const tickets = await withFileAccess(readTickets);
  const ticket = tickets.find(t => t.id === id);
  if (!ticket) {
    return sendJSON(res, 404, { error: 'Ticket not found' });
  }
  sendJSON(res, 200, ticket);
}

async function handlePatchTicket(req, res, id) {
  let body;
  try {
    body = await parseBody(req);
  } catch (err) {
    return sendJSON(res, 400, { error: 'Invalid JSON' });
  }

  const errors = validateTicket(body, true);
  if (errors.length) {
    return sendJSON(res, 400, { error: errors.join('; ') });
  }

  await withFileAccess(async () => {
    const tickets = await readTickets();
    const index = tickets.findIndex(t => t.id === id);
    if (index === -1) {
      return sendJSON(res, 404, { error: 'Ticket not found' });
    }

    const existing = tickets[index];
    const allowedFields = ['subject', 'description', 'priority', 'status'];
    let changed = false;
    for (const field of allowedFields) {
      if (body[field] !== undefined) {
        existing[field] = body[field];
        changed = true;
      }
    }
    if (changed) {
      existing.updated_at = new Date().toISOString();
    }
    tickets[index] = existing;
    await writeTickets(tickets);
    sendJSON(res, 200, existing);
  });
}

async function handleDeleteTicket(req, res, id) {
  await withFileAccess(async () => {
    const tickets = await readTickets();
    const index = tickets.findIndex(t => t.id === id);
    if (index === -1) {
      return sendJSON(res, 404, { error: 'Ticket not found' });
    }
    const removed = tickets.splice(index, 1)[0];
    await writeTickets(tickets);
    sendJSON(res, 200, removed);
  });
}

async function handleGetMetrics(req, res) {
  const tickets = await withFileAccess(readTickets);
  const now = Date.now();

  const statusCounts = {};
  const priorityCounts = {};
  let totalOpenAgeMs = 0;
  let openCount = 0;

  for (const t of tickets) {
    // status counts
    statusCounts[t.status] = (statusCounts[t.status] || 0) + 1;
    // priority counts
    priorityCounts[t.priority] = (priorityCounts[t.priority] || 0) + 1;
    // average age of open tickets (status === 'open')
    if (t.status === 'open') {
      openCount++;
      totalOpenAgeMs += now - new Date(t.created_at).getTime();
    }
  }

  const metrics = {
    status_counts: statusCounts,
    priority_counts: priorityCounts,
    average_open_age_seconds: openCount > 0 ? Math.round(totalOpenAgeMs / openCount / 1000) : 0,
  };
  sendJSON(res, 200, metrics);
}

// ----------------------------------------------------------------------
// Request dispatcher
// ----------------------------------------------------------------------
const routes = {
  GET: {},
  POST: {},
  PATCH: {},
  DELETE: {},
};

routes.GET['/tickets'] = handleGetTickets;
routes.POST['/tickets'] = handlePostTicket;
routes.GET['/metrics'] = handleGetMetrics;

const server = http.createServer(async (req, res) => {
  // CORS preflight
  if (req.method === 'OPTIONS') {
    res.writeHead(204, {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    });
    res.end();
    return;
  }

  const parsedUrl = url.parse(req.url, true);
  const pathname = parsedUrl.pathname;
  const method = req.method;

  // Try exact match first
  if (routes[method] && routes[method][pathname]) {
    try {
      await routes[method][pathname](req, res, parsedUrl.query);
    } catch (err) {
      console.error(err);
      sendJSON(res, 500, { error: 'Internal server error' });
    }
    return;
  }

  // Try parametric routes: /tickets/:id and /tickets/:id
  const ticketMatch = pathname.match(/^\/tickets\/(\d+)$/);
  if (ticketMatch) {
    const id = parseInt(ticketMatch[1], 10);
    if (isNaN(id)) {
      return sendJSON(res, 400, { error: 'Invalid ticket ID' });
    }
    try {
      switch (method) {
        case 'GET':
          await handleGetTicket(req, res, id);
          break;
        case 'PATCH':
          await handlePatchTicket(req, res, id);
          break;
        case 'DELETE':
          await handleDeleteTicket(req, res, id);
          break;
        default:
          sendJSON(res, 405, { error: 'Method not allowed' });
      }
    } catch (err) {
      console.error(err);
      sendJSON(res, 500, { error: 'Internal server error' });
    }
    return;
  }

  // Unknown route
  sendJSON(res, 404, { error: 'Not found' });
});

server.listen(PORT, HOST, () => {
  console.log(`Server running at http://${HOST}:${PORT}/`);
});
```
````
