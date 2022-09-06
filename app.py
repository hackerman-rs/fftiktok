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

from quart import Quart, redirect, send_file
import requests

app = Quart(__name__)
app.url_map.strict_slashes = False

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:104.0) Gecko/20100101 Firefox/104.0"

# i love you pato
VIDEO_API_ROUTE = "https://t.tiktok.com/api/item/detail/?itemId="
# VIDEO_API_ROUTE = "http://localhost:4444/"

@app.route("/")
async def home():
    return await send_file("home.html")


@app.route("/<_>/video/<video_id>")
async def common(_: str, video_id: str):
    return await redirect_to_play(video_id)  


@app.route("/t/<short_url>")
async def t(short_url: str):
    r = await get("https://www.tiktok.com/t/" + short_url + "/")
    return redirect(r.headers["Location"].replace("tiktok", "fftiktok"))

# vm.tiktok.com/...
@app.route("/<short_url>")
async def vm(short_url: str):
    return await t(short_url)

async def get_video_url(video_id: str):
    r = await get(VIDEO_API_ROUTE + video_id)
    json = r.json()
    return json["itemInfo"]["itemStruct"]["video"]["downloadAddr"]

async def get(url: str):
    # TODO: make async
    return requests.get(url, headers={"User-Agent": USER_AGENT}, allow_redirects=False)

async def redirect_to_play(video_id: str):
    return redirect(await get_video_url(video_id))
