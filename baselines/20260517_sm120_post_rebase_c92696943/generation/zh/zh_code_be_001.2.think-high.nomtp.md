# Generation Transcript

- Case: `zh_code_be_001`
- Language group: `zh`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `2`
- Thinking mode: `think-high`
- Thinking strength: `high`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 72.968853
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 363, "total_tokens": 7568, "completion_tokens": 7205, "prompt_tokens_details": null}`
- Prompt tokens: 363
- Completion tokens: 7205
- Total tokens: 7568

## Prompt

```markdown
请使用 Python 3 标准库编写一个单文件 HTTP API 服务，文件名假定为 `server.py`，不得使用 Flask/FastAPI/Django 等第三方库，总代码不超过1000行。

任务：实现一个小型库存预约服务，用于管理商品库存和短时预约。

数据要求：使用内置 `sqlite3` 持久化，首次启动自动建表。商品字段：`id`、`name`、`stock_total`、`stock_available`。预约字段：`id`、`item_id`、`quantity`、`status`、`expires_at`、`created_at`。

API 要求：
1. `GET /items`：列出商品和可用库存。
2. `POST /items`：新增商品，JSON 参数 `name`、`stock_total`。
3. `POST /reservations`：创建预约，JSON 参数 `item_id`、`quantity`、`ttl_seconds`。库存不足时返回409。
4. `POST /reservations/{id}/confirm`：确认预约，状态变为 confirmed，不再释放库存。
5. `POST /reservations/{id}/cancel`：取消预约，释放库存。
6. 每次请求前清理已过期且仍为 pending 的预约并释放库存。

工程要求：
- 正确处理并发请求下的库存一致性，可使用事务和线程锁。
- 返回 JSON；错误响应包含 `error` 字段。
- 包含一个 `if __name__ == "__main__"` 启动入口，默认监听 `127.0.0.1:8080`。

输出要求：只输出完整 Python 代码，不要解释。
```

## Reasoning Content

````text
我们被要求写一个单文件 HTTP API 服务，使用 Python 3 标准库，不能使用第三方库。需要实现一个库存预约服务，用 sqlite3 持久化，处理并发，有事务和线程锁。代码不超过1000行。

我们需要基于 http.server 模块（BaseHTTPRequestHandler 和 HTTPServer）或者使用更低级的 socket 但推荐 http.server。我会使用 http.server 的 ThreadingHTTPServer（Python 3.7+）或者自定义多线程。但为了正确处理并发，我们需要使用线程锁来保护数据库操作（虽然 sqlite3 本身有线程安全，但默认模式是 check_same_thread=False 时需要在每个连接使用锁，或者使用单个连接并加锁）。最简单的方式是用一个全局的 threading.Lock 包裹所有数据库写操作？但我们需要保证事务原子性。也可以在每次请求时创建新连接，并让 sqlite3 在 WAL 模式下支持并发读写。但为了简单，我会使用单个连接+锁。

不过，创建多个连接并启用 WAL 模式可能更好，但需要处理线程安全。sqlite3 模块默认连接不是线程安全的，除非设置 check_same_thread=False，且每个线程使用自己的连接对象。我们可以使用连接池？但标准库没有。一个简单的方法是：每个请求创建新连接，但共享同一个数据库文件，同时启用 WAL 模式以允许并发读写（多个读者一个写者）。而且 Python 的 sqlite3 模块在 check_same_thread=False 时可以在多线程中安全使用（只要每个线程不共享连接）。所以我们可以为每个请求创建一个新的连接，并在完成后关闭。同时使用 WAL 模式提高并发。但注意：多个写事务可能冲突，sqlite3 会使用文件锁，所以写操作会序列化。但我们需要确保不会出现死锁。我们可以接受 sqlite3 的默认行为。

另外，我们需要在每次请求前清理过期预约。这个清理操作可以在处理任何请求前执行（除了查询？但为了简单，每个请求都做清理，包括GET）。我们使用一个全局锁来确保清理和预约操作的原子性？实际上，清理本身是一个写操作，可能会与并发写冲突。如果使用每个连接单独，可能会有竞争条件：一个线程在清理过期并释放库存，另一个线程同时在进行预约，可能读取到过时的库存。我们可以使用一个写锁来保护所有修改数据库的操作。但 GET 请求是只读，不需要锁？但是清理动作会修改数据库，所以 GET 请求在读取的时候可能同时有写操作，但 sqlite3 的 WAL 模式允许读与写并发（写不阻塞读，读不阻塞写），所以可以不用锁。但需要注意：如果读操作在写事务进行时，读到的可能是旧版本数据，但这是可以接受的。对于预约这样的业务，可能需要更严格的一致性：比如，当清理过期预约的同时，另一个线程在创建预约，可能会读取到已经释放的库存？由于 WAL 模式中读事务结束时看到的是一致性的快照，所以应该没问题。但是，两个写事务之间会有冲突，sqlite3 会返回 "database is locked" 错误，我们需要重试或处理。为了简化，我们可以在写操作时使用一个全局的 threading.Lock 来确保同一时间只有一个写操作（包括清理）。这样更容易保证库存一致性，并且不会出现死锁。而且我们不需要担心重试。

那么，设计如下：

- 使用 http.server 的 ThreadingHTTPServer（多线程处理），但为了处理请求，我们使用 BaseHTTPRequestHandler 的子类。
- 创建一个全局锁 `db_lock = threading.Lock()` 用于保护所有写操作（INSERT, UPDATE, DELETE）。读操作不需要锁，但为了简化，也可以持有锁？但可能降低并发。因为我们的主要写操作只有：新增商品、创建预约（先读后写）、确认/取消预约、过期清理。这些都会写，且都需要原子性。我们可以让每个写操作在锁内执行一个事务。读操作可以不使用锁，但注意：在创建预约时，我们需要先读取库存（检查是否足够），然后在同一事务中插入预约并减少库存。这个读-写操作必须原子，所以必须在一个事务中，且需要锁保护。所以对于所有写请求，我们会在锁下执行整个数据库操作（包括可能的查询）。对于只读的 GET /items，我们无需锁（可以安全地读）。

- 数据库连接：每个请求（或每个线程）使用一个连接？如果使用锁，我们可以在锁内部创建一个连接，执行操作，然后关闭。但创建连接开销较大，也可以使用一个全局连接，但需要确保连接在锁内使用。一个简单方法：在锁内，使用一个全局连接，但连接对象不是线程安全的，不过因为我们在锁内使用，所以安全。但注意：不同线程在获得锁后都会使用同一个连接，而 sqlite3 连接默认是线程安全的吗？设置 check_same_thread 参数：如果连接是在一个线程中创建并在另一个线程中使用，需要设置 check_same_thread=False。但由于我们只会在锁内使用，而锁控制同一时刻只有一个线程使用该连接，所以即使设置 check_same_thread=True（默认），只要创建连接的线程和使用的线程相同（主线程）？实际上锁内的线程可能是任意一个工作线程，所以连接在主线程创建，在工作线程使用会触发异常。所以我们需要设置 check_same_thread=False。而且连接是全局唯一的，只要在多线程中加锁使用，没问题。但是，如果连接一直保持打开，我们需要考虑关闭？在程序结束时关闭。更安全的方式是每个请求在锁内创建一个新连接，用完后关闭。但创建连接可能慢，但可以接受。我选择每个请求创建新连接（在锁内），这样更简单，避免全局连接的状态问题。同时启用 WAL 模式以提高读并发（但我们在写锁内，读也在锁内？实际上写锁只对写操作，读操作不需要锁，所以读操作可以并发，好处是读操作可以使用自己的连接读WAL。而写操作在锁内使用新连接，也使用WAL。这样没问题。

- 但注意：执行 GET /items 时，我们可能想去掉锁以提高性能，但需要确保清理动作也在合适时机？题目要求“每次请求前清理已过期且仍为 pending 的预约并释放库存。” 这意味着每个请求（包括GET）都需要先执行清理。清理是一个写操作，所以 GET 请求也需要写锁，因为它会修改数据库。所以 GET 请求也需要先获得写锁，执行清理，然后释放锁，然后读取数据（不需要锁）。但我们可以将清理和读取一起放在锁内？为了简单，把所有请求都加上锁（包括GET），这样虽然降低了并发，但保证一致性。预约服务的并发量通常不会很高，而且1000行代码内简单实现更重要。但也可以尝试：清理操作独立，GET 请求先清理（需要写锁），然后释放锁，再读（无锁）。但这样在清理释放锁后和读取前，可能有其他写操作修改数据库，导致读取数据可能不是清理后的最新数据？但清理后库存已经释放，其他线程可能会创建预约并减少库存，读取到中间状态可能可以接受（因为数据最终一致）。但题目没有严格要求严格的读一致性，所以我们可以让 GET 不持有锁，只是清理时需要锁，然后在清理后释放，再读。但读可能读到旧数据（因为写锁已释放，还没来得及读取，其他线程就改了）。但符合预期：读到的库存是某个时间点的快照。不过，清理释放锁后，另一个线程可能完成了新的预约，然后当前线程读到的库存包含了释放的库存？（因为清理已经完成，释放了库存，新预约可能马上占用了，所以读到的库存可能比实际少？实际上，清理后释放了库存，其他线程可能立即预约，读到的库存可能是清理后的库存减去新预约，或者清理前的库存？取决于读的时间点。但无论如何，我们不需要严格线性一致性。所以可以这样做。

但为了简单，我选择把所有请求都放在一个写锁下（包括GET），这样代码简单。但这样GET会串行化，可能影响性能。不过对于小型服务，可以接受。我会在每个请求处理函数开始时获取锁，执行所有数据库操作（包括清理和业务逻辑），最后释放锁。这样并发控制简单。

- 数据库表设计：使用 `CREATE TABLE IF NOT EXISTS` 创建表和索引。自动使用 `INTEGER PRIMARY KEY`，`expires_at` 存储为整数秒时间戳。

- 解析 JSON：使用 `json` 模块。

- 路由：解析路径和方法，分发到不同处理函数。

- 错误处理：返回合适的HTTP状态码和JSON错误。

- 同时处理 100-continue, 等等，但简化处理。

- 启动：`if __name__ == "__main__":` 监听 127.0.0.1:8080。

现在编写代码。我会列出代码要点：

1. 导入模块：http.server, json, sqlite3, threading, time, urllib.parse, os, sys
2. 定义全局变量：数据库文件默认 `inventory.db`，也可以环境变量。
3. 定义 `init_db()` 函数：创建表，创建索引等。
4. 定义 `clean_expired_reservations(conn)` 函数：删除过期 pending 预约并释放库存（使用事务）。
5. 定义 RequestHandler 类继承 `BaseHTTPRequestHandler`。
   - 重写 `do_GET`, `do_POST`。
   - 解析路径，使用 `urlparse` 获取 path 和 query。
   - 根据 path 分发。
   - 所有请求先执行清理（但注意 POST 也可能需要先清理），我们将清理放在每个处理函数内。
   - 注意：创建预约时，需要先清理过期，然后再检查库存。
   - 数据库操作使用 `with db_lock:` 保护。
   - 写返回 JSON，设置 Content-Type: application/json。
6. 处理函数：
   - `handle_get_items()`: 返回所有商品列表（包括 id, name, stock_total, stock_available）。使用 `SELECT * FROM items`。
   - `handle_create_item()`: 读取 body JSON，验证 name, stock_total 存在且为正整数。插入新商品。
   - `handle_create_reservation()`: 读取 body，验证 item_id, quantity, ttl_seconds（正整数）。先清理过期，然后检查库存是否足够（SELECT stock_available），然后创建预约并更新库存（UPDATE），注意使用事务。如果库存不足，返回409。计算 expires_at = current_time + ttl_seconds。
   - `handle_confirm_reservation(id)` 和 `handle_cancel_reservation(id)`: 根据ID查找预约，检查状态（必须是pending），然后更新。确认：status改为confirmed，不释放库存。取消：status改为cancelled，释放库存（增加stock_available）。
7. 辅助函数：读取 body，解析 JSON，返回错误响应。
8. 错误响应：`send_error_json(status, message)` 方法。
9. 注意：在并发下，创建预约时，读库存和写预约+更新库存需要在一个事务中原子执行。使用 `SELECT ... FOR UPDATE` 在sqlite中不支持，但事务和写锁定会序列化。我们使用 `BEGIN IMMEDIATE` 或 `BEGIN EXCLUSIVE` 防止其他写操作。在锁内，使用 `conn.isolation_level` 设置为 'IMMEDIATE' 或者使用 `conn.execute("BEGIN IMMEDIATE")`。但简单的 `with conn:` 会以 `BEGIN` 开始，默认是 DEFERRED，在写操作时才升级。但如果在事务中先读后写，可能因为并发导致死锁（读写锁）。为了安全，我们可以使用 `conn.execute("BEGIN IMMEDIATE")` 显式。或者直接用 `conn.isolation_level = 'IMMEDIATE'` 设置。在事务内读数据，如果其他事务正在写，会等待。由于我们有全局锁，其实不需要担心并发事务，因为只有一个线程在写。但是为了代码健壮，我们可以使用 `BEGIN IMMEDIATE`。

由于我们有全局锁，其实不需要考虑事务的隔离级别，因为同一时刻只有一个写事务。但是，如果我们将清理和业务操作放在一个事务中，由于锁的存在，没问题。

10. 注意：POST /reservations 路径可能包含参数？根据题目，是 `POST /reservations` 创建，`POST /reservations/{id}/confirm` 和 `/cancel`。我们需要使用正则或字符串分割解析ID。

11. 实现细节：HTTP 请求体读取，需要处理 Content-Length。使用 `self.rfile.read(length)`。

12. 错误处理：如果请求体不是合法JSON或缺少字段，返回400。如果item_id不存在，返回404？题目没有明确，但可以返回404或400。我们可以返回404。

13. 清理函数：在每次请求处理开始时调用（在锁内）。但注意：清理操作本身也是修改数据库，需要事务。

14. 数据库初始化：在启动时，全局连接初始化？也可以每次请求创建连接。但为了性能，可以在启动时创建连接，设置WAL模式，然后所有请求使用该连接（在锁内）。为了避免线程问题，连接必须设置 check_same_thread=False，然后加锁。我们采用这种方案：全局连接 `db_conn = sqlite3.connect(DATABASE, check_same_thread=False)`，并在启动时初始化表。注意：`check_same_thread=False` 允许在不同线程中使用，但需要我们自己加锁保护。我们使用 `db_lock` 来序列化所有数据库访问（包括读）。所以所有 `db_conn` 的调用都要在锁内。这样简单。

但注意：在锁内使用同一个连接时，如果发生错误或连接断开，我们需要处理。简单起见，我们使用此方案。

15. 代码结构：

```python
#!/usr/bin/env python3
import http.server
import json
import sqlite3
import threading
import time
import urllib.parse
import os

DATABASE = 'inventory.db'
db_lock = threading.Lock()
db_conn = None

def init_db():
    global db_conn
    db_conn = sqlite3.connect(DATABASE, check_same_thread=False)
    db_conn.row_factory = sqlite3.Row  # for dict-like access
    db_conn.execute("PRAGMA journal_mode=WAL")
    db_conn.execute("PRAGMA foreign_keys=ON")
    db_conn.execute("""CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        stock_total INTEGER NOT NULL,
        stock_available INTEGER NOT NULL
    )""")
    db_conn.execute("""CREATE TABLE IF NOT EXISTS reservations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        status TEXT NOT NULL DEFAULT 'pending',
        expires_at INTEGER NOT NULL,
        created_at INTEGER NOT NULL,
        FOREIGN KEY (item_id) REFERENCES items(id)
    )""")
    db_conn.execute("CREATE INDEX IF NOT EXISTS idx_reservations_status ON reservations(status)")
    db_conn.commit()

def clean_expired():
    """Clean expired pending reservations and release stock. Must be called inside db_lock."""
    now = int(time.time())
    # Find expired pending reservations
    cur = db_conn.execute("SELECT id, item_id, quantity FROM reservations WHERE status='pending' AND expires_at <= ?", (now,))
    rows = cur.fetchall()
    if rows:
        # Start immediate transaction
        db_conn.execute("BEGIN IMMEDIATE")
        try:
            for row in rows:
                # Update item stock
                db_conn.execute("UPDATE items SET stock_available = stock_available + ? WHERE id = ?", (row['quantity'], row['item_id']))
                # Update reservation status to expired
                db_conn.execute("UPDATE reservations SET status='expired' WHERE id = ?", (row['id'],))
            db_conn.commit()
        except Exception:
            db_conn.rollback()
            raise
```

然后在每个处理函数中，我们都要先调用 `clean_expired()`。注意 `clean_expired` 假设已经在锁内。我们每个处理函数都会先获取锁，然后执行清理和业务逻辑。

对于 GET /items，我们不需要写事务，但清理是写操作，所以仍然需要锁。

对于 POST /reservations，我们需要读取库存，检查，插入，更新库存。使用事务。

对于确认/取消，也需要事务。

注意：在清理过期时，我们使用了 `BEGIN IMMEDIATE` 以防止其他写操作，其实在锁内不需要，但为了清晰保留。

另外，注意：当清理过期时，如果同一个商品有多个过期预约，我们逐个释放库存。这可能会导致库存超过 stock_total，因为可能同时有预约取消？但初始 stock_available <= stock_total，释放后应该正确。但如果一个商品被多次释放，没问题。

另外，创建预约时，需要确保 stock_available >= quantity。使用 `SELECT stock_available FROM items WHERE id = ?`，检查。

确认预约：将 status 改为 'confirmed'。不释放库存，也不修改库存。

取消预约：将 status 改为 'cancelled'，释放库存 (`UPDATE items SET stock_available = stock_available + ?`)。

这些操作都需要在事务中进行，以保证一致性。

由于我们在单个连接上操作，使用 `db_conn.execute` 默认会自动开始一个事务（如果 isolation_level 不是 None？默认是 ''，即隐式事务）。但为了显式控制，我们使用 `db_conn.execute("BEGIN")` 和 `db_conn.commit()`。我们可以使用 `with db_conn:` 上下文管理器，在 Python 3.7+ 中，`sqlite3.Connection.__enter__` 会开始一个事务，`__exit__` 提交或回滚。但注意：在锁内，需要确保事务不会覆盖。我们使用 `with db_conn:` 包裹业务逻辑，自动处理。

但要注意：`clean_expired` 函数内部也使用了 `db_conn.execute("BEGIN IMMEDIATE")`，然后提交。如果我们在同一锁内先调用 `clean_expired`，然后进行业务操作，那么 clean_expired 提交了事务，业务操作再开始一个新事务，没问题。但如果有多个操作，我们可以将整个请求（清理+业务）放在一个事务中。但为了逻辑清晰，我们分别处理。不过，如果业务操作失败，清理已经提交，可能导致不一致？例如，清理成功，但创建预约失败，那么清理的释放已经生效，一致。但假设创建预约需要依赖清理后的库存，所以先清理再创建是合理的。如果创建预约失败，清理已经提交，没有影响。所以没问题。

但注意：`clean_expired` 提交后，如果有其他线程在锁外读数据，可能会看到已经清理的状态。因为锁只控制写，读在其他线程可能同时进行，但读取到的数据可能包含清理后的结果（因为WAL模式
````

## Assistant

````markdown
）。没问题。

我们将整个处理流程写为：

```python
with db_lock:
    clean_expired()
    if path == '/items' and method == 'GET':
        c = db_conn.execute("SELECT * FROM items")
        items = [dict(row) for row in c.fetchall()]
        self.send_json(200, items)
    elif path == '/items' and method == 'POST':
        # parse body
        # insert
        ...
```

但是，对于 POST /reservations/{id}/confirm，我们需要解析路径，提取ID。

注意：在锁内调用 `clean_expired`，但 `clean_expired` 内部使用了 `db_conn.execute` 和提交。这些操作在同一连接上，由于我们有锁保护，没问题。

还需要处理错误：比如 item_id 不存在时返回 404。

另外，需要处理 body 读取：`self.headers.get('Content-Length')`，如果没有 Content-Length 或为0，返回400。

设置响应头：`self.send_response(status)`, `self.send_header('Content-Type', 'application/json')`, `self.end_headers()`, `self.wfile.write(json.dumps(...).encode())`。

注意：对于 HEAD 请求和 100-continue，我们可以忽略或者处理。我们简单处理：对于 POST 请求，先读取内容，忽略 100-continue。

现在编写完整代码。注意不要超过1000行，应该不会。

我们来实现。添加注释适量。

我将在代码中区分处理函数。

另外，考虑可扩展性：使用字典映射路径到处理函数，但为了简单，直接用 if-else。

另外，注意处理整数转换时可能引发的异常，给400错误。

我还会在响应中包含 `error` 字段。

开始编写代码。</think>```python
#!/usr/bin/env python3
"""
Single file HTTP API inventory reservation service.
Uses only Python 3 standard library.
"""

import http.server
import json
import sqlite3
import threading
import time
import urllib.parse
import os

# Global settings
DATABASE = 'inventory.db'
HOST = '127.0.0.1'
PORT = 8080

# Global lock and database connection
db_lock = threading.Lock()
db_conn = None


def init_db():
    """Initialize the database and create tables if they don't exist."""
    global db_conn
    if db_conn is not None:
        db_conn.close()
    db_conn = sqlite3.connect(DATABASE, check_same_thread=False)
    db_conn.row_factory = sqlite3.Row
    db_conn.execute("PRAGMA journal_mode=WAL")
    db_conn.execute("PRAGMA foreign_keys=ON")
    db_conn.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            stock_total INTEGER NOT NULL,
            stock_available INTEGER NOT NULL
        )
    """)
    db_conn.execute("""
        CREATE TABLE IF NOT EXISTS reservations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            expires_at INTEGER NOT NULL,
            created_at INTEGER NOT NULL,
            FOREIGN KEY (item_id) REFERENCES items(id)
        )
    """)
    db_conn.execute("CREATE INDEX IF NOT EXISTS idx_reservations_status ON reservations(status)")
    db_conn.commit()


def clean_expired():
    """
    Release stock for expired pending reservations.
    Must be called inside db_lock.
    """
    now = int(time.time())
    cur = db_conn.execute(
        "SELECT id, item_id, quantity FROM reservations WHERE status='pending' AND expires_at <= ?",
        (now,)
    )
    expired = cur.fetchall()
    if not expired:
        return

    # Use an immediate transaction to avoid deadlocks
    db_conn.execute("BEGIN IMMEDIATE")
    try:
        for row in expired:
            db_conn.execute(
                "UPDATE items SET stock_available = stock_available + ? WHERE id = ?",
                (row['quantity'], row['item_id'])
            )
            db_conn.execute(
                "UPDATE reservations SET status='expired' WHERE id = ?",
                (row['id'],)
            )
        db_conn.commit()
    except Exception:
        db_conn.rollback()
        raise


class RequestHandler(http.server.BaseHTTPRequestHandler):
    """HTTP request handler for the inventory reservation API."""

    # -------------------------------------------------------------------
    # Utility methods
    # -------------------------------------------------------------------

    def send_json(self, status, data):
        """Send a JSON response with given HTTP status."""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        body = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.wfile.write(body)

    def send_error_json(self, status, message):
        """Send an error JSON response."""
        self.send_json(status, {'error': message})

    def read_body_json(self):
        """Read request body and parse as JSON. Return dict or None on error."""
        content_length = self.headers.get('Content-Length')
        if content_length is None:
            return None
        try:
            length = int(content_length)
        except (ValueError, TypeError):
            return None
        if length == 0:
            return None
        try:
            raw = self.rfile.read(length)
            return json.loads(raw.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError, OSError):
            return None

    def parse_path(self):
        """Parse the request path, returning (base_path, path_id) or similar."""
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path.rstrip('/')
        return path

    # -------------------------------------------------------------------
    # HTTP method handlers
    # -------------------------------------------------------------------

    def do_GET(self):
        path = self.parse_path()
        if path == '/items':
            self.handle_get_items()
        else:
            self.send_error_json(404, 'Not Found')

    def do_POST(self):
        path = self.parse_path()
        # Route to appropriate handler
        if path == '/items':
            self.handle_create_item()
        elif path == '/reservations':
            self.handle_create_reservation()
        elif path.startswith('/reservations/') and path.endswith('/confirm'):
            # Extract reservation id
            parts = path.split('/')
            if len(parts) == 4 and parts[1] == 'reservations' and parts[3] == 'confirm':
                try:
                    res_id = int(parts[2])
                    self.handle_confirm_reservation(res_id)
                except ValueError:
                    self.send_error_json(400, 'Invalid reservation id')
            else:
                self.send_error_json(404, 'Not Found')
        elif path.startswith('/reservations/') and path.endswith('/cancel'):
            parts = path.split('/')
            if len(parts) == 4 and parts[1] == 'reservations' and parts[3] == 'cancel':
                try:
                    res_id = int(parts[2])
                    self.handle_cancel_reservation(res_id)
                except ValueError:
                    self.send_error_json(400, 'Invalid reservation id')
            else:
                self.send_error_json(404, 'Not Found')
        else:
            self.send_error_json(404, 'Not Found')

    # -------------------------------------------------------------------
    # API handlers (all are called within db_lock after cleaning expired)
    # -------------------------------------------------------------------

    def handle_get_items(self):
        """GET /items"""
        with db_lock:
            clean_expired()
            cursor = db_conn.execute("SELECT id, name, stock_total, stock_available FROM items")
            items = [dict(row) for row in cursor.fetchall()]
        self.send_json(200, items)

    def handle_create_item(self):
        """POST /items"""
        data = self.read_body_json()
        if data is None:
            self.send_error_json(400, 'Invalid JSON body')
            return
        name = data.get('name')
        stock_total = data.get('stock_total')
        if not name or not isinstance(stock_total, int) or stock_total < 0:
            self.send_error_json(400, 'name (string) and stock_total (non-negative int) required')
            return
        # Ensure name is not empty
        if not name.strip():
            self.send_error_json(400, 'name must not be empty')
            return

        with db_lock:
            clean_expired()
            db_conn.execute("BEGIN IMMEDIATE")
            try:
                db_conn.execute(
                    "INSERT INTO items (name, stock_total, stock_available) VALUES (?, ?, ?)",
                    (name.strip(), stock_total, stock_total)
                )
                db_conn.commit()
                # Fetch the created item
                cursor = db_conn.execute(
                    "SELECT id, name, stock_total, stock_available FROM items WHERE id = last_insert_rowid()"
                )
                item = dict(cursor.fetchone())
            except Exception:
                db_conn.rollback()
                self.send_error_json(500, 'Database error')
                return
        self.send_json(201, item)

    def handle_create_reservation(self):
        """POST /reservations"""
        data = self.read_body_json()
        if data is None:
            self.send_error_json(400, 'Invalid JSON body')
            return
        item_id = data.get('item_id')
        quantity = data.get('quantity')
        ttl_seconds = data.get('ttl_seconds')

        # Validate parameters
        if not isinstance(item_id, int) or not isinstance(quantity, int) or not isinstance(ttl_seconds, int):
            self.send_error_json(400, 'item_id, quantity, ttl_seconds must be integers')
            return
        if quantity <= 0 or ttl_seconds <= 0:
            self.send_error_json(400, 'quantity and ttl_seconds must be positive')
            return

        with db_lock:
            clean_expired()
            # Check item existence and stock
            cursor = db_conn.execute(
                "SELECT id, stock_available FROM items WHERE id = ?",
                (item_id,)
            )
            item = cursor.fetchone()
            if item is None:
                self.send_error_json(404, 'Item not found')
                return
            if item['stock_available'] < quantity:
                self.send_error_json(409, 'Insufficient stock')
                return

            # Create reservation and reduce stock in a transaction
            db_conn.execute("BEGIN IMMEDIATE")
            try:
                now = int(time.time())
                expires_at = now + ttl_seconds
                db_conn.execute(
                    "INSERT INTO reservations (item_id, quantity, status, expires_at, created_at) VALUES (?, ?, 'pending', ?, ?)",
                    (item_id, quantity, expires_at, now)
                )
                db_conn.execute(
                    "UPDATE items SET stock_available = stock_available - ? WHERE id = ?",
                    (quantity, item_id)
                )
                db_conn.commit()
                # Fetch the created reservation
                cursor = db_conn.execute(
                    "SELECT id, item_id, quantity, status, expires_at, created_at FROM reservations WHERE id = last_insert_rowid()"
                )
                reservation = dict(cursor.fetchone())
            except Exception:
                db_conn.rollback()
                self.send_error_json(500, 'Database error')
                return
        self.send_json(201, reservation)

    def handle_confirm_reservation(self, reservation_id):
        """POST /reservations/{id}/confirm"""
        with db_lock:
            clean_expired()
            # Find reservation
            cursor = db_conn.execute(
                "SELECT id, status FROM reservations WHERE id = ?",
                (reservation_id,)
            )
            row = cursor.fetchone()
            if row is None:
                self.send_error_json(404, 'Reservation not found')
                return
            if row['status'] != 'pending':
                self.send_error_json(409, f'Reservation is already {row["status"]}')
                return

            db_conn.execute("BEGIN IMMEDIATE")
            try:
                db_conn.execute(
                    "UPDATE reservations SET status='confirmed' WHERE id = ?",
                    (reservation_id,)
                )
                db_conn.commit()
            except Exception:
                db_conn.rollback()
                self.send_error_json(500, 'Database error')
                return
        self.send_json(200, {'message': 'Reservation confirmed', 'id': reservation_id})

    def handle_cancel_reservation(self, reservation_id):
        """POST /reservations/{id}/cancel"""
        with db_lock:
            clean_expired()
            # Find reservation with status and item_id
            cursor = db_conn.execute(
                "SELECT id, status, item_id, quantity FROM reservations WHERE id = ?",
                (reservation_id,)
            )
            row = cursor.fetchone()
            if row is None:
                self.send_error_json(404, 'Reservation not found')
                return
            if row['status'] != 'pending':
                self.send_error_json(409, f'Reservation is already {row["status"]}')
                return

            db_conn.execute("BEGIN IMMEDIATE")
            try:
                # Cancel reservation and release stock
                db_conn.execute(
                    "UPDATE reservations SET status='cancelled' WHERE id = ?",
                    (reservation_id,)
                )
                db_conn.execute(
                    "UPDATE items SET stock_available = stock_available + ? WHERE id = ?",
                    (row['quantity'], row['item_id'])
                )
                db_conn.commit()
            except Exception:
                db_conn.rollback()
                self.send_error_json(500, 'Database error')
                return
        self.send_json(200, {'message': 'Reservation cancelled', 'id': reservation_id})


def main():
    # Initialize database
    init_db()
    server = http.server.HTTPServer((HOST, PORT), RequestHandler)
    print(f'Server listening on {HOST}:{PORT}')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        if db_conn:
            db_conn.close()


if __name__ == '__main__':
    main()
```
````
