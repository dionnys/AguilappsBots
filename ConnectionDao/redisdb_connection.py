import redis

class RedisConnection:
    def __init__(self, host='localhost', port=6379, db=0):
        self.host = host
        self.port = port
        self.db = db
        self.redis_client = redis.StrictRedis(host=self.host, port=self.port, db=self.db)

    def get(self, key):
        value = self.redis_client.get(key)
        return value.decode() if value is not None else None

    def set(self, key, value, expire_time=None):
        self.redis_client.set(key, value)
        if expire_time is not None:
            self.redis_client.expire(key, expire_time)

    def delete(self, key):
        self.redis_client.delete(key)

    def get_keys(self, pattern):
        return self.redis_client.keys(pattern)

    @classmethod
    def from_url(cls, url):
        url_parts = urlparse(url)
        host = url_parts.hostname
        port = url_parts.port or 6379
        db = int(url_parts.path[1:]) if url_parts.path else 0
        return cls(host=host, port=port, db=db)