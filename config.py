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

from typing import Any, Dict, List


class PostgresConfig:
    host: str
    port: int
    database: str
    username: str
    password: str

    def __init__(
        self,
        host: str,
        port: int,
        database: str,
        username: str,
        password: str,
    ):
        self.host = host
        self.port = port
        self.database = database
        self.username = username
        self.password = password


class WebhookConfig:
    url: str
    user_id: str

    def __init__(self, url: str, user_id: str):
        self.url = url
        self.user_id = user_id


class Config:
    cloudflare: bool
    hmac_key: str
    host: str
    https: bool
    postgres: PostgresConfig
    webhook: WebhookConfig

    def __init__(
        self,
        cloudflare: bool,
        hmac_key: str,
        host: str,
        https: bool,
        postgres: PostgresConfig,
        webhook: WebhookConfig
    ):
        self.cloudflare = cloudflare
        self.hmac_key = hmac_key
        self.host = host
        self.https = https
        self.postgres = postgres
        self.webhook = webhook

    def from_dict(d: Dict[str, Any]):
        pg: Dict[str, Any] = d["postgres"]
        w: Dict[str, str] = d["webhook"]
        return Config(
            cloudflare=d["cloudflare"],
            hmac_key=d["hmac_key"],
            host=d["host"],
            https=d["https"],
            postgres=PostgresConfig(
                host=pg["host"],
                port=pg["port"],
                database=pg["database"],
                username=pg["username"],
                password=pg["password"],
            ),
            webhook=WebhookConfig(
                url=w["url"],
                user_id=w["user_id"],
            )
        )
