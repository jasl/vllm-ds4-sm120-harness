# Generation Transcript

- Case: `zh_code_be_001`
- Language group: `zh`
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
- Elapsed seconds: 260.215442
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 442, "total_tokens": 26002, "completion_tokens": 25560, "prompt_tokens_details": null}`
- Prompt tokens: 442
- Completion tokens: 25560
- Total tokens: 26002

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
我们被要求编写一个单文件HTTP API服务，使用Python 3标准库，使用sqlite3持久化，总代码不超过1000行。数据模型：商品表包含id, name, stock_total, stock_available；预约表：id, item_id, quantity, status, expires_at, created_at。

需要实现HTTP API：GET /items, POST /items, POST /reservations, POST /reservations/{id}/confirm, POST /reservations/{id}/cancel。同时，每次请求前清理过期的pending预约并释放库存。需要处理并发请求下的库存一致性，使用事务和线程锁。

我们使用标准库`http.server`来构建HTTP服务。注意：我们需要处理路径参数，`http.server`默认只支持简单路由。我们需要解析URL路径和方法。

可以使用`BaseHTTPRequestHandler`，然后重写`do_GET`, `do_POST`, `do_PUT`, `do_DELETE`等方法。这里只有GET和POST，所以只需要这两个。

我们需要一个全局的数据库连接，但注意sqlite3在多个线程中使用需要小心，建议每个请求使用新的连接，或者使用连接池。因为是在单个进程中，且使用`ThreadingHTTPServer`（Python 3.7+）或`ThreadingMixIn`配合HTTPServer来支持并发。每个请求会在一个线程中处理，所以我们需要为每个线程提供独立的数据库连接，或者使用连接锁确保一次只有一个请求使用连接。但Python的sqlite3默认可以在多线程中使用，但连接本身不是线程安全的，所以推荐每个线程使用自己的连接。我们可以使用`threading.local`来存储每个线程的连接，或者在使用时创建连接，注意关闭。

为了简单，可以为每个请求创建新的连接，但这可能开销较大。但考虑到这是一个小服务，可以接受。或者我们可以在主线程创建一个连接，并使用锁来保证每次只有一个请求使用该连接，但这样会退化为串行处理，影响并发性能。更合理的是使用连接池，但标准库不支持。最简单的办法：在每个请求处理函数中打开一个新连接，处理完后关闭。这样每个请求独立，不会互相干扰。sqlite3在WAL模式下可以支持并发读取，但写操作会锁数据库。不过使用每个请求独立连接是可行的。我们将使用`check_same_thread=False`来允许在所有线程中使用同一个连接？不，这是不安全的。使用独立连接。

但注意清理操作需要在每个请求前进行，而且数据库操作需要事务一致性。我们需要在清理和预约操作中使用事务，并使用锁来确保库存一致性。实际上，如果我们每个请求单独使用一个连接，那么数据库内部会处理锁（sqlite3有文件级锁）。但是，在库存更新和预约创建之间可能有竞态条件：例如，检查库存足够，然后插入预约，但其他线程可能同时修改了库存。我们需要使用事务和适当的隔离级别，或者使用`SELECT ... FOR UPDATE`，但sqlite3不支持行级锁。我们可以使用排他事务（BEGIN IMMEDIATE）来确保写操作序列化。或者我们可以在应用层使用线程锁来保护临界区，比如一个全局锁用于库存修改。更简单可靠：在创建预约、确认、取消等操作时，使用全局线程锁（`threading.Lock`）来串行化对库存和预约的修改操作，这样避免竞态条件。但是清理操作也可能修改库存，所以也需要加锁。使用锁可以确保库存一致性，但可能降低并发，但鉴于这个服务规模小，可以接受。

我们将定义一个全局锁`db_lock`，在每次涉及到修改数据库的操作（写操作）时获取锁，读操作可以不用锁，但如果读后写也需要锁。对于GET /items只是读取，不需要锁。对于POST /items（新增商品），修改库存，需要锁。对于POST /reservations，需要检查库存并插入预约，需要锁。对于confirm/cancel，需要修改状态并调整库存，需要锁。清理过期也需要锁。

在锁内，我们打开一个数据库连接，执行操作，提交或回滚，然后关闭。或者我们可以使用一个连接，但在锁内使用连接。但注意如果使用独立连接，锁只保护代码执行顺序，数据库文件仍然可能被多个连接访问，但锁确保同一时间只有一个线程在修改数据库，从而避免了并发写冲突。实际上，sqlite3在多个连接同时写时会返回`database is locked`错误，我们需要处理重试。但使用全局锁可以避免这种情况。

综上所述，我们选择使用全局锁和每个请求使用独立数据库连接（在锁内打开连接，操作完后关闭）。或者我们可以使用单个连接并在锁内使用，但单个连接不是线程安全的，但被锁保护，所以可以。为简单，我们可以使用单个连接，但需要设置`check_same_thread=False`，并在线程锁保护下使用。但注意，如果使用了锁，我们实际上只需要一个连接，因为所有操作都在锁内串行执行，连接可以重用。但要注意，如果在锁外有其他连接读写（如读操作不加锁），则可能产生不一致。为了简单，我们也对所有读操作不加锁，但读到的数据可能是旧的一致状态，没有关系。但对于GET /items，它读取库存，可能读到中间状态？如果我们对写操作加锁，读操作不加锁，则可能读到未提交的数据？sqlite3默认隔离级别是“可提交读”，未提交的更改对其他连接不可见。所以读操作不会读到未提交的更改。但是，如果在写操作执行期间（已BEGIN但未COMMIT），读操作可能会读到旧版本的数据，但不会读到脏数据。这是可以接受的。或者我们也可以让读操作使用锁，确保序列化。但为了性能，读操作通常不需要锁。

但是，对于清理操作，我们需要在每个请求前执行，包括GET请求。如果GET请求不加锁，清理操作需要修改数据库，所以也需要加锁。如果我们让每个请求（包括GET）先执行清理（可能修改数据库），那么我们需要在清理时加锁。所以，一个方案是：在每个请求处理开始时，我们获取锁，执行清理（如果需要），然后处理请求（可能是读或写），然后释放锁。这样所有请求都串行化，但性能可能降低，但实现简单。另一种方案：读操作不需要锁，但清理操作修改了数据库，所以如果要让读操作不阻塞，可以在读之前先尝试执行清理（但清理需要修改，所以需要锁），但可以用另一个锁专门用于清理，但这样复杂。为简化，我们使用全局锁串行化所有请求，虽然会降低并发，但满足要求，且易于实现一致性。总代码不超过1000行，这样简单。

实际上，还可以使用更细粒度的锁：比如使用多个锁分别保护不同资源？但这里比较简单，全局锁可行。

但是，考虑到“正确处理并发请求下的库存一致性”，我们可以使用数据库事务和适当的隔离级别，结合重试机制。如果我们使用`BEGIN IMMEDIATE`或`BEGIN EXCLUSIVE`，可以确保写操作不会发生死锁。但是，如果我们每个请求使用独立连接，且没有全局锁，多个写操作并发时，sqlite3可能会返回`database is locked`错误，我们需要重试。我们可以通过设置超时（`timeout`参数）让sqlite3等待锁。但是等待时间不确定，且可能产生死锁？实际上sqlite3内置了忙等待。我们可以设置`timeout`为5000毫秒，这样当写冲突时，会等待直到超时。这样我们不需要应用层锁，只需要处理超时异常。但是，对于库存一致性场景，我们需要在事务内执行检查库存和插入预约，需要保证原子性。使用`BEGIN IMMEDIATE`可以确保事务一开始就获取写锁，防止其他写者。但如果有两个线程同时开始，一个获取了锁，另一个会等待。这样就不会有竞争。这是数据库层面的并发控制，不需要应用锁。这样性能更好，因为读操作不需要锁。但需要注意，我们的清理操作也需要在事务内，且最好与请求操作在同一个事务中，以保证一致性。例如，创建预约前先清理过期，然后检查库存，插入预约，这些应该在同一个事务中，避免其他事务干扰。但清理操作也可能需要修改库存，所以我们建议将清理和主要操作放在同一个事务中。因此，每个请求处理函数内部，我们打开一个数据库连接，设置`isolation_level`为`'IMMEDIATE'`（在3.7+中，我们可以通过`execute('BEGIN IMMEDIATE')`来控制），然后执行操作，提交或回滚。如果发生锁等待超时，捕获异常返回503。这样我们可以很好地利用数据库的锁机制来保证一致性，而无需应用锁。

但需要注意的是，SQLite默认的事务行为是：在第一次写操作时自动开始事务，但使用的是DEFERRED模式，意味着直到实际写操作才获取锁，这可能导致在检查库存后，插入预约前，其他事务可能修改了库存，造成不一致。为了避免这种情况，我们应该在开始时使用`BEGIN IMMEDIATE`或`BEGIN EXCLUSIVE`来提前获取写锁。我们可以通过设置`isolation_level`为`'EXCLUSIVE'`，或者在执行任何操作前执行`PRAGMA busy_timeout=5000;`然后执行`BEGIN IMMEDIATE`。这样就能确保事务序列化。

Python的sqlite3连接默认`isolation_level`为`''`（即自动提交模式？不，默认是`None`？需要查文档。实际上，sqlite3模块的`connect()`函数有一个`isolation_level`参数，默认是`''`，表示使用python的默认行为（自动开启事务）。如果我们设置`isolation_level=None`，则自动提交模式，即每个DML语句后自动提交。如果我们设置`isolation_level='DEFERRED'`，则开始事务使用DEFERRED。我们可以设置`isolation_level='IMMEDIATE'`，则开始事务使用IMMEDIATE。或者我们可以在代码中显式控制`BEGIN`。

选择：使用每个请求独立连接，设置`isolation_level='IMMEDIATE'`（或显式`BEGIN IMMEDIATE`），这样事务一开始就获取写锁，确保序列化。然后执行清理和主要操作。如果锁等待超时，sqlite3会抛出`OperationalError: database is locked`，我们捕获并返回503。这样实现简单且正确。

但是注意：使用`IMMEDIATE`事务，即使只是读操作（如GET /items），也会获取写锁（因为IMMEDIATE会获取写锁），导致并发读也被阻塞。对于读请求，我们可能不需要写锁，但我们的清理操作需要写。如果我们在GET中也执行清理，那么也需要写锁。如果我们希望在GET中不阻塞，我们可以将清理分离，或者使用DEFERRED事务，但这样在清理需要写时自动升级锁。但可能导致死锁。另一种方案：对于只读请求，不执行清理（因为清理可能修改数据库，但只读请求不执行清理？要求是“每次请求前清理已过期且仍为pending的预约并释放库存”。这意味着每个请求，包括GET，都需要先执行清理。所以读请求也需要清理。这意味着每个请求都需要写操作。所以使用IMMEDIATE事务，每个请求都会获取写锁，这样并发请求实际上被序列化。虽然性能较低，但满足要求且简单。或者我们可以使用DEFERRED事务，让清理操作在需要时升级锁，但考虑到可能发生的死锁（两个事务等待对方释放读锁升级写锁），但SQLite使用文件锁，不会死锁，但会超时。为了简单，我们使用IMMEDIATE事务。

但还有更好的：我们可以让清理操作独立于请求操作，即先在一个单独的事务中执行清理，然后再在另一个事务中执行请求操作。但这样可能引入不一致，比如清理后、请求前的间隙可能有其他请求修改了数据。所以最好在同一个事务中执行清理和主要操作。所以每个请求一个事务，使用IMMEDIATE。

因此，我们将为每个请求打开一个连接，设置`isolation_level='IMMEDIATE'`（通过`connect(..., isolation_level='IMMEDIATE')`），然后执行操作。注意：在Python 3.12中，sqlite3.connect的isolation_level参数可以设置为'DEFERRED', 'IMMEDIATE', 'EXCLUSIVE'，或者None表示自动提交。但文档说从3.12开始，推荐使用autocommit参数，但传统方式仍然支持。为了兼容性，我们可以使用传统方式。

还有一个问题：每个请求前清理过期预约，我们需要扫描所有expires_at小于当前时间且status='pending'的预约，将其status改为'expired'，并释放库存（增加对应商品的stock_available）。这个操作需要在一个事务内完成。所以每个请求开始时，我们先执行这个清理，然后执行主要的请求逻辑。如果清理失败（如数据库锁），整个请求失败。

设计数据库表结构：
- items: id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE? 应该允许重复名称？没有明确说明，我们可以允许重复，但通常名称应唯一，但为简单不强制。stock_total INTEGER NOT NULL, stock_available INTEGER NOT NULL.
- reservations: id INTEGER PRIMARY KEY AUTOINCREMENT, item_id INTEGER NOT NULL REFERENCES items(id), quantity INTEGER NOT NULL, status TEXT NOT NULL DEFAULT 'pending', expires_at REAL NOT NULL (存储Unix时间戳), created_at REAL NOT NULL.

我们使用REAL存储时间戳，方便比较。

API细节：
1. GET /items：返回商品列表。每个商品包含id, name, stock_total, stock_available。返回格式：`{"items": [...]}`? 要求列出商品和可用库存，可以返回数组。最好包括所有字段。
2. POST /items：JSON body: {"name": "...", "stock_total": 123}。创建商品，stock_available初始等于stock_total。返回创建的商品，包括id（和所有字段）。或者只返回成功消息。最好返回商品对象。可以在响应中返回商品。需要检查参数是否提供，类型是否正确。stock_total应为正整数。name不能为空。
3. POST /reservations：JSON body: {"item_id": 1, "quantity": 5, "ttl_seconds": 3600}。创建预约，状态为pending，expires_at = now + ttl_seconds。库存不足时返回409 Conflict。成功返回预约对象（包括id）。
4. POST /reservations/{id}/confirm：确认预约，状态变为confirmed，不再释放库存（即确认后过期不会释放？但确认后库存已被占用，但不会再释放？题目说“确认预约，状态变为 confirmed，不再释放库存。” 所以confirmed状态不会因为过期而释放。但取消时释放库存。
5. POST /reservations/{id}/cancel：取消预约，释放库存（增加stock_available），状态变为cancelled。
检查：如果预约不存在返回404，如果状态不允许（如已确认或已取消）返回400？（没有明确，但最好处理。）
6. 清理操作：每次请求前执行，扫描所有过期的pending预约，将它们状态改为expired，并释放库存。注意：如果预约已被确认或取消，不应该被清理。

需要解析URL路径，对于GET /items简单；对于POST /items；对于POST /reservations和POST /reservations/{id}/confirm/cancel需要匹配模式。

注意：路径`/reservations/{id}/confirm`和`/reservations/{id}/cancel`，我们可以使用正则或字符串解析。因为只有两种带参数的模式，我们可以用字符串分割。

我们使用http.server模块，创建自定义Handler，在do_GET和do_POST中处理。

由于需要解析JSON请求体，使用`json`模块。

错误响应：状态码如400、404、409、500，JSON包含error字段。

我们还需要注意：请求头Content-Type应为application/json，但如果不是，我们可以处理或返回错误。为简单，我们假设是JSON。

实现步骤：
- 定义全局锁？如果使用数据库事务，可以不用应用锁。但为了避免多个连接同时写导致超时，我们可以不额外加锁。但如果我们使用IMMEDIATE事务，并设置busy_timeout，那么当多个线程并发时，会自动等待。我们可以设置PRAGMA busy_timeout=5000。这样当锁不可用时，sqlite会等待最多5秒。如果超时，则抛出异常。我们可以捕获并返回503或其他错误。

- 我们需要在每个请求开始时打开连接，执行PRAGMA busy_timeout=5000和BEGIN IMMEDIATE。如果BEGIN失败（锁超时），则返回503。但为了简化，我们可以在创建连接时设置timeout参数？sqlite3.connect有一个timeout参数，设置忙等待超时（秒）。默认是5秒？文档说timeout参数是等待锁的超时时间，单位秒。我们可以设置timeout=5。这样在尝试获取锁时，会自动等待最多5秒。如果超时，则抛出OperationalError。所以我们可以在连接时设置timeout=5，然后执行任何操作前，sqlite3会自动处理。但我们需要确保事务模式是IMMEDIATE。如果我们不显式BEGIN，python的sqlite3在执行第一个SQL语句时自动开始一个事务，默认为DEFERRED。我们需要在开始时立即获取写锁，所以我们应该在获取连接后立即执行`BEGIN IMMEDIATE`，或者在设置isolation_level为'IMMEDIATE'，这样连接会以IMMEDIATE行为开始事务。在Python 3.12之前，可以通过设置isolation_level='IMMEDIATE'来达到。但注意，在Python 3.12+中，推荐使用autocommit参数。为了兼容，我们使用传统方法：创建连接时将isolation_level设置为'IMMEDIATE'。这样，第一次执行任何SQL语句时，自动执行BEGIN IMMEDIATE。但问题：如果我们先执行SELECT，也是IMMEDIATE？文档没有明确，但应该是。所以我们可以这样做。

但是，如果我们在连接创建后立即执行SQL（如PRAGMA），也会开始一个事务。我们可以先执行PRAGMA busy_timeout，然后让后续操作在同一个事务中。但PRAGMA不会提交事务，但会影响后续。更好的做法：先执行PRAGMA busy_timeout=5000，然后执行BEGIN IMMEDIATE。如果我们设置了isolation_level='IMMEDIATE'，那么在执行第一个SQL（可能是PRAGMA或SELECT）时就会自动开始IMMEDIATE事务。所以我们可以先执行PRAGMA busy_timeout，它会在事务中执行。但PRAGMA通常不需要事务，但可以认为无害。然后我们在执行清理和主要操作。但要注意，Python的sqlite3可能会在执行某些语句（如SELECT）后自动开启事务，如果我们设置了isolation_level非None。但如果我们显式执行COMMIT，则事务结束，下一个语句会再次开启。所以我们最好显式控制事务，而不是依赖自动行为。因为我们要在同一个事务中执行多个语句（清理+主要操作），并且最后根据结果提交或回滚。

我建议使用显式事务控制：在连接创建后，我们设置连接为自动提交模式？不，我们手动控制。我们可以设置isolation_level=None（自动提交模式），然后手动执行BEGIN IMMEDIATE，然后执行操作，最后COMMIT或ROLLBACK。这样更清晰。而且这样可以更好地控制错误处理。

所以计划：
- 创建连接时，设置`isolation_level=None`，即自动提交模式，每个语句立即提交。
- 但在每个请求处理中，我们手动执行`con.execute("BEGIN IMMEDIATE")`，然后执行一系列操作，如果全部成功，`con.commit()`（实际上commit在BEGIN后生效？当我们执行BEGIN后，后续的DML不会自动提交，直到我们执行COMMIT。如果我们在自动提交模式下，execute会立即提交，但BEGIN后，后续的execute不会自动提交？实际上，当isolation_level=None时，每个execute语句会自动提交，但BEGIN语句开始一个事务，会改变行为？在Python sqlite3中，如果isolation_level=None，每个execute语句都会被包装在一个自动提交中。但如果我们显式执行BEGIN，则自动提交被暂停，直到COMMIT或ROLLBACK。但这是否可靠？文档建议，如果要手动控制事务，应使用`isolation_level='DEFERRED'`或更高级别，然后自动开始事务。或者设置isolation_level=None，但此时每个execute都会自动提交，不能手动控制。所以最好设置isolation_level='DEFERRED'，然后使用BEGIN IMMEDIATE？不，如果设置isolation_level='DEFERRED'，则执行第一个SQL时自动开始一个DEFERRED事务。如果我们想用IMMEDIATE，需要显式执行BEGIN IMMEDIATE，但这个语句应该在自动事务之前执行？但一旦开始事务，我们不能在同一连接中执行另一个BEGIN（会报错）。所以我们可以先设置isolation_level=None（或使用完全手动模式），但sqlite3的Connection对象有一个`execute`方法，如果我们要手动控制，可以将isolation_level设为`None`，然后每次执行都自动提交，但我们可以通过执行`BEGIN`来开始事务，之后执行的SQL会参与事务，直到`COMMIT`。但官方文档说，当设置`isolation_level=None`时，连接处于自动提交模式，每个SQL语句在其自己的事务中执行，但如果你执行`BEGIN`，则自动提交被禁用，直到`COMMIT`或`ROLLBACK`。所以这是可行的。我们就使用`isolation_level=None`，然后显式执行`BEGIN IMMEDIATE`。

但注意，在Python 3.12+中，isolation_level参数已被弃用，推荐使用autocommit。但为了兼容，我们使用传统方式。我们的代码将在3.10-3.12上运行，可以使用。

所以每个请求处理函数：
1. 创建连接：`conn = sqlite3.connect('inventory.db', timeout=5, isolation_level=None)`
2. 执行`conn.execute("BEGIN IMMEDIATE")`
3. 执行清理过期预约的SQL，并释放库存。
4. 根据请求方法执行主要逻辑。
5. 如果成功，`conn.commit()`，如果失败，`conn.rollback()`，然后返回错误响应。
6. 最后关闭连接。

注意：`BEGIN IMMEDIATE`在获取不到锁时会等待timeout秒，然后抛出OperationalError，我们捕获该异常，返回503或500。

现在编写代码。

首先定义Handler类，继承BaseHTTPRequestHandler。

我们需要将数据库文件放在当前目录，名称可以是`inventory.db`。

在请求开始前，我们还需要解析URL路径。我们可以使用`self.path`，结合`urllib.parse`解析。

对于GET /items，直接返回商品列表。对于POST /items，需要读取请求体JSON。对于POST /reservations，需要读取JSON。对于POST /reservations/{id}/confirm和cancel，需要从路径中提取id。

我们还需要处理CORS吗？不需要。

注意：BaseHTTPRequestHandler的do_GET和do_POST方法需要发送响应。我们使用`self.send_response(status_code)`，设置Content-Type为application/json，然后发送数据。

我们将错误处理封装为一个方法`send_error_json(status_code, message)`。

我们需要处理请求体的读取：self.rfile.read(content_length)。

定义路由映射：在do_GET中解析self.path，根据方法处理。

因为我们还有POST方法，我们可以在do_GET和do_POST中分别处理。

主要功能函数：

- `list_items(conn)`: 执行SELECT * FROM items，返回JSON。
- `create_item(conn, data)`: 插入新商品，返回商品对象。
- `create_reservation(conn, data)`: 检查库存，插入预约，返回预约对象。
- `confirm_reservation(conn, reservation_id)`: 更新状态为confirmed，不改变库存。
- `cancel_reservation(conn, reservation_id)`: 更新状态为cancelled，释放库存（增加商品stock_available）。

清理过期函数：`cleanup_expired(conn)`: 执行事务内操作：找出所有expires_at < datetime.now() AND status='pending'的记录，对于每个，将其status更新为'expired'，并UPDATE items SET stock_available = stock_available + quantity WHERE id = item_id。注意：如果多个满足，需要循环或使用子查询。最好用一条UPDATE来更新库存？我们可以使用UPDATE items SET stock_available = stock_available + (SELECT SUM(quantity) FROM reservations WHERE expires_at < ? AND status='pending' AND item_id = items.id) WHERE id IN (SELECT item_id FROM reservations WHERE expires_at < ? AND status='pending')? 但这样复杂。或者我们可以先查询所有过期预约，然后逐条更新库存，但需要确保原子性。但我们已经在一个事务中，所以可以逐条处理。为了简便，我们可以使用一个UPDATE语句结合子查询来一次性释放库存。但需要注意的是，一个商品可能有多个过期预约，我们需要将所有过期预约的库存加回。我们可以：

```sql
UPDATE items SET stock_available = stock_available +
    (SELECT COALESCE(SUM(quantity), 0) FROM reservations WHERE status='pending' AND expires_at < ? AND items.id = reservations.item_id)
WHERE id IN (SELECT item_id FROM reservations WHERE status='pending' AND expires_at < ?)
```
然后更新这些预约的状态为expired：
```sql
UPDATE reservations SET status='expired' WHERE status='pending' AND expires_at < ?
```
这可以在事务中安全执行，没有竞争。但两个UPDATE可能不是原子性的，但它们在同一个事务中，所以整体原子。我们还可以使用一个UPDATE来更新库存和状态，但状态更新不能和库存更新在一条语句中。所以使用两条语句没问题。

但注意：库存更新可能为负？不应该，因为只有pending才会过期，而且创建时stock_available减少quantity，过期时再加回来，所以应该正确。但如果有bug导致库存不一致，可能为负，我们不应该允许为负。但这里我们信任逻辑。

我们将清理操作放在请求开始时，即在执行主要操作前。但注意，如果请求本身是取消预约，那么取消操作也会释放库存，我们需要确保清理不会干扰？清理操作修改过期的预约，而取消操作取消的是pending（或其他状态）预约，两者无冲突。但要注意：如果在清理过程中，可能将某个预约标记为expired，然后同一个请求试图取消该预约，但因为请求已经获取了写锁，在事务中，清理先执行，所以预约已经expired，然后取消操作可能找不到该预约或状态不匹配。所以顺序很重要：对于取消操作，我们当然希望取消的是pending状态，如果已经被清理为expired，则不应再取消，应返回404或错误。这符合逻辑：过期的预约被清理后，不能取消。所以我们的实现是合理的。

另外，对于确认操作，确认不会释放库存，确认后预约状态变为confirmed，expired时不会被清理（因为status不是pending）。所以在清理时只清理pending且过期的。确认和取消都可能改变状态，所以要避免在事务中被清理？因为清理在事务开始就执行了，然后才执行确认/取消。如果确认/取消的目标预约在清理时已经过期，它会被清理，然后后续操作可能找不到该预约。所以我们需要考虑顺序：对于确认和取消请求，我们在清理后，再去查找预约。如果它被清理了，状态变成expired，那么后续我们无法再confirm或cancel。这符合预期：过期后被清理，不能再操作。所以没问题。

现在考虑并发：如果两个请求同时操作同一个预约，比如一个确认，一个取消，因为事务使用IMMEDIATE，它们会串行执行。第一个会成功，第二个在查找预约时会发现状态已经改变（不是pending），然后返回错误。所以合理。

库存一致性：对于创建预约，检查库存和插入预约在同一个事务中，由于事务是IMMEDIATE，其他写事务必须等待，所以不会出现超卖。

现在我们开始写代码。

需要考虑HTTP状态码：
- 成功：200
- 创建成功：201（对于POST返回资源）我们可以返回201 Created，对于POST /items和POST /reservations返回201及资源。对于POST confirm/cancel，可以返回200。
- 错误：400 Bad Request（参数缺失、无效）；404 Not Found（资源不存在）；409 Conflict（库存不足）；500 Internal Server Error（意外错误）；503 Service Unavailable（数据库锁超时等）。

注意：对于POST /items，如果stock_total不是正整数，返回400。

我们定义辅助函数：
- `read_json_body()`: 从请求读取JSON，如果解析失败返回None。
- `send_json(status, data)`: 发送JSON响应。
- `send_error(status, message)`: 发送错误JSON响应。

我们还需要处理路径匹配：使用正则或简单字符串分割。例如，对于路径`/reservations/123/confirm`，我们可以解析为`/reservations/{id}/confirm`模式。我们可以定义模式处理函数：如果路径以`/reservations/`开头，然后我们可以分割并检查后续部分。

更好的方法：使用`urlparse`解析路径部分，然后按照`/`分割。比如`path_parts = self.path.split('/')`，去除空元素。然后根据长度判断。

例如：
- `GET /items` -> parts = ['items']
- `POST /items` -> parts = ['items']
- `POST /reservations` -> parts = ['reservations']
- `POST /reservations/{id}/confirm` -> parts = ['reservations', id, 'confirm']
- `POST /reservations/{id}/cancel` -> parts = ['reservations', id, 'cancel']

所以我们可以根据parts长度和元素进行匹配。

在do_GET中，如果parts == ['items']，则调用list_items。

在do_POST中，根据parts处理：
- if parts == ['items']: create_item
- elif parts == ['reservations']: create_reservation
- elif len(parts) == 3 and parts[0] == 'reservations' and parts[2] == 'confirm': confirm_reservation(parts[1])
- elif len(parts) == 3 and parts[0] == 'reservations' and parts[2] == 'cancel': cancel_reservation(parts[1])
- else: 404

还需要处理可能的查询字符串？我们忽略。

注意：id应该是整数，需要验证，如果不是返回400。

现在开始编写代码，注意不要超过1000行，我们尽量简洁。

我们还需要在if __name__ == "__main__"中启动服务器。我们使用`ThreadingHTTPServer`（Python 3.7+）或`HTTPServer` + `ThreadingMixIn`。我们使用`ThreadingHTTPServer`，它在`http.server`模块中。但注意：Python 3.7引入了`ThreadingHTTPServer`。为了兼容更早版本？题目要求Python 3标准库，我们可以使用`HTTPServer` + `ThreadingMixIn`。我们采用`ThreadingMixIn`以确保兼容。

```python
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    pass
```

然后创建服务器，监听127.0.0.1:8080。

我们需要确保数据库文件存在，如果不存在则自动创建表。我们可以在启动时调用一个初始化函数，创建表如果不存在。注意：因为表的创建是DDL，在事务外执行更好。我们可以单独使用一个连接执行CREATE TABLE IF NOT EXISTS。

现在开始编写代码。

注意：使用Python 3标准库，需要导入：
- http.server
- json
- sqlite3
- threading (如果需要锁，但我们可能不需要)
- urllib.parse (用于解析路径，但也可以直接用字符串分割)
- datetime (获取当前时间戳)
- re (可选)

我们将使用time.time()获取当前时间戳。

我们设置数据库文件名为'inventory.db'。

数据库表结构：
```sql
CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    stock_total INTEGER NOT NULL CHECK(stock_total >= 0),
    stock_available INTEGER NOT NULL CHECK(stock_available >= 0)
);
CREATE TABLE IF NOT EXISTS reservations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER NOT NULL REFERENCES items(id),
    quantity INTEGER NOT NULL CHECK(quantity > 0),
    status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending', 'confirmed', 'cancelled', 'expired')),
    expires_at REAL NOT NULL,
    created_at REAL NOT NULL
);
```

我们使用REAL存储Unix时间戳。

在清理过期时，比较expires_at < current_time。

现在开始写代码。我们定义InventoryApp类（Handler）。

我们需要注意：BaseHTTPRequestHandler的do_GET和do_POST方法应该处理请求。它们不会返回异常，所以我们需捕获所有异常并返回500。

我们还需要设置响应头：Content-Type: application/json，以及适当的状态码。

考虑发送响应时，我们可能需要发送字节数据。我们将响应体JSON编码为UTF-8。

我们实现send_json(status, data)：其中data是字典或列表，我们将用json.dumps序列化，然后发送。

对于错误，我们创建包含error字段的字典。

在do_GET中：
- path = self.path
- parsed = urlparse(path)
- path = parsed.path
- 如果path == '/items'或'/items/'，处理list_items，否则返回404。

在do_POST中类似。

但注意：路径可能是/items?something，所以我们应使用parsed.path。

现在具体实现。

在请求处理开始时，我们需要打开数据库连接并执行清理。我们编写一个方法`process_request`，它接受一个函数（处理具体业务），该函数接收连接并返回结果（要发送的数据和状态码）。这样我们可以将清理和事务控制放在公共部分。

但是，我们需要区分读和写？所有操作都需要写（因为清理需要写），所以所有操作都使用写事务。所以我们可以在每个请求处理函数中直接编写代码。

为了减少重复代码，我们可以编写一个上下文管理器或辅助方法`with_db(handler_func)`，它会处理连接、事务、清理、提交/回滚。然后handler_func接收连接并返回(响应数据, 状态码)或抛出异常。

简化：在每个do_GET和do_POST的分支中，我们调用一个函数，该函数内部使用数据库连接。但为了避免重复，我们可以在do_GET和do_POST中统一处理：先创建连接，开始事务，执行清理，然后根据路径调用对应的处理函数，处理函数接收连接并返回结果，如果成功则提交，否则回滚，最后关闭连接。所以我们可以这样：

```python
def do_GET(self):
    try:
        conn = self._get_connection()
        conn.execute("BEGIN IMMEDIATE")
        self._cleanup_expired(conn)
        path = self._parse_path()
        if path == ('items',):
            data = self._list_items(conn)
            self._send_json(200, data)
        else:
            self._send_error(404, "Not found")
        conn.commit()
    except sqlite3.OperationalError as e:
        if 'database is locked' in str(e):
            self._send_error(503, "Service Unavailable: database locked")
        else:
            self._send_error(500, str(e))
    except Exception as e:
        self._send_error(500, str(e))
    finally:
        if conn:
            conn.close()
```

但注意，如果我们捕获到异常，我们需要回滚。而且要注意，如果已经commit或rollback，再close没问题。我们可以使用conn.rollback()在异常时。

但更好的结构：使用try-except-finally，在finally中确保关闭。

对于POST也是类似。

所以我们在Handler中定义一些通用方法。

现在我们编写各个业务函数。

### list_items(conn)
- 执行：`SELECT id, name, stock_total, stock_available FROM items ORDER BY id`
- 返回：列表，每个元素是字典。还要包含id, name, stock_total, stock_available。
- 注意：我们使用`conn.execute`返回cursor，然后获取所有行，然后转换为字典列表。

### create_item(conn, data)
- 参数：data字典，包含name和stock_total。
- 验证：name是字符串且不为空，stock_total是整数且>0，否则返回400。
- 执行插入：`INSERT INTO items (name, stock_total, stock_available) VALUES (?, ?, ?)`，stock_available = stock_total。
- 获取插入的id：`cursor.lastrowid`。
- 然后返回完整商品对象：可以再SELECT一次或直接构造。
- 返回201和商品对象。

### create_reservation(conn, data)
- 参数：data字典，包含item_id, quantity, ttl_seconds。
- 验证：item_id是整数存在，quantity是正整数，ttl_seconds正整数。
- 检查库存：查询items表获取stock_available，确保stock_available >= quantity。如果不够，返回409。
- 计算expires_at = time.time() + ttl_seconds, created_at = time.time()。
- 插入reservation：`INSERT INTO reservations (item_id, quantity, status, expires_at, created_at) VALUES (?, ?, 'pending', ?, ?)`
- 更新库存：`UPDATE items SET stock_available = stock_available - ? WHERE id = ?`（这里我们已经检查过库存足够，减少）。
- 获取插入的预约id，返回预约对象（可以用lastrowid构造部分字段）。
- 注意：库存更新和插入必须在同一事务中。
- 返回201。

### confirm_reservation(conn, reservation_id)
- 验证reservation_id是整数。
- 查找预约：`SELECT id, status, item_id, quantity FROM reservations WHERE id = ?`
- 如果不存在，返回404。
- 如果状态不是'pending'，返回400（错误：只能确认pending的预约）。
- 更新状态为'confirmed'：`UPDATE reservations SET status = 'confirmed' WHERE id = ?`。
- 注意：确认不需要释放库存，也不减少库存（库存已经占用）。
- 返回200和预约对象（包含所有字段）。

### cancel_reservation(conn, reservation_id)
- 类似confirm，但状态必须为'pending'（因为confirmed和cancelled及expired不能取消）。但也可以允许取消confirmed？题目描述“取消预约，释放库存”，但confirmed已经确认，不应再取消？通常确认后不能取消。所以我们规定只能取消pending状态的预约。如果状态为confirmed或其他，返回400或409？返回400冲突。
- 更新状态为'cancelled'。
- 释放库存：`UPDATE items SET stock_available = stock_available + ? WHERE id = ?`。
- 返回200。

### cleanup_expired(conn)
- 执行两个UPDATE：
```sql
UPDATE items SET stock_available = stock_available + COALESCE(
    (SELECT SUM(quantity) FROM reservations WHERE status='pending' AND expires_at < ? AND reservations.item_id = items.id),
0) WHERE id IN (SELECT item_id FROM reservations WHERE status='pending' AND expires_at < ?);
UPDATE reservations SET status='expired' WHERE status='pending' AND expires_at < ?;
```
- 参数是当前时间戳。
- 注意：这两个SQL顺序？先释放库存再更新状态，或者先更新状态再释放库存，顺序无所谓，因为都在同一事务中。但谨慎起见，先释放库存再更新状态，避免瞬间库存被错误释放两次？（不会，因为状态更新后，第一个UPDATE不会再包含这些记录，但我们的第一个UPDATE是独立于状态的？它根据条件status='pending'执行。如果我们先更新库存，此时pending状态还未改变，所以正确。然后更新状态。反过来：如果先更新状态为expired，则第一个UPDATE就选不到这些记录，库存得不到释放。所以必须先释放库存再更新状态。所以顺序重要：先释放库存，再更新状态。但注意，我们的第一个UPDATE使用了IN子句，该子句查询pending and expired的记录，如果先更新状态，IN子句就找不到记录。所以必须先执行库存释放UPDATE，再执行状态更新UPDATE。

但是，两个UPDATE都依赖于status='pending'，所以如果我们先执行库存释放，它看到的是当前pending的记录，没问题。然后更新状态。

所以实现如下：
```python
now = time.time()
conn.execute("""
    UPDATE items SET stock_available = stock_available + COALESCE(
        (SELECT SUM(quantity) FROM reservations WHERE status='pending' AND expires_at < ? AND reservations.item_id = items.id),
    0) WHERE id IN (SELECT item_id FROM reservations WHERE status='pending' AND expires_at < ?)
""", (now, now))
conn.execute("UPDATE reservations SET status='expired' WHERE status='pending' AND expires_at < ?", (now,))
```

但是，这里有一个潜在问题：如果多个商品有多个过期预约，SUM会正确求和。但注意，如果同一个商品有多个过期预约，IN子句会包含商品id一次，然后子查询会计算所有该商品过期预约的quantity总和，再加到stock_available上。所以正确。

我们也可以使用更简单的逐条处理，但这样已经足够。

还可以使用事务内先查询过期预约列表，然后逐条释放，但那样需要循环。SQL方式更高效。

现在考虑并发：两个请求同时执行清理，因为事务隔离，不会重复计算。由于我们使用了IMMEDIATE事务，它们会顺序执行。

我们还需要在项目开始时创建表。我们在模块级别（或在启动前）执行初始化。我们可以在if __name__ == "__main__"中创建一个连接执行建表语句。注意，这个连接不应该与请求连接冲突，但建表是唯一的，可以在开始监听前完成。

现在开始写代码。

我们需要考虑时间戳的精度和时间处理。我们使用time.time()返回浮点数。

我们需要将id解析为整数，使用int()，可能抛出ValueError，返回400。

在读取请求体时，我们使用self.rfile.read(content_length)，注意content_length可能是None，需要处理。如果Content-Length头部缺失，则返回400。

我们还需要处理JSON解析错误，返回400。

现在我们编写Handler类。

类名可以叫`RequestHandler`。

我们定义常量：HOST = '127.0.0.1', PORT = 8080, DB_FILE = 'inventory.db'。

在do_GET和do_POST中，我们按照上述结构。

现在考虑可维护性。我们可以将路径解析函数提取出来，返回一个元组或枚举。

我打算使用简单分割：

```python
def parse_path(self):
    parsed = urlparse(self.path)
    path = parsed.path.rstrip('/')  # 去掉尾部斜杠
    if not path:
        return []  # 根路径，但我们的API没有根
    parts = path.split('/')[1:]  # 去掉第一个空字符串
    return parts
```

然后根据parts列表进行匹配。

对于GET：
- parts == ['items'] => list_items

对于POST：
- parts == ['items'] => create_item
- parts == ['reservations'] => create_reservation
- len(parts) == 3 and parts[0] == 'reservations' and parts[2] == 'confirm' => confirm_reservation(parts[1])
- len(parts) == 3 and parts[0] == 'reservations' and parts[2] == 'cancel' => cancel_reservation(parts[1])
- else => 404

现在实现各个业务函数。

我们还有一个重要的细节：在create_reservation中，我们检查库存并更新库存。这里有一个潜在的竞态：如果我们先查询库存，然后更新，但如果在事务中，且事务是IMMEDIATE，其他写事务会等待，所以安全。但如果我们查询库存时使用了普通的SELECT，它也会在事务中，由于IMMEDIATE事务，它获取了写锁，其他事务等待，所以安全。但为了更保险，我们可以在查询库存时使用`SELECT stock_available FROM items WHERE id = ?`，然后检查条件，然后执行UPDATE扣减。由于事务隔离，没有问题。

但是，更好的做法是使用原子操作：`UPDATE items SET stock_available = stock_available - ? WHERE id = ? AND stock_available >= ?`，然后检查受影响的行数。如果为0，则库存不足。这样就不需要先SELECT再UPDATE，避免了间隙。这更健壮。我们采用这种方法。

对于创建预约：
1. 扣减库存：`UPDATE items SET stock_available = stock_available - ? WHERE id = ? AND stock_available >= ?`。如果rowcount == 0，则库存不足，回滚事务并返回409。
2. 插入预约记录。
注意：如果扣减库存成功，但插入预约失败，则事务回滚，库存自动恢复。所以没问题。

这样我们避免了检查库存的单独SELECT，而且保证了原子性。

对于取消预约：我们需要释放库存。先更新预约状态为cancelled，然后释放库存。但要注意：释放库存时，我们应该确保预约状态是pending。如果状态已被其他事务改变，我们的UPDATE可能影响0行。所以我们可以先UPDATE reservations SET status='cancelled' WHERE id=? AND status='pending'，检查rowcount，如果为0，则返回错误（可能不存在或状态不允许）。然后，如果成功，再释放库存。但释放库存应该基于预约的quantity，我们需要知道quantity。我们可以在第一个UPDATE时使用RETURNING？SQLite 3.35+支持RETURNING子句，但为了兼容，我们可以先查询quantity。但查询和更新之间可能有其他事务？既然我们在事务中，且使用了IMMEDIATE，安全。我们可以先SELECT quantity, item_id, status FROM reservations WHERE id=?，如果不存在或status不是'pending'，返回错误。然后执行UPDATE更新状态，然后UPDATE items释放库存。因为查询和更新在同一事务，安全。

对于confirm，类似，只需要检查状态并更新，不需要释放库存。

对于清理：我们使用按条件UPDATE。

现在开始实现细节。

先写init_db():

```python
def init_db():
    conn = sqlite3.connect(DB_FILE, timeout=5)
    conn.execute("PRAGMA journal_mode=WAL")  # 提高并发性能，可选
    conn.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            stock_total INTEGER NOT NULL CHECK(stock_total >= 0),
            stock_available INTEGER NOT NULL CHECK(stock_available >= 0)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS reservations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER NOT NULL REFERENCES items(id),
            quantity INTEGER NOT NULL CHECK(quantity > 0),
            status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending', 'confirmed', 'cancelled', 'expired')),
            expires_at REAL NOT NULL,
            created_at REAL NOT NULL
        )
    """)
    conn.commit()
    conn.close()
```

我们可以在启动时调用。注意：如果使用WAL模式，可以提高并发性能，因为读操作不会阻塞写操作，写操作可以并发一个读取者。但我们的写操作使用了IMMEDIATE事务，会获取写锁，可能还是会影响。但WAL模式允许并发读取。所以建议开启。

在请求连接中，我们也可以设置PRAGMA busy_timeout，但我们在连接时已经设置了timeout参数，所以不需要。但可以显式设置。

在我们的连接创建中，我们使用timeout=5。但还需要设置PRAGMA busy_timeout来让等待发生在SQLite层面。timeout参数实际上对应于PRAGMA busy_timeout？文档：`sqlite3.connect`的timeout参数指定连接等待锁的超时时间（秒），内部会设置PRAGMA busy_timeout。所以设置timeout=5等同于设置busy_timeout=5000。所以可以。

在我们的连接中，我们设置isolation_level=None，然后在每次请求时执行BEGIN IMMEDIATE。但注意：如果我们没有开始事务，执行任何SQL都会自动提交。但我们在请求开始时执行BEGIN IMMEDIATE，如果此时数据库被锁定，BEGIN会等待timeout秒，如果超时则抛出OperationalError。所以我们需要捕获此异常，返回503。

在业务函数中，我们可能会遇到其他数据库错误，比如约束错误（CHECK约束失败），但我们已经验证输入，所以应该不会出现。但可以统一捕获。

现在开始编写Handler代码。我们将所有业务函数定义为Handler的方法，从而可以访问self以便发送响应。但也可以将数据库操作提取为独立函数，接受连接并返回数据。

为了清晰，我将业务函数定义为Handler的方法，它们接收conn，并返回一个元组(status_code, response_data)。或者直接发送响应。但为了统一错误处理，可以在这些函数中抛出自定义异常？或者返回错误信息。我将在每个函数中完成所有操作，如果出错，发送错误响应并返回。但为了统一事务，我们可能需要在错误时回滚。所以最好让这些函数返回响应数据或触发异常。我们可以定义一个异常类AppError，包含状态码和消息。然后在顶层捕获，回滚并发送错误。这种方式更优雅。

可以使用最外层try-except，如果业务函数中检测到错误（如库存不足），可以raise AppError(409, "Insufficient stock")。然后顶层捕获，回滚，发送错误。

为此，定义AppError(HTTPException):

```python
class AppError(Exception):
    def __init__(self, status_code, message):
        self.status_code = status_code
        self.message = message
```

然后在业务函数中，如果发现问题，raise AppError。

在顶层，我们捕获AppError，回滚，发送错误。对于其他异常，也捕获，回滚并返回500。

但我们需要在业务函数中获取当前连接以执行SQL，所以连接需要传入。同时，业务函数需要访问请求体数据。所以我们可以将数据作为参数传入。

整体流程：

在do_GET或do_POST中:
```python
def do_GET(self):
    try:
        conn = self._get_connection()
        conn.execute("BEGIN IMMEDIATE")
        self._cleanup_expired(conn)
        parts = self._parse_path()
        if parts == ['items']:
            result = self._list_items(conn)
            self._send_json(200, result)
        else:
            raise AppError(404, "Not found")
        conn.commit()
    except AppError as e:
        if conn:
            conn.rollback()
        self._send_error(e.status_code, e.message)
    except sqlite3.OperationalError as e:
        if conn:
            conn.rollback()
        if 'database is locked' in str(e):
            self._send_error(503, "Service Unavailable: database locked")
        else:
            self._send_error(500, f"Database error: {str(e)}")
    except Exception as e:
        if conn:
            conn.rollback()
        self._send_error(500, f"Internal server error: {str(e)}")
    finally:
        if conn:
            conn.close()
```

但注意，在AppError时，我们需要回滚；在OperationalError时，可能连接已处于回滚状态？但捕获OperationalError时，可能事务已经失败，但我们可以rollback确保。需要小心：如果BEGIN IMMEDIATE失败，连接可能没有开始事务，但执行rollback可能会报错？但rollback在没有事务时可能没问题？sqlite3的rollback在没有事务时不会报错。所以安全。

我们还需要处理在发送响应后，不应该再对连接进行操作。所以顺序是先处理完数据库操作，再发送响应，再提交？我们目前是先处理数据库操作，得到结果，然后发送响应，然后提交。如果发送响应失败，事务可能未提交，但已经发送了响应，以后续请求可能看到未提交的数据。但可以通过在发送响应前提交。最优是：先提交事务，然后发送响应。但提交可能失败，此时响应应反映失败。所以较好顺序：完成业务计算，然后提交事务，然后发送成功响应。如果提交失败，回滚，发送错误响应。所以我们需要将提交放在try块内，但放在发送响应之前。但发送响应可能会抛出异常？通常不会。所以我们可以：

```python
try:
    conn = ...
    conn.execute("BEGIN IMMEDIATE")
    cleanup
    result = business_logic(conn)
    conn.commit()
    self._send_json(200, result)
except AppError as e:
    conn.rollback()
    self._send_error(e.status_code, e.message)
except ...
finally:
    conn.close()
```

这样提交成功后再发送响应。但对于业务逻辑中可能已经修改了数据库，但我们在发送响应前提交，如果提交失败，回滚，发送错误。这样客户端不会看到不存在的提交。但是，如果业务逻辑已经发送了响应（比如在函数中直接发送了响应），则可能无法回滚。所以我们最好只在顶层发送响应。

现在编写业务函数，它们返回结果数据（字典或列表），而不是发送响应。然后由do_方法发送。

对于list_items，返回商品列表。

对于create_item，返回新商品对象。

对于create_reservation，返回新预约对象。

对于confirm_reservation，返回预约对象。

对于cancel_reservation，返回预约对象。

所以这些函数签名：传入conn，可能还有附加参数（id或数据），返回响应数据。

现在我们考虑输入验证。在create_item和create_reservation中，我们需要从请求体读取JSON。我们可以在do_POST中先读取并解析JSON，然后传递给业务函数。如果解析失败，返回400。我们可以在do_POST中统一读取JSON，然后根据路径分发。但注意，confirm和cancel不需要请求体，所以不需要读取。

所以我们在do_POST中，先读取请求体，然后根据路径判断是否需要JSON。对于items和reservations需要，对于confirm/cancel不需要。

因此，在do_POST中，我们先解析路径，如果路径是需要JSON的，则读取并解析JSON；否则保持data为None。

我们还需要验证请求方法是否为POST，但显然do_POST只处理POST。

现在开始写代码。

为了代码简洁，我可能会使用一些结构。

由于总代码不能超过1000行，我们可以比较宽松。但也要注意不要过于啰嗦。

我将编写以下函数：
- _get_connection(): 返回新连接。
- _parse_path(): 返回路径部分列表。
- _cleanup_expired(conn): 清理过期预约。
- _read_json_body(): 读取并解析JSON，返回字典或None。
- _send_json(status, data): 发送JSON响应。
- _send_error(status, message): 发送错误响应。
- _get_int_param(value): 将字符串转为int，如果失败返回None或抛出。

业务方法：
- _list_items(conn)
- _create_item(conn, data)
- _create_reservation(conn, data)
- _confirm_reservation(conn, reservation_id)
- _cancel_reservation(conn, reservation_id)

同时，我们需要在do_GET和do_POST中调用。

现在，开始编码。注意：我们要确保数据库操作使用参数化查询，避免SQL注入。

为了避免重复，我们将db_lock定义？但我们已经通过IMMEDIATE事务和timeout实现并发控制，不需要额外锁。但是，如果我们在多个线程中同时打开连接并执行BEGIN IMMEDIATE，SQLite会通过锁机制让其中一个获得锁，其他的等待timeout。所以没问题。

但是，如果我们在清理时，有些连接可能正在等待，但最终会执行。所以不需要应用层锁。

但有一个潜在问题：如果两个请求同时对同一个商品进行创建预约和取消，取消释放库存，创建预约扣减库存，因为事务串行，所以库存一致。

所以不需要全局锁。

但为了安全，我们可以使用。不过更好的做法是不用，依赖数据库锁。

但是，Python的sqlite3默认情况下，多个连接写操作可能会产生deadlock？不会，SQLite使用文件锁，不会死锁。

所以我们可以。

现在，我们开始写代码。

在写代码之前，考虑一下是否需要创建索引？不需要，数据量小。

现在写。

注意：在`_create_item`中，我们要验证stock_total的类型。data.get('stock_total')可能是字符串，但我们应该将其转换为int。如果转换失败或不是正整数，返回400。

同样，quantity应该是正整数。

我们还需要确保item_id存在，我们可以先检查items表中是否有对应id，如果不存在，返回404（或400）。对于create_reservation，item_id应该引用存在的商品。我们可以在扣减库存前先检查商品是否存在，但既然我们使用UPDATE扣减，如果商品不存在，UPDATE会影响0行，但我们无法区分是库存不足还是商品不存在。所以我们最好先检查商品是否存在，如果不存在返回404。如果存在但库存不足，返回409。所以我们可以先SELECT items获取stock_available? 还是使用UPDATE? 我们可以使用两个语句：先SELECT检查存在性和库存量？但这样有竞态。更好的方法是使用一个UPDATE带条件，但无法处理商品不存在的情况。我们可以先检查存在性：`SELECT id FROM items WHERE id = ?`，如果返回None，则raise AppError(404, "Item not found")。然后检查库存是否充足（通过查询或使用UPDATE）。我们可以先查询，然后扣减。因为事务是序列化的，所以安全。为了代码清晰，我们这样做：

1. 查询商品：`SELECT id, stock_available FROM items WHERE id = ?`，如果不存在，raise 404。
2. 检查stock_available >= quantity，如果不满足，raise 409。
3. 执行UPDATE扣减库存。
4. 插入预约。

虽然在检查和扣减之间有微小间隙，但在IMMEDIATE事务中，没有其他写事务能插入，所以安全。但严格来说，使用一个UPDATE带条件是更好的避免竞争的做法。我们也可以使用UPDATE扣减条件检查stock_available >= quantity，如果rowcount为0，则要么库存不足要么商品不存在。但我们可以先检查存在性然后使用UPDATE。如果我们先检查存在性，但库存可能在检查后变化（尽管因为事务序列化，不会变化）。所以没问题。为了更保险，我们采用先检查存在性，再使用UPDATE条件扣减，即使检查后库存变化（但不可能因为事务隔离），所以没问题。

我决定使用：先SELECT查询商品存在性和当前库存，如果库存不足则raise 409；然后UPDATE扣减库存（UPDATE items SET stock_available = stock_available - ? WHERE id=? AND stock_available >= ?）。虽然此时条件仍然成立，但可以省略AND部分，因为我们确认库存充足。但为了安全，还是加上。然后检查rowcount，如果为0，说明并发问题，但事务序列化不会发生，所以可以忽略。但保留。

对于cancel：先SELECT预约，检查状态是否为pending，如果不存在或不是pending则raise；然后UPDATE reservations SET status='cancelled' WHERE id=? AND status='pending'；如果rowcount==0，说明并发修改，raise；然后UPDATE items释放库存。

对于confirm：类似，不释放库存。

对于清理：采用之前的两条UPDATE。

现在，我们开始写代码。

计划写一个完整的代码。

现在开始正式编码。我会在代码中增加注释以帮助理解，但注释不计入行数？我们需要确保总代码不超过1000行。代码可以包括注释，但最好保持简洁。

考虑到600-800行应该足够。

我们从import开始。

导入必要的模块：

```python
import json
import sqlite3
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from urllib.parse import urlparse
```

但我们可以不使用threading模块。

我们还可以导入os用于路径操作？不需要。

然后定义AppError。

定义配置变量。

定义连接函数。

定义Handler。

在if __name__ == "__main__"中，初始化数据库，启动服务器。

注意：我们需要确保在请求处理中，我们使用`self.send_response(status_code)`，`self.send_header('Content-Type', 'application/json')`，`self.end_headers()`，然后发送数据。

我们还需要处理HTTP版本？BaseHTTPRequestHandler会自动处理。

在发送错误时，我们也使用相同的方法。

我们实现`_send_json`:

```python
def _send_json(self, status, data):
    body = json.dumps(data, ensure_ascii=False).encode('utf-8')
    self.send_response(status)
    self.send_header('Content-Type', 'application/json')
    self.send_header('Content-Length', str(len(body)))
    self.end_headers()
    self.wfile.write(body)
```

类似地，`_send_error(status, message)`:

```python
def _send_error(self, status, message):
    self._send_json(status, {'error': message})
```

注意：在发送错误响应时，我们可能需要记录日志，但我们不实现。

现在我们开始编写do_GET和do_POST。我们将共享部分逻辑抽取为`_handle_request`方法，它接受一个处理函数。但为简单，我们分开写。

但注意，在do_GET和do_POST中，处理流程相同，除了路径分发的业务函数。我们可以写一个通用方法`_process(self, method)`，在其中打开连接，执行清理，根据路径和方法调用对应的函数。但GET和POST有不同的业务映射。我们可以将路径匹配结果和需要调用的函数存储在一个字典中，但不确定。

另一种：在do_GET和do_POST中直接写逻辑。

由于代码行数限制，我们尽量简洁。

我们定义`_get_connection`:

```python
def _get_connection(self):
    conn = sqlite3.connect(DB_FILE, timeout=5, isolation_level=None)
    conn.execute("PRAGMA journal_mode=WAL")  # 可选，但需要每次设置吗？WAL模式已经启用，但PRAGMA可以重复设置，无害。但通常只需设置一次。我们可以不在每个连接设置，因为数据库已经设置为WAL。但第一个连接设置后，数据库文件记录WAL模式，后续连接自动使用。所以我们可以省略。但安全起见，可以设置。
    return conn
```

但注意：在每个连接设置PRAGMA journal_mode=WAL可能无效，因为模式是数据库级别的，只能更改一次。已经在init_db中设置，此处可以省略。

所以我们可以直接返回连接。

现在编写业务函数。

在业务函数中，我们使用conn.execute和conn.cursor()。我们尽量直接使用conn.execute返回cursor，然后cursor.fetchone()等。

注意：在`_list_items`中，我们返回一个列表，每个元素是字典，包含id, name, stock_total, stock_available。

我们可以使用cursor.description获取列名，然后构造字典。但为了简单，我们可以硬编码列名。

例如：
```python
def _list_items(self, conn):
    cursor = conn.execute("SELECT id, name, stock_total, stock_available FROM items ORDER BY id")
    rows = cursor.fetchall()
    items = []
    for row in rows:
        items.append({
            'id': row[0],
            'name': row[1],
            'stock_total': row[2],
            'stock_available': row[3]
        })
    return {'items': items}
```

或者直接返回列表，但要求没有明确格式，我们可以返回字典包含items数组。为了有好的结构，我们返回{"items": items}。

类似地，对于单个资源，我们返回一个对象（字典）。

对于`_create_item`:
```python
def _create_item(self, conn, data):
    name = data.get('name')
    stock_total = data.get('stock_total')
    if not name or not isinstance(name, str):
        raise AppError(400, "Invalid or missing 'name'")
    if stock_total is None or not isinstance(stock_total, int) or stock_total <= 0:
        raise AppError(400, "Invalid or missing 'stock_total', must be positive integer")
    cursor = conn.execute("INSERT INTO items (name, stock_total, stock_available) VALUES (?, ?, ?)",
                          (name, stock_total, stock_total))
    item_id = cursor.lastrowid
    return {
        'id': item_id,
        'name': name,
        'stock_total': stock_total,
        'stock_available': stock_total
    }
```

注意：如果stock_total是字符串但可转换为整数，我们使用int()转换？但用户可能发送字符串"5"，我们应处理。更好的做法：尝试转换。我们允许int和float？最好只接受整数。我们可以使用`isinstance(stock_total, int)`或通过int()转换并捕获错误。我们采用`stock_total = int(stock_total)`如果输入是float/string，但要确保整数。我们检查类型：如果输入是int，直接用；如果是str且是数字，转换；如果不行返回400。但方便起见，我们要求输入必须是整数类型，但HTTP JSON可以是数字，Python解析后可能是int或float。我们检查`isinstance(stock_total, int) and not isinstance(stock_total, bool)`，并且`stock_total > 0`。如果stock_total是float，则拒绝。这样可以简化。或者我们接受float但只取整数值？为了严谨，我们要求正整数。

同样，对于quantity。

对于`_create_reservation`:
```python
def _create_reservation(self, conn, data):
    item_id = data.get('item_id')
    quantity = data.get('quantity')
    ttl_seconds = data.get('ttl_seconds')
    # 验证
    if not isinstance(item_id, int) or item_id <= 0:
        raise AppError(400, "Invalid or missing 'item_id'")
    if not isinstance(quantity, int) or quantity <= 0:
        raise AppError(400, "Invalid or missing 'quantity', must be positive integer")
    if not isinstance(ttl_seconds, int) or ttl_seconds <= 0:
        raise AppError(400, "Invalid or missing 'ttl_seconds', must be positive integer")
    # 检查商品存在性和库存
    cursor = conn.execute("SELECT id, stock_available FROM items WHERE id = ?", (item_id,))
    row = cursor.fetchone()
    if row is None:
        raise AppError(404, "Item not found")
    stock_available = row[1]
    if stock_available < quantity:
        raise AppError(409, "Insufficient stock")
    # 扣减库存（原子更新）
    now = time.time()
    expires_at = now + ttl_seconds
    # 更新库存（条件检查防止并发）
    cursor = conn.execute("UPDATE items SET stock_available = stock_available - ? WHERE id = ? AND stock_available >= ?",
                          (quantity, item_id, quantity))
    if cursor.rowcount == 0:
        # 理论上在事务中不会发生，但以防万一
        raise AppError(409, "Insufficient stock")
    # 插入预约
    cursor = conn.execute("""
        INSERT INTO reservations (item_id, quantity, status, expires_at, created_at)
        VALUES (?, ?, 'pending', ?, ?)
    """, (item_id, quantity, expires_at, now))
    res_id = cursor.lastrowid
    return {
        'id': res_id,
        'item_id': item_id,
        'quantity': quantity,
        'status': 'pending',
        'expires_at': expires_at,
        'created_at': now
    }
```

注意：我们使用了先检查库存然后扣减，但检查到扣减之间可能库存被其他事务减少？但事务IMMEDIATE保证不会。但是，如果我们使用两个事务，有可能。所以更健壮的方法是仅使用UPDATE带条件，而不单独检查。我们可以省略检查，直接更新并检查rowcount。如果rowcount为0，则库存不足（或商品不存在）。然后我们再检查商品是否存在以区分。所以更好的方法是：

```python
# 先检查商品存在性
cursor = conn.execute("SELECT id FROM items WHERE id = ?", (item_id,))
if cursor.fetchone() is None:
    raise AppError(404, "Item not found")
# 尝试扣减库存（原子）
cursor = conn.execute("UPDATE items SET stock_available = stock_available - ? WHERE id = ? AND stock_available >= ?",
                      (quantity, item_id, quantity))
if cursor.rowcount == 0:
    raise AppError(409, "Insufficient stock")
# 插入预约
```

这样不需要先查询库存，更安全。我们采用这种方法。

所以更新代码。

对于`_confirm_reservation`:
```python
def _confirm_reservation(self, conn, res_id):
    # 检查预约
    cursor = conn.execute("SELECT id, item_id, quantity, status FROM reservations WHERE id = ?", (res_id,))
    row = cursor.fetchone()
    if row is None:
        raise AppError(404, "Reservation not found")
    if row[3] != 'pending':
        raise AppError(400, f"Reservation status is '{row[3]}', expected 'pending'")
    # 更新状态
    conn.execute("UPDATE reservations SET status = 'confirmed' WHERE id = ?", (res_id,))
    # 返回更新后的预约（或直接构造）
    # 可以再次查询返回完整信息
    cursor = conn.execute("SELECT id, item_id, quantity, status, expires_at, created_at FROM reservations WHERE id = ?", (res_id,))
    row = cursor.fetchone()
    return {
        'id': row[0],
        'item_id': row[1],
        'quantity': row[2],
        'status': row[3],
        'expires_at': row[4],
        'created_at': row[5]
    }
```

对于`_cancel_reservation`:
```python
def _cancel_reservation(self, conn, res_id):
    # 检查预约
    cursor = conn.execute("SELECT id, item_id, quantity, status FROM reservations WHERE id = ?", (res_id,))
    row = cursor.fetchone()
    if row is None:
        raise AppError(404, "Reservation not found")
    if row[3] != 'pending':
        raise AppError(400, f"Reservation status is '{row[3]}', expected 'pending'")
    # 更新状态为cancelled
    conn.execute("UPDATE reservations SET status = 'cancelled' WHERE id = ? AND status = 'pending'", (res_id,))
    # 释放库存
    conn.execute("UPDATE items SET stock_available = stock_available + ? WHERE id = ?", (row[2], row[1]))
    # 返回预约
    cursor = conn.execute("SELECT id, item_id, quantity, status, expires_at, created_at FROM reservations WHERE id = ?", (res_id,))
    row2 = cursor.fetchone()
    return {
        'id': row2[0],
        'item_id': row2[1],
        'quantity': row2[2],
        'status': row2[3],
        'expires_at': row2[4],
        'created_at': row2[5]
    }
```

注意：在释放库存时，我们使用row[2]（quantity）和row[1]（item_id）。因为我们已经在前面检查了状态，所以应该安全。

对于清理`_cleanup_expired`:
```python
def _cleanup_expired(self, conn):
    now = time.time()
    # 释放过期预约的库存
    conn.execute("""
        UPDATE items SET stock_available = stock_available + COALESCE(
            (SELECT SUM(quantity) FROM reservations WHERE status='pending' AND expires_at < ? AND reservations.item_id = items.id),
        0) WHERE id IN (SELECT item_id FROM reservations WHERE status='pending' AND expires_at < ?)
    """, (now, now))
    # 将过期预约状态更新为expired
    conn.execute("UPDATE reservations SET status='expired' WHERE status='pending' AND expires_at < ?", (now,))
```

注意：这里可能更新多行。没有返回。

现在，我们需要在do_GET和do_POST中调用这些函数，并处理事务。

我们还需要读取请求体。我们实现`_read_json_body`:
```python
def _read_json_body(self):
    content_length = int(self.headers.get('Content-Length', 0))
    if content_length == 0:
        raise AppError(400, "Request body is empty")
    body = self.rfile.read(content_length)
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        raise AppError(400, "Invalid JSON")
    if not isinstance(data, dict):
        raise AppError(400, "JSON body must be an object")
    return data
```

注意：如果Content-Length缺失，我们可以设为0，读取body可能为空。但严格检查。

对于POST /items和/reservations，我们需要读取JSON。对于confirm和cancel，不需要。所以我们仅在必要时调用_read_json_body。

在do_POST中，我们先解析路径，然后根据路径决定是否读取JSON。

代码结构：

```python
def do_POST(self):
    conn = None
    try:
        conn = self._get_connection()
        conn.execute("BEGIN IMMEDIATE")
        self._cleanup_expired(conn)
        parts = self._parse_path()
        if parts == ['items']:
            data = self._read_json_body()
            result = self._create_item(conn, data)
            conn.commit()
            self._send_json(201, result)
        elif parts == ['reservations']:
            data = self._read_json_body()
            result = self._create_reservation(conn, data)
            conn.commit()
            self._send_json(201, result)
        elif len(parts) == 3 and parts[0] == 'reservations' and parts[2] == 'confirm':
            try:
                res_id = int(parts[1])
            except ValueError:
                raise AppError(400, "Invalid reservation ID")
            result = self._confirm_reservation(conn, res_id)
            conn.commit()
            self._send_json(200, result)
        elif len(parts) == 3 and parts[0] == 'reservations' and parts[2] == 'cancel':
            try:
                res_id = int(parts[1])
            except ValueError:
                raise AppError(400, "Invalid reservation ID")
            result = self._cancel_reservation(conn, res_id)
            conn.commit()
            self._send_json(200, result)
        else:
            raise AppError(404, "Not found")
    except AppError as e:
        if conn:
            try:
                conn.rollback()
            except:
                pass
        self._send_error(e.status_code, e.message)
    except sqlite3.OperationalError as e:
        if conn:
            try:
                conn.rollback()
            except:
                pass
        if 'database is locked' in str(e):
            self._send_error(503, "Service Unavailable: database locked")
        else:
            self._send_error(500, f"Database error: {str(e)}")
    except Exception as e:
        if conn:
            try:
                conn.rollback()
            except:
                pass
        self._send_error(500, f"Internal server error: {str(e)}")
    finally:
        if conn:
            conn.close()
```

同样，do_GET类似。

对于GET，不需要读取JSON体。

```python
def do_GET(self):
    conn = None
    try:
        conn = self._get_connection()
        conn.execute("BEGIN IMMEDIATE")
        self._cleanup_expired(conn)
        parts = self._parse_path()
        if parts == ['items']:
            result = self._list_items(conn)
            conn.commit()
            self._send_json(200, result)
        else:
            raise AppError(404, "Not found")
    except AppError as e:
        if conn:
            try:
                conn.rollback()
            except:
                pass
        self._send_error(e.status_code, e.message)
    except sqlite3.OperationalError as e:
        if conn:
            try:
                conn.rollback()
            except:
                pass
        if 'database is locked' in str(e):
            self._send_error(503, "Service Unavailable: database locked")
        else:
            self._send_error(500, f"Database error: {str(e)}")
    except Exception as e:
        if conn:
            try:
                conn.rollback()
            except:
                pass
        self._send_error(500, f"Internal server error: {str(e)}")
    finally:
        if conn:
            conn.close()
```

注意到重复的异常处理代码。我们可以抽取一个公共方法`_execute_with_handling(self, func)`，但func需要处理conn。不过我们可以将公共部分提取为一个上下文管理器或装饰器。但为了不超过1000行，重复代码可接受。我们也可以写一个辅助函数来处理连接和错误，但我们需要访问self来发送响应。我们可以写一个方法`_run_in_transaction(self, handler)`，其中handler接收conn并返回(状态码, 数据)或直接发送响应？我们让它返回状态码和数据，然后发送响应。这样可以减少重复。我们尝试实现。

```python
def _run_in_transaction(self, handler):
    conn = None
    try:
        conn = self._get_connection()
        conn.execute("BEGIN IMMEDIATE")
        self._cleanup_expired(conn)
        status, result = handler(conn)
        conn.commit()
        self._send_json(status, result)
    except AppError as e:
        if conn:
            try:
                conn.rollback()
            except:
                pass
        self._send_error(e.status_code, e.message)
    except sqlite3.OperationalError as e:
        if conn:
            try:
                conn.rollback()
            except:
                pass
        if 'database is locked' in str(e):
            self._send_error(503, "Service Unavailable: database locked")
        else:
            self._send_error(500, f"Database error: {str(e)}")
    except Exception as e:
        if conn:
            try:
                conn.rollback()
            except:
                pass
        self._send_error(500, f"Internal server error: {str(e)}")
    finally:
        if conn:
            conn.close()
```

然后do_GET和do_POST可以调用`_run_in_transaction`，传入一个lambda或函数。例如：

```python
def do_GET(self):
    parts = self._parse_path()
    if parts == ['items']:
        self._run_in_transaction(lambda conn: (200, self._list_items(conn)))
    else:
        self._send_error(404, "Not found")
```

但这样，如果路径不匹配，我们不需要事务，所以直接在外部处理404。注意，404响应直接发送，不需要事务和清理。但按照要求，每次请求前需要清理，包括404响应吗？要求是“每次请求前清理”，所以即使返回404，也应该执行清理。但我们的做法中，如果路径不匹配，我们直接返回404，没有执行清理。所以我们需要在返回非匹配路径时也执行清理。但为了简化，我们可以对所有请求（包括404）都执行清理，但404本身不需要修改数据库。但既然清理可能修改数据库，我们应该执行。所以最好将所有请求都经过`_run_in_transaction`，但404应答不需要数据库操作，但可以在事务内什么都不做。所以在`_run_in_transaction`中，我们调用handler，handler可以决定返回404。所以我们可以将路径匹配和业务逻辑都放在handler内。也就是说，在`_run_in_transaction`内部，handler根据路径判断。但handler已经接收conn，我们需要将path等传递进去。我们可以使用闭包。更好的方法：在do_GET中，我们调用一个统一方法`_handle_request`，它接收conn，在其中解析路径。或者我们可以将整个请求处理逻辑放在一个函数中，该函数接收conn并返回(状态, 数据)。例如，对于GET：

```python
def _do_get_logic(self, conn):
    parts = self._parse_path()
    if parts == ['items']:
        return 200, self._list_items(conn)
    else:
        raise AppError(404, "Not found")
```

然后在do_GET中调用`_run_in_transaction(self._do_get_logic)`，但方法绑定需要处理。我们可以写：

```python
def do_GET(self):
    self._run_in_transaction(self._get_handler_for_get)
```

但这样，_get_handler_for_get必须是接收conn并返回(status, data)的方法。我们可以在`_run_in_transaction`中调用handler(conn)。所以我们为GET和POST分别定义处理函数。

例如：

```python
def _handle_get(self, conn):
    parts = self._parse_path()
    if parts == ['items']:
        return 200, self._list_items(conn)
    else:
        raise AppError(404, "Not found")
```

然后do_GET: `self._run_in_transaction(self._handle_get)`

类似地，_handle_post。

这样，我们可以重用`_run_in_transaction`，减少了重复代码。而且所有请求都会经过事务和清理，包括404（在_handle_get中raise AppError，在_run_in_transaction中捕获并发送错误，同时回滚事务）。但是，对于404，我们没有进行任何写操作，但事务中包含了清理操作，所以清理操作会被提交（因为我们在捕获异常前没有提交？但在_run_in_transaction中，如果handler抛出AppError，我们会回滚事务，清理操作也会被回滚！这不符合要求：我们希望清理操作即使请求失败也生效。因为清理操作是维护系统状态，应该独立于请求成功与否。例如，如果用户请求了一个不存在的路径，我们仍然希望清理过期的预约。所以清理操作不应该被回滚。所以我们需要将清理操作在事务中执行，但即使后续业务失败，清理也应该提交。这意味着清理应该在业务事务之外执行，或者我们应在业务事务中先提交清理，再开启新事务执行业务。或者我们可以在业务事务中，先执行清理，然后如果业务失败，我们回滚事务，但清理也会被回滚，这不好。所以需要重新考虑。

正确的做法是：清理操作是独立的，应该在每个请求开始时执行，并且即使请求处理失败，清理也应该生效。所以我们应该在业务事务之前先执行一个独立的清理事务，然后再开始业务事务。这样清理操作被持久化，不影响后续业务事务的回滚。或者我们可以在一个事务中完成清理和业务，如果业务失败，我们仍然提交清理？但是事务必须回滚整个事务，所以无法保留清理。所以我们必须将清理作为单独的事务提前执行。

所以设计：在每个请求中，我们先打开一个连接，执行一个独立的事务执行清理（只做清理），提交关闭。然后我们再打开另一个连接（或相同连接）开始业务事务，处理请求。但这样需要两个连接，或者可以用同一个连接顺序执行两个事务。我们可以先执行清理事务（自动提交），再执行业务事务（手动控制）。我们可以使用isolation_level=None，然后执行清理语句（自动提交），然后再开始IMEMDIATE事务执行业务。但注意，清理语句也需要在事务中？如果使用自动提交，每个语句独立提交，那么清理的UPDATE可能不是原子的，但两条UPDATE之间如果服务器崩溃，可能造成不一致（如库存释放了但状态未更新）。但考虑到我们使用WAL，自动提交的每个语句都是原子提交的。两条语句不是原子，但应该问题不大：如果第一条成功，第二条失败，下次清理会处理剩余的（因为过期预约状态还是pending，但库存已经加了，会导致重复释放）。所以我们需要原子性。所以清理也应在一个事务中完成。所以最好在清理时使用一个事务，提交后，再开始一个新事务。

因此，我们可以使用同一个连接，先执行清理事务（使用`BEGIN IMMEDIATE`，然后执行清理语句，提交），然后再执行业务事务（再次`BEGIN IMMEDIATE`，执行操作）。但是，如果业务事务失败回滚，清理事务已经提交，不受影响。所以这是合理的。

所以我们的流程变为：
1. 打开连接。
2. 开始一个事务（IMMEDIATE），执行清理，提交。
3. 开始另一个事务（IMMEDIATE），执行业务逻辑，提交或回滚。
4. 关闭连接。

注意：如果清理事务失败，则整个请求失败。

我们可以将清理和业务分开步骤，都在同一个连接中，但使用两个独立的事务。

所以`_run_in_transaction`应修改为：先清理（单独事务），然后执行业务（单独事务）。但注意，如果业务抛出AppError，我们需要回滚业务事务，但清理事务已经提交，不需要回滚。

因此实现：

```python
def _run_in_transaction(self, handler):
    conn = None
    try:
        conn = self._get_connection()
        # 清理事务
        conn.execute("BEGIN IMMEDIATE")
        self._cleanup_expired(conn)
        conn.commit()
        # 业务事务
        conn.execute("BEGIN IMMEDIATE")
        status, result = handler(conn)
        conn.commit()
        self._send_json(status, result)
    except AppError as e:
        if conn:
            try:
                conn.rollback()  # 回滚业务事务（如果已开始），如果清理后业务开始前发生异常，rollback无害
            except:
                pass
        self._send_error(e.status_code, e.message)
    except sqlite3.OperationalError as e:
        if conn:
            try:
                conn.rollback()
            except:
                pass
        if 'database is locked' in str(e):
            self._send_error(503, "Service Unavailable: database locked")
        else:
            self._send_error(500, f"Database error: {str(e)}")
    except Exception as e:
        if conn:
            try:
                conn.rollback()
            except:
                pass
        self._send_error(500, f"Internal server error: {str(e)}")
    finally:
        if conn:
            conn.close()
```

注意：如果在清理事务中发生异常，捕获并返回错误；如果业务事务中发生异常，捕获并返回错误，此时清理事务已经提交，没问题。

但是，如果清理事务成功，但业务事务开始前连接出现问题，我们仍应返回错误。

还有一个问题：在业务事务中，如果handler执行失败，但我们已经发送了响应？我们在handler返回后提交，然后发送响应。如果handler抛出异常，我们在except中回滚，然后发送错误。所以没问题。

所以这种方法更好。

现在，我们需要修改do_GET和do_POST，它们调用`_run_in_transaction`，传递`_handle_get`等方法。

对于不存在的路径，我们在_handle_get或_handle_post中raise AppError(404)。所以即使在404情况下，也会先执行清理，然后业务失败回滚，但清理已提交，所以满足要求。

现在调整。

另外，对于读取请求体，应该在处理逻辑中，而不是在do_POST中。因为请求体需要在业务事务中使用（如果业务需要）。我们可以在_handle_post中读取JSON，但读取JSON需要在请求体没有读取之前。因为self.rfile是流式，读取后不能重复读取。所以我们需要在进入_run_in_transaction之前读取JSON？但_run_in_transaction中，我们可能需要读取JSON。我们可以将JSON解析后的数据作为参数传递给handler，但handler已经闭包捕获数据。因为_handler_post可以访问self，我们可以直接在_handle_post中调用_read_json_body。但注意，_read_json_body需要访问self.rfile，它应该在连接建立之前读取吗？因为连接建立不涉及流，所以可以在任何时间读取。但我们需要确保在事务开始之前读取JSON，但JSON的读取发生在_run_in_transaction内部调用的_handle_post中。此时连接已建立，但事务已开始（业务事务）。但读取请求体不涉及数据库，所以没有问题。所以可以在_handle_post中读取JSON。

但注意：如果JSON读取失败，会抛出AppError，此时业务事务已经开始了（但尚未进行任何数据库操作），我们可以回滚然后发送错误。但我们的异常捕获会回滚业务事务。所以可以。

但是，如果JSON读取失败，我们可能已经执行了清理事务并提交。所以清理仍然生效。这是合理的。

因此，我们在_handle_post中调用_read_json_body。

但有一个问题：_read_json_body需要消耗self.rfile，但如果在_handle_post之前有其他东西读取了rfile，会冲突。但我们的流程中，只有do_POST会调用，且一次只读取一次，所以没问题。

另外，对于confirm和cancel，不需要请求体。所以我们在_handle_post中根据路径判断是否需要读取。

所以我们定义_handle_post(self, conn)：连接已经由_run_in_transaction传入，我们使用conn进行操作。

现在，参考之前的逻辑，_handle_get和_handle_post接收conn，返回(status, data)。

我们需要在_handle_post中访问self._parse_path()，self._read_json_body()等。

所以写：

```python
def _handle_get(self, conn):
    parts = self._parse_path()
    if parts == ['items']:
        data = self._list_items(conn)
        return 200, data
    else:
        raise AppError(404, "Not found")

def _handle_post(self, conn):
    parts = self._parse_path()
    if parts == ['items']:
        data = self._read_json_body()
        result = self._create_item(conn, data)
        return 201, result
    elif parts == ['reservations']:
        data = self._read_json_body()
        result = self._create_reservation(conn, data)
        return 201, result
    elif len(parts) == 3 and parts[0] == 'reservations' and parts[2] == 'confirm':
        try:
            res_id = int(parts[1])
        except ValueError:
            raise AppError(400, "Invalid reservation ID")
        result = self._confirm_reservation(conn, res_id)
        return 200, result
    elif len(parts) == 3 and parts[0] == 'reservations' and parts[2] == 'cancel':
        try:
            res_id = int(parts[1])
        except ValueError:
            raise AppError(400, "Invalid reservation ID")
        result = self._cancel_reservation(conn, res_id)
        return 200, result
    else:
        raise AppError(404, "Not found")
```

然后do_GET和do_POST只需要：

```python
def do_GET(self):
    self._run_in_transaction(self._handle_get)

def do_POST(self):
    self._run_in_transaction(self._handle_post)
```

非常简洁。

现在我们需要实现所有辅助方法。

我们还需要初始化数据库。在if __name__ == "__main__"中，调用init_db()，然后启动服务器。

启动服务器：

```python
class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in separate threads."""
    allow_reuse_address = True
    daemon_threads = True  # 使线程随主线程退出

def main():
    init_db()
    server = ThreadedHTTPServer(('127.0.0.1', 8080), RequestHandler)
    print("Server running on http://127.0.0.1:8080")
    server.serve_forever()

if __name__ == "__main__":
    main()
```

现在，我们需要定义RequestHandler继承BaseHTTPRequestHandler。在类定义中，我们重写do_GET和do_POST，并添加其他方法。

同时，我们还需要重写`log_message`以抑制日志或保持简洁。可以保持默认。

现在，我们来考虑输入验证的细节。

在`_create_item`中，我们检查name是否为字符串且非空。但用户可能传入空字符串。我们应检查name.strip()是否为空，或者直接检查长度。

对于stock_total，我们允许int类型。但用户传入的是JSON，可能为数字。在Python中json.loads会将数字解析为int或float。所以我们检查isinstance(stock_total, int)且stock_total > 0。但如果stock_total是float且为整数（如3.0），我们可能不接受。但为了严格，我们要求必须是整数。我们可以尝试转换为int，但可能会丢失精度。简单起见，我们接受int和float，但只允许整数值？更安全：要求int。如果用户发送3.0，我们的检查isinstance(3.0, int)为False，所以会拒绝。但用户应该发送3。可以接受。

对于quantity和ttl_seconds类似。

对于item_id，我们要求int。

对于reservation_id，我们从路径解析为int，如果解析失败返回400。

现在，考虑数据库表结构的约束：我们使用了CHECK约束，但Python插入时如果违反，会抛出sqlite3.IntegrityError。但我们已在应用层验证，所以不应发生。但作为保护，我们可以在Exception中捕获IntegrityError，返回409或400。

但未避免代码复杂，暂时忽略。

现在，我们需要考虑时间戳精度：我们使用time.time()，返回float。expires_at和created_at使用的是real。在清理时，比较expires_at < now。

现在，测试场景。

我们可以模拟一些用例，但不需要在此编写。

现在，我们需要注意，在`_cleanup_expired`中，我们使用了两个UPDATE语句。确保在事务中。

另外，清理操作应该在业务事务前单独提交。但我们的`_run_in_transaction`中，先执行清理事务并提交，再开始业务事务。所以清理的更改已经持久化。

现在，我们需要处理当清理事务执行后，业务事务开始前，如果有其他线程的请求，可能会看到清理后的状态，这是好的。

现在，考虑并发：如果两个请求同时进入，第一个执行清理事务并提交，第二个执行清理事务，可能会重复清理，但清理是幂等的：如果已经过期，状态已被修改为expired，则下次清理不会选中。所以安全。

但是，如果两次清理同时进行，第一个将过期预约库存释放并设状态为expired，第二个执行时，因为状态已不是pending，不会重复处理。所以没问题。

现在，实现细节：我们是不是需要在每个连接中设置PRAGMA foreign_keys=ON？我们没有定义外键约束的实际强制，因为我们创建表时使用了REFERENCES，但SQLite默认不强制外键，除非启用PRAGMA foreign_keys。但我们可以启用以获得级联或约束检查。但我们的应用逻辑处理了约束，所以可以不启用。但为了数据完整性，可以启用。我们可以在init_db中设置PRAGMA foreign_keys=ON？但因为数据库持久，只需要在连接时设置。我们可以在_get_connection中执行PRAGMA foreign_keys=ON。这样每个连接都启用外键约束。但注意，外键约束可能会影响性能，但可以接受。我们可以在_get_connection中添加`conn.execute("PRAGMA foreign_keys=ON")`。但注意，PRAGMA foreign_keys不能在一个事务中执行？实际上可以。但最好在连接后立即执行。因为我们的连接是isolation_level=None，所以执行后会立即提交。但我们将它放在清理事务之前。这不会影响业务。

我们可以在_get_connection中先设置，然后再开始事务。但注意，设置foreign_keys=ON可能需要单独提交？实际上，PRAGMA不需要提交，它立即生效。所以没问题。

我们决定在_get_connection中设置：
```python
conn.execute("PRAGMA foreign_keys = ON")
```
但注意，这个设置是连接级别的，所以每个连接都需要设置。

但我们可能不需要强制外键，因为我们的应用逻辑会检查item_id存在性。为安全，我们还是启用。

现在，还需要考虑：在_create_item中，我们未验证name是否唯一。不要求。

现在，代码差不多完成。

我们需要在业务函数中，如果发生AppError，我们raise。在_run_in_transaction中，我们捕获AppError，回滚业务事务，发送错误。因为我们的业务事务已经开始了，如果发生AppError，我们需要回滚业务事务。但注意：如果在业务事务中，发生AppError，可能已经执行了一些数据库操作（例如，在_create_reservation中，我们先扣减库存后插入预约，但如果在插入预约前发生错误（如AppError），我们还未插入预约，但扣减已经执行。如果我们回滚事务，扣减会被撤销。所以正确。

但在_create_reservation中，我们扣减库存是在确认商品存在并且库存充足后。如果扣减成功，但随后插入预约时发生约束失败（比如某些检查），会抛出IntegrityError，我们会在Exception中捕获并回滚事务，扣减也会回滚。所以数据一致。

所以异常处理是安全的。

现在，我们实现代码。注意：在`_run_in_transaction`中，我们调用了cleanup事务和业务事务。在cleanup事务中，也可能发生AppError吗？清理函数不会主动raise AppError，但如果数据库锁超时，会抛出OperationalError，我们在外层捕获。如果清理失败，整个请求失败，我们不应该再执行业务。所以我们可以在清理部分也捕获异常，并直接返回错误。我们在_run_in_transaction中，将清理也放在try块内，但before业务事务开始。如果清理失败，我们进入except块，但由于未开始业务事务，conn.rollback()可能对清理事务回滚，但清理事务已经提交？不，如果清理事务中发生异常（如OperationalError），可能事务未提交，我们需要回滚中断。我们目前的代码：先conn.execute("BEGIN IMMEDIATE")，如果成功，执行cleanup，然后conn.commit()。如果其中任何一步失败，会抛出异常，进入except块，我们执行conn.rollback()来回滚当前事务（清理事务）。然后发送错误。所以清理事务会被回滚，不符合“清理操作必须执行”的要求。但清理事务失败本身意味着数据库问题，我们无法完成清理，所以请求失败，可能可以接受。但理想情况下，我们应重试清理。但简单起见，我们认为清理失败是致命错误，返回503。这也是合理的。

所以现有的结构可以接受。

但是，如果清理事务提交成功，但业务事务开始失败（例如BEGIN IMMEDIATE时数据库被锁定），我们会进入except，此时业务事务尚未开始，但conn.rollback()可能作用于上一个事务？如果在conn.commit()后没有进行新的BEGIN，则执行rollback()会rollback no transaction is active，不会报错。但此时清理事务已经提交，不会回滚。所以安全。所以我们的异常处理在清理事务后、业务事务前的BEGIN失败时，会rollback（无操作），然后发送错误。所以清理已经提交，符合要求。

所以总体设计良好。

现在，我们可编写最终代码。

考虑代码风格，确保命名规范。

我们还要定义DB_FILE为全局变量，在Handler中引用。

另外，我们需要确保所有方法接收self。

现在编写最终代码。

注意：在发送JSON响应时，我们可能需要添加一个换行符，但不必。

在`_list_items`中，我们返回{"items": items}。在GET响应中体现。

现在，测试可能的bug。

### 在`_create_reservation`中，我们使用了

```python
cursor = conn.execute("SELECT id FROM items WHERE id = ?", (item_id,))
if cursor.fetchone() is None:
    raise AppError(404, "Item not found")
cursor = conn.execute("UPDATE items SET stock_available = stock_available - ? WHERE id = ? AND stock_available >= ?",
                      (quantity, item_id, quantity))
if cursor.rowcount == 0:
    raise AppError(409, "Insufficient stock")
```

这里注意：如果商品存在但stock_available < quantity，UPDATE rowcount为0，raise 409。所以不用先查询库存。完美。

但注意：如果quantity等于stock_available，UPDATE成功，rowcount为1。

但是，如果我们之前已经确认了商品存在，但UPDATE返回0行，一定是库存不足。所以正确。

但是，如果quantity为0，我们已经验证quantity>0，所以没问题。

### 在`_cancel_reservation`中，我们更新状态后释放库存：

我们使用row[2] (quantity) 和 row[1] (item_id)。但我们没有检查状态变化后是否还有效？我们使用UPDATE reservations SET status='cancelled' WHERE id=? AND status='pending'，但我们在前面已经检查过status，所以应该成功。但如果由于并发，状态在检查和更新之间被改变，但事务隔离保证不会，所以安全。

但我们也可以使用UPDATE条件，然后检查rowcount是否1，如果0则可能状态已变，但此时我们可以raise。但我们没有这么做，因为我们前面已检查，而且在同一事务中，不会变化。所以可以信任。

但为了更健壮，我们也可以对UPDATE使用条件并检查rowcount。我们可以在UPDATE中使用status='pending'条件，然后检查rowcount：

```python
cursor = conn.execute("UPDATE reservations SET status='cancelled' WHERE id=? AND status='pending'", (res_id,))
if cursor.rowcount == 0:
    # 可能不存在或状态不是pending
    # 但我们已经检查过存在和状态，所以不应该发生；但以防并发，我们可以再次查询确定原因
    raise AppError(400, "Reservation cannot be cancelled (status not pending)")
```

但我们在前面已经查询了row，并确认status为pending。所以不需要。

### 在确认时，也类似。

现在，我们需要处理路径解析：当路径为'/items'时，parse_path返回['items']；如果路径为'/items/'，经过rstrip('/')后也变成'/items'，所以['items']。所以应该兼容带斜杠的情况。

但是，如果路径为'//items'，可能导致空部分？不过我们使用split('/')[1:]，如果有多余斜杠，可能出现空字符串，但我们使用了rstrip('/')，所以不会有尾部斜杠，但中间斜杠如'//items'会在分割后出现空字符串。例如path='//items' => after rstrip => '//items' => split('/') => ['', '', 'items'] => [1:] => ['', 'items']，所以parts[0]是''。这会导致匹配失败，返回404。但通常客户端不会发这样路径。我们可以忽略。

### 关于错误处理：当数据库操作异常时，我们返回500和错误信息。我们不希望暴露内部信息，但题目未要求隐藏，所以可以。

### 关于并发：使用ThreadingMixIn，每个请求在独立线程中处理。我们使用数据库连接是线程安全的（因为每个线程有自己的连接）。我们使用IMMEDIATE事务确保写锁竞争超时重试。没有问题。

### 关于认证：不需要。

### 关于测试：我们可以测试几个场景。

现在，我们编写完整的代码。

我们还需要考虑一个潜在问题：在_run_in_transaction中，我们使用了两个连续的事务：先清理，再业务。但是，如果清理事务中提交后，业务事务开始前，有其他请求的清理事务也执行了，这没问题。但如果在清理和业务之间，其他请求的业务事务修改了数据，那么业务事务看到的是最新数据，因为我们的事务是IMMEDIATE，它会等待锁，安全。所以没问题。

但是，如果清理事务自己没有释放锁？事务提交后锁释放。

所以整体没问题。

现在，我们编写代码。

确保在return语句中，我们返回的status_code是整数，result是字典或列表。

在send_json中，我们使用json.dumps。我们需要将datetime对象？没有datetime，只有时间戳浮点数，所以直接序列化没问题。

注意：expires_at和created_at是浮点数，在JSON中会显示为数字，可以。如果需要可读性，可以转换，但不需要。

现在，我们完成代码。

检查所有函数。

在`_list_items`中，我们返回{ 'items': items }。如果items为空，返回空列表。

在`_create_item`中，我们返回商品对象。

在`_create_reservation`中，我们返回预约对象。

在`_confirm_reservation`中，我们返回预约对象。

在`_cancel_reservation`中，我们返回预约对象。

现在，编写代码时需要注意：在`_create_item`中，如果stock_total为0，我们要求>0，所以不包括0。

现在，代码。

### 最终完整代码

我将在下面写出。
````

## Assistant

````markdown
```python
#!/usr/bin/env python3
"""
Single-file HTTP API service for inventory reservations.
Uses only Python 3 standard library.
"""

import json
import sqlite3
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from urllib.parse import urlparse

DB_FILE = "inventory.db"


class AppError(Exception):
    """Application-level error with HTTP status code and message."""

    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message


class RequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler for the inventory reservation API."""

    # ------------------------------------------------------------------
    #  Helper methods for sending responses
    # ------------------------------------------------------------------
    def _send_json(self, status: int, data):
        """Send a JSON response with the given status code and data."""
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_error(self, status: int, message: str):
        """Send a JSON error response."""
        self._send_json(status, {"error": message})

    # ------------------------------------------------------------------
    #  Database connection
    # ------------------------------------------------------------------
    def _get_connection(self) -> sqlite3.Connection:
        """Create and return a new database connection."""
        conn = sqlite3.connect(DB_FILE, timeout=5, isolation_level=None)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    # ------------------------------------------------------------------
    #  Path parsing
    # ------------------------------------------------------------------
    def _parse_path(self):
        """Parse the request path into a list of components."""
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        if not path:
            return []
        return path.split("/")[1:]

    # ------------------------------------------------------------------
    #  Request body parsing
    # ------------------------------------------------------------------
    def _read_json_body(self) -> dict:
        """Read and parse the JSON request body."""
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length == 0:
            raise AppError(400, "Request body is empty")
        body = self.rfile.read(content_length)
        try:
            data = json.loads(body)
        except json.JSONDecodeError as exc:
            raise AppError(400, "Invalid JSON") from exc
        if not isinstance(data, dict):
            raise AppError(400, "JSON body must be an object")
        return data

    # ------------------------------------------------------------------
    #  Business logic – queries
    # ------------------------------------------------------------------
    def _list_items(self, conn):
        """Return a list of all items with their current stock."""
        cursor = conn.execute(
            "SELECT id, name, stock_total, stock_available FROM items ORDER BY id"
        )
        rows = cursor.fetchall()
        items = []
        for row in rows:
            items.append({
                "id": row[0],
                "name": row[1],
                "stock_total": row[2],
                "stock_available": row[3],
            })
        return {"items": items}

    def _create_item(self, conn, data: dict) -> dict:
        """Create a new item and return it."""
        name = data.get("name")
        stock_total = data.get("stock_total")

        if not name or not isinstance(name, str) or not name.strip():
            raise AppError(400, "Invalid or missing 'name'")
        if not isinstance(stock_total, int) or stock_total <= 0:
            raise AppError(400, "Invalid or missing 'stock_total', must be a positive integer")

        cursor = conn.execute(
            "INSERT INTO items (name, stock_total, stock_available) VALUES (?, ?, ?)",
            (name, stock_total, stock_total),
        )
        return {
            "id": cursor.lastrowid,
            "name": name,
            "stock_total": stock_total,
            "stock_available": stock_total,
        }

    def _create_reservation(self, conn, data: dict) -> dict:
        """Create a new reservation, deduct stock, return the reservation."""
        item_id = data.get("item_id")
        quantity = data.get("quantity")
        ttl_seconds = data.get("ttl_seconds")

        if not isinstance(item_id, int) or item_id <= 0:
            raise AppError(400, "Invalid or missing 'item_id'")
        if not isinstance(quantity, int) or quantity <= 0:
            raise AppError(400, "Invalid or missing 'quantity', must be a positive integer")
        if not isinstance(ttl_seconds, int) or ttl_seconds <= 0:
            raise AppError(400, "Invalid or missing 'ttl_seconds', must be a positive integer")

        # check item existence
        cursor = conn.execute("SELECT id FROM items WHERE id = ?", (item_id,))
        if cursor.fetchone() is None:
            raise AppError(404, "Item not found")

        # atomically deduct stock if enough available
        cursor = conn.execute(
            "UPDATE items SET stock_available = stock_available - ? "
            "WHERE id = ? AND stock_available >= ?",
            (quantity, item_id, quantity),
        )
        if cursor.rowcount == 0:
            raise AppError(409, "Insufficient stock")

        now = time.time()
        expires_at = now + ttl_seconds
        cursor = conn.execute(
            "INSERT INTO reservations (item_id, quantity, status, expires_at, created_at) "
            "VALUES (?, ?, 'pending', ?, ?)",
            (item_id, quantity, expires_at, now),
        )
        return {
            "id": cursor.lastrowid,
            "item_id": item_id,
            "quantity": quantity,
            "status": "pending",
            "expires_at": expires_at,
            "created_at": now,
        }

    def _confirm_reservation(self, conn, res_id: int) -> dict:
        """Confirm a pending reservation."""
        cursor = conn.execute(
            "SELECT id, item_id, quantity, status, expires_at, created_at "
            "FROM reservations WHERE id = ?",
            (res_id,),
        )
        row = cursor.fetchone()
        if row is None:
            raise AppError(404, "Reservation not found")
        if row[3] != "pending":
            raise AppError(400, f"Reservation status is '{row[3]}', expected 'pending'")

        conn.execute(
            "UPDATE reservations SET status = 'confirmed' WHERE id = ?",
            (res_id,),
        )
        return {
            "id": row[0],
            "item_id": row[1],
            "quantity": row[2],
            "status": "confirmed",
            "expires_at": row[4],
            "created_at": row[5],
        }

    def _cancel_reservation(self, conn, res_id: int) -> dict:
        """Cancel a pending reservation and release stock."""
        cursor = conn.execute(
            "SELECT id, item_id, quantity, status, expires_at, created_at "
            "FROM reservations WHERE id = ?",
            (res_id,),
        )
        row = cursor.fetchone()
        if row is None:
            raise AppError(404, "Reservation not found")
        if row[3] != "pending":
            raise AppError(400, f"Reservation status is '{row[3]}', expected 'pending'")

        # change status first, then release stock (both inside the same transaction)
        conn.execute(
            "UPDATE reservations SET status = 'cancelled' WHERE id = ? AND status = 'pending'",
            (res_id,),
        )
        conn.execute(
            "UPDATE items SET stock_available = stock_available + ? WHERE id = ?",
            (row[2], row[1]),
        )
        return {
            "id": row[0],
            "item_id": row[1],
            "quantity": row[2],
            "status": "cancelled",
            "expires_at": row[4],
            "created_at": row[5],
        }

    # ------------------------------------------------------------------
    #  Cleanup of expired pending reservations
    # ------------------------------------------------------------------
    def _cleanup_expired(self, conn):
        """Release stock for expired pending reservations and mark them as expired."""
        now = time.time()
        # release stock
        conn.execute(
            """
            UPDATE items
            SET stock_available = stock_available + COALESCE(
                (SELECT SUM(quantity) FROM reservations
                 WHERE status='pending' AND expires_at < ? AND reservations.item_id = items.id),
            0)
            WHERE id IN (SELECT item_id FROM reservations WHERE status='pending' AND expires_at < ?)
            """,
            (now, now),
        )
        # mark reservations as expired
        conn.execute(
            "UPDATE reservations SET status='expired' WHERE status='pending' AND expires_at < ?",
            (now,),
        )

    # ------------------------------------------------------------------
    #  Request handling – transaction wrapper
    # ------------------------------------------------------------------
    def _run_in_transaction(self, handler):
        """
        Execute a handler inside two sequential transactions:
        1. Cleanup expired reservations (committed separately).
        2. The actual business logic (committed on success, rolled back on error).
        """
        conn = None
        try:
            conn = self._get_connection()

            # ---- cleanup transaction ----
            conn.execute("BEGIN IMMEDIATE")
            self._cleanup_expired(conn)
            conn.commit()

            # ---- business transaction ----
            conn.execute("BEGIN IMMEDIATE")
            status, result = handler(conn)
            conn.commit()

            self._send_json(status, result)

        except AppError as exc:
            if conn:
                try:
                    conn.rollback()
                except Exception:
                    pass
            self._send_error(exc.status_code, exc.message)

        except sqlite3.OperationalError as exc:
            if conn:
                try:
                    conn.rollback()
                except Exception:
                    pass
            if "database is locked" in str(exc):
                self._send_error(503, "Service Unavailable: database locked")
            else:
                self._send_error(500, f"Database error: {exc}")

        except Exception as exc:
            if conn:
                try:
                    conn.rollback()
                except Exception:
                    pass
            self._send_error(500, f"Internal server error: {exc}")

        finally:
            if conn:
                conn.close()

    # ------------------------------------------------------------------
    #  GET handler
    # ------------------------------------------------------------------
    def _handle_get(self, conn):
        parts = self._parse_path()
        if parts == ["items"]:
            data = self._list_items(conn)
            return 200, data
        raise AppError(404, "Not found")

    def do_GET(self):
        self._run_in_transaction(self._handle_get)

    # ------------------------------------------------------------------
    #  POST handler
    # ------------------------------------------------------------------
    def _handle_post(self, conn):
        parts = self._parse_path()

        if parts == ["items"]:
            data = self._read_json_body()
            result = self._create_item(conn, data)
            return 201, result

        if parts == ["reservations"]:
            data = self._read_json_body()
            result = self._create_reservation(conn, data)
            return 201, result

        if len(parts) == 3 and parts[0] == "reservations" and parts[2] == "confirm":
            try:
                res_id = int(parts[1])
            except ValueError as exc:
                raise AppError(400, "Invalid reservation ID") from exc
            result = self._confirm_reservation(conn, res_id)
            return 200, result

        if len(parts) == 3 and parts[0] == "reservations" and parts[2] == "cancel":
            try:
                res_id = int(parts[1])
            except ValueError as exc:
                raise AppError(400, "Invalid reservation ID") from exc
            result = self._cancel_reservation(conn, res_id)
            return 200, result

        raise AppError(404, "Not found")

    def do_POST(self):
        self._run_in_transaction(self._handle_post)

    # ------------------------------------------------------------------
    #  Suppress default logging
    # ------------------------------------------------------------------
    def log_message(self, format, *args):
        pass


# ------------------------------------------------------------------
#  Server initialisation
# ------------------------------------------------------------------
def init_db():
    """Create database tables if they do not exist."""
    conn = sqlite3.connect(DB_FILE, timeout=5)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            stock_total INTEGER NOT NULL CHECK(stock_total >= 0),
            stock_available INTEGER NOT NULL CHECK(stock_available >= 0)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS reservations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER NOT NULL REFERENCES items(id),
            quantity INTEGER NOT NULL CHECK(quantity > 0),
            status TEXT NOT NULL DEFAULT 'pending'
                CHECK(status IN ('pending', 'confirmed', 'cancelled', 'expired')),
            expires_at REAL NOT NULL,
            created_at REAL NOT NULL
        )
    """)
    conn.commit()
    conn.close()


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """HTTP server that handles each request in a separate thread."""
    allow_reuse_address = True
    daemon_threads = True


def main():
    init_db()
    server = ThreadedHTTPServer(("127.0.0.1", 8080), RequestHandler)
    print("Server running on http://127.0.0.1:8080")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer shutting down.")
        server.server_close()


if __name__ == "__main__":
    main()
```
````
