```python
import sys
import json
import datetime
import bisect

class Session:
    __slots__ = ('id', 'start', 'end', 'value')
    def __init__(self, id_, start, end, value):
        self.id = id_
        self.start = start
        self.end = end
        self.value = value

def parse_dt(s):
    """Parse an ISO-like timestamp without timezone information."""
    if not isinstance(s, str):
        return None
    # Try fromisoformat (Python 3.7+)
    try:
        dt = datetime.datetime.fromisoformat(s)
        if dt.tzinfo is not None:
            return None
        return dt
    except ValueError:
        pass
    # Fallback formats (without timezone)
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M"):
        try:
            dt = datetime.datetime.strptime(s, fmt)
            return dt
        except ValueError:
            continue
    return None

def validate_session(sess):
    """Validate a session dict and return a (Session, None) or (None, reason)."""
    if not isinstance(sess, dict):
        return None, "invalid session object"
    sid = sess.get('id')
    if not isinstance(sid, str):
        return None, "missing or invalid id"
    start_str = sess.get('start')
