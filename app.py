from quart import Quart, redirect, send_file
import aiohttp
import requests

app = Quart(__name__)
http: aiohttp.ClientSession = None
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

async def get_video_url(video_id: str):
    r = await get(VIDEO_API_ROUTE + video_id)
    json = r.json()
    return json["itemInfo"]["itemStruct"]["video"]["downloadAddr"]

async def get(url: str) -> aiohttp.ClientResponse:
    # TODO: make async
    return requests.get(url, headers={"User-Agent": USER_AGENT}, allow_redirects=False)

async def redirect_to_play(video_id: str):
    return redirect(await get_video_url(video_id))
