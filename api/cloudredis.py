# Import the redis library
import redis
from api.config import settings

# Define the connection parameters
host = settings.redis_host
port = settings.redis_port
db = settings.redis_db

# Create a Redis connection object
r = redis.Redis(host=host, port=port, password=settings.redis_password)


def read(key: str) -> str:
    return str(r.get(key)).replace("'", "")[1:]

def write(key: str, value: str) -> None:
    r.set(key, value)