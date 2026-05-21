import sys
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

def download(url):
    downloads_dir = Path("downloads")
    downloads_dir.mkdir(exist_ok=True)

    resolved = asyncio.run(resolve_short_url(url))
    print(f"Downloading: {resolved}")

    try:
        images = PinterestDL.with_api().scrape_and_download(
            url=resolved,
            output_dir=str(downloads_dir),
            num=1,
            download_streams=True,  # Download video streams
        )
        print(f"Downloaded {len(images)} item(s) to {downloads_dir}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else ""
    if url:
        download(url)
    else:
        print("Usage: python download.py <pinterest_url>")
