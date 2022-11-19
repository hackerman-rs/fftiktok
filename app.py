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

from config import Config
from quart import Quart, redirect, send_file, g, request
import aiohttp
import asyncpg
import bans
import hmac
import json
import stats
import traceback

app = Quart(__name__)
app.url_map.strict_slashes = False
http: aiohttp.ClientSession = None
pool: asyncpg.Pool = None

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:104.0) Gecko/20100101 Firefox/104.0"

# i love you pato
VIDEO_API_ROUTE = "https://t.tiktok.com/api/item/detail/?itemId="
# VIDEO_API_ROUTE = "http://localhost:4444/"


@app.before_serving
async def setup():
    global http
    global config
    global pool

    http = aiohttp.ClientSession()

    with open("config.json", "r") as f:
        config = Config.from_dict(json.load(f))

    pg_conf = config.postgres

    pool = await asyncpg.create_pool(
        f"postgres://{pg_conf.username}:{pg_conf.password}@" +
        f"{pg_conf.host}:{pg_conf.port}/{pg_conf.database}"
    )

    await stats.init(pool)
    await bans.init(pool)


@app.before_request
async def before():
    g.http = http
    g.pool = pool


@app.route("/")
async def home():
    return await send_file("home.html")


@app.route("/api/status")
async def status():
    try:
        await vm("ZTRHTQyY8")
        return "ඞ"
    except Exception as e:
        http: aiohttp.ClientSession = g.http
        await http.post(
            config.webhook.url,
            data=json.dumps(
                {"content": f"<@{config.webhook.user_id}> fftiktok failure: \n\n{e}\n{traceback.format_exc()}"}
            ),
            headers={"Content-Type": "application/json"}
        )
        return "😨", 500


@app.route("/<_>/video/<video_id>")
async def common(_: str, video_id: str):
    orig = "direct"

    if "orig" in request.args and "orig_hmac" in request.args:
        orig = request.args.get("orig")
        orig_hmac = request.args.get("orig_hmac")
        orig_hmac_expected = hmac_encode(video_id + ":" + orig)

        if not hmac.compare_digest(orig_hmac, orig_hmac_expected):
            return "You trying to do something funky?", 400

    try:
        redir = await redirect_to_play(video_id)
    except:
        traceback.print_exc()
        return "Sorry -- looks like this video doesn't exist.", 400

    await stats.record(get_ip(), request.headers["User-Agent"], video_id, orig)
    return redir


@app.route("/t/<short_url>")
async def t(short_url: str):
    r = await get("https://www.tiktok.com/t/" + short_url + "/")
    loc = r.headers["Location"]

    if ".html" in loc:
        r = await get(loc)
        loc = r.headers["Location"]

    loc = loc.replace("www.tiktok.com", config.host)

    if not config.https:
        loc = loc.replace("https://", "http://")

    orig = "t:" + short_url

    # you can technically forge this but i really do not care
    if "from_vm" in request.args:
        orig = "vm:" + short_url

    # last element is video
    orig_hmac = hmac_encode(loc.split("/")[-1].split("?")[0] + ":" + orig)

    query_char = "?"

    if "?" in loc:
        query_char = "&"

    return redirect(f"{loc}{query_char}orig={orig}&orig_hmac={orig_hmac}")

# vm.tiktok.com/...


@app.route("/<short_url>")
async def vm(short_url: str):
    return redirect("/t/" + short_url + "?from_vm=1")


@app.get("/api-tos.txt")
async def api_tos():
    return await send_file("api-tos.txt")


async def get_video_url(video_id: str):
    r = await get(VIDEO_API_ROUTE + video_id)
    json = await r.json()
    return json["itemInfo"]["itemStruct"]["video"]["playAddr"]


async def get(url: str):
    http: aiohttp.ClientSession = g.http
    return await http.get(url, headers={"User-Agent": USER_AGENT}, allow_redirects=False)


def get_ip():
    if config.cloudflare:
        return request.headers.get("CF-Connecting-IP")
    else:
        return request.remote_addr


async def redirect_to_play(video_id: str):
    if await bans.is_banned():
        return (
            "Banned - please contact fftiktok[at]viomck.com if you think this was done in error." +
            '<br>Automated usage guidelines: <a href="/api-tos.txt">fftiktok.com/api-tos.txt</a>'
        ), 403
    return redirect(await get_video_url(video_id))


def hmac_encode(input: str) -> str:
    return hmac.digest(config.hmac_key.encode(), input.encode(), "sha256").hex()
