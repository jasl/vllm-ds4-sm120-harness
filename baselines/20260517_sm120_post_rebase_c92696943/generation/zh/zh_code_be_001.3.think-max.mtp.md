# Generation Transcript

- Case: `zh_code_be_001`
- Language group: `zh`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `3`
- Thinking mode: `think-max`
- Thinking strength: `max`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 132.001233
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 442, "total_tokens": 22633, "completion_tokens": 22191, "prompt_tokens_details": null}`
- Prompt tokens: 442
- Completion tokens: 22191
- Total tokens: 22633

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
我们被要求使用Python 3标准库编写单文件HTTP API服务，实现一个小型库存预约服务。不能使用Flask/FastAPI/Django等第三方库，必须使用内置库。总代码不超过1000行。

我们需要使用内置的`http.server`模块或`socketserver`？最直接的是使用`http.server`模块。但`http.server`提供基本HTTP服务器，我们可以继承`BaseHTTPRequestHandler`或`SimpleHTTPRequestHandler`，然后实现`do_GET`, `do_POST`等。但是解析路径和JSON。另外并发方面，`http.server`默认是单线程的，但我们可以在启动时设置`ThreadingHTTPServer` (Python 3.7+) 或使用`ThreadingMixIn`来实现并发处理请求。由于要求并发请求下的库存一致性，我们可以使用SQLite的WAL模式+事务，并可能添加一个threading.Lock来确保写操作互斥。SQLite本身支持事务，如果使用合适的隔离级别，默认是可串行化的？但为了绝对安全，可以加一个全局锁。

数据：使用sqlite3持久化，首次启动自动建表。商品字段：id, name, stock_total, stock_available。预约字段：id, item_id, quantity, status, expires_at, created_at。

API：
- GET /items: 列出商品和可用库存。
- POST /items: 新建商品，JSON参数name, stock_total。
- POST /reservations: 创建预约，JSON参数item_id, quantity, ttl_seconds。库存不足时返回409。
- POST /reservations/{id}/confirm: 确认预约，状态变为confirmed，不再释放库存。
- POST /reservations/{id}/cancel: 取消预约，释放库存。
- 每次请求前清理已过期且仍为pending的预约并释放库存。就是每个请求之前（或中间）都要做清理操作，确保库存一致。

错误响应包含error字段。

启动入口监听127.0.0.1:8080。

我们需要考虑如何路由请求。`BaseHTTPRequestHandler`只提供了`self.path`, `self.command`。我们需要解析路径和方法，然后调用对应处理程序。解析路径时可以提取路径参数，比如`/reservations/{id}/confirm`。我们可以通过路径分割来匹配。

我们还需处理JSON解析：读取`self.rfile`中的body并解析为dict。

响应：设置状态码和Content-Type，然后返回JSON。

并发：可以使用`ThreadingHTTPServer` (Python 3.7+) 或者 `socketserver.ThreadingMixIn` 加上 `HTTPServer`。SQLite默认支持多线程读，但写需要串行化。我们可以使用`check_same_thread=False`来连接，然后每个请求获得一个连接，但为了事务一致性，我们可以使用一个线程锁(`threading.Lock`)来保护所有写操作（或使用SQLite的`PRAGMA journal_mode=WAL` + 事务，但并发写还是会冲突）。更简单：在每次处理请求时获取一个全局锁，确保同一时间只有一个请求在修改数据库（包括清理操作）。因为清理操作也可能修改库存。但读操作可以并发？为了简化，我们可以让所有请求（包括GET）都获取读锁？或者使用读写锁，但标准库没有。我们可以只保护写操作，但清理操作也需要写，所以我们可以在每次请求开始（可能是读）时先执行清理（可能会写）。这样如果多个读同时触发清理，可能会冲突。所以最好在写操作时加锁，清理也在写锁下。但清理也是写操作。或者我们可以不锁，依赖SQLite的事务串行化。SQLite默认在写入时锁定数据库文件，如果使用WAL模式，读和写可以并发但写只能有一个。所以使用WAL模式+事务应该足够了。但Python sqlite3模块默认在一个连接中事务是串行的，但多个连接之间可能冲突。我们可以启用WAL模式，并设置`timeout`，如果写入冲突会等待。但为了安全性，我们还是加一个线程锁来序列化所有数据库操作。但读操作不需要锁，因为读不会导致不一致。但是清理操作（写）可能和另一个写冲突，所以我们可以为写操作加锁。但清理操作也是写，所以也得在锁下进行。我们可以定义一个函数 `cleanup_expired()` 在锁下执行。然后每个请求调用它。

由于要求“每次请求前清理已过期且仍为 pending 的预约并释放库存”，意味着无论GET还是POST，每次请求都先清理。如果多个请求同时到达，同时执行清理，可能会重复释放或冲突。所以我们应该让清理操作是原子的，并且避免冲突。可以这样做：每次请求处理开始时，获取一个全局锁，执行清理，然后释放锁？那样的话所有请求都串行化了，性能差。但题目要求并发处理，所以我们需要更好的方案。

更合理的是：清理操作可以安全地并发执行？如果两个请求同时清理，它们都会尝试找到过期pending的预约并释放库存。SQLite的事务隔离可以保证：一个事务中的SELECT FOR UPDATE? 但SQLite不支持SELECT FOR UPDATE。我们可以使用`UPDATE ... WHERE expires_at < ? AND status='pending'`一次完成标记和释放？但释放库存需要更新商品表。我们需要原子地先查出哪些预约过期，然后释放库存，然后更新这些预约状态为expired。但两个并发清理可能会重复处理同一个预约，但通过状态判断可以避免，因为第一个处理会将其状态改为expired，第二个再查就查不到了。但释放库存时，第一个已释放，第二个也会尝试释放同一条，但预约状态已改变，所以不会重复，因为条件中status='pending'。所以并发的清理是安全的。但库存更新需要确保原子性：更新商品库存时使用`UPDATE items SET stock_available = stock_available + ? WHERE id = ?`，这是原子操作。所以不需要全局锁。对于POST /reservations，我们需要检查库存是否足够，然后扣减库存，同时创建预约。这个过程需要原子操作，即在一个事务内完成：检查库存、扣减、创建预约。如果使用WAL模式，事务提交时如果冲突会回滚。对于并发请求，如果一个请求扣减库存但没提交，另一个请求检查库存会看到旧值（取决于隔离级别），可能会导致超额预订。SQLite的默认隔离级别是DEFERRED，在第一个写操作时开始事务，读取也是在该事务中读取，所以两个并发事务可能都读取到足够的库存然后都扣减，但最终提交时一个会失败因为数据库层面有行锁？实际上SQLite在写操作时会锁定整个数据库文件（或区域），所以第二个事务的写操作会等待，直到第一个提交。但第一个事务在写之前检查库存，第二个事务如果在第一个提交前开始，它读取时也会看到旧的库存值（因为第一个事务还没提交），然后当第一个提交后，第二个开始写，但它的检查基于旧数据，可能导致超额预订。为了避免这种情况，我们需要更严格的隔离，比如立即开始事务（使用`BEGIN IMMEDIATE`）来获得写锁，这样第二个事务会立即失败或等待，确保不会基于过期数据。在sqlite3中，我们可以通过设置`isolation_level=None`然后手动执行`BEGIN IMMEDIATE`或`BEGIN EXCLUSIVE`。或者使用`execute("BEGIN IMMEDIATE")`。这样可以确保并发安全。

所以，我们可以使用`BEGIN IMMEDIATE`事务，并在处理写操作时使用该事务。对于清理操作，也可以使用同样的方式。

另外，对于GET请求，不需要写锁，可以使用普通的读事务。

所以总结：使用`ThreadingHTTPServer`处理并发请求。对于每个请求，根据需要（是否涉及写操作）使用不同的事务模式。清理操作虽然是对过期预约的写操作，但也是写，所以也可以使用IMMEDIATE事务。但为了简单，我们可以对所有请求都执行清理，清理也使用IMMEDIATE事务。

或者，我们可以在每个请求开始前调用清理函数，该函数使用单独的连接并立即提交。但并发清理是安全的，所以不需要锁。

现在，我们开始设计代码。

我们使用`http.server.HTTPServer`和`socketserver.ThreadingMixIn`来实现多线程服务器。这样每个请求在新的线程处理。

然后定义请求处理器`RequestHandler`继承`BaseHTTPRequestHandler`。

我们需要在处理器中处理`do_GET`和`do_POST`。

路径路由：
- `GET /items` -> list_items()
- `POST /items` -> create_item()
- `POST /reservations` -> create_reservation()
- `POST /reservations/{id}/confirm` -> confirm_reservation(id)
- `POST /reservations/{id}/cancel` -> cancel_reservation(id)

路径解析：我们可以使用`re`模块或简单的字符串分割。例如，对于`/reservations/123/confirm`，可以split('/')得到['', 'reservations', '123', 'confirm']，然后匹配。

我们还需要处理JSON body，使用`json`模块。

数据库设计：

建表：
```sql
CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    stock_total INTEGER NOT NULL,
    stock_available INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS reservations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    expires_at TEXT NOT NULL, -- ISO format or timestamp
    created_at TEXT NOT NULL,
    FOREIGN KEY (item_id) REFERENCES items(id)
);
```

expires_at存储为ISO格式字符串或unix时间戳。为了方便，我们可以存储unix时间戳（浮点数或整数）。在Python中可以用`time.time() + ttl_seconds`。

在清理时，比较过期时间与当前时间。

在`POST /reservations`中，我们需要`ttl_seconds`参数，表示预约过期秒数。

库存一致性：创建预约时，必须在一个事务内检查库存、扣减库存、插入预约。使用`BEGIN IMMEDIATE`。

确认预约：更新状态为'confirmed'，但不释放库存。需要验证预约存在且为pending。

取消预约：更新状态为'cancelled'，并将商品库存`stock_available`增加quantity。需要检查预约存在且为pending，确保不重复释放。

清理：每次请求前，查找`status='pending'`且`expires_at < ?`的预约，对于每个此类预约，更新其状态为'expired'，并释放库存（增加对应商品的stock_available）。这个过程也应该在事务中进行，以避免并发问题。但是否需要IMMEDIATE？我们可以使用普通的BEGIN，但在清理中涉及多个表，并且是写操作，使用IMMEDIATE会更好。

我们可以在数据库连接上设置`isolation_level=None`，然后手动控制事务。

每个请求处理时，我们可以创建一个新的数据库连接，用完关闭。但连接创建开销不大，但我们需要确保每个线程使用自己的连接。连接可以设置为`check_same_thread=False`。由于服务器是多线程的，每个线程创建自己的连接是合适的。

我们也可以使用连接池，但没必要。

现在，编写代码框架。

首先，导入需要的模块：
```python
import http.server
import socketserver
import json
import sqlite3
import time
import re
import os
```

数据库初始化函数`init_db()`：连接数据库，创建表。

路径解析函数`parse_path(path)`：返回方法名和参数。

定义`ThreadingHTTPServer`：如果Python版本低于3.7，可能需要手动继承。

在`__main__`中启动服务器。

对于请求处理器：

- 在`__init__`中调用父类`__init__`。
- 定义`do_GET`和`do_POST`。
- 每个方法中先调用`cleanup_expired()`，然后处理具体逻辑。

清理函数`cleanup_expired()`：使用事务，更新过期预约状态和库存。

需要小心：清理函数和主处理逻辑可能会使用同一个数据库连接吗？为了简单，我们让每个请求内调用`cleanup_expired`时使用当前请求的连接。所以我们在每个请求开始创建一个连接，或者在我们处理请求的函数中创建连接。但`do_GET`等方法中，我们需要访问数据库，所以我们可以创建一个数据库连接作为实例变量，但要注意每个线程一个实例，所以安全。我们在`do_GET`开始创建连接，然后清理，然后处理，然后关闭连接。但连接可以用上下文管理器。

更好：为每个请求创建一个新的`DatabaseManager`或直接使用连接。

我们也可以创建一个全局的`threading.local`来存储每个线程的连接，但每次请求后需要清理？因为HTTP服务器可能使用线程池，但连接复用可能导致事务残留。所以每次请求创建新连接更安全。

在清理和主处理中使用同一个连接，确保事务一致。例如，清理可以使用一个单独的事务，但在创建预约时，我们可能也同时需要清理？但要求是每次请求前清理，所以我们在创建预约之前先清理，但这两步可能使用两个不同的事务。如果清理在之前完成单独事务，然后创建预约又是一个事务，这没问题。但如果在清理中已经释放了一些库存，然后创建预约时会看到新的库存。要保证最终一致性。所以分开事务也是可以的。

不过，如果我们想做得更严谨，可以将清理和主要操作放在同一个事务中，但那是可选的。

现在，实现细节。

我们写一个`Database`类来管理连接？实际上可以直接在请求处理方法中直接使用sqlite3。

考虑到代码清晰，定义函数`get_db()`，返回一个连接。但为了并发安全，每个请求创建新连接。

现在开始写代码。

注意：代码不能超过1000行。

我们一步一步构造。

首先，数据库初始化：

```python
DB_PATH = "inventory.db"

def init_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            stock_total INTEGER NOT NULL,
            stock_available INTEGER NOT NULL
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS reservations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            expires_at REAL NOT NULL,
            created_at REAL NOT NULL,
            FOREIGN KEY (item_id) REFERENCES items(id)
        )
    ''')
    # Create index for cleanup
    conn.execute('''CREATE INDEX IF NOT EXISTS idx_reservations_status_expires ON reservations(status, expires_at)''')
    conn.commit()
    conn.close()
```

注意：使用REAL存储时间戳。

然后定义请求处理器。

我们定义`class RequestHandler(http.server.BaseHTTPRequestHandler):`

我们需要重写`log_message`以抑制日志？但可以保留。

在类中定义几个辅助方法：
- `_send_json(data, status=200)`：设置状态码，content-type为application/json，发送json。
- `_send_error(message, status=400)`：发送错误json `{"error": message}`。
- `_read_body()`：读取请求体并解析JSON，返回dict或None。
- `_parse_path(path)`：解析路径，返回一个字符串元组 `(resource, id, action)`。

对于路径解析，我们使用re？更简单：使用`urlparse`？`urllib.parse.urlparse`可以解析路径和查询，但我们只需要路径部分。

我们可以这样做：
```python
parts = self.path.strip('/').split('/')
if parts[0] == 'items':
    # 如果没有其他部分，就是列表或创建；如果有id，但GET items没有单个获取，所以忽略
    return ('items', None, None)
elif parts[0] == 'reservations':
    if len(parts) == 1:
        return ('reservations', None, None)
    elif len(parts) == 3:
        # /reservations/{id}/confirm or cancel
        return ('reservations', parts[1], parts[2])
    else:
        return None
```

但我们需要对有查询参数的GET不需要解析。

所以我们可以：

```python
def _parse_path(self):
    parsed = urlparse(self.path)
    path = parsed.path.strip('/')
    parts = path.split('/')
    if len(parts) >= 1:
        resource = parts[0]
        if resource == 'items':
            if len(parts) == 1:
                return ('items', None, None)
            else:
                return ('items', parts[1], None)  # 但items没有单个操作
        elif resource == 'reservations':
            if len(parts) == 1:
                return ('reservations', None, None)
            elif len(parts) == 3 and parts[2] in ('confirm', 'cancel'):
                return ('reservations', parts[1], parts[2])
            else:
                return None
        else:
            return None
    return None
```

但注意method：`GET /items` 和 `POST /items`；`POST /reservations`；`POST /reservations/{id}/confirm` 等。所以我们在`do_GET`和`do_POST`中分别解析并调用。

数据库操作函数：

我们定义一个`DatabaseManager`类？为了保持代码清晰且不超行，直接写函数。

但我们需要在每个请求中创建连接。所以我们在`do_GET`等中创建连接`conn = sqlite3.connect(DB_PATH, check_same_thread=False)`，然后使用`conn`进行操作。注意，需要设置`isolation_level=None`来手动控制事务。

```python
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
conn.row_factory = sqlite3.Row
conn.execute("PRAGMA journal_mode=WAL")
conn.execute("PRAGMA busy_timeout=5000")
```

现在，实现具体功能。

### GET /items
查询所有items，返回每个项的id, name, stock_total, stock_available。我们还需要可用库存（直接是stock_available）。所以直接SELECT * FROM items。

### POST /items
解析JSON：name, stock_total。stock_total应该是正整数。新商品刚创建时，stock_available = stock_total（因为还没预约）。注意name应该唯一（我们可以加UNIQUE约束）。在事务中插入。如果name重复，返回错误。插入后返回对象，包含id。

注意：由于要求使用线程锁来确保并发请求下的库存一致性，但我们使用了IMMEDIATE事务，应该可以避免写冲突。但为了防止插入重复名称等多个请求同时插入导致违反约束，可以使用INSERT OR ROLLBACK，或者检查存在性。

### POST /reservations
解析JSON：item_id, quantity, ttl_seconds。ttl_seconds是整数（过期秒数）。检查参数有效性。然后需要先清理过期预约（但我们在每次请求前已经调用清理，所以这里不需要再调）。处理逻辑：使用`BEGIN IMMEDIATE`开始事务。检查商品是否存在，库存是否足够（stock_available >= quantity）。如果不足，返回409 Conflict。如果足够，扣减库存：`UPDATE items SET stock_available = stock_available - ? WHERE id = ?`，然后插入预约：status='pending', created_at=now, expires_at=now+ttl_seconds。然后返回预约对象（包含id）。注意，如果ttl_seconds为0或负，则立即过期？可以视情况处理。

### POST /reservations/{id}/confirm
检查预约存在且状态为pending。如果不是404或409？如果预约状态不是pending，返回错误（例如已确认或已取消）。如果已过期？但在确认之前先清理，所以如果过期已被清理，则状态已变为expired。所以需要检查status='pending'。然后更新status为'confirmed'。无需释放库存。

### POST /reservations/{id}/cancel
检查预约存在且状态为pending。更新status为'cancelled'，并释放库存：`UPDATE items SET stock_available = stock_available + ? WHERE id = ?`。

### cleanup_expired()
在每次请求开始时调用。函数接收数据库连接conn，然后在一个事务中查找所有expired pending的预约，并处理。我们可以用一个UPDATE来批量？但需要知道具体的商品id和数量。所以我们需要先查询，然后逐条处理。使用`BEGIN IMMEDIATE`事务。查询：`SELECT id, item_id, quantity FROM reservations WHERE status='pending' AND expires_at <= ?`。对于每条记录，更新预约状态为expired，并更新商品库存。可以组合使用两个UPDATE在一个循环中。确保事务提交。

注意：使用`conn.execute`进行逐条操作。

现在，关于并发：如果两个线程同时执行清理，可能会找到同一条记录，但由于第一个线程的事务提交后，第二个线程的查询会看到已更新，所以不会重复处理。但第二个线程可能会看到第一个线程未提交的数据？取决于隔离级别。默认是DEFERRED，但如果我们使用IMMEDIATE，事务会获取写锁，第二个事务会等待。所以并发的清理会串行化。这没问题。

现在，我们考虑错误处理：各种无效请求返回错误JSON。

现在，编写代码。

我们按照顺序写。

首先，模块导入。

```python
import http.server
import socketserver
import json
import sqlite3
import time
import re
import os
from urllib.parse import urlparse
from threading import Lock
```

写全局变量：DB_PATH，可能还有一个写锁？我们决定使用IMMEDIATE事务，所以可能不需要全局锁。但为了保险，我们可以添加一个`write_lock = Lock()`，在每次清理和写操作前获取。但是这样会降低并发。我认为可以使用IMMEDIATE事务，但我们需要确保所有写操作都使用IMMEDIATE，否则一个IMMEDIATE和一个DEFERRED可能死锁？如果一个线程使用IMMEDIATE等待写锁，另一个线程使用DEFERRED并且已开始读，那么IMMEDIATE会等待DEFERRED事务完成，而DEFERRED事务可能在等待读锁？但SQLite中，写锁是排他的，读锁是共享的。DEFERRED事务在第一次写操作前不会获取写锁，而IMMEDIATE立即获取写锁。所以如果一个线程使用IMMEDIATE等待获取写锁，而另一个线程在DEFERRED事务中在做读操作，但没有写锁，那么IMMEDIATE会等待直到DEFERRED结束（因为写锁必须等待其他读事务完成？实际上SQLite的锁机制：在WAL模式下，一个IMMEDIATE事务会获得一个写锁（即WAL的写锁），而读操作不会持有锁（因为WAL允许读写并发）。所以IMMEDIATE不会因为DEFERRED读事务而阻塞。但如果另一个是DEFERRED写事务，它可能在开始写操作前才获取锁。但DEFERRED写事务在第一个写操作时可能会被IMMEDIATE阻塞。所以整体上，使用IMMEDIATE事务是安全的。

但是，如果没有使用WAL模式，则IMMEDIATE会立即获得写锁（RESERVED锁），而读事务使用SHARED锁。IMMEDIATE会等SHARED锁释放，但SHARED锁可能被多个读共享，所以IMMEDIATE要等所有读事务结束。如果我们的读事务（如GET）可能长时间占据读锁？GET操作很快，所以可以接受。但是，为了简单和一致，我们可以使用全局写锁`write_lock`来序列化所有写操作（包括清理和创建/确认/取消）。读操作不受锁影响。这样更简单且安全。因为SQLite的并发写冲突可能导致回滚，我们需要重试等，比较麻烦。使用全局写锁，每次写请求前获取锁，然后执行数据库写操作，释放锁。由于我们使用的是多线程服务器，写操作只在短暂时间内，不会成为瓶颈。

所以，我们定义`write_lock = threading.Lock()`。

然后，在每个写操作函数中，使用`with write_lock:`包裹。

对于清理操作，应该在每次请求前执行，且它也是写操作，所以也需要锁。因此，每次请求前，如果获取锁后清理，可能读请求也需要等待写锁，这会影响性能。但读请求也会有清理步骤，所以为了简化，对所有请求（包括GET）都先获取写锁执行清理，然后释放锁，然后执行主要操作（读操作不需要锁）。但这样会序列化所有请求，包括读请求，导致性能下降。这不是理想的方式。

更好的方式是：清理操作本身可以安全地并发，因为多个清理不会冲突（依赖DB事务）。但为了确保清理和写操作不冲突，我们可以让写操作（创建/确认/取消）先获取写锁，而清理操作可以在写锁外执行。但清理操作本身也是写，所以也需要锁保护。如果我们让清理也使用写锁但允许读请求不等待？还是那句话，读请求需要清理，所以读请求也需要执行清理，但读请求可能不需要写锁（如果清理锁独立），但清理和读请求本身不冲突。所以我们可以设计一个独立的清理锁来保护清理操作，而主写锁保护其他写操作。但这样复杂。

可以考虑依赖SQLite的锁机制，因为它内部会处理并发写操作（会等待或重试）。我们只需在写操作时设置超时和重试。但Python sqlite3的默认行为是当检测到数据库锁定时，可能会引发`OperationalError: database is locked`。我们可以设置`timeout`参数在连接时，这样写操作会等待指定时间。例如，设置`conn.execute("PRAGMA busy_timeout=5000")`，这样如果数据库被锁，它会等待5秒，如果超时则抛出异常。我们可以捕获异常并重试。这样就不需要全局锁了。

这种方式可以充分利用SQLite的并发能力，且只要设计合理，可以处理并发。所以，我们可以选择不使用全局锁，而是依靠busy_timeout和重试机制。但需要保证事务的原子性。

考虑到题目要求“正确处理并发请求下的库存一致性，可使用事务和线程锁”，并没有指定一定要用哪种，我们使用事务和busy_timeout即可。但为了保险，也可以使用线程锁。

权衡后，我决定使用全局写锁来确保库存一致性，因为这样简单且避免了对SQLite锁机制的依赖。读请求虽然也需要执行清理（写操作），但我们可以让读请求先执行清理（需要写锁），然后执行读（不需要锁）。这样读请求就会串行化，导致并发读取性能下降。但考虑到这是一个小型服务，可以接受。

或者，我们可以将清理操作独立成一个定时任务，而不是每次请求前。但题目要求“每次请求前清理”，所以必须每次请求前。

我们可以这样做：在每次请求进入处理函数时（do_GET/do_POST），先执行清理，但清理本身不单独使用写锁，而是在全局写锁的保护下执行。但这样所有请求的清理都串行化。如果读请求很多，会互相阻塞。但清理操作很快：查询过期记录，更新，提交。所以性能影响可能不大。而且题目是小型库存预约服务，适合这种简单方式。

我决定使用全局写锁`write_lock`，在所有写操作和清理操作前获取。读操作（GET /items）也需要清理，所以也需要获取写锁进行清理，然后释放，再读（读不需要锁）。所以，我们可以在处理函数中这样：
```python
with write_lock:
    self._cleanup_expired(conn)
# 然后进行具体操作，如果是写操作，再次获取write_lock；如果是读操作，不需要。
```

或更简单：所有操作都先获取写锁执行清理，然后对于写操作，需要再获取写锁执行主操作？这会导致重复获取锁，可能死锁（如果锁不是可重入的）。所以我们可以统一在所有操作前获取写锁执行清理，然后对于写操作，再获取锁进行主操作。但再次获取锁会阻塞（如果使用普通Lock，不是RLock）。所以为了避免死锁，我们可以使用`threading.RLock`可重入锁，这样同一个线程可以多次获取。或者，我们可以在清理之后，释放锁，然后写操作时再获取锁。但这之间有间隙，另一个线程可能插入写操作导致清理后的状态被改变？例如，一个线程刚清理完释放了库存，另一个线程立即创建预约消耗了库存，然后当前线程继续执行写操作，但写操作基于清理后的状态，可能会冲突？写操作本身会检查库存，所以没问题。因为写操作会在事务内再次检查库存，如果库存被其他线程改变了，事务会基于最新版本检查（取决于隔离级别）。如果使用IMMEDIATE事务，它会阻塞直到其他事务完成，然后读取最新数据。所以释放锁再获取锁是可行的。但这样也确保了并发读取不受写锁影响：读请求在清理（写锁）后释放锁，然后直接读，不需要再获取锁。

所以，我们可以：
- 在`do_GET`、`do_POST`开始时（创建conn后），先获取`write_lock`，执行`cleanup_expired`，然后释放`write_lock`。
- 然后，如果方法是GET，直接读取数据并返回。
- 如果方法是POST，对于写操作（创建items、创建/确认/取消reservations），需要再次获取`write_lock`，执行写操作事务，然后释放。

这样，读操作在清理后可以并发读取（不获取锁），写操作串行化执行（但写操作需要获取锁）。之所以写操作需要再次获取锁，是为了确保写操作之间的互斥，避免冲突。同时清理也需要互斥（以免与写操作冲突）。所以这个方案合理。

但注意：读操作在清理期间会等待写锁，但清理很快，所以影响不大。

实现细节：
- `cleanup_expired(conn)`：接收数据库连接，执行清理。需要获取写锁？不，该函数总是在获取`write_lock`后调用，所以不需要内部再获取锁。但为了安全，我们假设调用者已经持有写锁。

现在，我们需要在`do_GET`和`do_POST`中先创建连接，然后获取写锁，清理，释放锁。注意创建连接必须在清理前，因为清理需要连接。

另外，对于POST，写操作需要再次获取锁。但为了简化，我们也可以在获取写锁后执行清理和主操作一起，但这样读请求也会一直持有写锁直到完成读，会阻塞其他请求。所以还不如读请求在清理后释放锁。

注意：在写操作中，我们还需要确保事务使用`BEGIN IMMEDIATE`或`BEGIN EXCLUSIVE`？既然已经持有全局写锁，串行化写操作，我们可以使用普通`BEGIN DEFERRED`事务，因为锁已经确保同一时间只有一个线程在写，所以数据库不会出现并发写冲突。但如果我们使用锁，SQLite的锁就不会被触发，我们可以使用`isolation_level=None`并手动提交。但需要注意的是，在写锁下，我们可以直接执行更新，其他线程不会同时写。所以使用`BEGIN`即可。但为了更安全，我们仍可以设置busy_timeout为0。

现在，我们开始编码。

### 数据库操作函数

我们有：
- `list_items(conn)` -> list of item dicts
- `create_item(conn, data)` -> item dict or error response
- `create_reservation(conn, data)` -> reservation dict or error
- `confirm_reservation(conn, rid)` -> success or error
- `cancel_reservation(conn, rid)` -> success or error
- `cleanup_expired(conn)` -> None

这些函数接收数据库连接，自行处理事务（如果需要）。由于写操作在全局锁下，我们不需要担心并发，但为了数据一致性，我们仍应该在写操作中使用事务。`cleanup_expired`也是写操作，需要在锁下。

注意：`create_item`可能在插入时违反UNIQUE约束，如果两个线程同时插入同名商品，在锁保护下不会同时发生，所以不会冲突。

### 请求处理

在`do_GET`:
1. Parse path to determine if it's GET /items.
2. Create db connection.
3. Acquire write_lock, cleanup_expired, release write_lock.
4. If GET /items: list items, send json.
5. Else: 404.

在`do_POST`:
1. Parse path to determine resource.
2. Create db connection.
3. Acquire write_lock, cleanup_expired, release write_lock.
4. For POST /items: acquire write_lock, create_item, release write_lock.
5. For POST /reservations: acquire write_lock, create_reservation, release write_lock.
6. For POST /reservations/{id}/confirm: acquire write_lock, confirm_reservation, release write_lock.
7. For POST /reservations/{id}/cancel: acquire write_lock, cancel_reservation, release write_lock.
8. Return appropriate response.

注意：在`cleanup_expired`后，我们释放了锁，但随后需要再获取锁进行写操作。由于锁是普通锁，不会导致死锁（不同线程，同一线程释放后再次获取是允许的）。但如果有多个线程同时到达写操作，它们会排队。

### 代码结构

我们使用一个`Handler`类，继承`BaseHTTPRequestHandler`。

定义一个类变量`write_lock = threading.Lock()`，这样所有实例共享。

在`__init__`中不做什么特别。

注意：由于我们重写了`do_GET`和`do_POST`，我们需要在每处理一个请求时创建数据库连接，并确保连接被关闭。可以使用`try...finally`。

还可以定义一个`_connect_db()`方法。

### 路径路由

我们定义一个字典映射？但简单使用条件判断。

因为路径有限，我们可以直接在`do_GET`和`do_POST`中解析。

### 细节

- 时间戳：使用`time.time()`。
- JSON响应：`self.send_response(status)`, `self.send_header('Content-Type', 'application/json')`, `self.end_headers()`, `self.wfile.write(json.dumps(data).encode('utf-8'))`。
- 请求体读取：`content_length = int(self.headers['Content-Length'])`, `body = self.rfile.read(content_length)`，然后`json.loads(body)`。
- 错误处理：对于无效JSON，返回400。

### 错误状态码

- 400：参数错误（缺少、无效等）。
- 404：资源未找到（如商品、预约不存在，或路径不存在）。
- 409：库存不足，或预约状态冲突（如确认时预约不是pending，或取消时不是pending等）。

### 预约状态

status: pending, confirmed, cancelled, expired。

我们定义常量？或用字符串。

在创建时，默认为'pending'。在清理时改为'expired'。确认时改为'confirmed'。取消时改为'cancelled'。

注意：确认后释放库存？不需要，确认后库存不再释放。只有取消或过期才释放。

### 清理策略

在清理`cleanup_expired`中：
```sql
SELECT id, item_id, quantity FROM reservations WHERE status='pending' AND expires_at <= ?
```
对于每一条，执行：
```
UPDATE reservations SET status='expired' WHERE id = ?
UPDATE items SET stock_available = stock_available + ? WHERE id = ?
```
最好在一个事务中完成。

注意：有可能同一个预约在清理时刚被其他线程确认或取消，但状态可能改变。由于我们使用写锁，这种情况不会发生。但如果我们不使用锁，可能发生。所以锁简化了。

### 返回对象的字段

对于商品：id, name, stock_total, stock_available。
对于预约：id, item_id, quantity, status, expires_at, created_at。时间戳可能转换为ISO格式？为了可读性，可以保持为时间戳（客户端可以理解）。但API通常返回ISO字符串。题目没有明确，我们可以返回时间戳浮点数。简单起见返回时间戳。

或者，我们可以返回ISO字符串格式，使用`datetime.datetime.fromtimestamp(ts).isoformat()`。但这样需要额外转换。我认为返回时间戳简单。

### 路径配置

我们使用正则匹配？简单字符串分割。但需要处理可能的尾部斜杠。

例如，path可能是`/items/`等。我们在分割前去除首尾斜杠。

对于GET /items，path是`/items`。

对于POST /reservations/{id}/confirm，path是`/reservations/123/confirm`。

所以我们分割后：
- parts[0] = resource
- 对于reservations，如果len(parts)==3，则parts[1]是id，parts[2]是action。

对于items，如果len(parts)==2，则可能是单个操作，但我们没有定义，所以返回404。

我们可以根据method和resource决定。

### 验证参数

对于POST /items：需要name（非空字符串），stock_total（正整数）。stock_total必须大于0。
对于POST /reservations：需要item_id（整数），quantity（正整数），ttl_seconds（正整数）。
对于confirm/cancel：需要id（整数）。

当参数缺少或无法解析时，返回400。

### 错误响应格式

`{"error": "message"}`。

### 启动入口

```python
if __name__ == '__main__':
    init_db()
    server = ThreadingHTTPServer(('127.0.0.1', 8080), RequestHandler)
    print('Starting server on 127.0.0.1:8080...')
    server.serve_forever()
```

但我们需要`ThreadingHTTPServer`。可以使用`socketserver.ThreadingMixIn`和`http.server.HTTPServer`结合：

```python
class ThreadingHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    pass
```

这是常见做法。

或者，直接使用`http.server.ThreadingHTTPServer`（Python 3.7+）。为了兼容，自定义。

### 其他

- 设置数据库行工厂为`sqlite3.Row`，以便按列名访问。
- 注意：每个连接都需要设置row_factory等。

### 编写代码

现在，我们开始写代码。由于是单文件，我们直接将所有代码写在一起。

考虑到代码长度，我们需要简洁。但要求通过。

我们将使用`threading.Lock`。

定义WriteLock为模块级别。

写一个帮助函数`_send_json`和`_read_json`。

在类内部。

现在开始。

我担心代码是否超过1000行，但估计500行左右。

开始写。

首先导入模块。

```python
import http.server
import socketserver
import json
import sqlite3
import time
import os
import threading
from urllib.parse import urlparse
```

定义数据库文件路径。

```python
DB_PATH = "inventory.db"
```

初始化数据库：

```python
def init_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            stock_total INTEGER NOT NULL,
            stock_available INTEGER NOT NULL
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS reservations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            expires_at REAL NOT NULL,
            created_at REAL NOT NULL,
            FOREIGN KEY (item_id) REFERENCES items(id)
        )
    ''')
    conn.execute('''CREATE INDEX IF NOT EXISTS idx_res_s_exp ON reservations(status, expires_at)''')
    conn.commit()
    conn.close()
```

定义锁：

```python
write_lock = threading.Lock()
```

定义Handler类：

```python
class RequestHandler(http.server.BaseHTTPRequestHandler):
    server_version = "InventoryAPI/1.0"

    def do_GET(self):
        conn = None
        try:
            conn = sqlite3.connect(DB_PATH, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            # 清理过期预约
            with write_lock:
                self._cleanup_expired(conn)
            # 路径解析
            parsed = urlparse(self.path)
            path = parsed.path.strip('/')
            parts = path.split('/')
            if len(parts) == 1 and parts[0] == 'items' and self.path == '/items':
                # GET /items
                self._handle_get_items(conn)
            elif len(parts) == 1 and parts[0] == '':
                # root, maybe redirect?
                self._send_error("Not Found", 404)
            else:
                self._send_error("Not Found", 404)
        except Exception as e:
            self._send_error(f"Internal Server Error: {str(e)}", 500)
        finally:
            if conn:
                conn.close()
```

同理，`do_POST`更复杂。

我们需要实现各种处理函数。

先定义`_send_json`和`_send_error`：

```python
    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def _send_error(self, message, status=400):
        self._send_json({"error": message}, status)
```

注意：错误状态码可能在400-500之间。

实现`_read_json`：

```python
    def _read_json(self):
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length == 0:
            return None
        body = self.rfile.read(content_length)
        try:
            return json.loads(body.decode('utf-8'))
        except json.JSONDecodeError:
            return None
```

现在，实现各个处理函数。它们需要操作conn。注意这些函数在锁外调用（对于GET）或锁内调用（对于POST的写操作）。所以写操作函数自己会获取锁？我们设计在调用写操作函数前已经获取了write_lock（在do_POST中）。所以这些函数假设锁已经获取。但为了灵活性，我们可以在函数内部再次获取锁吗？不行，因为锁不是RLock，会死锁。所以约定：写操作的函数在被调用时，调用者已经持有write_lock；读操作函数没有锁。

因此，对于写操作（create_item, create_reservation, confirm, cancel），我们在调用时在do_POST中已经`with write_lock:`包围，然后再调用这些函数。这些函数内不再有锁。

对于`_cleanup_expired`，同样在锁下调用。

在do_GET中，我们调用`_handle_get_items`，这个函数没有锁，可以读。

所以，我们来写`_handle_get_items`：

```python
    def _handle_get_items(self, conn):
        cursor = conn.execute('SELECT id, name, stock_total, stock_available FROM items')
        items = [dict(row) for row in cursor.fetchall()]
        self._send_json(items)
```

注意`dict(row)`可以把Row转成字典。

对于POST /items:

```python
    def _handle_create_item(self, conn, data):
        if not data or 'name' not in data or 'stock_total' not in data:
            self._send_error("Missing required fields: name, stock_total", 400)
            return
        name = data['name'].strip()
        if not name:
            self._send_error("name must not be empty", 400)
            return
        stock_total = data['stock_total']
        if not isinstance(stock_total, int) or stock_total <= 0:
            self._send_error("stock_total must be a positive integer", 400)
            return
        # 插入
        try:
            conn.execute('INSERT INTO items (name, stock_total, stock_available) VALUES (?, ?, ?)',
                         (name, stock_total, stock_total))
            conn.commit()
            item_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
            item = {'id': item_id, 'name': name, 'stock_total': stock_total, 'stock_available': stock_total}
            self._send_json(item, 201)
        except sqlite3.IntegrityError:
            conn.rollback()
            self._send_error(f"Item with name '{name}' already exists", 409)
```

注意：我们需要在插入后提交。如果失败回滚。

对于POST /reservations:

```python
    def _handle_create_reservation(self, conn, data):
        if not data or 'item_id' not in data or 'quantity' not in data or 'ttl_seconds' not in data:
            self._send_error("Missing required fields: item_id, quantity, ttl_seconds", 400)
            return
        item_id = data['item_id']
        quantity = data['quantity']
        ttl_seconds = data['ttl_seconds']
        if not isinstance(item_id, int) or item_id <= 0:
            self._send_error("item_id must be a positive integer", 400)
            return
        if not isinstance(quantity, int) or quantity <= 0:
            self._send_error("quantity must be a positive integer", 400)
            return
        if not isinstance(ttl_seconds, (int, float)) or ttl_seconds <= 0:
            self._send_error("ttl_seconds must be a positive number", 400)
            return
        # 开始事务 IMMEDIATE 以获取写锁（但我们已经持有 write_lock，所以可以普通BEGIN）
        conn.execute('BEGIN')
        try:
            # 检查商品存在和库存
            cursor = conn.execute('SELECT id, stock_available FROM items WHERE id = ?', (item_id,))
            item = cursor.fetchone()
            if not item:
                conn.rollback()
                self._send_error("Item not found", 404)
                return
            if item['stock_available'] < quantity:
                conn.rollback()
                self._send_error("Insufficient stock", 409)
                return
            # 扣减库存
            conn.execute('UPDATE items SET stock_available = stock_available - ? WHERE id = ?',
                         (quantity, item_id))
            # 创建预约
            now = time.time()
            expires_at = now + ttl_seconds
            created_at = now
            conn.execute('''
                INSERT INTO reservations (item_id, quantity, status, expires_at, created_at)
                VALUES (?, ?, 'pending', ?, ?)
            ''', (item_id, quantity, expires_at, created_at))
            # 提交
            conn.commit()
            reservation_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
            # 返回预约
            reservation = {
                'id': reservation_id,
                'item_id': item_id,
                'quantity': quantity,
                'status': 'pending',
                'expires_at': expires_at,
                'created_at': created_at
            }
            self._send_json(reservation, 201)
        except Exception as e:
            conn.rollback()
            raise
```

注意：我们使用了`conn.execute('BEGIN')`，因为我们设置了隔离级别吗？我们没有设置`isolation_level`，默认情况下sqlite3模块会隐式地管理事务：每次执行`execute`会自动开始一个事务，并在`commit`或`rollback`时结束。但我们想要手动控制事务，所以我们需要设置`isolation_level=None`，然后手动调用`execute('BEGIN')`或`begin()`。我们可以在创建连接时设置`isolation_level=None`。

所以，在连接创建后，我们需要设置`conn.isolation_level = None`。或者，我们可以在`_cleanup_expired`和其他函数中手动控制。为了统一，我们在创建连接时设置`conn.isolation_level = None`。然后所有事务手动控制。

调整连接部分：在do_GET和do_POST创建conn后，设置`conn.isolation_level = None`。

在`_cleanup_expired`中也需要使用手动事务。

所以，我们修改连接创建：
```python
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
conn.row_factory = sqlite3.Row
conn.execute("PRAGMA journal_mode=WAL")
conn.execute("PRAGMA busy_timeout=5000")
conn.isolation_level = None
```

然后我们可以在需要时使用`conn.execute('BEGIN')`或`conn.begin()`。但SQLite Python的`execute('BEGIN')`会开始一个事务。注意：我们也可以使用`conn.begin()`方法？sqlite3.Connection没有begin方法，但可以执行`conn.execute("BEGIN")`。

所以，在每个写操作函数中，我们需要手动调用`begin()`和`commit()`或`rollback()`。

对于读操作，不需要事务，但为了确保读一致性，可以使用`conn.execute('BEGIN')`然后读？不需要，直接SELECT即可。默认情况下，每一个SELECT语句本身是在隐式事务中，但如果没有手动BEGIN，它会在单独的自洽事务中执行。但为了与清理保持一致，我们可以不必显式BEGIN。

对于`_cleanup_expired`，我们需要一个事务。我们使用手动事务。

```python
    def _cleanup_expired(self, conn):
        conn.execute('BEGIN')
        try:
            now = time.time()
            # 查询过期pending预约
            rows = conn.execute('''
                SELECT id, item_id, quantity FROM reservations
                WHERE status='pending' AND expires_at <= ?
            ''', (now,)).fetchall()
            if rows:
                for row in rows:
                    conn.execute('UPDATE reservations SET status=? WHERE id=?', ('expired', row['id']))
                    conn.execute('UPDATE items SET stock_available = stock_available + ? WHERE id=?',
                                 (row['quantity'], row['item_id']))
            conn.commit()
        except Exception:
            conn.rollback()
            raise
```

注意：在清理中，我们不应在锁外执行，所以它会在锁下调用了。

现在，对于其他写操作，我们遵循类似模式。

对于confirm和cancel：

```python
    def _handle_confirm_reservation(self, conn, rid):
        conn.execute('BEGIN')
        try:
            # 检查预约
            row = conn.execute('SELECT * FROM reservations WHERE id=?', (rid,)).fetchone()
            if not row:
                conn.rollback()
                self._send_error("Reservation not found", 404)
                return
            if row['status'] != 'pending':
                conn.rollback()
                self._send_error(f"Cannot confirm reservation with status '{row['status']}'", 409)
                return
            conn.execute("UPDATE reservations SET status='confirmed' WHERE id=?", (rid,))
            conn.commit()
            # 返回更新后的预约（可选）
            updated = conn.execute('SELECT * FROM reservations WHERE id=?', (rid,)).fetchone()
            self._send_json(dict(updated), 200)
        except Exception:
            conn.rollback()
            raise
```

注意：确认不需要释放库存。

取消：

```python
    def _handle_cancel_reservation(self, conn, rid):
        conn.execute('BEGIN')
        try:
            row = conn.execute('SELECT * FROM reservations WHERE id=?', (rid,)).fetchone()
            if not row:
                conn.rollback()
                self._send_error("Reservation not found", 404)
                return
            if row['status'] != 'pending':
                conn.rollback()
                self._send_error(f"Cannot cancel reservation with status '{row['status']}'", 409)
                return
            # 释放库存
            item_id = row['item_id']
            quantity = row['quantity']
            conn.execute("UPDATE reservations SET status='cancelled' WHERE id=?", (rid,))
            conn.execute("UPDATE items SET stock_available = stock_available + ? WHERE id=?",
                         (quantity, item_id))
            conn.commit()
            updated = conn.execute('SELECT * FROM reservations WHERE id=?', (rid,)).fetchone()
            self._send_json(dict(updated), 200)
        except Exception:
            conn.rollback()
            raise
```

注意：在更新库存时，我们没有检查库存上限，因为取消释放不应该超过库存总量，但无需检查。

现在，实现`do_POST`。它需要解析路径和方法，然后将控制权交给适当的处理函数。注意：在调用写处理函数之前，我们已经持有了write_lock（在清理后释放，然后又获取了write_lock）。我们将在do_POST中设计如下：

```python
    def do_POST(self):
        conn = None
        try:
            conn = sqlite3.connect(DB_PATH, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA busy_timeout=5000")
            conn.isolation_level = None

            # 1. 清理过期预约（获取写锁）
            with write_lock:
                self._cleanup_expired(conn)

            # 2. 解析路径
            parsed = urlparse(self.path)
            path = parsed.path.strip('/')
            parts = path.split('/')

            # 3. 根据路径和方法处理
            if len(parts) == 1 and parts[0] == 'items':
                # POST /items
                data = self._read_json()
                with write_lock:
                    self._handle_create_item(conn, data)
            elif len(parts) == 1 and parts[0] == 'reservations':
                # POST /reservations
                data = self._read_json()
                with write_lock:
                    self._handle_create_reservation(conn, data)
            elif len(parts) == 3 and parts[0] == 'reservations' and parts[2] == 'confirm':
                rid = self._parse_int(parts[1])
                if rid is None:
                    self._send_error("Invalid reservation id", 400)
                    return
                with write_lock:
                    self._handle_confirm_reservation(conn, rid)
            elif len(parts) == 3 and parts[0] == 'reservations' and parts[2] == 'cancel':
                rid = self._parse_int(parts[1])
                if rid is None:
                    self._send_error("Invalid reservation id", 400)
                    return
                with write_lock:
                    self._handle_cancel_reservation(conn, rid)
            else:
                self._send_error("Not Found", 404)
        except Exception as e:
            self._send_error(f"Internal Server Error: {str(e)}", 500)
        finally:
            if conn:
                conn.close()
```

注意：我们使用`_parse_int`辅助函数。

```python
    def _parse_int(self, s):
        try:
            return int(s)
        except (ValueError, TypeError):
            return None
```

对于GET /items，路径简单，我们已经在do_GET中处理了。但需要注意，路径可能是`/items`或`/items/`？我们最好处理尾部斜杠。所以，在do_GET中，我们判断路径去掉首尾斜杠后是`items`或`items/`。我们使用`self.path == '/items'`或者使用`path.strip('/') == 'items'`。更通用：`if resource == 'items'`。

我们在do_GET中解析路径和parts，类似do_POST中的做法。这样统一。

修改do_GET：

```python
    def do_GET(self):
        conn = None
        try:
            conn = sqlite3.connect(DB_PATH, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA busy_timeout=5000")
            conn.isolation_level = None

            # 清理
            with write_lock:
                self._cleanup_expired(conn)

            parsed = urlparse(self.path)
            path = parsed.path.strip('/')
            parts = path.split('/')

            if len(parts) == 1 and parts[0] == 'items':
                self._handle_get_items(conn)
            else:
                self._send_error("Not Found", 404)
        except Exception as e:
            self._send_error(f"Internal Server Error: {str(e)}", 500)
        finally:
            if conn:
                conn.close()
```

这样就很统一。

现在，实现`_handle_get_items`和`_handle_create_item`等。

注意：在写操作函数中，我们假设调用者已经获取了write_lock，所以我们不再在函数内部获取锁。同样，我们在清理时也持有锁。在do_GET和do_POST中，我们会在写操作前重新获取锁。注意：我们可能在do_POST中已经持有了锁进行清理，然后释放了锁，然后又获取锁进行写操作。这是可行的。

但是，有一个小问题：如果我们创建连接时没有设置`isolation_level=None`，那么`conn.execute('BEGIN')`会失败或有意外行为。所以我们设置。

现在，确保所有写操作都使用`conn.execute('BEGIN')`并正确处理提交和回滚。注意：在发生错误时，我们需要回滚。在`_handle_create_item`中，我们使用异常捕获回滚。

但是，对于确认和取消，如果预约状态不是pending，我们在回滚后发送错误。注意：回滚必须在发送错误前。所以我们的顺序正确。

在`_cleanup_expired`中，如果查询结果为空，我们直接提交空事务？我们可以在没有行时也提交（或只是执行begin/commit），但不一定需要。但为了简单，我们在没有行时也提交。

还有，在`_cleanup_expired`中，我们使用了`conn.execute('BEGIN')`，但在每次请求开始时，我们可能有一个未提交的事务吗？不会，因为我们在清理前没有开始事务，所以安全。在清理后，我们提交了，所以数据库处于无事务状态。

在do_GET中，清理后我们可能直接执行SELECT，这会在单独的事务中（隐含）。在do_POST中，清理后我们释放锁，然后可能会再次获取锁进行写操作，这没问题。

但要注意，在有些错误情况下，我们可能在`_read_json`中抛出异常，但连接会正常关闭（finally）。

现在，实现`_handle_create_item`：当name重复时，我们返回409。我们已经处理了`IntegrityError`。

在`_handle_create_item`中，我们使用了`self._send_json`等，但这些方法可能会抛出异常（如BrokenPipeError如果客户端断开）？通常没关系。

我们需要在所有路径下都正确处理资源释放。例如，如果连接未提交就关闭，可能导致数据不一致。但在我们的函数中，我们总是提交或回滚。

现在，让我们考虑一个问题：`_cleanup_expired`和`_handle_create_reservation`都是写操作，且分别获取锁。如果在一个请求中，先清理然后创建预约，两者之间有释放锁并重新获取锁的间隙。其他线程可以在此期间插入写操作，但这不会导致不一致，因为每个写操作都检查最新状态。例如，清理释放了一些库存，创建预约时如果库存足够就扣减。如果另一个线程在清理和创建预约之间获取锁修改了库存，创建预约时看到的是最新的库存（因为它在获取锁后才开始事务），所以是安全的。

但是，如果我们希望清理和创建预约在同一个事务中进行，我们可以将清理和创建预约放在同一个锁保护下，甚至同一个事务中。但题目没要求。目前的方式也应该是合理的。

如果必须保证每次请求前清理，并且清理会释放库存，然后我们的写操作可能立即使用这些库存，我们的设计满足了。

现在，测试基本路径。

我们构造一些测试：

- 启动服务器。
- POST /items {"name":"test","stock_total":10} -> 201，返回对象。
- GET /items -> 列表。
- POST /reservations {"item_id":1,"quantity":3,"ttl_seconds":300} -> 201，返回预约。
- GET /items -> stock_available变成7。
- 等待过期（或手动清理）？清理由每次请求触发。我们可以执行一个GET，然后检查库存是否恢复？但需要等过期。或者我们可以设置ttl_seconds=1，然后过1秒后请求，清理应该释放库存。
- POST /reservations/1/confirm -> 确认，返回确认后对象，状态confirmed。
- POST /reservations/1/cancel -> 返回错误，因为状态不是pending。
- 创建另一个预约，然后取消，检查库存。

需要注意：`POST /reservations/{id}/confirm`和`POST /reservations/{id}/cancel`路径中`{id}`应该是整数，我们使用`_parse_int`转换。

现在，补充一些细节：

- 对于GET，如果路径不是`/items`，返回404。
- 对于POST，如果路径不匹配，返回404。

- 对于JSON请求体，如果读取时出现错误，返回400错误。

在`_read_json`中，如果读取失败，返回None。我们调用者检查data是否为None并返回400。

在`do_POST`中，对于需要body的请求，如`create_item`和`create_reservation`，我们调用`_read_json`。对于`confirm`和`cancel`，它们不需要body。但`_read_json`会读取body，所以可能也需要处理空body。因为confirm/cancel不需要参数，所以不需要读取body。我们应该忽略body。所以对于这两个，我们不调用`_read_json`。我们在处理时会检查`_read_json`的返回值吗？事实上，我们只为create_item和create_reservation读取body。所以没问题。

我们还需要确保`_read_json`在Content-Length为0时返回None，那么create_item和create_reservation会因为没有数据而返回400。

现在，我们还需要实现`_handle_get_items`，返回列表。注意：如果我们使用`dict(row)`，结果中的键就是列名。时间戳是浮点数。

对于创建商品，我们需要返回包含id的JSON。注意：`last_insert_rowid()`需要在同一连接中，在INSERT后立即调用。

现在，注意SQL注入：我们使用参数化查询，安全。

现在，考虑数据库的PRAGMA设置：我们设置了`journal_mode=WAL`，`busy_timeout=5000`。这允许读写并发，但我们在应用层使用锁保护写操作，所以WAL可能不是必须的，但有助于性能。

现在，考虑初始化数据库：我们在main入口调用`init_db()`。注意：如果数据库文件已经存在，我们不应该覆盖。`CREATE TABLE IF NOT EXISTS`是安全的。

现在，路径处理中的边缘情况：如果path为空（根路径），parts可能是['']，长度1且元素空字符串，所以我们判断part[0]是否为空字符串，如果是，返回404。我们已经在do_GET和do_POST中判断了长度1且part[0]==''，但我们的条件目前只检查part[0]=='items'，其他情况会返回404。所以不需要特别处理根路径，因为根路径不是items，所以会404。

对于path如`/items/`，`path.strip('/')`得到`items`，所以parts[0]=='items'，没问题。

对于`/reservations/`，`path.strip('/')`得到`reservations`，parts[0]=='reservations'，但长度1，我们期望在POST中匹配`reservations`（创建），所以没问题。

对于`/reservations`（无斜杠），同样。

对于`/reservations/1/confirm/`（尾部斜杠），`path.strip('/')`得到`reservations/1/confirm`，parts长度3，所以我们匹配成功。但如果尾部有斜杠，strip会去掉，所以没问题。

现在，我们还需注意路径中可能包含查询字符串，我们使用`urlparse`只解析路径，忽略查询。

在`do_GET`和`do_POST`中，我们使用`parsed = urlparse(self.path)`，然后`path = parsed.path.strip('/')`。

现在，考虑HTTP版本和头部：我们不需要特殊处理。

现在，检查代码是否满足所有需求。

需求列表：

1. `GET /items`：列出商品和可用库存。 -> 实现。
2. `POST /items`：新增商品，JSON参数name, stock_total。 -> 实现。
3. `POST /reservations`：创建预约，JSON参数item_id, quantity, ttl_seconds。库存不足返回409。 -> 实现。
4. `POST /reservations/{id}/confirm`：确认预约，状态变为confirmed，不再释放库存。
5. `POST /reservations/{id}/cancel`：取消预约，释放库存。
6. 每次请求前清理已过期且仍为pending的预约并释放库存。 -> 实现（在请求开始时调用_cleanup_expired）。
7. 正确处理并发请求下的库存一致性，可使用事务和线程锁。 -> 我们使用了线程锁和事务。
8. 返回JSON；错误响应包含error字段。 -> 实现。
9. 包含if __name__ == "__main__"启动入口，默认监听127.0.0.1:8080。

所有代码不超过1000行。

现在，检查一些细节：

- 在`_handle_create_reservation`中，我们使用了`conn.execute('BEGIN')`，但我们在调用前已经获取了write_lock，所以不需要使用`BEGIN IMMEDIATE`；普通BEGIN即可。但是，如果我们在释放锁后另一个线程可能修改数据，但我们在持有锁时执行整个事务，所以没问题。
- 同样，在`_cleanup_expired`中，我们使用`BEGIN`。

- 注意：在`_handle_create_item`中，我们使用`conn.execute('INSERT ...')`，没有显式BEGIN。由于我们设置了`isolation_level=None`，所以直接执行INSERT不会自动开始事务。我们需要手动BEGIN。如果没有手动BEGIN，默认会在首次执行DML时自动开始一个事务吗？实际上，当`isolation_level`为None时，Python sqlite3模块不会自动管理事务，你必须手动调用execute('BEGIN')。如果没有手动BEGIN，每个单独的execute会在它自己的隐式事务中执行？不是的：在`isolation_level=None`模式下，每个execute语句都会在单独的自动提交模式中运行（即自动提交？）。文档：当isolation_level设置为None时，连接处于自动提交模式。这意味着每个execute调用都会立即提交。所以，如果我们不手动BEGIN，每个操作都会独立提交。这会导致数据不一致。所以我们必须显式地手动BEGIN和COMMIT。

因此，在所有的写操作函数中，我们必须以`conn.execute('BEGIN')`开始一个事务。目前我们在`_handle_create_reservation`, `_handle_confirm_reservation`, `_handle_cancel_reservation`, `_cleanup_expired`中都这样做了。但在`_handle_create_item`中，我还没有显式BEGIN。我在代码中只使用了try/except，但缺少BEGIN。所以我需要添加`conn.execute('BEGIN')`。此外，在`_handle_create_item`中，我使用了`conn.commit()`和`conn.rollback()`，所以需要BEGIN。

修正`_handle_create_item`：

```python
    def _handle_create_item(self, conn, data):
        if not data or 'name' not in data or 'stock_total' not in data:
            self._send_error("Missing required fields: name, stock_total", 400)
            return
        name = data['name'].strip()
        if not name:
            self._send_error("name must not be empty", 400)
            return
        stock_total = data['stock_total']
        if not isinstance(stock_total, int) or stock_total <= 0:
            self._send_error("stock_total must be a positive integer", 400)
            return
        conn.execute('BEGIN')
        try:
            conn.execute('INSERT INTO items (name, stock_total, stock_available) VALUES (?, ?, ?)',
                         (name, stock_total, stock_total))
            conn.commit()
            item_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
            item = {'id': item_id, 'name': name, 'stock_total': stock_total, 'stock_available': stock_total}
            self._send_json(item, 201)
        except sqlite3.IntegrityError:
            conn.rollback()
            self._send_error(f"Item with name '{name}' already exists", 409)
```

注意：在发送响应之前我们提交了，但如果在发送响应时抛出异常，事务已经提交了，无数据丢失。

现在，对于读操作（GET /items），我们不需要事务，因为每个单独SELECT会自动提交（在自动提交模式下）? 如果isolation_level为None，SELECT不会被自动事务包围，但每个SELECT会看到数据库的最新状态（因为即时提交）。这也是可以接受的。而且读操作不需要跨多个查询的一致性，所以没问题。所以`_handle_get_items`中不需要BEGIN。

但注意：如果我们想要在读操作中保证一致性（比如在清理后立即读取），因为清理已经在之前的事务中提交了，所以读取可以。所以没问题。

现在，一个潜在问题：在`_cleanup_expired`中，我们使用`conn.execute('BEGIN')`，然后执行SELECT，再UPDATE，再COMMIT。这没错。

但是，在`_cleanup_expired`中，如果我们没有找到过期记录，我们仍然会提交空事务？我们执行了BEGIN，然后检查rows，如果没有行，我们也会执行COMMIT。在SQLite中，BEGIN后不执行任何语句直接COMMIT是有效的。但也可以在BEGIN之前就返回。为了效率，我们可以先检查是否有过期记录，再决定是否BEGIN。但为了简单，我们仍然BEGIN并COMMIT。这会产生不必要的写事务开销（可能需要获取写锁）。但写锁已经被我们持有，所以没关系。或者，我们可以在BEGIN之前先SELECT（在自动提交模式下）检查是否有记录，如果没有，就不开始事务。但SELECT在自动提交模式下可能会与并发的写冲突？但因为我们持有写锁，所以安全。而且这样可以减少不必要的事务。但代码复杂度增加。由于代码行数要求不超过1000，可以保留。不过，还是改进一下：先使用SELECT查询过期记录（在自动提交模式下），但注意SELECT是在我们持有写锁的情况下进行的，因为调用_cleanup_expired时我们已经获取了write_lock，所以其他线程不能写，因此我们的SELECT能看到所有数据。然后如果有行，再BEGIN。这样可以避免空事务。但是，在自动提交模式下执行SELECT，然后BEGIN，这些操作之间没有其他线程插足（因为我们持有锁），所以安全。所以：

```python
    def _cleanup_expired(self, conn):
        now = time.time()
        rows = conn.execute('''
            SELECT id, item_id, quantity FROM reservations
            WHERE status='pending' AND expires_at <= ?
        ''', (now,)).fetchall()
        if rows:
            conn.execute('BEGIN')
            try:
                for row in rows:
                    conn.execute('UPDATE reservations SET status=? WHERE id=?', ('expired', row['id']))
                    conn.execute('UPDATE items SET stock_available = stock_available + ? WHERE id=?',
                                 (row['quantity'], row['item_id']))
                conn.commit()
            except:
                conn.rollback()
                raise
```

但是，注意：在BEGIN和UPDATE之间，其他线程可能会修改这些记录？因为我们持有write_lock，所以其他线程不能执行任何写操作。但读操作可以（在锁外读），但他们不会修改记录。所以安全。所以我们可以这样做。但要注意：如果我们在BEGIN之前先SELECT（自动提交），然后BEGIN，这期间没有其他写操作，所以数据显示一致。因此我们可以这样优化。但为了简单，我可能会继续使用原先的版本（先BEGIN再SELECT）。但那样会有一个不必要的空事务。空事务对性能影响很小，所以保留也无妨。但我倾向于优化，因为代码不多。

但需要小心：在自动提交模式下，SELECT获取的快照是在每个语句开始时的数据库状态。而在我们获得锁之后，其他线程不能写，所以状态一致。所以没问题。

我将采用优化版本。

另一个点：在`_handle_create_reservation`中，我们使用`conn.execute('BEGIN')`后，其他操作可能在写锁被持有时进行。所以安全。

现在，确认`_handle_confirm_reservation`和`_handle_cancel_reservation`也使用了BEGIN。

现在，思考一个情况：在`_handle_create_reservation`中，如果库存不足，我们回滚事务并返回错误。但这时我们还没有提交，回滚后连接回到自动提交模式。正确。

现在，注意在写操作中，我们使用`conn.execute('BEGIN')`后，如果某个操作失败，我们调用`conn.rollback()`。但如果在rollback之前，我们已经发送了响应（例如发送了错误json），但响应发送可能不会失败，但我们需要确定在发送json之前回滚。在代码中，我们在检查失败后立即rollback，然后发送错误。所以顺序正确。

现在，关于并发控制：我们使用write_lock来确保写操作互斥。但是，在清理操作中，我们也需要获取write_lock。在do_GET和do_POST的开始，我们都会获取write_lock进行清理。这样，如果有大量请求同时到达，它们会在清理步骤串行化。但是，清理步骤通常很快（如果没有过期记录，很快就过去了）。但如果很多请求同时到达，它们会排队等待清理锁。这可能会限制并发。但是，这对于小型服务可以接受，而且题目要求“正确处理并发请求下的库存一致性”，我们做到了。我们可以考虑将清理锁与写锁分开，但为了简单，我们使用同一个锁。

注意：我们可以使用读写锁（`threading.Lock`不支持，但可以使用共享锁？标准库没有读写锁）。所以使用普通锁即可。

现在，我们确认代码逻辑没有错误。

我们还需要处理超时：如果客户端没有在内容头中提供Content-Length，`self.rfile.read()`可能会阻塞。默认BaseHTTPRequestHandler会处理。

现在，编写完整的代码。

在`__main__`中，我们需要创建一个多线程服务器。使用`ThreadingMixIn`。

我们需要定义`ThreadingHTTPServer`。

```python
class ThreadingHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True
```

我们也可以使用`http.server.ThreadingHTTPServer`（如果Python 3.7+）。但为了兼容性，我们自定义。

启动服务器：

```python
def main():
    init_db()
    server = ThreadingHTTPServer(('127.0.0.1', 8080), RequestHandler)
    print('Starting server on http://127.0.0.1:8080')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nShutting down...')
        server.server_close()

if __name__ == '__main__':
    main()
```

现在，检查代码完整性。

现在，列出所有函数：

- init_db()
- ThreadingHTTPServer
- RequestHandler继承BaseHTTPRequestHandler
  - do_GET
  - do_POST
  - _send_json
  - _send_error
  - _read_json
  - _parse_int
  - _cleanup_expired
  - _handle_get_items
  - _handle_create_item
  - _handle_create_reservation
  - _handle_confirm_reservation
  - _handle_cancel_reservation

还有常量DB_PATH, write_lock。

现在，确保我们使用了正确的`import`： `import threading`。

现在，编写最终代码。

注意：路径匹配时，我们需要区分`POST /reservations`（创建）和`POST /reservations/{id}/confirm`。所以在do_POST中，我们用条件判断。我们使用了`parts[0]=='reservations'`和`len(parts)==3`来匹配confirm和cancel。如果`len(parts)==2`或`len(parts)==3`但action不是confirm/cancel，我们返回404。目前我们的条件覆盖了。

对于`parts[0]=='reservations' and len(parts)==1`，匹配创建。

对于`parts[0]=='reservations' and len(parts)==2`，可能是`/reservations/1`，但我们在API中没有定义，所以返回404。我们在else里返回404。

所以，在do_POST中：
- 如果路径匹配'items'，调用create_item。
- 如果路径匹配'reservations'，长度1，调用create_reservation。
- 如果长度3且action是confirm或cancel，调用对应函数。
- 否则404。

同样，在do_GET中，只有长度1且resource是items。

注意：我们还应考虑`/items/`（尾部斜杠），处理后path是'items'，所以匹配。

现在，我们测试一些边缘情况：

- 请求体不是JSON时，_read_json返回None，create_item和create_reservation会检查data是否为None，并返回400。
- 对于confirm/cancel，不读取body，所以即使发送了body也无影响。

- 如果在读取body时出现异常（如Content-Length太大等），我们让异常传播到外层catch。

- 在写操作中，如果数据库操作异常（如外键约束失败），我们捕获并回滚。当前我们没有显式捕获外键异常（除非我们定义了foreign key constraints并设置PRAGMA foreign_keys=ON）。我们可以设置PRAGMA foreign_keys=ON，但默认是关闭的。在我们的建表语句中有FOREIGN KEY ON items，但不启用。我们可以启用，这样插入外键不存在的预约会失败。但我们的代码在创建预约时会检查商品是否存在，所以不会导致外键异常。为了安全，可以在连接上设置`conn.execute("PRAGMA foreign_keys=ON")`。但这不是必须。

- 在确认/取消时，如果预约id不存在，我们返回404。

- 在取消时，我们释放库存。注意：释放后stock_available可能超过stock_total？比如多次取消同一个预约是不可能的，因为状态检查确保只有pending才能取消，而取消后状态变为cancelled，不能再取消。所以不会多次释放。所以安全。

- 在清理时，如果预约被释放后，库存恢复，但可能超过stock_total？理论上不会，因为每次扣减都是在stock_available足够时，最终stock_available总是小于等于stock_total。释放后不会超过stock_total，因为释放的数量是之前扣除的，不会超。所以安全。

- 关于时间戳过期：比较expires_at <= now。我们使用time.time()得到的时间戳是秒级浮点数。在我们的清理中，如果预约的expires_at <= now，则过期。

- 注意：如果在清理时，同一个事务中我们可能在SELECT之后，UPDATE之前，另一个线程也执行了类似操作（但由于写锁不会）。所以安全。

现在，我们编写完整代码。

我还会加入一些日志（可选），但可以省略。

最后，确保代码行数不超过1000。这个代码量大概在300行左右。

现在，让我们写出最终代码。

在写之前，检查一下是否遗漏了任何需求：

- 商品有stock_total和stock_available，创建时stock_available=stock_total。我们做了。
- 预约字段：id, item_id, quantity, status, expires_at, created_at。我们使用了expires_at和created_at。
- 创建预约需要ttl_seconds，我们用了。
- 库存不足时409，我们返回了包含error的409。
- 确认后不再释放库存（我们只改了状态，没释放）。
- 取消释放库存。
- 每次请求前清理过期pending预约。我们在do_GET和do_POST开始都做了。
- 并发控制：用了write_lock和事务。
- 返回JSON，错误包含error。
- 监听127.0.0.1:8080。
- 启动入口。

所有都满足。

现在，编写代码。注意：需要将代码放在一个代码块中。按照输出要求，只输出完整Python代码，不要解释。

为了确保代码可运行，我们需要注意以下几点：

- 在创建连接后设置`conn.isolation_level = None`。
- 在每次写操作前调用`conn.execute('BEGIN')`。
- 在清理中使用`conn.execute('BEGIN')`（优化版本）。

- 注意在`_handle_create_item`中，我们放在锁下执行，但其中又调用`conn.execute('BEGIN')`。这是正确的。

- 在`_cleanup_expired`中，我们在持有锁的情况下，首先使用自动提交SELECT，然后如果有记录，再BEGIN。但是，在自动提交模式下执行SELECT不会与后面的BEGIN冲突，因为我们持有写锁，防止了其他线程同时写。注意：在自动提交模式下，每条语句独立提交。但SELECT不会改变数据库，所以没问题。但有一个微妙点：自动提交模式下，SELECT会开始一个隐式读事务，这个读事务可能持有共享锁，直到语句完成。我们在锁下，不会影响其他线程的写。但是，如果我们在BEGIN之后，之前自动提交的读事务已经完成，所以不会有冲突。所以可以。

- 但是，在实现中，我决定不使用优化版本，而是始终使用BEGIN清理（简单）。因为优化版本需要额外的判断，且我们持有锁，性能差异不大。但我可以选择简单版本。为了代码清晰，我选择简单版本（先BEGIN，然后SELECT和UPDATE，然后COMMIT）。空事务也是可以的。

- 但注意：在清理中，如果无过期记录，BEGIN一个事务然后COMMIT，这个操作本身会在写锁下进行（因为我们在写锁下），所以会短暂获取写锁。如果没有过期记录，这个空事务可能影响性能。但写锁本身是串行化的，所有请求都要经过这里，所以空事务的开销是存在的。但鉴于这是一个小型服务，并且持有写锁的时间非常短，可以接受。为了稍微优化，我们可以在持有写锁后，先快速SELECT（在自动提交下）检查是否有过期记录，如果没有，直接跳过事务。这样写锁持有的时间更短。所以我采用优化版本。

具体实现：

```python
    def _cleanup_expired(self, conn):
        now = time.time()
        cursor = conn.execute('''
            SELECT id, item_id, quantity FROM reservations
            WHERE status='pending' AND expires_at <= ?
        ''', (now,))
        rows = cursor.fetchall()
        if rows:
            conn.execute('BEGIN')
            try:
                for row in rows:
                    conn.execute('UPDATE reservations SET status=? WHERE id=?', ('expired', row['id']))
                    conn.execute('UPDATE items SET stock_available = stock_available + ? WHERE id=?',
                                 (row['quantity'], row['item_id']))
                conn.commit()
            except:
                conn.rollback()
                raise
```

这样做会多次SELECT（对于没有过期记录的情况，不需要事务）。注意：在持有写锁的情况下，自动提交SELECT与并发无关，所以安全。

但在BEGIN之前，SELECT是在自动提交模式下执行，不会持有数据库锁？但我们已经通过write_lock保护了写操作，所以SELECT仍看到一致的数据。但是，如果同时有其他线程查询（GET），它们可能在自动提交模式下读取，可能会读到中间状态吗？由于我们在write_lock中，其他线程的写操作不能同时进行，但读操作可以（它们没有锁）。在读操作中，可能同时执行清理（在其他线程）？实际上，清理是在write_lock中，所以同一时间只有一个线程在清理。其他线程的读操作在清理锁外，所以可能看到一个中间状态（当清理线程在BEGIN和COMMIT之间时，其他读操作可能读取到未提交的数据？这取决于SQLite隔离级别。SQLite默认的隔离级别是“可重复读”或“读已提交”？实际上，在WAL模式下，读操作看到的是开始读取时的快照，直到语句完成。但是在我们的清理中，我们在持有write_lock时在事务中修改了数据，但尚未提交，那么其他线程的读操作能否看到未提交的修改？取决于隔离级别。在默认的“deferred”模式下，如果一个写事务正在执行且未提交，读操作可能会看到旧的版本（因为WAL允许读未提交？）。但实际上，在SQLite中，读操作不会看到未提交的更改，因为WAL使用快照。所以其他线程的读操作不会看到未提交的数据。但这意味着在清理事务提交之前，其他线程可能认为库存没有释放。这在某些情况下可能需要考虑。但我们的请求处理流程是先清理再操作，如果在清理事务提交之前，其他线程开始一个读操作，可能看到旧的库存。但只有清理和当前线程在同一个锁下，其他线程不能同时进行写操作。读操作可能在清理锁释放后才开始（因为清理在锁内，而读操作在锁外，但它们可能同时运行？当清理线程持有锁时，其他线程的读操作可以运行（因为锁只保护写，读不需要锁），但清理线程可能尚未提交，其他读操作会看到清理前的状态。这对于读操作是可以接受的，因为读操作看到的是稍旧一点的数据（但是事务最终会提交，读取稍旧的数据在允许范围内）。对于写操作（在清理之后的同一请求中），我们在清理释放锁后，可能会等待写锁，然后开始写事务，此时清理已经提交，所以会看到最新数据。所以没问题。

因此设计合理。

现在，确认`_handle_get_items`是在清理之后（清理可能已经提交）执行的，所以它看到的是最新数据。

现在，代码中还应该注意：对于POST /items，我们返回item对象。对于POST /reservations，返回预约对象。对于confirm和cancel，我们也返回更新后的对象（可选）。题目没有明确要求返回内容，但返回是有益的。

对于confirm和cancel，我们返回了完整的预约对象。

现在，思考一下：在`_handle_create_item`中，我们返回201状态码。在`_handle_create_reservation`中返回201。对于confirm和cancel返回200。对于GET返回200。错误返回相应的状态码。

现在，错误处理：如果数据库连接失败，我们返回500。但是，如果连接创建成功但后续数据库操作异常，我们也返回500。我们的catch块捕获Exception，返回500。在catch块中，我们没有关闭连接？finally会关闭。但注意，如果在`_cleanup_expired`中异常，我们可能已经回滚，但异常会传播到do_GET/do_POST的try，然后返回500。但此时conn可能处于不一致状态（事务未完成），但我们会在finally中关闭连接，关闭时会回滚未提交的事务。所以安全。

现在，注意：在`_cleanup_expired`内部，我们处理了异常并重新抛出（raise）。所以外部的catch也会捕获。

在写操作函数中，如果我们捕获到异常（如外键异常），我们会在函数内回滚并发送错误，但不会重新抛出。所以对外部是正常的。如果在这些函数中发生未捕获的异常，会由外部catch处理，外部会发送500并关闭连接。

现在，验证库存检查：在`_handle_create_reservation`中，我们在BEGIN之后，SELECT库存然后检查。如果库存不足，回滚并发送错误。注意：在回滚后，我们直接返回，不再进行任何数据库操作。正确。

现在，确保在创建预约时，我们使用了`conn.execute('BEGIN')`。但在我们调用之前，写锁已经被获取，所以事务是安全的。但是，如果我们没有获取写锁，可能会发生并发问题。所以写锁是必要的。

现在，我们检查do_POST中的写操作：每个写操作都在`with write_lock:`块中。这意味着同一时间只有一个写操作（包括清理）在执行。注意：清理在之前已经完成（也使用了写锁），所以不会有冲突。

但是，在do_POST中，我们首先获取写锁执行清理，释放锁，然后对于写操作再次获取锁。这是两个独立的锁区间。可能两个请求同时到达，A先获取清理锁，清理后释放，然后等待写锁；B在A释放清理锁后，获取清理锁，清理后释放，然后等待写锁。这两个请求的写操作会排队。所以最终写操作是串行的。这实现了写操作的互斥。

但是，需要注意：如果在清理和写操作之间，有其他线程的写操作插队（因为写锁是同一个锁，清理和写操作是同一把锁），所以如果A正在清理，B可能正在等待写锁（因为B在do_POST中先等待清理锁，但清理锁和写锁是同一个锁？是的，我们使用的是同一个`write_lock`，所以A在清理时持有write_lock，B的清理（也是write_lock）会被阻塞。所以A清理完后释放锁，B才能获得锁进行清理。所以实际上，所有请求的清理和写操作都用一个锁串行化了。所以do_POST的整体流程是：等待write_lock（清理），释放；等待write_lock（写操作），释放。所以两个连续的锁区间，但其他线程可以在中间插足吗？如果在A的清理释放锁和写操作获取锁之间，B可能获取锁进行清理或写操作？可能。但最终写操作是互斥的。一致性还是可以保证的。

但这样，写操作和清理完全串行化，所以性能可能较低。但对我们的小型服务可接受。

另一种设计：清理使用单独的锁，写操作使用写锁。这样读请求在清理时只需要清理锁，写操作在清理锁和写锁之间可以并发？但增加了复杂性。我们保持简单。

现在，写代码。

我将在代码中保持清晰的注释，方便阅读。注释不计入行数？题目要求代码行数不超过1000，但不强制无注释。我会添加必要注释。

最终代码开始。

注意：在do_GET和do_POST中，我们可能会捕获所有异常，但需要避免捕获一些退出信号如KeyboardInterrupt。但是`serve_forever`在主线程，不会在这里。

现在，输出代码。
````

## Assistant

````markdown
```python
import http.server
import socketserver
import json
import sqlite3
import time
import os
import threading
from urllib.parse import urlparse

DB_PATH = "inventory.db"
write_lock = threading.Lock()


def init_db():
    """Initialize database with required tables."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            stock_total INTEGER NOT NULL,
            stock_available INTEGER NOT NULL
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS reservations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            expires_at REAL NOT NULL,
            created_at REAL NOT NULL,
            FOREIGN KEY (item_id) REFERENCES items(id)
        )
    ''')
    conn.execute('''
        CREATE INDEX IF NOT EXISTS idx_res_status_expires
        ON reservations(status, expires_at)
    ''')
    conn.commit()
    conn.close()


class ThreadingHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True


class RequestHandler(http.server.BaseHTTPRequestHandler):
    server_version = "InventoryAPI/1.0"

    # ------------------------------------------------------------------
    #  Utility methods
    # ------------------------------------------------------------------
    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def _send_error(self, message, status=400):
        self._send_json({"error": message}, status)

    def _read_json(self):
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length == 0:
            return None
        body = self.rfile.read(content_length)
        try:
            return json.loads(body.decode('utf-8'))
        except json.JSONDecodeError:
            return None

    @staticmethod
    def _parse_int(s):
        try:
            return int(s)
        except (ValueError, TypeError):
            return None

    # ------------------------------------------------------------------
    #  Database helper – cleanup expired reservations
    # ------------------------------------------------------------------
    def _cleanup_expired(self, conn):
        """Must be called while write_lock is held."""
        now = time.time()
        cursor = conn.execute('''
            SELECT id, item_id, quantity FROM reservations
            WHERE status='pending' AND expires_at <= ?
        ''', (now,))
        rows = cursor.fetchall()
        if rows:
            conn.execute('BEGIN')
            try:
                for row in rows:
                    conn.execute('UPDATE reservations SET status=? WHERE id=?',
                                 ('expired', row['id']))
                    conn.execute('UPDATE items SET stock_available = stock_available + ? WHERE id=?',
                                 (row['quantity'], row['item_id']))
                conn.commit()
            except Exception:
                conn.rollback()
                raise

    # ------------------------------------------------------------------
    #  Route handlers – GET
    # ------------------------------------------------------------------
    def _handle_get_items(self, conn):
        cursor = conn.execute('SELECT id, name, stock_total, stock_available FROM items')
        items = [dict(row) for row in cursor.fetchall()]
        self._send_json(items)

    # ------------------------------------------------------------------
    #  Route handlers – POST
    # ------------------------------------------------------------------
    def _handle_create_item(self, conn, data):
        if not data or 'name' not in data or 'stock_total' not in data:
            self._send_error("Missing required fields: name, stock_total", 400)
            return
        name = data['name'].strip()
        if not name:
            self._send_error("name must not be empty", 400)
            return
        stock_total = data['stock_total']
        if not isinstance(stock_total, int) or stock_total <= 0:
            self._send_error("stock_total must be a positive integer", 400)
            return

        conn.execute('BEGIN')
        try:
            conn.execute('INSERT INTO items (name, stock_total, stock_available) VALUES (?, ?, ?)',
                         (name, stock_total, stock_total))
            conn.commit()
            item_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
            item = {
                'id': item_id,
                'name': name,
                'stock_total': stock_total,
                'stock_available': stock_total
            }
            self._send_json(item, 201)
        except sqlite3.IntegrityError:
            conn.rollback()
            self._send_error(f"Item with name '{name}' already exists", 409)

    def _handle_create_reservation(self, conn, data):
        if not data or 'item_id' not in data or 'quantity' not in data or 'ttl_seconds' not in data:
            self._send_error("Missing required fields: item_id, quantity, ttl_seconds", 400)
            return
        item_id = data['item_id']
        quantity = data['quantity']
        ttl_seconds = data['ttl_seconds']
        if not isinstance(item_id, int) or item_id <= 0:
            self._send_error("item_id must be a positive integer", 400)
            return
        if not isinstance(quantity, int) or quantity <= 0:
            self._send_error("quantity must be a positive integer", 400)
            return
        if not isinstance(ttl_seconds, (int, float)) or ttl_seconds <= 0:
            self._send_error("ttl_seconds must be a positive number", 400)
            return

        conn.execute('BEGIN')
        try:
            item = conn.execute('SELECT id, stock_available FROM items WHERE id=?',
                                (item_id,)).fetchone()
            if not item:
                conn.rollback()
                self._send_error("Item not found", 404)
                return
            if item['stock_available'] < quantity:
                conn.rollback()
                self._send_error("Insufficient stock", 409)
                return

            # Deduct stock
            conn.execute('UPDATE items SET stock_available = stock_available - ? WHERE id=?',
                         (quantity, item_id))
            # Create reservation
            now = time.time()
            created_at = now
            expires_at = now + ttl_seconds
            conn.execute('''
                INSERT INTO reservations (item_id, quantity, status, expires_at, created_at)
                VALUES (?, ?, 'pending', ?, ?)
            ''', (item_id, quantity, expires_at, created_at))
            conn.commit()

            reservation_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
            reservation = {
                'id': reservation_id,
                'item_id': item_id,
                'quantity': quantity,
                'status': 'pending',
                'expires_at': expires_at,
                'created_at': created_at
            }
            self._send_json(reservation, 201)
        except Exception:
            conn.rollback()
            raise

    def _handle_confirm_reservation(self, conn, reservation_id):
        conn.execute('BEGIN')
        try:
            row = conn.execute('SELECT * FROM reservations WHERE id=?',
                               (reservation_id,)).fetchone()
            if not row:
                conn.rollback()
                self._send_error("Reservation not found", 404)
                return
            if row['status'] != 'pending':
                conn.rollback()
                self._send_error(
                    f"Cannot confirm reservation with status '{row['status']}'", 409)
                return
            conn.execute("UPDATE reservations SET status='confirmed' WHERE id=?",
                         (reservation_id,))
            conn.commit()
            updated = conn.execute('SELECT * FROM reservations WHERE id=?',
                                   (reservation_id,)).fetchone()
            self._send_json(dict(updated), 200)
        except Exception:
            conn.rollback()
            raise

    def _handle_cancel_reservation(self, conn, reservation_id):
        conn.execute('BEGIN')
        try:
            row = conn.execute('SELECT * FROM reservations WHERE id=?',
                               (reservation_id,)).fetchone()
            if not row:
                conn.rollback()
                self._send_error("Reservation not found", 404)
                return
            if row['status'] != 'pending':
                conn.rollback()
                self._send_error(
                    f"Cannot cancel reservation with status '{row['status']}'", 409)
                return
            # Release stock
            conn.execute('UPDATE items SET stock_available = stock_available + ? WHERE id=?',
                         (row['quantity'], row['item_id']))
            conn.execute("UPDATE reservations SET status='cancelled' WHERE id=?",
                         (reservation_id,))
            conn.commit()
            updated = conn.execute('SELECT * FROM reservations WHERE id=?',
                                   (reservation_id,)).fetchone()
            self._send_json(dict(updated), 200)
        except Exception:
            conn.rollback()
            raise

    # ------------------------------------------------------------------
    #  HTTP method dispatchers
    # ------------------------------------------------------------------
    def do_GET(self):
        conn = None
        try:
            conn = sqlite3.connect(DB_PATH, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA busy_timeout=5000")
            conn.isolation_level = None

            # Clean up expired reservations before every request
            with write_lock:
                self._cleanup_expired(conn)

            parsed = urlparse(self.path)
            path = parsed.path.strip('/')
            parts = path.split('/')

            if len(parts) == 1 and parts[0] == 'items':
                self._handle_get_items(conn)
            else:
                self._send_error("Not Found", 404)
        except Exception as e:
            self._send_error(f"Internal Server Error: {str(e)}", 500)
        finally:
            if conn:
                conn.close()

    def do_POST(self):
        conn = None
        try:
            conn = sqlite3.connect(DB_PATH, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA busy_timeout=5000")
            conn.isolation_level = None

            # Clean up expired reservations before every request
            with write_lock:
                self._cleanup_expired(conn)

            parsed = urlparse(self.path)
            path = parsed.path.strip('/')
            parts = path.split('/')

            if len(parts) == 1 and parts[0] == 'items':
                # POST /items
                data = self._read_json()
                with write_lock:
                    self._handle_create_item(conn, data)
            elif len(parts) == 1 and parts[0] == 'reservations':
                # POST /reservations
                data = self._read_json()
                with write_lock:
                    self._handle_create_reservation(conn, data)
            elif len(parts) == 3 and parts[0] == 'reservations' and parts[2] == 'confirm':
                # POST /reservations/{id}/confirm
                rid = self._parse_int(parts[1])
                if rid is None:
                    self._send_error("Invalid reservation id", 400)
                    return
                with write_lock:
                    self._handle_confirm_reservation(conn, rid)
            elif len(parts) == 3 and parts[0] == 'reservations' and parts[2] == 'cancel':
                # POST /reservations/{id}/cancel
                rid = self._parse_int(parts[1])
                if rid is None:
                    self._send_error("Invalid reservation id", 400)
                    return
                with write_lock:
                    self._handle_cancel_reservation(conn, rid)
            else:
                self._send_error("Not Found", 404)
        except Exception as e:
            self._send_error(f"Internal Server Error: {str(e)}", 500)
        finally:
            if conn:
                conn.close()


def main():
    init_db()
    server = ThreadingHTTPServer(('127.0.0.1', 8080), RequestHandler)
    print("Starting server on http://127.0.0.1:8080")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.server_close()


if __name__ == "__main__":
    main()
```
````
