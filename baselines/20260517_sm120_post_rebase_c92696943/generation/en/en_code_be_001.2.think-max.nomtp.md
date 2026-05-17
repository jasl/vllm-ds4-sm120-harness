# Generation Transcript

- Case: `en_code_be_001`
- Language group: `en`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `2`
- Thinking mode: `think-max`
- Thinking strength: `max`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 69.589904
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 397, "total_tokens": 7270, "completion_tokens": 6873, "prompt_tokens_details": null}`
- Prompt tokens: 397
- Completion tokens: 6873
- Total tokens: 7270

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

````text
We need to write a single-file Node.js HTTP server named `server.js` that fulfills the requirements. Use built-in modules only: http, fs, path, url, etc. No external packages. Keep under 1000 lines.

We'll create an HTTP server that listens on 127.0.0.1:8080. Data stored in tickets.json.

We need to handle request methods and routes. Parse URL and query parameters using url module (or manually). For query strings, use url.parse or new URL. Since it's built-in, we can use the 'url' module's parse method with true for query object.

We need to read/write tickets.json safely. For sequential requests, we can use file locking or just read and write each time. Since Node.js is single-threaded, requests are handled sequentially but in event loop; we must ensure file operations are not overlapping incorrectly. Using synchronous file operations could block, but for safety we can use async with callbacks/promises and ensure we don't have race conditions. Since we are in single thread, as long as we read and then write atomically (i.e., read file, modify, write back) without awaiting something else that could interleave, it's safe if we use promises and don't start another operation until the previous one is complete. However, multiple requests could come in concurrently, leading to interleaving if we use async/await with file operations. To be safe, we can implement a simple queue or use a mutex (e.g., using a promise chain). Or we can use synchronous fs methods but that would block the event loop for other requests? But for a small API it's acceptable, but better to use async with a lock.

We'll implement a simple lock using a promise that resolves when file is free. Or we can use a queue of operations. Since it's small, we can use synchronous file reads/writes for simplicity, but it will block the event loop during I/O. For this exercise, it might be acceptable. However, requirements say "Read/write a tickets.json file safely enough for sequential requests." That suggests we need to handle concurrency properly. I'll implement a simple mutex.

We'll use a helper function `readTickets` and `writeTickets` that use fs.promises but with a lock to prevent overlapping writes/reads that could cause lost updates.

Since it's a single file, we can implement a simple promise chain: maintain a promise variable that starts resolved, and each read/write operation adds a .then to it. That ensures sequential access. Alternatively, we can use a queue.

Let's design:

- Use http.createServer.
- Parse url using new URL(req.url, `http://${req.headers.host}`) or use url.parse. We'll use URL class.
- Handle CORS: set headers Access-Control-Allow-Origin: *, etc.
- Handle preflight OPTIONS.
- Parse body for POST/PATCH: collect chunks, then JSON parse. Handle errors.
- Routes: /tickets, /tickets/{id}, /metrics.
- Validate data: required fields for POST: subject, description, priority, status? The spec says "Validate required fields." It doesn't list which ones are required. For POST, presumably subject and description are required? Possibly also priority and status? Typically status defaults to open. We'll require subject and description, priority with default low? But spec says "Validate required fields." We'll check that subject and description are present and non-empty. For priority, if not provided, default to 'low'? The data model shows it as an enum. We'll accept priority only if valid, else default or error. But validation: if priority is given but invalid, return error. Similarly status for POST: if not given, default to 'open'. We'll accept status only if valid. For PATCH, we only update fields that are present and valid.

- Generate IDs: use incremental integer or UUID? We can use simple incremental int stored in memory or read from existing tickets to compute next ID. I'll use auto-increment: get max id + 1. Or generate uuid with crypto, but integer is simpler. We'll use integer.

- Metrics: GET /metrics returns counts by status and priority, and average age of open tickets in seconds (average time since created_at for tickets with status 'open').

- Error responses: JSON object with "error" key.

- Logging: minimal.

Implementation steps:

1. Define constants: PORT = process.env.PORT || 8080; HOST = '127.0.0.1'; DATA_FILE = path.join(__dirname, 'tickets.json').

2. File lock: Use a promise variable: let fileLock = Promise.resolve(); Then function withLock(fn) returns fileLock = fileLock.then(fn).catch(err => console.error(err)); But we need to ensure errors don't break chain. We'll implement a simple mutex class with acquire/release using promise queue.

Simpler: Since Node is single-threaded, if we always await file operations sequentially using a queue, it's fine. We'll create a queue using an array of functions, but we can just use a promise chain.

Let's implement a function `updateTickets(updater)` that takes a callback that receives the current tickets array and returns new tickets array (or modified). It will read, call updater, write. And we'll ensure that each call is chained via a promise.

We'll maintain a `tickets` variable in memory? Could cache but we need to persist. For simplicity, we can keep an in-memory copy and write to file every time, but also read from file on start. For concurrent safety, we need to ensure reads and writes are serialized. Using an in-memory variable with a lock might be easier: on start, read file into memory. Then all operations modify the in-memory array and then write to file asynchronously. We need to ensure that writes don't overlap. We'll use a mutex for writing to file, but reads from memory can happen concurrently. However, if we have multiple requests that modify and then write, we could have race: request A reads memory, modifies, writes; request B reads memory, modifies, writes; but B's read might happen before A's write, so B's changes might overwrite A's. To avoid that, we need to lock the entire critical section: read-modify-write. So we should use a lock that ensures only one request is doing read-modify-write at a time. For read-only requests (GET), we can read from memory without lock.

Thus design: maintain an in-memory `tickets` array. On start, read from file if exists, else empty array. Then for any modification (POST, PATCH, DELETE), we acquire a lock, read current memory (which is already in sync after previous write), modify, write to file, then release lock. For GET requests that modify nothing, no lock needed. But we must ensure that after a modification, the in-memory array is updated before the next modification reads it. So using a lock ensures serial execution of modifications. For simplicity, we can use a simple queue with a promise that resolves when the modification is complete.

We'll create a class `FileStore` with methods like `read()` (returns a copy of tickets), `update(updater)` (acquires lock, reads current, applies updater, writes back, releases lock). The lock can be implemented using a promise chain where each update adds a .then to a shared promise.

We'll implement:

```js
let tickets = [];
let lastOperation = Promise.resolve();

function withLock(fn) {
  return lastOperation = lastOperation.then(fn);
}
```

But if fn returns a promise, we need to wait for it. We'll do:

```js
function enqueueOperation(fn) {
  return lastOperation = lastOperation.then(fn).catch(err => console.error('Operation error:', err));
}
```

However, we also need to handle errors without breaking chain. Each operation should catch its own errors and return the chain. We'll use a mutex class with a queue.

Simpler: Use async/await and a simple promise chain with a shared promise variable that we await each operation on. Let's code:

```js
let operationQueue = Promise.resolve();

async function performOperation(op) {
  await operationQueue;
  try {
    return await op();
  } finally {
    // no need to release; we chain to operationQueue
  }
}
```

But this does not guarantee exclusivity because after `await operationQueue`, another async function could have also awaited and started. So we need to set operationQueue to a new promise that resolves when this operation completes. So we need to maintain a chain.

Better: use a queue with a `next` function that runs only when the previous task completes.

For simplicity, given the scope, we can use synchronous file I/O for reading and writing tickets.json inside a lock via a queue. But synchronous I/O would block the event loop, but it's okay for small API. However, to be more robust, we'll use async with a proper mutex.

I'll implement a simple mutex using an array of waiters.

But let's not overcomplicate. Since the requirement says "safely enough for sequential requests", we can use a simple queue. I'll use a function `withFileLock` that returns a promise that resolves to a function that releases the lock. This way we can do:

```js
const lock = new Mutex();
// usage:
await lock.acquire();
// read file, modify, write file
lock.release();
```

But implementing a mutex with acquire/release requires careful handling.

Alternatively, we can use a helper function that reads, transforms, writes, and queues these operations using a promise chain.

Let's implement:

```js
let fileLock = Promise.resolve();

async function updateTickets(transform) {
  // Wait for previous operation to complete
  await fileLock;
  // Set the lock to a new promise that resolves when this operation is done
  let resolveLock;
  fileLock = new Promise(resolve => { resolveLock = resolve; });
  try {
    // Read current data
    const data = await readTicketsFile(); // using fs.promises
    const tickets = JSON.parse(data);
    const newTickets = transform(tickets);
    await writeTicketsFile(JSON.stringify(newTickets, null, 2));
  } catch (err) {
    // Handle error (log, maybe store to respond later)
    throw err;
  } finally {
    resolveLock();
  }
}
```

But there is a subtlety: if two concurrent calls to updateTickets both await fileLock simultaneously, the first one will proceed, set fileLock to a new promise, then the second one will wait on the first's fileLock (which was replaced). But when the first finishes and resolves the new lock, the second can proceed. However, after the first replaces fileLock, the second's await fileLock is waiting on the old promise? No: because let's track:

Initially fileLock = resolvedPromise.

Request A: awaits fileLock (resolved immediately). Then sets fileLock = newPromise1. A continues (async).
Request B: arrives, awaits fileLock (now newPromise1). So B waits until A's resolveLock is called. Good.
When A finishes, it calls resolveLock(), which resolves newPromise1, allowing B to proceed. B then sets fileLock = newPromise2, and so on.

This works if we set fileLock before any await inside the critical section. In the code above, we set fileLock immediately after awaiting the previous, before any async I/O. That ensures the next request will wait on the new promise.

But we need to be careful: if there's an error, we must still resolve the lock to avoid deadlock. That's why we have finally block.

So this pattern works for sequential operations.

However, we also need to handle the case where we read the file on startup. That's outside the lock. We'll read once at startup.

Now, for read-only operations (GET /tickets, GET /tickets/:id, GET /metrics), we don't need to modify file, but we still need to read the current data. Since we have an in-memory array that we update after each successful modification, we can serve from memory without reading file each time. That's more efficient and avoids file I/O on every GET. But we must ensure that after a modification, the in-memory array is updated before the lock is released, so subsequent reads see the new data.

Thus, we can maintain a `tickets` array in memory. On updates, we modify this array and then write to file. For reads, we use this array directly. To keep consistency, we can read the file on startup into memory. Then modifications are done to the in-memory array and persisted. No need to read file for each request.

But what about if the file is modified externally? Not required. So we can keep in-memory.

Thus the lock is only needed to serialize write operations to file to prevent overlapping writes that could corrupt the file. However, if we are writing to file with asynchronous writes but we ensure only one write at a time, it's fine. We can serialize writes via a promise chain as above. The in-memory array can be modified directly, but we need to ensure that if two modifications come in, they don't interfere. If we use async/await with the lock, each modification will read the current in-memory array (which is a reference to the array), modify it, then write. But if two modifications interleave without lock, they could both read the same array and then write, causing lost updates. So the lock should cover the entire read-modify-write cycle, but we already have in-memory, so we can just do: lock, modify in-memory array, write file, unlock. Since we modify the same array object, we don't need to read file. But we must ensure that when we modify in-memory, we do it atomically under lock.

So we can manage tickets as a module-level variable that is an array. Modifications under lock ensure only one modification at a time. Reads can access the array without lock safely in JavaScript single-threaded? Actually, JavaScript execution is single-threaded, but async functions can be interleaved. If a read happens during a modification (between reading the array and writing the file), the read might see the partially modified array? But if modifications are done synchronously (like splice or push) while holding the lock (but the lock is just a promise, not a real lock; JavaScript is single-threaded so no two pieces of code run concurrently. However, due to async/await, execution can be suspended at await points. So if we modify the array synchronously before writing, there is no interleaving because the event loop is not yielding to other requests between synchronous operations. But while we are doing async file write (await writeFile), the event loop can process other requests. If we release the lock after the file write, but before that, another request could start and read the in-memory array which may have been modified while the write is in progress. That would cause the read to see the new data even before it's persisted, which is acceptable if we consider eventual consistency? But it might be okay for this API. However, the requirement says "safely enough for sequential requests." If we want atomicity, we should ensure that reads also see a consistent snapshot. Since we modify the array immediately under lock and then write asynchronously, other requests that arrive during the write will see the updated array. That's probably fine. But if the write fails, we might have updated the in-memory state but not persisted, leading to inconsistency on restart. To avoid that, we could write to file first, then update memory, or we could wrap both in a transaction. But we can keep it simple: update memory, write file, and if write fails, log error and maybe revert? Hard. We'll assume success.

Alternatively, we can keep the lock for the entire duration of the write operation. That means we only release the lock after the file is written. Then any read during that time would be blocked if they try to acquire the lock? But reads don't need to acquire the lock if they just read in-memory. However, if we want reads to see a consistent state, we might want to hold the lock for modification and write, and have reads also acquire a read lock? Too complex.

For simplicity, we'll have the modification function (POST, PATCH, DELETE) use a mutex that ensures only one modification runs at a time, but we do not block reads. The in-memory array is updated before the file write, so reads after that point see the new data, which is fine. The file write might still be pending, but that's okay.

Thus our design:

- Global variable `let tickets = [];`
- On server start, load from file if exists.
- For endpoints that modify: acquire a queue slot (lock), then perform operation on in-memory array, then write to file (async), then release lock.
- For GET endpoints: just read from in-memory array (no lock).

Now, for the queue we can use a promise chain as described.

Implementation:

```js
let operationQueue = Promise.resolve();

async function queueOperation(fn) {
  const prev = operationQueue;
  let resolve;
  operationQueue = new Promise(r => { resolve = r; });
  await prev;
  try {
    return await fn();
  } finally {
    resolve();
  }
}
```

This ensures sequential execution.

Now, file I/O: use fs.promises.readFile, fs.promises.writeFile.

We'll need to parse body: collect chunks, then JSON.parse.

We'll set response headers: Content-Type application/json, CORS headers.

Handle errors: try-catch on operations, return 500 or appropriate.

Validation:

POST /tickets: required fields: subject, description. Also check priority and status if provided.

We'll generate id: auto-increment from max existing id + 1, or if none, start at 1.

Set created_at and updated_at to ISO string.

PATCH /tickets/:id: update only provided fields: subject, description, priority, status. Validate values if provided (priority must be low/medium/high, status must be open/in_progress/resolved). Set updated_at to now.

DELETE /tickets/:id: remove by id.

GET /metrics: count statuses, priorities, compute average age of open tickets in seconds. Age = (Date.now() - new Date(created_at).getTime()) / 1000.

Return JSON.

Edge cases: invalid JSON body -> 400, invalid ID -> 404, unknown route -> 404, unsupported method -> 405.

CORS: handle OPTIONS preflight.

Now, implement:

- Use http.createServer.
- In request handler, parse method and url.
- Use URL object: `const parsedUrl = new URL(req.url, `http://${req.headers.host}`);` or use `parse` from url module.
- Get pathname and searchParams.
- For /tickets, handle GET (list with optional filters), POST.
- For /tickets/:id, handle GET, PATCH, DELETE.
- For /metrics, GET.
- For other routes, 404.

We'll need to extract id from path: e.g., /tickets/123. We can use regex or split.

Let's write clean helper functions.

Now, code structure:

1. Imports: http, fs, path, url?
2. Constants.
3. Helper functions:
   - readTicketsFile (async) - but we'll use in-memory.
   - writeTicketsFile (async) - write to file.
   - loadTickets on startup.
   - queueOperation.
   - handleCors.
   - parseBody.
   - sendJson.
   - sendError.
   - validateTicketFields.
   - generateId.
4. Server creation with event handler.

Let's write.

Note: The file name is `tickets.json`. We'll use `__dirname` to get script directory.

We'll also handle the case where tickets.json doesn't exist on startup: create empty array.

Now, write code under 1000 lines.

I'll produce the complete code.
````

## Assistant

````markdown
```javascript
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
```
````
