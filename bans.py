import asyncpg
from quart import g, request

BANNED_UA_PHRASES_SCHEMA = "phrase TEXT PRIMARY KEY"


async def init(pool: asyncpg.Pool):
    async with pool.acquire() as conn:
        conn: asyncpg.Connection = conn
        await conn.execute(f"CREATE TABLE IF NOT EXISTS banned_ua_phrases ({BANNED_UA_PHRASES_SCHEMA})")


async def is_banned() -> bool:
    if "User-Agent" not in request.headers:
        return True

    async with g.pool.acquire() as conn:
        conn: asyncpg.Connection = conn
        phrases = list(map(
            lambda r: r["phrase"],
            await conn.fetch("SELECT phrase FROM banned_ua_phrases")
        ))

        ua = request.headers.get("User-Agent").lower()

        for phrase in phrases:
            if phrase.lower() in ua:
                return True

    return False
