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
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 116.878943
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 442, "total_tokens": 20572, "completion_tokens": 20130, "prompt_tokens_details": null}`
- Prompt tokens: 442
- Completion tokens: 20130
- Total tokens: 20572

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
我们被要求使用Python 3标准库编写一个单文件HTTP API服务，用于管理库存和预约。要求使用内置sqlite3持久化，首次启动自动建表。API端点包括：GET /items, POST /items, POST /reservations, POST /reservations/{id}/confirm, POST /reservations/{id}/cancel，以及每次请求前清理过期pending预约。

我们需要处理并发，使用事务和线程锁。需要监听127.0.0.1:8080。

由于不能使用第三方库，我们需要使用http.server或类似的模块。我们可以使用http.server.BaseHTTPRequestHandler并子类化。但要注意，处理POST请求体需要解析JSON。我们也可以使用socketserver.ThreadingMixIn来支持多线程。

我们需要一个全局的线程锁（threading.Lock）来保护数据库写入操作，因为sqlite3本身有一定程度的并发支持，但为了安全，我们可以在每次操作数据库时加锁，或者使用SQLite的WAL模式，但最简单是用锁。

我们还需要在每次请求前清理过期预约，这意味着在每个请求处理开始时，我们可以运行一个清理函数，删除所有status='pending'且expires_at < now的记录，并更新相应的items.stock_available。

数据库设计：

- items表：id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, stock_total INTEGER NOT NULL, stock_available INTEGER NOT NULL
- reservations表：id INTEGER PRIMARY KEY AUTOINCREMENT, item_id INTEGER NOT NULL, quantity INTEGER NOT NULL, status TEXT NOT NULL DEFAULT 'pending', expires_at TEXT NOT NULL (存储ISO格式或timestamp), created_at TEXT NOT NULL。

我们将使用sqlite3，连接时检查是否需要创建表。我们可以在模块加载时创建连接并设置。但要注意，每个线程应该使用自己的连接，或者在处理请求时创建连接，但为了简单，我们可以使用全局连接并加锁。sqlite3连接默认不是线程安全的，但如果我们加锁，则可以在线程间共享。也可以使用check_same_thread=False，然后加锁。我们选择后者。

我们将定义一个类InventoryService，封装所有数据库操作。使用一个锁来序列化对数据库的写操作，读操作也可以加锁或直接读（但为了简单，统一加锁）。在清理过期预约时也需要写。

锁可以是threading.Lock()，在每个请求处理开始时加锁。

我们实现一个简单的HTTP服务器：MyHTTPHandler继承BaseHTTPRequestHandler。我们需要重写do_GET, do_POST，并解析路径和方法。

注意：我们需要解析路径参数如/reservations/{id}/confirm，所以可以使用正则或简单split。

我们还需要处理JSON请求体，读取body并使用json.loads。

错误处理：返回JSON包含error字段。

启动入口：if __name__ == "__main__": 创建服务器并启动。

代码总行数不超过1000行。

我们尽量写得清晰。

需要考虑：POST /items需要参数name, stock_total，然后设置stock_available等于stock_total。

POST /reservations需要item_id, quantity, ttl_seconds。我们需要检查库存充足（stock_available >= quantity），如果不足返回409。注意：在创建预约时，我们检查stock_available，然后减少stock_available，插入预约记录，设置expires_at为当前时间+ttl_seconds，status为'pending'。这里需要在同一个事务中完成，使用锁。

POST /reservations/{id}/confirm：将预约状态改为confirmed，不释放库存（已经扣减了，确认后库存不再释放）。但是注意：如果预约已过期，不应该可以确认？我们需要检查状态是否为pending，如果不是则返回错误。同样，取消时释放库存，将状态改为cancelled，增加stock_available。都需要在事务中操作。

清理功能：在每个请求开始时执行。我们需要查找所有status='pending'且expires_at < now的记录，然后将这些记录的status更新为'expired'，并对于每个这样的预约，增加对应item的stock_available。可以在一个事务中处理所有：查询过期预约，然后逐个更新库存，或者使用UPDATE ... RETURNING？sqlite3不支持，需要编程方式。我们可以先查询出所有过期的pending预约，然后在一个事务中更新状态和库存。为了简单，可以使用循环。

由于每次请求都会清理，可能频繁执行，但可以接受。

但是，注意清理需要在每次请求前执行，但可能重复清理已经清理过的。但是为了确保一致性，我们可以在处理请求的开始（在路由之前）执行清理。注意：清理时也需要锁。

为了效率，我们可以在初始化时启动一个后台线程定期清理，但要求是“每次请求前清理”，所以我们就在请求处理开始时做。我们可以在do_GET/do_POST的开头调用清理函数。

现在开始写代码。

需要考虑的点：

- 数据库路径：使用当前目录下的inventory.db。
- 使用with语句管理锁和数据库操作。
- JSON响应：设置Content-Type: application/json。
- 对于错误响应，状态码错误（如400, 404, 409）。
- 对于POST请求，验证必要的参数。
- 使用try-except处理JSON解析错误和数据库错误。
- 使用http.server.HTTPServer和socketserver.ThreadingMixIn实现多线程。

代码结构：

1. 导入模块：http.server, json, sqlite3, threading, socketserver, os, time, datetime, re, sys等。
2. 定义数据库初始化函数。
3. 定义清理函数。
4. 定义服务类InventoryService（包含数据库操作方法）。
5. 定义请求处理器类MyHandler。
6. 在if __name__中启动服务器。

为了简化，我们也可以将所有数据库操作封装在请求处理器中直接调用，但有单独的服务类更清晰。

注意：锁需要是模块级别的，因为处理器实例每个请求创建，但锁需要共享。

锁：db_lock = threading.Lock()

数据库连接：在每个线程中使用独立的连接，或者在进入锁后使用全局连接？为了简单，我们可以使用全局连接，设置check_same_thread=False，并且在每次操作时加锁。但是SQLite连接不是完全线程安全的，即使加锁，也可能出现问题（例如，如果在一个线程中使用连接在锁内，没问题）。我们使用全局连接，在每次请求时，在锁的保护下使用连接。但要注意，由于我们使用ThreadingMixIn，每个请求在单独的线程中处理，所以如果我们在锁内使用连接，是安全的。为了进一步安全，我们可以在进入锁后，获取连接并执行操作。但是全局连接在锁的保护下是安全的。

另外，我们也可以在每个请求中创建新连接，并在锁内执行，但创建连接开销稍大。全局连接+锁可以工作。

我们使用全局连接：conn = sqlite3.connect('inventory.db', check_same_thread=False) 并且 conn.execute("PRAGMA journal_mode=WAL") 提高并发性。但WAL允许读写并发，但我们的锁会序列化写，但读可以同时进行。但我们简化，使用一个锁保护所有数据库访问（读写都加锁）。由于每次请求都需要清理（写操作），所以基本上所有请求都会获得锁，这样的话性能可能成为瓶颈，但对于小型服务应该可以接受。注意：清理也涉及到写，所以所有请求都需要锁（除了GET items是读，但清理需要写，所以也需要锁）。我们可以将读操作不加锁，但为了简单，全部加锁。但我们可以优化：读操作不需要锁？但清理需要写，如果读不加锁，可能会读到不一致的数据。因为清理会修改库存，所以读和写之间应该同步。我们可以用一个读写锁，但标准库没有。使用单一锁最简单。

所以：我们在每个请求处理器中，在调用清理和数据库操作之前获取锁，完成整个处理过程后释放。但注意，在do_GET中，我们可能需要先获取锁执行清理，然后释放锁，再获取锁执行查询？这样会有问题，因为清理后可能其他线程做了修改。最好在一个锁保护下完成整个请求处理。所以我们在do_GET/do_POST开始处获取锁，在响应发送后释放。但是注意，BaseHTTPRequestHandler的响应通常是在方法内完成，所以我们可以获取锁，然后处理所有逻辑，发送响应，最后释放。但需要注意，我们发送响应后，锁释放前，如果我们有异常，也可能不释放。所以最好用try-finally。

我们可以在__init__方法中获取锁？不，因为每个请求一个实例。我们可以在处理请求的方法开头获取锁。

但是，如果我们使用ThreadingMixIn，每个线程处理一个请求，所以锁在方法开头获取，在整个请求期间持有，会阻塞其他请求。但是因为每个请求都需要写清理，所以即使是GET也要执行清理，所以所有请求都将序列化。这可能是最简单的做法。

为了稍微提高性能，我们可以在清理完成后，对于读请求（如GET /items）可以释放锁然后重新获取？但释放后其他写可能改变，读会看到新的状态，这可能可以接受。但要求是“每次请求前清理”，我们必须在请求处理之前进行清理，以确保数据的时效性。所以我们可以先执行清理（需要写锁），然后如果请求是读，我们可以释放锁，再读（可能需要锁？读不需要锁但可能读不到最新的？）。或者，我们可以在清理后，使用一个单独的事务来执行查询，但也可以保持锁直到响应完成。为了简单，我们保持锁直到响应完成，这样能保证一致性且简单。

所以，整体方案：全局锁db_lock，在每个请求处理方法开始时获取，在结束时释放。

但是，如果我们使用类级别的锁，我们在方法前获取，那么多个请求会序列化。对于GET请求，如果很多，可能会慢。但我们是小型库存服务，可以接受。

另外，注意HTTP请求的并发性可能通过ThreadingMixIn支持多线程，但锁会序列化请求，但至少不会死锁。

现在开始写代码。

首先，导入模块：

import http.server
import json
import sqlite3
import threading
import socketserver
import os
import time
import re
from datetime import datetime, timezone, timedelta
import sys

接下来，定义数据库路径：

DB_PATH = 'inventory.db'

定义全局锁：

db_lock = threading.Lock()

定义数据库连接（全局，在初始化时创建）：

conn = None

但我们可能需要在初始化时创建表。最好在模块级别进行初始化。

定义初始化函数：

def init_db():
    global conn
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute('''CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        stock_total INTEGER NOT NULL,
        stock_available INTEGER NOT NULL
    )''')
    conn.execute('''CREATE TABLE IF NOT EXISTS reservations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        status TEXT NOT NULL DEFAULT 'pending',
        expires_at TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY(item_id) REFERENCES items(id)
    )''')
    conn.commit()

在if __name__中调用init_db().

然后定义清理函数clean_expired()，它使用全局锁获取连接执行清理。但注意，这个函数会在每个请求处理方法中调用，并且已经在锁的保护下（获取锁后调用），所以锁可以重用。我们也可以在clean_expired内部获取锁，但为了避免重复加锁，最好在调用之前已经获取锁。所以clean_expired假设调用者已经持有锁。

我们也可以将clean_expired作为InventoryService的方法，传入连接。

我们定义一个类InventoryService，包含所有数据库操作方法。这些方法将conn作为参数传入，由调用者提供连接。调用者在获取锁后使用连接。

但是，由于我们有全局连接，我们可以直接在方法中使用conn。不过要确保调用时已经获取锁。

我们也可以将服务方法定义为类方法，不在类中。

为了组织，我可以定义一个Handler类，包含静态方法操作数据库，使用全局conn，但调用前必须获取锁。

为了简化，我们直接在MyHandler中实现所有逻辑，但这样可能不便于重用。但代码量不大，可以直接写。

我们可以将数据库操作函数定义在模块级别，例如：

def get_all_items(conn): ...
def create_item(conn, name, stock_total): ...
def create_reservation(conn, item_id, quantity, ttl_seconds): ...
def confirm_reservation(conn, reservation_id): ...
def cancel_reservation(conn, reservation_id): ...
def clean_expired(conn): ...

这些函数接收conn作为参数，由调用者提供。调用者在获取锁后调用。

现在，实现HTTP处理器MyHandler：

class MyHandler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        with db_lock:
            try:
                self._clean_expired()
                if self.path == '/items':
                    self._handle_get_items()
                else:
                    self._send_error(404, "Not found")
            except Exception as e:
                self._send_error(500, str(e))

    def do_POST(self):
        with db_lock:
            try:
                self._clean_expired()
                # parse path
                path = self.path
                if path == '/items':
                    self._handle_post_items()
                elif re.match(r'^/reservations/\d+/confirm$', path):
                    # extract id
                    id = int(path.split('/')[2])
                    self._handle_post_confirm(id)
                elif re.match(r'^/reservations/\d+/cancel$', path):
                    id = int(path.split('/')[2])
                    self._handle_post_cancel(id)
                elif path == '/reservations':
                    self._handle_post_reservations()
                else:
                    self._send_error(404, "Not found")
            except Exception as e:
                self._send_error(500, str(e))

注意：我们需要在do_GET和do_POST中获取锁，然后调用_clean_expired，再处理具体逻辑。

我们需要实现_clean_expired和具体处理方法。

_send_error方法发送错误响应：

def _send_error(self, code, message):
    self.send_response(code)
    self.send_header('Content-Type', 'application/json')
    self.end_headers()
    self.wfile.write(json.dumps({'error': message}).encode())

_send_json发送成功响应：

def _send_json(self, data, code=200):
    self.send_response(code)
    self.send_header('Content-Type', 'application/json')
    self.end_headers()
    self.wfile.write(json.dumps(data).encode())

读请求体：对于POST，我们需要读取body。我们可以使用self.rfile.read(content_length)来读取。

def _read_body(self):
    content_length = int(self.headers.get('Content-Length', 0))
    if content_length == 0:
        return {}
    body = self.rfile.read(content_length)
    return json.loads(body.decode())

注意处理JSON解析错误。

现在实现具体逻辑：

_handle_get_items: 查询items表，返回列表，包含id, name, stock_total, stock_available。

使用conn.execute('SELECT id, name, stock_total, stock_available FROM items')，fetchall()，转换为dict列表。

_handle_post_items: 从body获取name和stock_total。验证name非空，stock_total是正数。插入items，stock_available初始等于stock_total。返回新创建的item（包括id）。

_handle_post_reservations: 从body获取item_id, quantity, ttl_seconds。验证参数。检查库存：SELECT stock_available FROM items WHERE id=? FOR UPDATE? 在SQLite中，我们使用BEGIN TRANSACTION，然后执行SELECT ... WHERE id=? 在事务中可以获得行级锁？SQLite默认是乐观锁，但在事务中执行SELECT会读取数据。我们可以在事务中更新，但需要检查库存。由于我们在锁保护下，并且使用了全局锁，所以可以安全地先查询再更新。我们使用conn.execute("BEGIN")开始事务，然后查询，如果库存不足，回滚并返回409；否则减少stock_available，插入预约记录，计算expires_at = now + ttl_seconds。最后提交。注意：我们已经在全局锁下，所以多线程不会同时执行，因此不需要额外的事务锁？但是为了数据一致性，我们仍然应该使用事务，因为可能有中间状态。使用事务可以保证原子性。我们可以在try中执行，如果出错则rollback。但使用with db_lock保证一次只有一个线程修改，所以事务是多余的？但是即使只有一个线程，事务可以保证我们操作的一致性：如果中间步骤失败，我们可以回滚。所以加上事务是好的。

注意：我们需要在创建预约时，如果库存不足，返回409。错误响应包含error字段。

_handle_post_confirm: 接收reservation_id。需要验证预约存在且状态为pending。如果已经confirmed或cancelled或expired，返回错误。如果状态是pending，更新状态为confirmed。不需要修改库存（因为库存已经在创建时减少了）。注意：如果预约已经过期（通过之前的清理已经变为expired），则状态不再pending，所以无法确认。

_handle_post_cancel: 接收reservation_id。验证预约存在且状态为pending。如果是pending，更新状态为cancelled，并增加对应item的stock_available。如果预约已过期或被确认，则不能取消。

注意：在确认或取消时，我们需要使用事务。

还需要注意：在清理过期预约时，我们也会将状态设为expired并释放库存。所以，如果一个预约已过期但尚未清理，可能在确认或取消时仍然pending（但expires_at已经过去）。根据要求，清理在每个请求前执行，所以处理其他请求时已经清理过了，所以确认或取消时，如果预约已过期，清理会先把它变成expired，所以后续的确认或取消会看到状态不是pending，从而返回错误。但如果我们想更安全，我们可以在确认/取消时检查expires_at。但规范只要求清理在每次请求前，所以我们可以依赖清理。但如果ttl_seconds非常短，可能在请求间隔中过期，但清理会先处理，所以没问题。但为了安全，我们也可以在确认/取消时检查如果状态是pending但expires_at已经过去，我们也可以拒绝。但这是额外的逻辑。我们可以让清理去除过期，所以一般来说，清理会先于这些操作。所以我们只检查status。

但是，如果在确认/取消的请求中没有获取锁之前，另一个线程可能已经执行了确认或取消，但我们有锁所以不会并发。所以清理后，状态可能是pending（未过期）。所以状态检查足够。

现在，清理函数_clean_expired: 查询所有status='pending'且expires_at < 当前时间的记录。使用conn.execute("SELECT id, item_id, quantity FROM reservations WHERE status='pending' AND expires_at < ?", (now_iso,))。然后对于每一条，在事务中更新status为'expired'，并且UPDATE items SET stock_available = stock_available + quantity WHERE id = ?。注意：我们需要在同一个事务中原子性完成，以避免部分释放。我们可以先开始事务，然后循环操作。注意：清理函数可能使用conn，我们需要确保在调用之前已经获取锁。因为我们在调用_clean_expired时已经持有锁，所以我们可以使用conn执行操作。注意：在清理函数中，我们不能长时间持有锁？但锁已经由外部持有，所以可以。

但注意：conn是全局的，并且我们在锁内使用，是安全的。

我们还需要处理时间格式：我们将使用ISO 8601字符串存储时间，带小数秒和时区？为了简单，我们使用UTC时间，格式为'%Y-%m-%dT%H:%M:%S'或带毫秒。比较时，我们直接比较字符串，因为ISO字符串按字典序可比较。我们使用datetime.utcnow().isoformat() 或手动。更好的使用time.time()存储数字？要求expires_at可以是任意格式，但要求使用sqlite3持久化。我们可以存储Unix时间戳（整数或浮点数），这样比较方便。但也可以存储字符串。我们选择存储字符串ISO格式，便于阅读。比较时使用字符串比较，因为ISO格式是字母顺序的，可以比较。注意：如果使用带小数秒，默认isoformat()会包含微秒，字符串比较仍然OK。

所以，我们使用datetime.utcnow().isoformat() 作为created_at，expires_at计算为 (datetime.utcnow() + timedelta(seconds=ttl_seconds)).isoformat()。

在查询过期预约时，比较字符串：WHERE expires_at < ? 其中?是当前时间的ISO字符串。

但是，由于我们可能有微秒，比较会精确。可以。

现在，我们需要考虑：在清理时，我们获取所有过期预约，然后更新它们的status为expired，并增加stock_available。这里使用了两个步骤，我们需要确保原子性。我们可以使用一个事务：BEGIN; SELECT ...; 然后对于每个UPDATE items; UPDATE reservations; COMMIT。但是注意，如果有很多，可能会持锁很久。但这是局部的。

另一个方法：我们可以使用UPDATE ... WHERE ... 一次性更新预约状态为expired，但是释放库存需要知道每个预约的quantity和item_id，所以不能一步完成。所以我们需要逐条。

我们可以使用一个事务：首先查询所有过期的pending预约（SELECT id, item_id, quantity FROM reservations WHERE status='pending' AND expires_at < ?），然后对于每一条，执行UPDATE items SET stock_available = stock_available + quantity WHERE id = ?，然后UPDATE reservations SET status='expired' WHERE id = ? AND status='pending'（确保没有被其他操作改变）。由于我们有锁，不会并发，所以不需要额外的状态检查。但为了安全，可以加条件。

总的来说，清理函数内应该使用事务。

注意：我们可能需要在清理时考虑性能，但库存服务通常数据量不大。

现在，具体实现。

我们还需要处理异常，例如数据库操作失败时回滚事务，并返回错误。

在请求处理方法中，我们使用try-except捕获异常并返回500。

我们还需要处理路径中id不合法的情况（如非数字）。我们可以用正则捕获。

对于确认和取消的路由，我们使用正则匹配，如：reservations/(\d+)/confirm 和 reservations/(\d+)/cancel。注意路径可能以/结尾。我们可以使用re.fullmatch。

在do_POST中，我们使用re.match来判断。

但注意：端点还包括/reservations（无参数），所以需要先检查完全匹配。

我们可以在do_POST中按顺序匹配。

我们还需要处理404错误。

对错误响应统一使用_send_error。

注意：当库存不足时，我们应该返回409 Conflict。

在_handle_get_items中，调用清理后，直接查询。

现在开始编码。

考虑代码组织：在if __name__中，创建HTTPServer，并启动。

HTTPServer使用ThreadingMixIn来多线程：

class ThreadHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True

这样每个请求在新的线程中处理。

我们还需要设置地址重用：在server_allow_reuse？

我们可以设置server.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

在创建服务器之前。

现在，需要确保在服务器启动前调用init_db()。

完整的代码框架。

注意：我们需要确保在清理和更新库存时，数据库连接使用正确的cursor。我们在conn上直接执行。

因为我们使用全局conn，在锁内使用，所以没有问题。

但是，有一个问题：由于我们使用ThreadingMixIn，每个请求线程调用do_GET/do_POST，它们获取锁并使用conn。如果多个请求同时到达，它们会排队获取锁，但conn是同一个。在锁内，我们使用conn执行操作，但conn的默认行为是每个操作会立即提交吗？我们使用的是conn.execute，如果没有使用事务，它是自动提交（隐式事务）每个语句。如果我们在事务中（BEGIN），则需要显式提交。我们在多个步骤的地方使用事务。注意：如果你在conn.execute("BEGIN")后，执行多个语句，然后conn.commit()。但是，如果不小心在事务中使用conn.execute，它是在事务内。但是，conn.execute("BEGIN")是显式开始事务，但sqlite3在Python中，每次执行DML会自动开启事务（如果没有事务），但显式BEGIN可以控制。最好使用conn.execute("BEGIN")...conn.commit()。但是，当我们使用conn.execute("UPDATE ...")，它是立即生效的，如果不在显式事务内，它会自动开启事务并立即提交？实际上，Python的sqlite3模块在execute()方法执行时，如果连接未处于事务中，会自动开始一个事务（对于DML）。这个事务会在下一次调用commit或rollback时结束，或者在连接关闭时提交。为了确保事务控制，我们更倾向于使用conn.execute("BEGIN")然后conn.execute("COMMIT")。但也可以使用conn.execute("BEGIN")，然后执行语句，最后conn.commit()。注意：在显式BEGIN之后，如果执行DML，不会自动提交。但是，如果在执行DML之前没有BEGIN，Python会自动开始一个事务（behind the scenes），但你无法控制提交，它会自动在下一个非DML语句（如SELECT）之前自动提交？这行为复杂。为了安全，我们使用显式的BEGIN和COMMIT/ROLLBACK。

我们写一个函数：def execute_transaction(conn, func): 在调用func之前执行BEGIN，然后func中执行数据库操作，最后提交或回滚。但为了简化，我们直接在方法中写BEGIN...COMMIT。

但是注意：在锁内，我们使用conn，如果我们在一个方法中执行了BEGIN但没有提交，然后另一个方法使用同一个conn，但锁是同一个，所以下一个方法会在前一个方法提交后执行。但是，如果我们在一个方法中使用conn执行了BEGIN，但没有提交，锁释放后，下一个方法取得锁后使用同一个conn，它会处于未完成的事务中，可能导致问题。所以我们务必要在每个方法中确保事务要么提交要么回滚。因此，在每个使用事务的方法中，我们需要在finally中处理回滚，如果发生异常。

所以，我们将每个数据库操作方法设计为在内部使用事务，并确保在返回之前提交或回滚。

注意：在_clean_expired中，我们使用事务，所以我们开始事务，循环更新，然后提交。如果中间出错，回滚。因为我们已经持有锁，所以安全。

但还有一点：我们调用_clean_expired在具体处理方法之前。在_clean_expired中，我们使用conn，并且可能开启了一个事务。然后在具体处理方法中，我们也会开启事务。这可能导致嵌套事务？SQLite不允许嵌套事务，但是如果我们先BEGIN了一个事务，然后在同一个连接上再BEGIN，会得到错误。所以我们需要在_clean_expired中结束事务（提交或回滚）后，再由具体方法开始新的事务。所以我们在_clean_expired中必须确保在返回前提交或回滚。

因此，在设计_clean_expired时，我们在函数内部完成事务，并在函数结束前提交（或由于异常回滚）。这样调用后，连接回到非事务状态。

类似地，其他方法也如此。

现在，我们来写这些函数。我们定义为模块级函数，它们接受conn参数。

我们还需要一个函数来获取当前时间字符串：

def _now_iso():
    return datetime.utcnow().isoformat()

但是，我们需要多次使用当前时间，为了避免时间偏移，在同一个请求中，清理使用的时间应该与后续操作的时间一致（例如，在创建预约时，我们应该使用与清理相同的当前时间？但清理先执行，创建时使用后来的时间，可能会导致清理后刚创建的预约可能过去了吗？不太可能。但为了精确，我们可以记录一个时间点。但这不是必须的。我们在清理时使用一个时间变量，然后在创建时使用另一个时间，但创建时的时间肯定大于清理时的时间，所以不会误清理。所以可以。

但更好的是：在_clean_expired中，我们使用当前时间作为比较点，然后创建预约时使用稍后的时间，这没问题。

现在写具体函数：

def get_all_items(conn):
    cursor = conn.execute('SELECT id, name, stock_total, stock_available FROM items')
    rows = cursor.fetchall()
    return [dict(row) for row in rows]

注意：conn.row_factory = sqlite3.Row，所以row可以像字典一样访问，但返回的是Row对象，我们需要转换为字典。使用dict(row)可以吗？Row对象支持映射接口，可以用dict(row)。但是Row对象包含键和值，所以dict(row)可以。但需要注意，Row的keys()包含列名。dict(row)会生成正确的字典。所以可行。

def create_item(conn, name, stock_total):
    # 验证参数
    if not name or stock_total <= 0:
        raise ValueError("name must be non-empty and stock_total must be positive")
    # 插入
    stock_available = stock_total
    cursor = conn.execute('INSERT INTO items (name, stock_total, stock_available) VALUES (?, ?, ?)',
                         (name, stock_total, stock_available))
    conn.commit()  # 需要提交吗？注意，我们打算在外部控制事务，但这个函数没有开始事务。我们可以在调用者的外部开始事务，然后在这里执行，然后提交。但为了简单，每个函数自己管理事务？但这样可能嵌套。我们约定：每个写函数（create_item, create_reservation, confirm, cancel）都会开始并提交事务。而clean_expired也会。所以它们内部都有BEGIN/COMMIT。但是，如果我们尝试在create_item中使用BEGIN/COMMIT，而调用者可能已经在外层开启了事务，会产生问题。所以我们应该只有一个外层事务管理。对于清理，我们通常单独，对于每个请求的操作，我们也可以在一个事务内完成多个函数。但我们的请求处理通常只调用一个写函数（如创建预约），所以没问题。而对于GET /items，我们不写，所以无需事务。

我们设计：对于需要写操作的方法，它们自己开始事务并提交。对于只读的方法，不需要事务。

但clean_expired可能在GET之前调用，所以它自己开始和提交事务。

在请求处理方法中，顺序：先调用clean_expired，它自己提交事务；然后处理具体请求，比如create_reservation，它自己开始事务并提交。这样不会冲突，因为clean_expired在调用后已经提交，连接回到非事务状态，然后create_reservation开始新事务。

所以，我们可以这样设计。

在clean_expired内部我们使用BEGIN/COMMIT。在create_reservation内部也使用。在其他函数中类似。

那么在_handle_get_items中，我们只读，不需要事务。但为了确保一致性，我们可以在一个读事务中执行，但不需要，因为我们在锁内。

但是在_clean_expired中，我们如果执行SELECT然后UPDATE，需要原子性，所以使用事务。

具体实现：

def clean_expired(conn):
    now = _now_iso()
    # 查询过期pending预约
    cursor = conn.execute("SELECT id, item_id, quantity FROM reservations WHERE status='pending' AND expires_at < ?", (now,))
    expired = cursor.fetchall()
    if not expired:
        return
    # 开始事务
    conn.execute("BEGIN")
    try:
        for row in expired:
            # 释放库存
            conn.execute("UPDATE items SET stock_available = stock_available + ? WHERE id = ?", (row['quantity'], row['item_id']))
            # 更新预约状态
            conn.execute("UPDATE reservations SET status='expired' WHERE id = ? AND status='pending'", (row['id'],))
        conn.commit()
    except Exception:
        conn.rollback()
        raise

注意：这里我们在事务中循环。如果出现错误，回滚。这样，要么全部更新，要么不变。

在确认和取消的函数中类似。

但注意：在确认（confirm）中，我们只需要更新状态，不需要操作库存。但我们需要检查状态是否为pending。我们应该在一个事务中完成检查并更新，以确保原子性（避免在检查和更新之间状态发生变化，但因为有锁，不会并发改变，但使用事务仍然好）。所以我们可以：

def confirm_reservation(conn, reservation_id):
    conn.execute("BEGIN")
    try:
        cursor = conn.execute("SELECT status, item_id, quantity FROM reservations WHERE id = ?", (reservation_id,))
        row = cursor.fetchone()
        if row is None:
            conn.rollback()
            return None, "Reservation not found"
        if row['status'] != 'pending':
            conn.rollback()
            return None, "Reservation not pending"
        conn.execute("UPDATE reservations SET status='confirmed' WHERE id = ?", (reservation_id,))
        conn.commit()
        return {"id": reservation_id, "status": "confirmed"}, None
    except Exception:
        conn.rollback()
        raise

注意：事务开始后，我们可能需要检查我们查询的行是否被其他锁保护，由于全局锁，是安全的。

类似地，cancel函数：

def cancel_reservation(conn, reservation_id):
    conn.execute("BEGIN")
    try:
        cursor = conn.execute("SELECT status, item_id, quantity FROM reservations WHERE id = ?", (reservation_id,))
        row = cursor.fetchone()
        if row is None:
            conn.rollback()
            return None, "Reservation not found"
        if row['status'] != 'pending':
            conn.rollback()
            return None, "Reservation not pending"
        # 释放库存
        conn.execute("UPDATE items SET stock_available = stock_available + ? WHERE id = ?", (row['quantity'], row['item_id']))
        conn.execute("UPDATE reservations SET status='cancelled' WHERE id = ?", (reservation_id,))
        conn.commit()
        return {"id": reservation_id, "status": "cancelled"}, None
    except Exception:
        conn.rollback()
        raise

对于create_reservation函数：

def create_reservation(conn, item_id, quantity, ttl_seconds):
    # 参数验证
    if quantity <= 0:
        return None, "quantity must be positive"
    if ttl_seconds <= 0:
        return None, "ttl_seconds must be positive"
    conn.execute("BEGIN")
    try:
        # 检查商品存在且库存足够
        cursor = conn.execute("SELECT id, stock_available FROM items WHERE id = ?", (item_id,))
        item = cursor.fetchone()
        if item is None:
            conn.rollback()
            return None, "Item not found"
        if item['stock_available'] < quantity:
            conn.rollback()
            return None, "Insufficient stock"  # 调用者检查这个错误返回409
        # 减少库存
        conn.execute("UPDATE items SET stock_available = stock_available - ? WHERE id = ?", (quantity, item_id))
        # 创建预约
        now = _now_iso()
        expires_at = (datetime.utcnow() + timedelta(seconds=ttl_seconds)).isoformat()
        cursor = conn.execute(
            "INSERT INTO reservations (item_id, quantity, status, expires_at, created_at) VALUES (?, ?, 'pending', ?, ?)",
            (item_id, quantity, expires_at, now)
        )
        reservation_id = cursor.lastrowid
        conn.commit()
        return {"id": reservation_id, "item_id": item_id, "quantity": quantity, "status": "pending", "expires_at": expires_at, "created_at": now}, None
    except Exception:
        conn.rollback()
        raise

注意：返回的结果可以是对象或错误字符串。调用者检查错误。

在_handle_post_reservations中，如果返回错误 "Insufficient stock"，我们应该用409响应；其他错误用400或404。

类似地，对于create_item：

def create_item(conn, name, stock_total):
    if not name:
        return None, "name is required"
    if stock_total <= 0:
        return None, "stock_total must be positive"
    conn.execute("BEGIN")
    try:
        cursor = conn.execute("INSERT INTO items (name, stock_total, stock_available) VALUES (?, ?, ?)", (name, stock_total, stock_total))
        item_id = cursor.lastrowid
        conn.commit()
        return {"id": item_id, "name": name, "stock_total": stock_total, "stock_available": stock_total}, None
    except Exception:
        conn.rollback()
        raise

现在，实现MyHandler的方法。

在do_GET中，除了/items，我们还可以考虑将来可能添加其他，但现在只有/items。

在do_POST中，根据路径不同处理。

注意：对于POST /reservations，路径是/reservations，没有参数id。

我们需要解析body。使用_read_body方法。

_read_body需要考虑错误，如果JSON无效，返回错误。

在具体处理中，我们调用数据库函数，传递conn。

注意：我们在do_GET/do_POST开头获取了db_lock，所以当我们调用数据库函数时，我们是在锁内。我们需要注意，数据库函数内部也会使用conn，它们可能会开始事务，所以我们必须在锁内完成。

但是，如果有失败，我们需要确保事务回滚，并且连接回到非事务状态，以便后续使用。所以我们的函数内部已经处理了回滚，但如果在函数内发生了异常（如rollback失败），可能会让连接处于错误状态。但我们可以信任。

为了更健壮，我们可以使用conn.rollback()确保状态。

现在，处理header。我们需要在每次响应时设置Content-Type: application/json。

对于错误响应，我们统一用_send_error。

对于成功响应，用_send_json。

在_send_error和_send_json中，我们需要在发送之前确保响应行和头已经发送。

我们还需要处理潜在的大型响应，但这里不大。

注意：在发送响应时，我们需要调用send_response(code)，然后send_header，然后end_headers，然后write body。

我们需要编码body为bytes。

我们还需要处理可能的数据类型，如列表等。

现在开始写完整代码。

我们还需要处理HTTP版本，使用默认。

我们还需要处理异常在_clean_expired中。

我们还应该注意，在do_GET/do_POST中，我们可能会捕获所有异常，但有些系统退出异常（如BrokenPipe）我们不该捕获，但为简单，我们捕获所有并返回500。

但我们也可以让BaseHTTPRequestHandler处理常见异常。

现在，写代码时注意缩进。

开始写代码：

我们先用注释组织。

我们将所有功能函数放在模块级别，然后在MyHandler中调用。

注意：因为我们在do_GET和do_POST中获取锁，但锁可能被长时间持有，因此我们需要尽快释放。我们可以在每个函数内获取锁，但锁是模块级的，我们需要保证每个请求获取锁的顺序。我们使用with db_lock在方法开始，在方法结束时释放。但是在_send_error或_send_json之后，方法结束，with语句释放锁。但是如果在发送响应后还有额外操作，锁会保持，但我们的方法在发送响应后通常没有更多工作，所以可以。

但注意：如果发送响应时出现异常，锁会在finally中被释放？我们使用with语句，所以即使异常，锁也会释放（with语句在退出时会释放锁，即使异常）。所以安全。

但是，我们在方法中使用了try-except，捕获异常并发送500，所以异常不会传播到with外部，但如果在发送500时又异常，则可能会传播，但with语句仍会释放锁。所以可以。

现在，我们编写代码。注意：我们需要import json, sqlite3, threading, socketserver, http.server, os, re, time, datetime, sys.

现在开始。

注意：要求“首次启动自动建表”，所以我们在初始化时使用CREATE TABLE IF NOT EXISTS。

可能还需要检查数据库文件是否创建。

另外，我们不需要显式设置端口和地址，默认127.0.0.1:8080。

代码总长度不超过1000行，我们希望代码简洁。

现在开始写完整的server.py。

在写之前，考虑一些边界情况：例如，当ttl_seconds为0或负数时的处理；quantity为0或负数；item_id不存在；商品stock_available不足；确认或取消不存在的预约；确认或取消已经确认/取消的预约；POST /items没有参数或无效；JSON解析错误；路径不合法等。

我们将这些错误处理。

特别注意：在读取请求体时，如果Content-Length不存在或为0，我们返回空字典。对于POST /items和POST /reservations，必需参数缺失，返回400。

对于JSON解析错误，返回400。

对于路径不匹配，返回404。

对于锁，我们使用python的threading.Lock()。

另外，我们需要考虑在创建预约时，如果quantity > stock_total？但stock_available可能小于stock_total（已被其他预约占用），所以只检查stock_available。

还要注意，在释放库存时，stock_available可能增加超过stock_total？理论上如果每次预约都正确释放，不会超过。但如果我们多次取消或过期，可能会超过stock_total？不会，因为每次释放的数量等于之前扣减的数量，所以stock_available不会超过stock_total。但如果有bug可能会，但我们不额外检查。

无论如何，我们按规范实现。

现在开始编写代码。

第一步：导入

import http.server
import json
import sqlite3
import threading
import socketserver
import os
import re
from datetime import datetime, timedelta, timezone
import sys

第二步：定义全局变量

DB_PATH = 'inventory.db'
db_lock = threading.Lock()
conn = None

第三步：定义辅助函数

def _now_iso():
    return datetime.utcnow().isoformat()

第四步：数据库初始化

def init_db():
    global conn
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("""CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        stock_total INTEGER NOT NULL,
        stock_available INTEGER NOT NULL
    )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS reservations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        status TEXT NOT NULL DEFAULT 'pending',
        expires_at TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY(item_id) REFERENCES items(id)
    )""")
    conn.commit()

第五步：定义数据库操作函数（这些函数都假定调用者已经获取锁，且conn可用）

def clean_expired(conn):
    now = _now_iso()
    cursor = conn.execute("SELECT id, item_id, quantity FROM reservations WHERE status='pending' AND expires_at < ?", (now,))
    expired = cursor.fetchall()
    if not expired:
        return
    conn.execute("BEGIN")
    try:
        for row in expired:
            # 释放库存
            conn.execute("UPDATE items SET stock_available = stock_available + ? WHERE id = ?", (row['quantity'], row['item_id']))
            # 更新预约状态
            conn.execute("UPDATE reservations SET status='expired' WHERE id = ? AND status='pending'", (row['id'],))
        conn.commit()
    except Exception:
        conn.rollback()
        raise

def get_all_items(conn):
    cursor = conn.execute("SELECT id, name, stock_total, stock_available FROM items")
    rows = cursor.fetchall()
    return [dict(row) for row in rows]

def create_item(conn, name, stock_total):
    if not name:
        return None, "name is required"
    try:
        stock_total = int(stock_total)
        if stock_total <= 0:
            return None, "stock_total must be a positive integer"
    except (ValueError, TypeError):
        return None, "stock_total must be a positive integer"
    conn.execute("BEGIN")
    try:
        cursor = conn.execute("INSERT INTO items (name, stock_total, stock_available) VALUES (?, ?, ?)", (name, stock_total, stock_total))
        item_id = cursor.lastrowid
        conn.commit()
        return {"id": item_id, "name": name, "stock_total": stock_total, "stock_available": stock_total}, None
    except Exception:
        conn.rollback()
        raise

def create_reservation(conn, item_id, quantity, ttl_seconds):
    # 参数验证
    try:
        item_id = int(item_id)
        quantity = int(quantity)
        ttl_seconds = int(ttl_seconds)
    except (ValueError, TypeError):
        return None, "item_id, quantity, ttl_seconds must be integers"
    if quantity <= 0:
        return None, "quantity must be positive"
    if ttl_seconds <= 0:
        return None, "ttl_seconds must be positive"
    conn.execute("BEGIN")
    try:
        # 检查商品存在和库存
        cursor = conn.execute("SELECT id, stock_available FROM items WHERE id = ?", (item_id,))
        item = cursor.fetchone()
        if item is None:
            conn.rollback()
            return None, "Item not found"
        if item['stock_available'] < quantity:
            conn.rollback()
            return None, "Insufficient stock"
        # 减少库存
        conn.execute("UPDATE items SET stock_available = stock_available - ? WHERE id = ?", (quantity, item_id))
        # 创建预约
        now = _now_iso()
        expires_at = (datetime.utcnow() + timedelta(seconds=ttl_seconds)).isoformat()
        cursor = conn.execute("INSERT INTO reservations (item_id, quantity, status, expires_at, created_at) VALUES (?, ?, 'pending', ?, ?)", (item_id, quantity, expires_at, now))
        reservation_id = cursor.lastrowid
        conn.commit()
        return {"id": reservation_id, "item_id": item_id, "quantity": quantity, "status": "pending", "expires_at": expires_at, "created_at": now}, None
    except Exception:
        conn.rollback()
        raise

def confirm_reservation(conn, reservation_id):
    try:
        reservation_id = int(reservation_id)
    except (ValueError, TypeError):
        return None, "Invalid reservation id"
    conn.execute("BEGIN")
    try:
        cursor = conn.execute("SELECT status, item_id, quantity FROM reservations WHERE id = ?", (reservation_id,))
        row = cursor.fetchone()
        if row is None:
            conn.rollback()
            return None, "Reservation not found"
        if row['status'] != 'pending':
            conn.rollback()
            return None, "Reservation cannot be confirmed (current status: {})".format(row['status'])
        conn.execute("UPDATE reservations SET status='confirmed' WHERE id = ?", (reservation_id,))
        conn.commit()
        return {"id": reservation_id, "status": "confirmed"}, None
    except Exception:
        conn.rollback()
        raise

def cancel_reservation(conn, reservation_id):
    try:
        reservation_id = int(reservation_id)
    except (ValueError, TypeError):
        return None, "Invalid reservation id"
    conn.execute("BEGIN")
    try:
        cursor = conn.execute("SELECT status, item_id, quantity FROM reservations WHERE id = ?", (reservation_id,))
        row = cursor.fetchone()
        if row is None:
            conn.rollback()
            return None, "Reservation not found"
        if row['status'] != 'pending':
            conn.rollback()
            return None, "Reservation cannot be cancelled (current status: {})".format(row['status'])
        # 释放库存
        conn.execute("UPDATE items SET stock_available = stock_available + ? WHERE id = ?", (row['quantity'], row['item_id']))
        conn.execute("UPDATE reservations SET status='cancelled' WHERE id = ?", (reservation_id,))
        conn.commit()
        return {"id": reservation_id, "status": "cancelled"}, None
    except Exception:
        conn.rollback()
        raise

第六步：定义HTTP请求处理器

class MyHandler(http.server.BaseHTTPRequestHandler):

    def _send_json(self, data, code=200):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def _send_error(self, code, message):
        self._send_json({"error": message}, code)

    def _read_body(self):
        content_length = self.headers.get('Content-Length')
        if not content_length:
            return {}
        try:
            content_length = int(content_length)
        except ValueError:
            return {}
        if content_length <= 0:
            return {}
        body = self.rfile.read(content_length)
        try:
            return json.loads(body.decode())
        except (json.JSONDecodeError, UnicodeDecodeError):
            return None

    def do_GET(self):
        with db_lock:
            try:
                clean_expired(conn)
                if self.path == '/items':
                    items = get_all_items(conn)
                    self._send_json(items)
                else:
                    self._send_error(404, "Not found")
            except Exception as e:
                self._send_error(500, str(e))

    def do_POST(self):
        with db_lock:
            try:
                clean_expired(conn)
                path = self.path
                if path == '/items':
                    self._handle_post_items()
                elif path == '/reservations':
                    self._handle_post_reservations()
                elif re.fullmatch(r'/reservations/\d+/confirm', path):
                    id = int(path.split('/')[2])
                    self._handle_post_confirm(id)
                elif re.fullmatch(r'/reservations/\d+/cancel', path):
                    id = int(path.split('/')[2])
                    self._handle_post_cancel(id)
                else:
                    self._send_error(404, "Not found")
            except Exception as e:
                self._send_error(500, str(e))

    def _handle_post_items(self):
        body = self._read_body()
        if body is None:
            self._send_error(400, "Invalid JSON")
            return
        name = body.get('name')
        stock_total = body.get('stock_total')
        if not name:
            self._send_error(400, "name is required")
            return
        try:
            stock_total = int(stock_total)
            if stock_total <= 0:
                raise ValueError
        except (ValueError, TypeError):
            self._send_error(400, "stock_total must be a positive integer")
            return
        item, err = create_item(conn, name, stock_total)
        if err:
            # 理论上create_item不会返回错误如果参数已验证，但保留
            self._send_error(400, err)
            return
        self._send_json(item, 201)

    def _handle_post_reservations(self):
        body = self._read_body()
        if body is None:
            self._send_error(400, "Invalid JSON")
            return
        item_id = body.get('item_id')
        quantity = body.get('quantity')
        ttl_seconds = body.get('ttl_seconds')
        if item_id is None or quantity is None or ttl_seconds is None:
            self._send_error(400, "item_id, quantity, ttl_seconds are required")
            return
        try:
            item_id = int(item_id)
            quantity = int(quantity)
            ttl_seconds = int(ttl_seconds)
        except (ValueError, TypeError):
            self._send_error(400, "item_id, quantity, ttl_seconds must be integers")
            return
        reservation, err = create_reservation(conn, item_id, quantity, ttl_seconds)
        if err:
            if err == "Insufficient stock":
                self._send_error(409, err)
            elif "not found" in err.lower():
                self._send_error(404, err)
            else:
                self._send_error(400, err)
            return
        self._send_json(reservation, 201)

    def _handle_post_confirm(self, reservation_id):
        reservation, err = confirm_reservation(conn, reservation_id)
        if err:
            if "not found" in err.lower():
                self._send_error(404, err)
            else:
                self._send_error(400, err)
            return
        self._send_json(reservation)

    def _handle_post_cancel(self, reservation_id):
        reservation, err = cancel_reservation(conn, reservation_id)
        if err:
            if "not found" in err.lower():
                self._send_error(404, err)
            else:
                self._send_error(400, err)
            return
        self._send_json(reservation)

第七步：定义服务器

class ThreadHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True

第八步：启动入口

if __name__ == '__main__':
    init_db()
    server = ThreadHTTPServer(('127.0.0.1', 8080), MyHandler)
    print("Server starting on 127.0.0.1:8080")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Server shutting down")
        server.server_close()
        sys.exit(0)

现在我们有一个完整的服务器。

检查代码是否满足要求：

- 单文件，server.py。
- 使用标准库，没有第三方库。
- 总代码行数：我们计算一下，目前代码约200多行，小于1000。
- 数据：使用sqlite3自动建表。
- API端点：实现所有要求。
- 每次请求前清理过期预约：在do_GET和do_POST中首先调用clean_expired。
- 并发处理：使用线程锁db_lock，所有请求序列化数据库操作。虽然使用ThreadingMixIn支持多线程，但锁会串行化。但可以保证一致性。
- 返回JSON，错误包含error字段。
- 启动入口监听127.0.0.1:8080。

潜在问题：

- 在clean_expired中，我们使用事务，但在查询之前没有开始事务。我们只对更新操作使用事务。其实查询不需要事务。但为了安全，对整个循环使用事务。
- 在create_reservation中，我们使用事务，检查库存，减少库存，插入预约。这是正确的。
- 注意：当库存更新时，我们在减少时使用了UPDATE，然后插入预约。如果之后提交失败，回滚会恢复库存。
- 在clean_expired中，我们使用了一个时间点，然后查询所有小于这个时间的记录。然后更新状态。如果在这之间有新的预约创建，不受影响。
- 在确认和取消时，我们检查状态是否为pending。如果预约已经被清理（过期），则状态为expired，所以返回错误。
- 注意：在清理后，pending的预约有可能没有过期，所以我们还可以操作。
- 关于时间格式：我们使用ISO格式，比较使用字符串比较，因为ISO格式的字符串排序与时间排序一致。但需要确保所有时间都是UTC且格式一致。我们使用datetime.utcnow().isoformat()，产生类似"2024-01-01T12:00:00.123456"的字符串。在SQLite中比较时，是按字符串比较。由于ISO格式数字位数一致（如果微秒位数不同可能会导致字典序不一致？如果微秒位数不同，如"2024-01-01T12:00:00.1" 和 "2024-01-01T12:00:00.123456"，比较时前者在后的前面？但实际时间上后者更晚。但如果微秒位数不同，字符串比较可能不正确。为了避免这个问题，我们可以使用固定格式，如不带微秒，或者使用时间戳（浮点数）作为存储。更稳健的方式是使用Unix时间戳（整数或浮点数）。这样比较和计算更简单。我们将expires_at和created_at存储为实数（float），表示Unix时间戳。这样比较时直接比较数字，更可靠。而ISO字符串虽然可读性好，但有风险。我们改为使用时间戳（秒级浮点数）。推荐使用time.time()。

我们修改：使用time.time()获取当前时间戳（浮点数），在存储时使用浮点数。在比较时使用数字。

所以，我们修改_now_iso为_timestamp，返回time.time()。然后在创建时，expires_at = time.time() + ttl_seconds。created_at = time.time()。

在clean_expired中，比较expires_at < time.time()。

这样更简单和可靠。

我们修改相关函数。

注意：在返回给客户端时，我们可能希望返回可读格式，但API未指定格式，返回时间戳或ISO都可以。但为了方便，我们返回ISO字符串可能更好看。但既然存储的是时间戳，我们可以返回时转换。但为了简化，返回时间戳也可以。但要求没有明确。我们可以选择返回ISO字符串便于阅读。在创建预约的响应中，我们返回expires_at和created_at，可以使用ISO字符串。我们可以在返回时转换时间为ISO，或者存储为ISO但存储时用时间戳？我们决定存储为时间戳，但在API响应中转换成ISO字符串，这样客户端易读。所以，在create_reservation中，我们存储时间戳，但在返回的字典中使用datetime.utcfromtimestamp(timestamp).isoformat()。

同样，在get_all_items中没有时间字段。

在confirm_response中我们不需要返回时间。

在cancel_response中不需要。

所以，修改：

在create_reservation中，now_ts = time.time(); expires_ts = now_ts + ttl_seconds; 存储这两个浮点数到expires_at和created_at字段。在返回时，使用datetime.utcfromtimestamp(now_ts).isoformat()和datetime.utcfromtimestamp(expires_ts).isoformat()。

在clean_expired中，使用 time.time() 作为当前时间比较。

我们需要修改表的定义：expires_at和created_at字段类型改为REAL（浮点数）。我们使用sqlite3的REAL。

修改建表语句：created_at REAL, expires_at REAL。因为我们是数值，所以比较方便。

我们修改：

CREATE TABLE reservations (
    ...
    status TEXT NOT NULL DEFAULT 'pending',
    expires_at REAL NOT NULL,
    created_at REAL NOT NULL,
    ...
)

注意：需要使用REAL而不是TEXT。

在数据库操作中，使用浮点数。

但是，我们也可以继续使用TEXT，存储ISO字符串，比较时也可以，但为了可靠，使用REAL。

我们决定使用REAL（浮点数）。

现在修改代码。

另外，在clean_expired中，我们需要使用当前时间戳，所以将_now_iso改为_now_ts或直接使用time.time()。

我们定义一个函数 _now_ts() 返回 time.time()。

然后修改所有相关部分。

现在重写相关部分。

注意：在_handle_post_reservations中，我们返回的响应字段，我们要求返回expires_at和created_at。我们可以返回ISO字符串。

实现细节：

def _now_ts():
    return time.time()

def create_reservation(conn, item_id, quantity, ttl_seconds):
    ...
    now_ts = _now_ts()
    expires_ts = now_ts + ttl_seconds
    conn.execute("INSERT INTO reservations (item_id, quantity, status, expires_at, created_at) VALUES (?, ?, 'pending', ?, ?)",
                 (item_id, quantity, expires_ts, now_ts))
    reservation_id = cursor.lastrowid
    conn.commit()
    return {"id": reservation_id, "item_id": item_id, "quantity": quantity, "status": "pending",
            "expires_at": datetime.utcfromtimestamp(expires_ts).isoformat(),
            "created_at": datetime.utcfromtimestamp(now_ts).isoformat()}, None

在clean_expired中:

def clean_expired(conn):
    now_ts = _now_ts()
    cursor = conn.execute("SELECT id, item_id, quantity FROM reservations WHERE status='pending' AND expires_at < ?", (now_ts,))
    ...

注意：我们需要确保建表时字段类型正确。

现在，调整代码。

另外，在create_item中，我们直接插入name, stock_total, stock_available（整数）。

现在，我们还需要在clean_expired中，可能有很多过期预约，但我们的事务会处理。

我们还应该考虑：在clean_expired时，我们使用了SELECT和UPDATE。如果很多记录，可能会锁住一段时间，但库存服务一般不会太多。

还有一个细节：我们在请求处理过程中获取了全局锁，这会阻塞其他请求，但清理过程中我们持有锁，所以其他请求等待。但我们可以考虑在清理完成后释放锁，然后重新获取？但是清理是在请求开始时，所以如果清理耗时，会延长锁持有时间。但鉴于清理通常很快，可以接受。

现在，我们写完整代码，确保导入所有必要模块。

我们还需要在confirm_reservation和cancel_reservation中，如果没有找到预约，返回None和错误字符串。我们之前已经写了。

现在，我们检查代码一致性。

在MyHandler中，我们使用了re.fullmatch来匹配路径。但需要注意的是，路径可能以/结尾？我们假设没有。如果客户端发送/reservations/1/confirm/，fullmatch会不匹配，所以返回404。可以接受。

也可以使用re.match，但需要锚定，所以我们使用fullmatch。

此外，我们需要导入re。

现在，重写整个代码。

我们逐部分写。

开始：

import http.server
import json
import sqlite3
import threading
import socketserver
import os
import re
import time
from datetime import datetime, timedelta, timezone
import sys

# 全局变量
DB_PATH = 'inventory.db'
db_lock = threading.Lock()
conn = None

# 辅助函数
def _now_ts():
    return time.time()

# 数据库初始化
def init_db():
    global conn
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute('''CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        stock_total INTEGER NOT NULL,
        stock_available INTEGER NOT NULL
    )''')
    conn.execute('''CREATE TABLE IF NOT EXISTS reservations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        status TEXT NOT NULL DEFAULT 'pending',
        expires_at REAL NOT NULL,
        created_at REAL NOT NULL,
        FOREIGN KEY(item_id) REFERENCES items(id)
    )''')
    conn.commit()

# 数据库操作函数
def clean_expired(conn):
    now = _now_ts()
    cursor = conn.execute("SELECT id, item_id, quantity FROM reservations WHERE status='pending' AND expires_at < ?", (now,))
    expired = cursor.fetchall()
    if not expired:
        return
    conn.execute("BEGIN")
    try:
        for row in expired:
            # 释放库存
            conn.execute("UPDATE items SET stock_available = stock_available + ? WHERE id = ?", (row['quantity'], row['item_id']))
            # 更新预约状态
            conn.execute("UPDATE reservations SET status='expired' WHERE id = ? AND status='pending'", (row['id'],))
        conn.commit()
    except Exception:
        conn.rollback()
        raise

def get_all_items(conn):
    cursor = conn.execute("SELECT id, name, stock_total, stock_available FROM items")
    rows = cursor.fetchall()
    return [dict(row) for row in rows]

def create_item(conn, name, stock_total):
    if not name:
        return None, "name is required"
    try:
        stock_total = int(stock_total)
        if stock_total <= 0:
            return None, "stock_total must be a positive integer"
    except (ValueError, TypeError):
        return None, "stock_total must be a positive integer"
    conn.execute("BEGIN")
    try:
        cursor = conn.execute("INSERT INTO items (name, stock_total, stock_available) VALUES (?, ?, ?)", (name, stock_total, stock_total))
        item_id = cursor.lastrowid
        conn.commit()
        return {"id": item_id, "name": name, "stock_total": stock_total, "stock_available": stock_total}, None
    except Exception:
        conn.rollback()
        raise

def create_reservation(conn, item_id, quantity, ttl_seconds):
    try:
        item_id = int(item_id)
        quantity = int(quantity)
        ttl_seconds = int(ttl_seconds)
    except (ValueError, TypeError):
        return None, "item_id, quantity, ttl_seconds must be integers"
    if quantity <= 0:
        return None, "quantity must be positive"
    if ttl_seconds <= 0:
        return None, "ttl_seconds must be positive"
    conn.execute("BEGIN")
    try:
        # 检查商品存在和库存
        cursor = conn.execute("SELECT id, stock_available FROM items WHERE id = ?", (item_id,))
        item = cursor.fetchone()
        if item is None:
            conn.rollback()
            return None, "Item not found"
        if item['stock_available'] < quantity:
            conn.rollback()
            return None, "Insufficient stock"
        # 减少库存
        conn.execute("UPDATE items SET stock_available = stock_available - ? WHERE id = ?", (quantity, item_id))
        # 创建预约
        now_ts = _now_ts()
        expires_ts = now_ts + ttl_seconds
        cursor = conn.execute("INSERT INTO reservations (item_id, quantity, status, expires_at, created_at) VALUES (?, ?, 'pending', ?, ?)",
                             (item_id, quantity, expires_ts, now_ts))
        reservation_id = cursor.lastrowid
        conn.commit()
        # 返回可读时间
        return {
            "id": reservation_id,
            "item_id": item_id,
            "quantity": quantity,
            "status": "pending",
            "expires_at": datetime.utcfromtimestamp(expires_ts).isoformat(),
            "created_at": datetime.utcfromtimestamp(now_ts).isoformat()
        }, None
    except Exception:
        conn.rollback()
        raise

def confirm_reservation(conn, reservation_id):
    try:
        reservation_id = int(reservation_id)
    except (ValueError, TypeError):
        return None, "Invalid reservation id"
    conn.execute("BEGIN")
    try:
        cursor = conn.execute("SELECT status, item_id, quantity FROM reservations WHERE id = ?", (reservation_id,))
        row = cursor.fetchone()
        if row is None:
            conn.rollback()
            return None, "Reservation not found"
        if row['status'] != 'pending':
            conn.rollback()
            return None, "Reservation cannot be confirmed (current status: {})".format(row['status'])
        conn.execute("UPDATE reservations SET status='confirmed' WHERE id = ?", (reservation_id,))
        conn.commit()
        return {"id": reservation_id, "status": "confirmed"}, None
    except Exception:
        conn.rollback()
        raise

def cancel_reservation(conn, reservation_id):
    try:
        reservation_id = int(reservation_id)
    except (ValueError, TypeError):
        return None, "Invalid reservation id"
    conn.execute("BEGIN")
    try:
        cursor = conn.execute("SELECT status, item_id, quantity FROM reservations WHERE id = ?", (reservation_id,))
        row = cursor.fetchone()
        if row is None:
            conn.rollback()
            return None, "Reservation not found"
        if row['status'] != 'pending':
            conn.rollback()
            return None, "Reservation cannot be cancelled (current status: {})".format(row['status'])
        # 释放库存
        conn.execute("UPDATE items SET stock_available = stock_available + ? WHERE id = ?", (row['quantity'], row['item_id']))
        conn.execute("UPDATE reservations SET status='cancelled' WHERE id = ?", (reservation_id,))
        conn.commit()
        return {"id": reservation_id, "status": "cancelled"}, None
    except Exception:
        conn.rollback()
        raise

# HTTP请求处理器
class MyHandler(http.server.BaseHTTPRequestHandler):

    def _send_json(self, data, code=200):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def _send_error(self, code, message):
        self._send_json({"error": message}, code)

    def _read_body(self):
        content_length = self.headers.get('Content-Length')
        if not content_length:
            return {}
        try:
            content_length = int(content_length)
        except ValueError:
            return {}
        if content_length <= 0:
            return {}
        body = self.rfile.read(content_length)
        try:
            return json.loads(body.decode())
        except (json.JSONDecodeError, UnicodeDecodeError):
            return None

    def do_GET(self):
        with db_lock:
            try:
                clean_expired(conn)
                if self.path == '/items':
                    items = get_all_items(conn)
                    self._send_json(items)
                else:
                    self._send_error(404, "Not found")
            except Exception as e:
                self._send_error(500, str(e))

    def do_POST(self):
        with db_lock:
            try:
                clean_expired(conn)
                path = self.path
                if path == '/items':
                    self._handle_post_items()
                elif path == '/reservations':
                    self._handle_post_reservations()
                elif re.fullmatch(r'/reservations/\d+/confirm', path):
                    id = int(path.split('/')[2])
                    self._handle_post_confirm(id)
                elif re.fullmatch(r'/reservations/\d+/cancel', path):
                    id = int(path.split('/')[2])
                    self._handle_post_cancel(id)
                else:
                    self._send_error(404, "Not found")
            except Exception as e:
                self._send_error(500, str(e))

    def _handle_post_items(self):
        body = self._read_body()
        if body is None:
            self._send_error(400, "Invalid JSON")
            return
        name = body.get('name')
        stock_total = body.get('stock_total')
        if not name:
            self._send_error(400, "name is required")
            return
        try:
            stock_total = int(stock_total)
            if stock_total <= 0:
                raise ValueError
        except (ValueError, TypeError):
            self._send_error(400, "stock_total must be a positive integer")
            return
        item, err = create_item(conn, name, stock_total)
        if err:
            self._send_error(400, err)
            return
        self._send_json(item, 201)

    def _handle_post_reservations(self):
        body = self._read_body()
        if body is None:
            self._send_error(400, "Invalid JSON")
            return
        item_id = body.get('item_id')
        quantity = body.get('quantity')
        ttl_seconds = body.get('ttl_seconds')
        if item_id is None or quantity is None or ttl_seconds is None:
            self._send_error(400, "item_id, quantity, ttl_seconds are required")
            return
        try:
            item_id = int(item_id)
            quantity = int(quantity)
            ttl_seconds = int(ttl_seconds)
        except (ValueError, TypeError):
            self._send_error(400, "item_id, quantity, ttl_seconds must be integers")
            return
        reservation, err = create_reservation(conn, item_id, quantity, ttl_seconds)
        if err:
            if err == "Insufficient stock":
                self._send_error(409, err)
            elif "not found" in err.lower():
                self._send_error(404, err)
            else:
                self._send_error(400, err)
            return
        self._send_json(reservation, 201)

    def _handle_post_confirm(self, reservation_id):
        reservation, err = confirm_reservation(conn, reservation_id)
        if err:
            if "not found" in err.lower():
                self._send_error(404, err)
            else:
                self._send_error(400, err)
            return
        self._send_json(reservation)

    def _handle_post_cancel(self, reservation_id):
        reservation, err = cancel_reservation(conn, reservation_id)
        if err:
            if "not found" in err.lower():
                self._send_error(404, err)
            else:
                self._send_error(400, err)
            return
        self._send_json(reservation)

# 服务器类
class ThreadHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True

# 启动入口
if __name__ == '__main__':
    init_db()
    server = ThreadHTTPServer(('127.0.0.1', 8080), MyHandler)
    print("Server starting on 127.0.0.1:8080")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Server shutting down")
        server.server_close()
        sys.exit(0)

现在，代码已经完整。我们检查一下。

- 在do_POST中，我们使用re.fullmatch来匹配路径。但是，对于/reservations/1/confirm，fullmatch会匹配，但我们的路径中可能有额外的查询字符串？如果客户端发送/reservations/1/confirm?foo=bar，fullmatch会失败，返回404。但通常API不会要求处理查询参数，所以可以忽略。如果要允许查询字符串，我们可以使用re.match并忽略？但为了简单，只支持路径。

- 在_handle_post_confirm中，我们直接调用confirm_reservation，如果reservation_id无效，我们调用_send_error(404)或400取决于错误。注意：confirm_reservation会尝试转换为int，如果失败返回None和"Invalid reservation id"，我们在函数中已经转换为int，但我们在调用时已经传入了整数，所以不会触发。但我们还是在函数内处理了类型错误。

- 在_handle_post_confirm中，我们不再验证reservation_id是否为整数，因为路径已经确保是数字（通过正则\d+），所以我们直接int()转换，不会有问题。

- 在_handle_post_cancel类似。

- 在_handle_post_items中，我们手动验证了name和stock_total，然后调用create_item，其中还会验证一次，但双重验证无害。

- 在clean_expired中，我们使用了BEGIN/COMMIT，但是在查询之前我们没有显式BEGIN，只是执行SELECT，然后如果没有过期记录，直接返回。如果有，再BEGIN。但注意：SELECT语句可能会自动开始一个事务（在Python sqlite3中，当执行DML时才会自动开始事务；SELECT不会）。所以这样是安全的。但更好的是，我们可以在查询之前显式BEGIN？不需要。

- 我们使用conn.execute("BEGIN")，但Python sqlite3的execute方法默认会检查连接是否已经在事务中，如果已经在事务中，会抛出错误（"Cannot start a transaction within a transaction"）。所以我们需要确保在调用之前没有未结束的事务。我们在调用clean_expired之前没有事务，因为我们每个方法都会在结束时提交或回滚。所以没问题。

- 在create_reservation中，我们使用BEGIN，如果后续发生异常，回滚。但是，在异常时我们捕获并rollback，然后异常会重新抛出，被do_POST捕获，然后发送500。这样连接状态被重置。但是在do_POST的捕获中，我们发送500，然后with db_lock释放。这样连接处于无事务状态。没问题。

- 在confirm_reservation中类似。

- 注意：在clean_expired中，如果用户请求时没有获取锁？我们在with db_lock内调用，所以安全。

- 还有一个问题：在do_GET中，我们调用了clean_expired(conn)，但clean_expired内部也可能抛出异常，我们捕获并返回500。但如果在clean_expired中发生异常，事务可能未正确回滚，但我们在clean_expired中使用了try-except回滚并重新抛出，所以会回滚。所以最终状态应该是好的。

- 在clean_expired中，如果expired列表很大，我们逐条执行UPDATE，效率较低。可以考虑使用UNION之类的，但简单实现可以接受。

- 我们还需要注意：在clean_expired中，如果某个item被删除（从items表中），但我们的预约仍然引用它（通过外键）。在释放库存时，可能items记录已不存在，会违反外键约束？我们在创建时使用外键，但sqlite默认外键约束是关闭的，所以不会检查。我们可以在连接时设置PRAGMA foreign_keys=ON，但这里没有设置。如果items被删除，但在我们的操作中不会主动删除items，只有创建，所以不会出现。所以忽略。

- 在创建预约时，我们检查item存在，如果item被其他并发删除？由于锁，不会。

- 关于库存一致性：在create_reservation中，我们先查询库存，若充足，则更新。在事务中，所有操作是原子的。所以如果多个线程同时请求，由于锁序列化，所以没问题。

- 在cancel和clean时释放库存，也是正确的。

- 注意：在clean_expired中，我们更新预约状态时使用了WHERE status='pending'，这是为了防止竞态条件，但因为有锁，不会有线程同时修改，但可以保持。

- 在confirm_reservation和cancel_reservation中，我们更新状态时没有加额外的WHERE条件，但我们在事务中，并且之前查询了一致性，且在锁保护下，所以安全。

现在，代码满足要求。

但是，我们可能还需要考虑更详细的错误情况，例如在读取body时如果出现IOError等，我们捕获所有异常。

另外，在发送响应时，可能需要处理wfile.write的异常，但这里我们忽略。

测试可以手动。

现在，确认所有导入：我们已经导入time，datetime，re等。

在create_reservation中，我们使用了datetime.utcfromtimestamp，所以导入datetime。

在clean_expired中，我们只用time。

确认不需要其他.

现在代码总行数：大约200多行，远小于1000。

现在检查是否遗漏了任何要求：要求包括“每次请求前清理已过期且仍为 pending 的预约并释放库存。”我们在do_GET和do_POST开头都调用了clean_expired。满足。

“可使用事务和线程锁。”我们使用了锁和事务。满足。

“返回 JSON；错误响应包含 error 字段。”满足。

“包含一个 if __name__ == "__main__" 启动入口，默认监听 127.0.0.1:8080。”满足。

“文件名假定为 server.py” 我们将在输出中提供完整代码，包括文件名提示？我们只需要输出代码。

“只输出完整 Python 代码，不要解释。”所以最后我们输出代码。

但是，我们需要确保没有语法错误，逻辑正确。

还有一些潜在问题：在do_POST中，我们使用re.fullmatch匹配路径，需要确保re已导入。是的。

在clean_expired中，如果我们查询到的过期预约记录，然后开始事务，但在事务中又查询了同样的记录？我们在循环中使用UPDATE，不会再次查询。可以。

但是，在事务中，如果某些预约在查询后、事务开始前，被其他线程取消？但因为有锁，所以不会。

在clean_expired中，我们使用BEGIN，然后执行UPDATE。但是，如果另一个线程在等待锁，所以没问题。

另外，注意：在clean_expired中，我们使用了begin/commit/rollback，但如果在begin之前，conn可能已经处于事务中？由于我们在每个请求处理前会调用clean_expired，而clean_expired会在完成后提交或回滚，所以下一个请求开始时连接处于非事务状态。但是，如果某个请求处理过程中（例如在do_POST的_handle_post_reservations中），调用了create_reservation，其中使用了begin和commit，然后返回。在do_POST中，在调用_handle_post_reservations之前已经调用了clean_expired，所以两个独立的事务。没问题。

但是，在_handle_post_reservations中，我们调用了create_reservation，如果它发生了异常并回滚，异常会抛出到do_POST，do_POST发送500。然后do_POST结束，释放锁。连接状态被回滚，正常。

但注意：在do_POST中，我们捕获所有Exception并发送500。如果异常发生在clean_expired中，我们发送500后，连接可能处于事务中？但在clean_expired中，我们在try中如果发生异常，会rollback然后raise，所以连接回到非事务状态。所以没关系。

同样，在具体处理函数中发生异常，被do_POST捕获，但函数内会回滚并抛出，连接状态正常。

所以整体稳健。

现在我们输出最终代码。
```

## Assistant

````markdown
```python
import http.server
import json
import sqlite3
import threading
import socketserver
import os
import re
import time
from datetime import datetime, timedelta, timezone
import sys

DB_PATH = 'inventory.db'
db_lock = threading.Lock()
conn = None


def _now_ts():
    return time.time()


def init_db():
    global conn
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute('''CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        stock_total INTEGER NOT NULL,
        stock_available INTEGER NOT NULL
    )''')
    conn.execute('''CREATE TABLE IF NOT EXISTS reservations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        status TEXT NOT NULL DEFAULT 'pending',
        expires_at REAL NOT NULL,
        created_at REAL NOT NULL,
        FOREIGN KEY(item_id) REFERENCES items(id)
    )''')
    conn.commit()


def clean_expired(conn):
    now = _now_ts()
    cursor = conn.execute(
        "SELECT id, item_id, quantity FROM reservations WHERE status='pending' AND expires_at < ?",
        (now,))
    expired = cursor.fetchall()
    if not expired:
        return
    conn.execute("BEGIN")
    try:
        for row in expired:
            conn.execute("UPDATE items SET stock_available = stock_available + ? WHERE id = ?",
                         (row['quantity'], row['item_id']))
            conn.execute("UPDATE reservations SET status='expired' WHERE id = ? AND status='pending'",
                         (row['id'],))
        conn.commit()
    except Exception:
        conn.rollback()
        raise


def get_all_items(conn):
    cursor = conn.execute("SELECT id, name, stock_total, stock_available FROM items")
    rows = cursor.fetchall()
    return [dict(row) for row in rows]


def create_item(conn, name, stock_total):
    if not name:
        return None, "name is required"
    try:
        stock_total = int(stock_total)
        if stock_total <= 0:
            return None, "stock_total must be a positive integer"
    except (ValueError, TypeError):
        return None, "stock_total must be a positive integer"
    conn.execute("BEGIN")
    try:
        cursor = conn.execute("INSERT INTO items (name, stock_total, stock_available) VALUES (?, ?, ?)",
                              (name, stock_total, stock_total))
        item_id = cursor.lastrowid
        conn.commit()
        return {"id": item_id, "name": name, "stock_total": stock_total, "stock_available": stock_total}, None
    except Exception:
        conn.rollback()
        raise


def create_reservation(conn, item_id, quantity, ttl_seconds):
    try:
        item_id = int(item_id)
        quantity = int(quantity)
        ttl_seconds = int(ttl_seconds)
    except (ValueError, TypeError):
        return None, "item_id, quantity, ttl_seconds must be integers"
    if quantity <= 0:
        return None, "quantity must be positive"
    if ttl_seconds <= 0:
        return None, "ttl_seconds must be positive"
    conn.execute("BEGIN")
    try:
        cursor = conn.execute("SELECT id, stock_available FROM items WHERE id = ?", (item_id,))
        item = cursor.fetchone()
        if item is None:
            conn.rollback()
            return None, "Item not found"
        if item['stock_available'] < quantity:
            conn.rollback()
            return None, "Insufficient stock"
        conn.execute("UPDATE items SET stock_available = stock_available - ? WHERE id = ?",
                     (quantity, item_id))
        now_ts = _now_ts()
        expires_ts = now_ts + ttl_seconds
        cursor = conn.execute(
            "INSERT INTO reservations (item_id, quantity, status, expires_at, created_at) VALUES (?, ?, 'pending', ?, ?)",
            (item_id, quantity, expires_ts, now_ts))
        reservation_id = cursor.lastrowid
        conn.commit()
        return {
            "id": reservation_id,
            "item_id": item_id,
            "quantity": quantity,
            "status": "pending",
            "expires_at": datetime.utcfromtimestamp(expires_ts).isoformat(),
            "created_at": datetime.utcfromtimestamp(now_ts).isoformat()
        }, None
    except Exception:
        conn.rollback()
        raise


def confirm_reservation(conn, reservation_id):
    try:
        reservation_id = int(reservation_id)
    except (ValueError, TypeError):
        return None, "Invalid reservation id"
    conn.execute("BEGIN")
    try:
        cursor = conn.execute("SELECT status, item_id, quantity FROM reservations WHERE id = ?", (reservation_id,))
        row = cursor.fetchone()
        if row is None:
            conn.rollback()
            return None, "Reservation not found"
        if row['status'] != 'pending':
            conn.rollback()
            return None, "Reservation cannot be confirmed (current status: {})".format(row['status'])
        conn.execute("UPDATE reservations SET status='confirmed' WHERE id = ?", (reservation_id,))
        conn.commit()
        return {"id": reservation_id, "status": "confirmed"}, None
    except Exception:
        conn.rollback()
        raise


def cancel_reservation(conn, reservation_id):
    try:
        reservation_id = int(reservation_id)
    except (ValueError, TypeError):
        return None, "Invalid reservation id"
    conn.execute("BEGIN")
    try:
        cursor = conn.execute("SELECT status, item_id, quantity FROM reservations WHERE id = ?", (reservation_id,))
        row = cursor.fetchone()
        if row is None:
            conn.rollback()
            return None, "Reservation not found"
        if row['status'] != 'pending':
            conn.rollback()
            return None, "Reservation cannot be cancelled (current status: {})".format(row['status'])
        conn.execute("UPDATE items SET stock_available = stock_available + ? WHERE id = ?",
                     (row['quantity'], row['item_id']))
        conn.execute("UPDATE reservations SET status='cancelled' WHERE id = ?", (reservation_id,))
        conn.commit()
        return {"id": reservation_id, "status": "cancelled"}, None
    except Exception:
        conn.rollback()
        raise


class MyHandler(http.server.BaseHTTPRequestHandler):

    def _send_json(self, data, code=200):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def _send_error(self, code, message):
        self._send_json({"error": message}, code)

    def _read_body(self):
        content_length = self.headers.get('Content-Length')
        if not content_length:
            return {}
        try:
            content_length = int(content_length)
        except ValueError:
            return {}
        if content_length <= 0:
            return {}
        body = self.rfile.read(content_length)
        try:
            return json.loads(body.decode())
        except (json.JSONDecodeError, UnicodeDecodeError):
            return None

    def do_GET(self):
        with db_lock:
            try:
                clean_expired(conn)
                if self.path == '/items':
                    items = get_all_items(conn)
                    self._send_json(items)
                else:
                    self._send_error(404, "Not found")
            except Exception as e:
                self._send_error(500, str(e))

    def do_POST(self):
        with db_lock:
            try:
                clean_expired(conn)
                path = self.path
                if path == '/items':
                    self._handle_post_items()
                elif path == '/reservations':
                    self._handle_post_reservations()
                elif re.fullmatch(r'/reservations/\d+/confirm', path):
                    rid = int(path.split('/')[2])
                    self._handle_post_confirm(rid)
                elif re.fullmatch(r'/reservations/\d+/cancel', path):
                    rid = int(path.split('/')[2])
                    self._handle_post_cancel(rid)
                else:
                    self._send_error(404, "Not found")
            except Exception as e:
                self._send_error(500, str(e))

    def _handle_post_items(self):
        body = self._read_body()
        if body is None:
            self._send_error(400, "Invalid JSON")
            return
        name = body.get('name')
        stock_total = body.get('stock_total')
        if not name:
            self._send_error(400, "name is required")
            return
        try:
            stock_total = int(stock_total)
            if stock_total <= 0:
                raise ValueError
        except (ValueError, TypeError):
            self._send_error(400, "stock_total must be a positive integer")
            return
        item, err = create_item(conn, name, stock_total)
        if err:
            self._send_error(400, err)
            return
        self._send_json(item, 201)

    def _handle_post_reservations(self):
        body = self._read_body()
        if body is None:
            self._send_error(400, "Invalid JSON")
            return
        item_id = body.get('item_id')
        quantity = body.get('quantity')
        ttl_seconds = body.get('ttl_seconds')
        if item_id is None or quantity is None or ttl_seconds is None:
            self._send_error(400, "item_id, quantity, ttl_seconds are required")
            return
        try:
            item_id = int(item_id)
            quantity = int(quantity)
            ttl_seconds = int(ttl_seconds)
        except (ValueError, TypeError):
            self._send_error(400, "item_id, quantity, ttl_seconds must be integers")
            return
        reservation, err = create_reservation(conn, item_id, quantity, ttl_seconds)
        if err:
            if err == "Insufficient stock":
                self._send_error(409, err)
            elif "not found" in err.lower():
                self._send_error(404, err)
            else:
                self._send_error(400, err)
            return
        self._send_json(reservation, 201)

    def _handle_post_confirm(self, reservation_id):
        reservation, err = confirm_reservation(conn, reservation_id)
        if err:
            if "not found" in err.lower():
                self._send_error(404, err)
            else:
                self._send_error(400, err)
            return
        self._send_json(reservation)

    def _handle_post_cancel(self, reservation_id):
        reservation, err = cancel_reservation(conn, reservation_id)
        if err:
            if "not found" in err.lower():
                self._send_error(404, err)
            else:
                self._send_error(400, err)
            return
        self._send_json(reservation)


class ThreadHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True


if __name__ == '__main__':
    init_db()
    server = ThreadHTTPServer(('127.0.0.1', 8080), MyHandler)
    print("Server starting on 127.0.0.1:8080")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Server shutting down")
        server.server_close()
        sys.exit(0)
```
````
