# Generation Transcript

- Case: `zh_code_be_001`
- Language group: `zh`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `1`
- Thinking mode: `think-max`
- Thinking strength: `max`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 92.19112
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 442, "total_tokens": 9533, "completion_tokens": 9091, "prompt_tokens_details": null}`
- Prompt tokens: 442
- Completion tokens: 9091
- Total tokens: 9533

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

```text
我们被要求编写一个单文件HTTP API服务，使用Python 3标准库，没有任何第三方库。我们需要实现一个库存预约服务，使用sqlite3作为数据库，并且必须处理并发。我们需要使用http.server模块或类似的东西。因为不能使用第三方库，我们必须使用Python内置的HTTP服务器。通常我们使用http.server模块中的HTTPServer和BaseHTTPRequestHandler。但是，我们需要处理不同的HTTP方法，并解析JSON请求体，还需要数据库操作。此外，我们需要确保并发安全。由于http.server是同步的（一个请求处理完毕才处理下一个），但可能会使用线程池（如ThreadingHTTPServer）来处理并发请求。为了处理并发，我们应该使用ThreadingHTTPServer，这样每个请求在单独的线程中处理。但是，我们需要确保数据库操作的线程安全：sqlite3连接不能在线程之间共享，通常每个线程使用单独的连接，或者使用连接池并加锁。我们可以使用一个全局的线程锁来保护数据库写入操作，或者每个请求创建新连接（sqlite3连接可以在线程间共享如果设置了check_same_thread=False，但通常不推荐并发写入除非使用序列化）。为了简单，我们可以使用一个全局的锁，在线程之间同步数据库访问。sqlite3本身支持WAL模式或多线程模式，但为了更安全，我们可以使用一个threading.Lock来保护所有数据库操作。

我们需要实现以下端点：
- GET /items
- POST /items
- POST /reservations
- POST /reservations/{id}/confirm
- POST /reservations/{id}/cancel

此外，每次请求前清理过期pending预约。这可以在每个请求的handle方法中调用清理函数。

设计：
- 使用BaseHTTPRequestHandler的子类。
- 覆盖do_GET和do_POST方法。
- 解析路径和方法，分发到不同的处理函数。
- 使用json模块解析请求体和生成响应。
- 数据库：表结构：
  - items: id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, stock_total INTEGER NOT NULL, stock_available INTEGER NOT NULL
  - reservations: id INTEGER PRIMARY KEY AUTOINCREMENT, item_id INTEGER NOT NULL, quantity INTEGER NOT NULL, status TEXT NOT NULL DEFAULT 'pending', expires_at TEXT (ISO format), created_at TEXT (ISO format)
- 使用时间戳：expires_at存储为ISO 8601字符串（方便比较）。
- ttl_seconds参数决定expires_at = now + ttl_seconds。
- 清理：DELETE FROM reservations WHERE status='pending' AND expires_at < datetime('now')，然后更新对应items的stock_available（需要先查询这些预约占用的库存再删除，或者使用更复杂的逻辑）。我们可以先选择所有过期的pending预约，然后依次释放库存（使用事务）。
- 因为可能有并发，我们需要使用事务来保证一致性。使用locking。

响应格式：
- 成功：返回JSON数据，状态码200或其他适当状态码（201 for created）。
- 错误：返回包含"error"字段的JSON，适当的状态码（400, 404, 409等）。

路径解析：
- 我们可以在do_GET和do_POST中解析self.path，使用urllib.parse。
- 对于/reservations/{id}/confirm和/reservations/{id}/cancel，匹配路径格式。

设计思路：

1. 使用ThreadingHTTPServer（在Python 3.7+中可用，但需要从socketserver导入ThreadingMixIn，结合HTTPServer）。或者直接使用ThreadingHTTPServer（Python 3.7+内置）。为了兼容更早版本，我们可以手动混合。但题目要求Python 3，我们可以假设使用较新版本。我会使用http.server.ThreadingHTTPServer（在Python 3.7+中可用，但文档说从Python 3.7开始，但实际上在3.7中可用）。如果担心兼容性，可以自己定义class ThreadedHTTPServer(ThreadingMixIn, HTTPServer): pass。我选择这个以确保线程安全。

2. 数据库：初始化时创建表。使用一个全局Connection对象？在单进程多线程中，不能共享连接，因为sqlite3不是线程安全的。我们可以让每个请求创建新的连接，并在完成时关闭。但是创建连接有开销，但可以接受。或者在每个线程中维护一个本地连接。最安全和简单的方式：使用一个全局的锁，并在每个请求中创建一个新的连接（或者从sqlite3中获取一个连接，并设置check_same_thread=False，然后用锁保护所有操作）。使用锁加本地连接（每个请求创建新连接）是简单的。

更好的方法是使用一个连接池，但标准库没有。我们使用每个请求创建新连接，并使用一个threading.Lock确保序列化数据库访问，避免多个连接同时写入冲突。或者我们可以使用单个连接并设置check_same_thread=False，但需要确保只有一个线程在写（通过锁）。我们可以使用全局锁保护所有数据库操作。我选择使用单个连接（全局），设置check_same_thread=False，并在线程中使用锁。这样只需要一个连接，不需要频繁创建。但要注意事务：锁可以确保同一时间只有一个线程使用连接。

我选择使用全局连接和全局锁。连接在启动时创建，用于所有请求。在每个请求处理中，使用lock.acquire()，然后使用连接进行操作，最后释放。这样可以避免多线程同时访问连接。

3. 清理过期预约：在每个请求开始时执行。要注意在清理时也可能需要锁。我们可以在每个请求处理函数中首先调用一个清理函数（在锁保护下）。

4. 处理POST的请求体：使用Content-Length读取数据，然后json.loads。

5. 路径匹配：使用正则或字符串方法。用re模块。

6. 错误处理：返回JSON错误。设置状态码通过send_response，然后send_header等。

代码结构：

Imports:
- http.server
- json
- sqlite3
- threading
- urllib.parse
- datetime
- time
- re

全局变量：
- DB_NAME = 'reservations.db'
- lock = threading.Lock()
- conn: sqlite3.Connection (在__main__中初始化，并传递给handler类，或者作为全局使用)

我们可以定义一个函数create_tables()来创建表。

定义处理函数：
- handle_list_items()
- handle_create_item()
- handle_create_reservation()
- handle_confirm_reservation(reservation_id)
- handle_cancel_reservation(reservation_id)

路由分发：
- do_GET: 如果path == '/items'则handle_list_items，否则返回404。
- do_POST: 解析path，匹配不同模式。

注意：我们还需要处理OPTIONS? 不需要。

我们需要设置响应头Content-Type: application/json。

一些具体实现细节：

- 在创建Item时，stock_available应该设置为stock_total。
- 在创建Reservation时，需要检查库存是否足够（item的stock_available >= quantity），如果不够返回409。如果足够，扣除stock_available，创建预约记录（status='pending'，expires_at = current_time + ttl_seconds，created_at = now）。使用事务：先select item锁住？事务和锁配合使用。
- 确认预约：找到预约，必须是pending状态，否则错误。如果是pending，将status改为confirmed，并记录确认时间？题目没有要求确认时间，但可以更新status。需要释放锁？确认后，库存不再释放（保持已扣除）。所以不需要更新stock_available。
- 取消预约：找到预约，必须是pending（或confirmed？通常只有pending可以取消？题目说取消预约，释放库存。没有指定状态，但一般只有pending可以取消。如果已经confirmed，可能不允许取消。我们假设只有pending可以取消。如果状态不是pending，返回错误。对于取消，需要释放库存：将item的stock_available加回预约数量，并将预约状态改为cancelled或删除？题目没有指定状态变化，但我们可以保留记录，设置status为'cancelled'。
- 清理过期预约：找出所有status='pending'且expires_at < now的记录。对于每条记录，需要释放库存：将对应item的stock_available加回quantity。然后删除这些记录或将status改为expired。题目说“清理已过期且仍为 pending 的预约并释放库存”。我们应当将这些预约状态改为'expired'并释放库存。但为了简单，我们可以直接删除记录并释放库存。或者保留记录但设置status='expired'。我更倾向于设置status='expired'，这样历史可查。同时释放库存。注意：在清理时，也要考虑并发，所以要在一个事务中完成。

关于时间比较：我们将expires_at存储为ISO格式字符串（如'2023-01-01T12:00:00'），这样可以用字符串比较，但要注意时区。我们使用UTC时间。在Python中，使用datetime.utcnow()或time.time()。我们可以存储Unix时间戳（整数），比较更方便。我选择存储Unix时间戳（整数），因为比较快且避免时区问题。expires_at存储为整数秒（自epoch）。所以创建预约时，expires_at = int(time.time()) + ttl_seconds。清理时，DELETE FROM reservations WHERE status='pending' AND expires_at < ? (当前时间戳)。

更简单：使用SQLite的datetime函数：expires_at存储为TEXT VARCHAR，比较时使用strftime。但整数更快。我们就用整数。

所以字段定义：
reservations:
- id INTEGER PRIMARY KEY AUTOINCREMENT
- item_id INTEGER NOT NULL
- quantity INTEGER NOT NULL
- status TEXT NOT NULL DEFAULT 'pending'
- expires_at INTEGER NOT NULL (Unix timestamp)
- created_at INTEGER NOT NULL

items:
- id INTEGER PRIMARY KEY AUTOINCREMENT
- name TEXT NOT NULL UNIQUE (可选)
- stock_total INTEGER NOT NULL
- stock_available INTEGER NOT NULL

创建表的SQL。

现在，编写完整的代码。

首先导入模块。

定义全局变量：
DB = 'reservations.db'
lock = threading.Lock()
conn = None (在main中初始化)

但是，Handler类需要访问lock和conn，我们可以将它们作为类变量或模块级变量。由于是单文件，模块级变量即可。

我们需要创建表的函数。

定义RequestHandler类，继承BaseHTTPRequestHandler。

覆盖do_GET和do_POST。

在do_GET中：
if self.path == '/items':
    self.handle_list_items()
else:
    self.send_error(404, 'Not Found')

在do_POST中：
使用urlparse解析路径，去掉查询参数。
path = urllib.parse.urlparse(self.path).path

然后匹配：
if path == '/items':
    self.handle_create_item()
elif re.match(r'^/reservations/\d+/confirm$', path):
    reservation_id = int(path.split('/')[2])
    self.handle_confirm_reservation(reservation_id)
elif re.match(r'^/reservations/\d+/cancel$', path):
    reservation_id = int(path.split('/')[2])
    self.handle_cancel_reservation(reservation_id)
elif path == '/reservations':
    self.handle_create_reservation()
else:
    self.send_error(404, 'Not Found')

在每次处理请求前（即在具体方法开始时），先调用cleanup_expired_reservations()，它会在锁保护下执行。

现在定义辅助方法：
- read_json_body(): 从请求读取JSON，解析并返回字典，如果出错返回None。
- send_json(data, status=200): 发送JSON响应。
- send_error(status, message): 发送JSON错误响应。

具体处理函数：

handle_list_items:
   lock.acquire()
   try:
       cursor = conn.execute("SELECT id, name, stock_total, stock_available FROM items")
       items = [{'id': row[0], 'name': row[1], 'stock_total': row[2], 'stock_available': row[3]} for row in cursor.fetchall()]
       self.send_json(items)
   finally:
       lock.release()

handle_create_item:
   body = self.read_json_body()
   if not body or 'name' not in body or 'stock_total' not in body:
       self.send_error(400, 'Missing parameters')
       return
   name = body['name']
   try:
       stock_total = int(body['stock_total'])
   except (ValueError, TypeError):
       self.send_error(400, 'Invalid stock_total')
       return
   lock.acquire()
   try:
       cursor = conn.execute("INSERT INTO items (name, stock_total, stock_available) VALUES (?, ?, ?)", (name, stock_total, stock_total))
       conn.commit()
       item_id = cursor.lastrowid
       self.send_json({'id': item_id, 'name': name, 'stock_total': stock_total, 'stock_available': stock_total}, status=201)
   except sqlite3.IntegrityError as e:
       self.send_error(400, f'Item could not be created: {str(e)}')
   finally:
       lock.release()

handle_create_reservation:
   body = self.read_json_body()
   if not body or 'item_id' not in body or 'quantity' not in body or 'ttl_seconds' not in body:
       self.send_error(400, 'Missing parameters')
       return
   item_id = body['item_id']
   quantity = body['quantity']
   ttl_seconds = body['ttl_seconds']
   # 验证类型
   try:
       item_id = int(item_id)
       quantity = int(quantity)
       ttl_seconds = int(ttl_seconds)
   except (ValueError, TypeError):
       self.send_error(400, 'Invalid parameters')
       return
   if quantity <= 0 or ttl_seconds <= 0:
       self.send_error(400, 'Invalid quantity or ttl_seconds')
       return

   lock.acquire()
   try:
       # 先清理过期，确保库存准确
       cleanup_expired()
       # 查询商品
       cursor = conn.execute("SELECT id, stock_available FROM items WHERE id = ?", (item_id,))
       row = cursor.fetchone()
       if not row:
           self.send_error(404, 'Item not found')
           return
       stock_available = row[1]
       if stock_available < quantity:
           self.send_error(409, 'Insufficient stock')
           return
       # 扣除库存
       now = int(time.time())
       expires_at = now + ttl_seconds
       conn.execute("UPDATE items SET stock_available = stock_available - ? WHERE id = ?", (quantity, item_id))
       conn.execute("INSERT INTO reservations (item_id, quantity, status, expires_at, created_at) VALUES (?, ?, 'pending', ?, ?)", (item_id, quantity, expires_at, now))
       conn.commit()
       # 返回预约信息
       reservation_id = cursor.lastrowid? 需要获取上一条插入的id，但之前执行了update，lastrowid可能不对。我们可以分别获取：在执行INSERT后，cursor对于INSERT操作，lastrowid是刚插入的行的id。但是conn.execute返回的cursor会改变，所以我们需要在INSERT后获取cursor.lastrowid。所以应该：
       cursor = conn.execute("INSERT INTO reservations ...") 然后 conn.commit() ，接着 reservation_id = cursor.lastrowid。
       修改流程：
       cursor = conn.execute("UPDATE ...")
       # 没有直接返回lastrowid
       应该先执行INSERT，再执行UPDATE？但是UPDATE需要先检查库存，然后扣除。更好的方式是先INSERT，然后UPDATE？不行，因为可能库存不足。我们可以在一个事务中先SELECT...FOR UPDATE？SQLite不支持。我们使用锁确保序列化，所以先检查库存，然后扣除，然后INSERT。为了获取lastrowid，我们可以在INSERT后获取conn.execute("SELECT last_insert_rowid()")，或者将INSERT放在最后，然后cursor = conn.execute("INSERT ...") 然后 commit，使用cursor.lastrowid。所以顺序：检查库存（SELECT），然后扣除（UPDATE），然后INSERT（最后）。在INSERT后，cursor.lastrowid可用。
   except Exception as e:
       conn.rollback()
       self.send_error(500, str(e))
   finally:
       lock.release()

更细致：

def handle_create_reservation(self):
    ...
    lock.acquire()
    try:
        cleanup_expired()  # 这本身会使用conn，注意锁已经获取
        # 开始事务
        conn.execute("BEGIN")
        cursor = conn.execute("SELECT stock_available FROM items WHERE id = ?", (item_id,))
        row = cursor.fetchone()
        if not row:
            conn.execute("ROLLBACK")
            self.send_error(404, 'Item not found')
            return
        if row[0] < quantity:
            conn.execute("ROLLBACK")
            self.send_error(409, 'Insufficient stock')
            return
        # 扣除库存
        conn.execute("UPDATE items SET stock_available = stock_available - ? WHERE id = ?", (quantity, item_id))
        # 创建预约
        now = int(time.time())
        expires_at = now + ttl_seconds
        cursor = conn.execute("INSERT INTO reservations (item_id, quantity, status, expires_at, created_at) VALUES (?, ?, 'pending', ?, ?)", (item_id, quantity, expires_at, now))
        reservation_id = cursor.lastrowid
        conn.commit()
        # 返回
        self.send_json({
            'id': reservation_id,
            'item_id': item_id,
            'quantity': quantity,
            'status': 'pending',
            'expires_at': expires_at,
            'created_at': now
        }, status=201)
    except Exception as e:
        conn.rollback()
        self.send_error(500, str(e))
    finally:
        lock.release()

注意：conn.execute("BEGIN")是隐式开始的？在Python sqlite3中，默认是自动提交模式，当执行INSERT/UPDATE/DELETE时自动提交。如果手动使用BEGIN，需要设置conn.isolation_level=None，或者直接使用conn.execute("BEGIN")，但必须在non-autocommit模式下。或者我们可以使用conn.execute("BEGIN")，但默认的isolation_level=''（ deferred）? 在Python sqlite3中，默认是开启了事务的，但你可以通过设置isolation_level来控制。为了明确地管理事务，我们可以在连接创建后设置conn.isolation_level = None（手动提交模式），然后使用BEGIN/COMMIT/ROLLBACK。这是推荐的方式。否则，默认情况下，每个语句都自动提交？实际上，在默认的isolation_level（''）下，sqlite3会在执行DML之前隐式开启一个事务，直到调用commit或rollback。但是，这可能导致多个语句在不同的自动事务中。为了安全，我们设置isolation_level=None，然后手动管理事务。

我在初始化连接时设置isolation_level=None。

然后每个处理函数中，显式begin和commit。

在handle_create_item中我们也需要事务吗？单个INSERT，可以使用自动模式，但为了与其他一致，也可以手动。

在handle_list_items中不需要事务，只是SELECT。

confirm和cancel也需要事务。

confirm:
- 检查预约存在且状态为pending
- 更新状态为confirmed
- 不需要释放库存
- 返回预约对象

cancel:
- 检查预约存在且状态为pending
- 更新状态为cancelled
- 释放库存：UPDATE items SET stock_available = stock_available + quantity WHERE id = item_id
- 返回预约对象或成功消息

注意：如果预约已经confirmed或cancelled，应返回错误（比如400）。

cleanup_expired函数：
lock应该已经被持有（在调用时外部已经加锁），或者我们可以设计为内部加锁。但为了减少锁获取次数，在每个处理函数开始处我们获取锁，然后调用cleanup，之后执行具体操作。所以cleanup不会单独获取锁，假设锁已经由调用者持有。

实现cleanup_expired：
def cleanup_expired():
    now = int(time.time())
    # 选择所有过期pending预约
    cursor = conn.execute("SELECT id, item_id, quantity FROM reservations WHERE status='pending' AND expires_at < ?", (now,))
    rows = cursor.fetchall()
    if rows:
        # 释放库存
        for rid, iid, qty in rows:
            conn.execute("UPDATE items SET stock_available = stock_available + ? WHERE id = ?", (qty, iid))
        # 标记为已过期
        conn.executemany("UPDATE reservations SET status='expired' WHERE id=?", [(row[0],) for row in rows])  # 注意，rows是tuple (id, item_id, quantity)
        # 或者直接删除？为了保留历史，标记为expired。
        # 注意：这里我们使用executemany，但需要正确传递参数。
        # 我们也可以用循环更新，但executemany更高效。
        # 但是我们需要的是更新多个记录，可以一次性更新：WHERE id IN (...)
        ids = [row[0] for row in rows]
        conn.execute("UPDATE reservations SET status='expired' WHERE id IN ({})".format(','.join('?' * len(ids))), ids)
        conn.commit()

注意：在cleanup中，我们执行了UPDATE和还有UPDATE，这些都需要在事务中。但调用者已经开始了一个事务或将要开始？为了避免复杂，我们可以在每个处理函数中在调用cleanup之前开始一个事务，或者在cleanup内部使用单独的事务（在锁保护下）。但是，在handle_create_reservation中，我们在加锁后先调用cleanup_expired，然后开始事务。如果cleanup_expired内部有commit，会破坏外部的事务。因此，我们需要协调事务。我们可以让cleanup_expired使用全局的连接，但不在其中commit，而是由调用者管理事务。在创建预约时，我们希望cleanup和后续操作在同一个事务中。所以应该在开始事务后调用cleanup，然后接着处理。但在我们之前的流程中，我们是在事务开始前调用cleanup的。更好的做法是：在加锁后，立即开始一个事务，然后先执行cleanup，再执行具体操作，最后commit。这样cleanup和操作在同一个事务中。这样更ACID。

所以修改所有需要写操作的处理函数（除了list是只读）：
- 加锁
- 开始事务 (conn.execute("BEGIN"))
- 执行cleanup_expired()
- 执行操作
- 如果成功，commit；如果失败，rollback。
- 释放锁

对于list，不需要事务，但为了安全可以用锁，不需要开始事务。

对于create_item，可以使用事务。

对于confirm/cancel，同样。

注意：在cleanup_expired中，我们不需要额外begin，因为外部已经有BEGIN。但cleanup仍然需要执行SELECT和UPDATE。只要在同一个连接上，它们会参与外部事务。所以cleanup_expired内部不能有commit/rollback，必须留给调用者。

所以修改cleanup_expired，不包含commit，假定外部已经开启事务。

那么所有写操作的标准流程：
lock.acquire()
try:
    conn.execute("BEGIN")
    cleanup_expired()
    # 业务逻辑
    conn.commit()
except:
    conn.rollback()
    self.send_error(...)
finally:
    lock.release()

对于只读操作（list），我们仍然需要锁来防止其他线程的写干扰吗？其实读可以并行，但为了简单，我们也可以使用锁。但为了性能，我们可以使用读锁（共享锁）或不用锁。但鉴于我们使用同一个连接，如果读和写同时进行，即使读没有锁，写操作会获取锁，但读操作可能访问旧的或中间状态。如果我们在读时不加锁，且使用同一个连接，可能会看到未提交的数据？但sqlite使用MVCC，读不会阻塞写，但写会阻塞读？实际上，使用锁保护可以确保读看到一致的数据。为了简单，也对读加锁，但不开始事务。因为我们的读操作不需要事务，只用一个SELECT。

但是，如果读操作在写事务进行时获取锁，会等待写事务完成，这是正确的。所以使用全局锁也可以保护读。

我们可以定义一个全局的RLock? 但是SQLite连接是排他的，所以使用Lock即可。

现在，处理handle_confirm和handle_cancel。

handle_confirm:
- 从路径提取id。
- 检查id是否存在，以及status是否为'pending'
- 更新status为'confirmed'
- 返回预约对象

handle_cancel:
- 类似，但更新status为'cancelled'并释放库存。

注意：在释放库存时，需要将对应item的stock_available加回quantity。

确认不需要释放。

现在，关于返回的预约对象，我们可能希望在创建、确认、取消后返回完整的预约信息（包括id, item_id, quantity, status, expires_at, created_at）。所以我们可以从数据库查询并返回。

所以辅助函数：get_reservation_by_id(id) -> dict or None。

在写操作后，我们可以查询并返回。

现在，我们需要考虑输入验证。例如，数量>0，ttl_seconds>0等。

处理JSON请求体时，需要处理可能的异常。

现在，编写代码。

此外，我们需要在启动时创建表。

在if __name__ == '__main__'中：
- 初始化数据库连接：conn = sqlite3.connect(DB) 并设置isolation_level=None（手动控制事务）
- 创建表
- 启动HTTP服务器：使用ThreadingHTTPServer(('127.0.0.1', 8080), RequestHandler)
- 然后server_forever()

注意：RequestHandler需要访问conn和lock，我们可以将它们作为模块级变量。Handler的实例在每次请求时创建，不能直接通过self.conn访问（除非使用类变量）。所以我们将conn和lock定义为模块级的全局变量，在Handler方法中直接引用。这是可以的。

另外，我们需要确保线程安全：conn是全局连接，但我们在每个请求中用锁保护。但Python的sqlite3连接在设置了check_same_thread=False后可以在多线程中使用，但需要外部锁。我们可以在创建连接时设置check_same_thread=False。

所以：
conn = sqlite3.connect(DB, check_same_thread=False)
conn.row_factory = sqlite3.Row (可选，方便访问列名)

但我们不使用Row，使用元组即可。

现在，生成完整代码。

我们需要处理一些边缘情况：
- 如果POST /reservations 时商品不存在，返回404。
- 如果商品库存不足，返回409。
- 如果确认或取消时预约不存在，返回404。
- 如果状态不正确（如不是pending），返回400错误（或409？用400）。
- 如果预约已过期（pending但已过期），应该在取消或确认时处理？因为每次请求前清理过期，所以如果有过期但还没清理，那么状态还是pending，但实际已过期。在确认时，我们应该检查是否已过期（expires_at < now），如果已过期，应拒绝确认，并考虑清理？因为我们在操作前已经调用了cleanup，所以过期记录已经被标记为expired，所以不会被找到（除非我们只标记状态为expired，保留记录）。所以确认时，如果预约已经被清理（标记为expired），则找不到，返回404。如果尚未清理（因为清理函数在事务中，但可能过期但还未执行清理），我们也可以额外检查expires_at。为了保险，在确认和取消时，可以额外检查expires_at是否过期。但既然我们每个请求前都会清理，一般不会有这种情况。但为了健壮性，可以加检查。

简单起见，我们相信清理函数。

现在，编写代码。

要考虑响应状态码：
- GET /items: 200
- POST /items: 201
- POST /reservations: 201
- POST /reservations/{id}/confirm: 200
- POST /reservations/{id}/cancel: 200
- 错误: 400, 404, 409, 500

send_json方法：
def send_json(self, data, status=200):
    self.send_response(status)
    self.send_header('Content-Type', 'application/json')
    self.end_headers()
    self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

send_error:
def send_error(self, status, message):
    self.send_json({'error': message}, status=status)

注意：不要覆盖父类的send_error，使用不同的名称。

read_json_body:
def read_json_body(self):
    content_length = int(self.headers.get('Content-Length', 0))
    if content_length == 0:
        return None
    body = self.rfile.read(content_length)
    try:
        return json.loads(body.decode('utf-8'))
    except:
        return None

现在，路径解析：我们需要抓出reservation_id。使用re或split。

在do_POST中，使用：
parsed = urllib.parse.urlparse(self.path)
path = parsed.path
然后：

if path == '/items':
    self.handle_create_item()
elif path == '/reservations':
    self.handle_create_reservation()
elif re.match(r'^/reservations/\d+/confirm$', path):
    reservation_id = int(path.split('/')[2])
    self.handle_confirm_reservation(reservation_id)
elif re.match(r'^/reservations/\d+/cancel$', path):
    reservation_id = int(path.split('/')[2])
    self.handle_cancel_reservation(reservation_id)
else:
    self.send_error(404, 'Not Found')

注意：如果路径匹配但使用非数字，我们可以返回错误。但这里已经假设匹配\d+。

现在，实现每个处理函数。

注意：在handle_confirm和handle_cancel中，获取预约时，我们可以使用SELECT ... WHERE id=？，然后检查状态是否为'pending'。如果status不是'pending'，返回400错误（"Reservation is not pending"）。如果预约不存在，返回404。

对于取消，同样。

注意：在取消中释放库存，要确保在该事务中执行。

还要注意，当释放库存时，要更新对应item的stock_available。

另外，在创建预约时，我们假设商品存在。还要确保quantity是正整数。

现在，编码。

一些额外细节：
- 使用datetime.utcnow() 但整数时间戳简单。我们用int(time.time())
- 对于expires_at，在返回时，我们可以返回时间戳，或者格式化为字符串。要求中没有规定，我们可以返回时间戳。
- 对于created_at，返回时间戳。

在返回的预约对象中，包括id, item_id, quantity, status, expires_at, created_at。

现在，编写完整代码。

考虑性能：清理过期可能涉及多行，但一般不会太多。

考虑并发：全局锁可能成为瓶颈，但对于这个服务足够了。

现在，输出代码。

检查代码行数：应该在1000行内。

现在，开始写代码。
```

## Assistant

````markdown
```python
#!/usr/bin/env python3
import http.server
import json
import sqlite3
import threading
import time
import re
import urllib.parse

DB = 'reservations.db'
lock = threading.Lock()
conn = None

# ------------------ Database ------------------
def init_db():
    global conn
    conn = sqlite3.connect(DB, check_same_thread=False)
    conn.isolation_level = None  # manual transaction control
    conn.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            stock_total INTEGER NOT NULL,
            stock_available INTEGER NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS reservations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            expires_at INTEGER NOT NULL,
            created_at INTEGER NOT NULL
        )
    """)
    conn.commit()

# ------------------ Cleanup expired reservations ------------------
def cleanup_expired():
    """Call inside a transaction (lock already held)"""
    now = int(time.time())
    cursor = conn.execute(
        "SELECT id, item_id, quantity FROM reservations WHERE status='pending' AND expires_at < ?",
        (now,)
    )
    rows = cursor.fetchall()
    if not rows:
        return
    # Release stock for each expired reservation
    for rid, iid, qty in rows:
        conn.execute(
            "UPDATE items SET stock_available = stock_available + ? WHERE id = ?",
            (qty, iid)
        )
    # Mark them as expired
    ids = tuple(row[0] for row in rows)
    placeholders = ','.join(['?'] * len(ids))
    conn.execute(
        f"UPDATE reservations SET status='expired' WHERE id IN ({placeholders})",
        ids
    )

# ------------------ HTTP Handler ------------------
class RequestHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        if path == '/items':
            self._list_items()
        else:
            self._send_error(404, 'Not Found')

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == '/items':
            self._create_item()
        elif path == '/reservations':
            self._create_reservation()
        elif re.match(r'^/reservations/\d+/confirm$', path):
            reservation_id = int(path.split('/')[2])
            self._confirm_reservation(reservation_id)
        elif re.match(r'^/reservations/\d+/cancel$', path):
            reservation_id = int(path.split('/')[2])
            self._cancel_reservation(reservation_id)
        else:
            self._send_error(404, 'Not Found')

    # ---------- helpers ----------
    def _read_json_body(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
        except ValueError:
            return None
        if content_length == 0:
            return None
        try:
            raw = self.rfile.read(content_length)
            return json.loads(raw.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return None

    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

    def _send_error(self, status, message):
        self._send_json({'error': message}, status)

    # ---------- GET /items ----------
    def _list_items(self):
        lock.acquire()
        try:
            cursor = conn.execute(
                "SELECT id, name, stock_total, stock_available FROM items"
            )
            items = []
            for row in cursor.fetchall():
                items.append({
                    'id': row[0],
                    'name': row[1],
                    'stock_total': row[2],
                    'stock_available': row[3]
                })
            self._send_json(items)
        finally:
            lock.release()

    # ---------- POST /items ----------
    def _create_item(self):
        body = self._read_json_body()
        if not body or 'name' not in body or 'stock_total' not in body:
            self._send_error(400, 'Missing parameters')
            return
        name = body['name']
        try:
            stock_total = int(body['stock_total'])
        except (ValueError, TypeError):
            self._send_error(400, 'Invalid stock_total')
            return
        if stock_total <= 0:
            self._send_error(400, 'stock_total must be positive')
            return

        lock.acquire()
        try:
            conn.execute("BEGIN")
            cursor = conn.execute(
                "INSERT INTO items (name, stock_total, stock_available) VALUES (?, ?, ?)",
                (name, stock_total, stock_total)
            )
            item_id = cursor.lastrowid
            conn.commit()
            self._send_json({
                'id': item_id,
                'name': name,
                'stock_total': stock_total,
                'stock_available': stock_total
            }, status=201)
        except sqlite3.IntegrityError as e:
            conn.rollback()
            self._send_error(400, f'Item already exists or invalid: {str(e)}')
        except Exception as e:
            conn.rollback()
            self._send_error(500, str(e))
        finally:
            lock.release()

    # ---------- POST /reservations ----------
    def _create_reservation(self):
        body = self._read_json_body()
        if not body or 'item_id' not in body or 'quantity' not in body or 'ttl_seconds' not in body:
            self._send_error(400, 'Missing parameters')
            return

        try:
            item_id = int(body['item_id'])
            quantity = int(body['quantity'])
            ttl_seconds = int(body['ttl_seconds'])
        except (ValueError, TypeError):
            self._send_error(400, 'Invalid parameters')
            return

        if quantity <= 0 or ttl_seconds <= 0:
            self._send_error(400, 'Quantity and ttl_seconds must be positive')
            return

        lock.acquire()
        try:
            conn.execute("BEGIN")
            # First cleanup expired reservations
            cleanup_expired()
            # Check item existence and stock
            cursor = conn.execute(
                "SELECT id, stock_available FROM items WHERE id = ?",
                (item_id,)
            )
            row = cursor.fetchone()
            if not row:
                conn.rollback()
                self._send_error(404, 'Item not found')
                return
            if row[1] < quantity:
                conn.rollback()
                self._send_error(409, 'Insufficient stock')
                return
            # Deduct stock
            conn.execute(
                "UPDATE items SET stock_available = stock_available - ? WHERE id = ?",
                (quantity, item_id)
            )
            # Create reservation
            now = int(time.time())
            expires_at = now + ttl_seconds
            cursor = conn.execute(
                "INSERT INTO reservations (item_id, quantity, status, expires_at, created_at) "
                "VALUES (?, ?, 'pending', ?, ?)",
                (item_id, quantity, expires_at, now)
            )
            reservation_id = cursor.lastrowid
            conn.commit()
            self._send_json({
                'id': reservation_id,
                'item_id': item_id,
                'quantity': quantity,
                'status': 'pending',
                'expires_at': expires_at,
                'created_at': now
            }, status=201)
        except Exception as e:
            conn.rollback()
            self._send_error(500, str(e))
        finally:
            lock.release()

    # ---------- POST /reservations/{id}/confirm ----------
    def _confirm_reservation(self, reservation_id):
        lock.acquire()
        try:
            conn.execute("BEGIN")
            # Cleanup before to avoid confirming an already expired reservation
            cleanup_expired()
            # Fetch reservation
            cursor = conn.execute(
                "SELECT id, item_id, quantity, status, expires_at, created_at FROM reservations WHERE id = ?",
                (reservation_id,)
            )
            row = cursor.fetchone()
            if not row:
                conn.rollback()
                self._send_error(404, 'Reservation not found')
                return
            if row[3] != 'pending':
                conn.rollback()
                self._send_error(400, f"Reservation is not pending (status={row[3]})")
                return
            # Confirm: set status to confirmed
            conn.execute(
                "UPDATE reservations SET status='confirmed' WHERE id = ?",
                (reservation_id,)
            )
            conn.commit()
            self._send_json({
                'id': row[0],
                'item_id': row[1],
                'quantity': row[2],
                'status': 'confirmed',
                'expires_at': row[4],
                'created_at': row[5]
            })
        except Exception as e:
            conn.rollback()
            self._send_error(500, str(e))
        finally:
            lock.release()

    # ---------- POST /reservations/{id}/cancel ----------
    def _cancel_reservation(self, reservation_id):
        lock.acquire()
        try:
            conn.execute("BEGIN")
            # Cleanup before to avoid double release
            cleanup_expired()
            # Fetch reservation
            cursor = conn.execute(
                "SELECT id, item_id, quantity, status, expires_at, created_at FROM reservations WHERE id = ?",
                (reservation_id,)
            )
            row = cursor.fetchone()
            if not row:
                conn.rollback()
                self._send_error(404, 'Reservation not found')
                return
            if row[3] != 'pending':
                conn.rollback()
                self._send_error(400, f"Reservation is not pending (status={row[3]})")
                return
            # Release stock
            conn.execute(
                "UPDATE items SET stock_available = stock_available + ? WHERE id = ?",
                (row[2], row[1])
            )
            # Mark as cancelled
            conn.execute(
                "UPDATE reservations SET status='cancelled' WHERE id = ?",
                (reservation_id,)
            )
            conn.commit()
            self._send_json({
                'id': row[0],
                'item_id': row[1],
                'quantity': row[2],
                'status': 'cancelled',
                'expires_at': row[4],
                'created_at': row[5]
            })
        except Exception as e:
            conn.rollback()
            self._send_error(500, str(e))
        finally:
            lock.release()

# ------------------ Main ------------------
if __name__ == '__main__':
    init_db()
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 8080), RequestHandler)
    print("Server running on http://127.0.0.1:8080")
    server.serve_forever()
```
````
