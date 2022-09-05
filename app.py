from TikTokApi import TikTokApi
from quart import Quart, redirect, send_file
import requests

app = Quart(__name__)
api = None
app.url_map.strict_slashes = False

@app.before_first_request
async def setup():
    global api

    with await TikTokApi.create() as ttapi:
        api = ttapi


@app.route("/")
async def home():
    return await send_file("home.html")


@app.route("/<_>/video/<video_id>")
async def common(_: str, video_id: str):
    return await redirect_to_play(video_id)  


@app.route("/t/<short_url>")
async def t(short_url: str):
    print("https://www.tiktok.com/t/" + short_url + "/")
    r = requests.get("https://www.tiktok.com/t/" + short_url + "/", allow_redirects=False)
    return redirect(r.headers["Location"].replace("tiktok", "fftiktok"))


async def redirect_to_play(video_id: str):
    return redirect((await api.video(id=video_id).info())["video"]["playAddr"])
