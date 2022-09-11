# fftiktok - tiktok video downloader
# Copyright (C) 2022  Violet McKinney <fftiktok@viomck.com>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import asyncpg
from quart import g

STATS_TABLE_DEF = """
ip          TEXT        NOT NULL,
user_agent  TEXT        NOT NULL,
video_id    TEXT        NOT NULL,
orig        TEXT        NOT NULL,
accessed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
PRIMARY KEY (ip, user_agent, accessed_at)
"""

# we can't use the request here, b/c we're still in before_serving
async def init(pool: asyncpg.Pool):
    async with pool.acquire() as conn:
        conn: asyncpg.Connection = conn
        await conn.execute(
            f"CREATE TABLE IF NOT EXISTS stats ({STATS_TABLE_DEF})",
        )

async def record(ip: str, user_agent: str, video_id: str, orig: str):
    pool: asyncpg.Pool = g.pool
    async with pool.acquire() as conn:
        conn: asyncpg.Connection = conn
        await conn.execute(
            "INSERT INTO stats (ip, user_agent, video_id, orig)" +
            "VALUES ($1, $2, $3, $4)",
            ip, user_agent, video_id, orig
        )
