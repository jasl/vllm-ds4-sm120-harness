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
