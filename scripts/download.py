import sys
import os
import re
import json
import asyncio
import aiohttp
from pathlib import Path

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
    """Extract media URL from Pinterest pin page"""
    try:
        async with aiohttp.ClientSession() as session:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return None, False
                html = await r.text()

                # Try __PWS_DATA__ first
                pws = re.search(r'<script[^>]*id="__PWS_DATA__"[^>]*>(.+?)</script>', html, re.DOTALL)
                if pws:
                    data = json.loads(pws.group(1))
                    pins = data.get("props", {}).get("initialReduxState", {}).get("pins", {})

                    for pid, pin in pins.items():
                        # Check story_pin_data for video
                        story = pin.get("story_pin_data")
                        if story:
                            for page in story.get("pages", []):
                                for block in page.get("blocks", []):
                                    video = block.get("video")
                                    if video:
                                        vlist = video.get("video_list", {})
                                        for q in ["V_720P", "V_EXP7", "V_480P", "V_360P"]:
                                            if q in vlist:
                                                vurl = vlist[q].get("url", "")
                                                if vurl and ".mp4" in vurl:
                                                    return vurl, True

                        # Check videos field
                        videos = pin.get("videos")
                        if videos:
                            vlist = videos.get("video_list", {})
                            for q in ["V_720P", "V_EXP7", "V_480P", "V_360P"]:
                                if q in vlist:
                                    vurl = vlist[q].get("url", "")
                                    if vurl and ".mp4" in vurl:
                                        return vurl, True

                        # Fallback to image
                        images = pin.get("images", {})
                        for k in ["orig", "736x", "474x"]:
                            if k in images and images[k].get("url"):
                                return images[k]["url"], False

                # Fallback: regex for video URL
                vm = re.search(r'"url"\s*:\s*"(https://v[^"]*\.pinimg\.com/videos/[^"]+\.mp4[^"]*)"', html)
                if vm:
                    return vm.group(1).replace("\\u002F", "/"), True

                # Fallback: regex for image
                im = re.search(r'"url"\s*:\s*"(https://i\.pinimg\.com/originals/[^"]+)"', html)
                if im:
                    return im.group(1).replace("\\u002F", "/"), False

    except Exception as e:
        print(f"Error: {e}")
    return None, False

async def download_file(url, is_video, output_dir):
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
                    print(f"Downloaded: {fpath}")
                    return True
    except Exception as e:
        print(f"Download error: {e}")
    return False

async def main(url):
    downloads_dir = Path("downloads")
    downloads_dir.mkdir(exist_ok=True)

    resolved = await resolve_short_url(url)
    print(f"URL: {resolved}")

    media_url, is_video = await get_media_url(resolved)
    if media_url:
        print(f"Found {'video' if is_video else 'image'}: {media_url}")
        await download_file(media_url, is_video, str(downloads_dir))
    else:
        print("No media found")

if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else ""
    if url:
        asyncio.run(main(url))
    else:
        print("Usage: python download.py <pinterest_url>")
