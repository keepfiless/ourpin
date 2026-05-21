import sys
import os
import re
import json
import asyncio
import aiohttp
from pathlib import Path
from pinterest_dl import PinterestDL

async def resolve_short_url(url):
    if "pin.it" in url:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.head(url, allow_redirects=True, timeout=aiohttp.ClientTimeout(total=10)) as r:
                    return str(r.url)
        except:
            pass
    return url

async def get_media_url(url):
    try:
        async with aiohttp.ClientSession() as session:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status == 200:
                    html = await r.text()
                    pws = re.search(r'<script[^>]*id="__PWS_DATA__"[^>]*>(.+?)</script>', html, re.DOTALL)
                    if pws:
                        data = json.loads(pws.group(1))
                        pins = data.get("props", {}).get("initialReduxState", {}).get("pins", {})
                        for pid, pin in pins.items():
                            # Check story_pin_data first (video pins)
                            story_data = pin.get("story_pin_data")
                            if story_data and story_data.get("pages"):
                                pages = story_data["pages"]
                                if len(pages) > 0 and pages[0].get("blocks"):
                                    blocks = pages[0]["blocks"]
                                    if len(blocks) > 0 and blocks[0].get("video"):
                                        vlist = blocks[0]["video"].get("video_list", {})
                                        for vkey in ["V_720P", "V_EXP7", "V_EXP6", "V_480P", "V_360P"]:
                                            if vkey in vlist:
                                                u = vlist[vkey].get("url", "")
                                                if u and ".m3u8" not in u and u.endswith(".mp4"):
                                                    return u, True
                                        # Try any mp4 in video_list
                                        for vkey, vdata in vlist.items():
                                            if isinstance(vdata, dict):
                                                u = vdata.get("url", "")
                                                if u and u.endswith(".mp4"):
                                                    return u, True

                            # Check regular videos.video_list
                            if pin.get("videos"):
                                vlist = pin["videos"].get("video_list", {})
                                for vkey in ["V_720P", "V_EXP7", "V_EXP6", "V_480P", "V_360P"]:
                                    if vkey in vlist:
                                        u = vlist[vkey].get("url", "")
                                        if u and ".m3u8" not in u and u.endswith(".mp4"):
                                            return u, True
                                # Try any mp4 in video_list
                                for vkey, vdata in vlist.items():
                                    if isinstance(vdata, dict):
                                        u = vdata.get("url", "")
                                        if u and u.endswith(".mp4"):
                                            return u, True

                            # Fallback to images
                            images = pin.get("images", {})
                            for ikey in ["orig", "736x", "474x"]:
                                if ikey in images:
                                    return images[ikey].get("url", ""), False
    except Exception as e:
        print(f"Metadata error: {e}")
    return None, False

async def download_direct(url, is_video, output_dir):
    try:
        async with aiohttp.ClientSession() as session:
            headers = {"User-Agent": "Mozilla/5.0", "Referer": "https://www.pinterest.com/"}
            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=120)) as r:
                if r.status == 200:
                    content = await r.read()
                    ext = ".mp4" if is_video else ".jpg"
                    fname = f"pin_{os.urandom(4).hex()}{ext}"
                    fpath = Path(output_dir) / fname
                    fpath.write_bytes(content)
                    return str(fpath)
    except Exception as e:
        print(f"Download error: {e}")
    return None

async def download(url):
    downloads_dir = Path("downloads")
    downloads_dir.mkdir(exist_ok=True)

    resolved = await resolve_short_url(url)
    print(f"Downloading: {resolved}")

    # Try direct download
    media_url, is_video = await get_media_url(resolved)
    if media_url:
        print(f"Found {'video' if is_video else 'image'}: {media_url}")
        result = await download_direct(media_url, is_video, str(downloads_dir))
        if result:
            print(f"Downloaded: {result}")
            return

    # Fallback to pinterest_dl
    try:
        client = PinterestDL.with_api()
        pins = client.scrape(url=resolved, num=1)
        client.download(pins[:1], output_dir=str(downloads_dir))
        print("Downloaded with pinterest_dl")
    except Exception as e:
        print(f"Fallback error: {e}")
        try:
            PinterestDL.with_api().scrape_and_download(url=resolved, output_dir=str(downloads_dir), num=1)
        except Exception as e2:
            print(f"Final fallback error: {e2}")

if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else ""
    if url:
        asyncio.run(download(url))
    else:
        print("Usage: python download.py <pinterest_url>")
