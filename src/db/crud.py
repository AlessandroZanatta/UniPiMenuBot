import redis
from typing import List

from settings.settings import settings

r = redis.Redis(
    connection_pool=redis.BlockingConnectionPool(
        host="unipibotmenu_redis-db", port=6379, db=0, max_connections=10
    )
)


def add_user(chat_id: int) -> None:
    r.sadd(settings.redis_users, chat_id)


def remove_user(chat_id: int) -> None:
    r.spop(settings.redis_users, chat_id)


def is_already_subbed(chat_id: int) -> bool:
    return r.sismember(settings.redis_users, chat_id)


def get_users() -> List[str]:
    return r.smembers(settings.redis_users)


def get_number_of_users() -> int:
    return r.scard(settings.redis_users)


def set_number_of_active_users(active_users: int) -> None:
    r.set(settings.redis_active_users, active_users)


def get_number_of_active_users() -> int:
    return int(r.get(settings.redis_active_users))


def increment_number_of_active_users() -> None:
    r.incr(settings.redis_active_users)
