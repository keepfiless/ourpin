import sys
import os
import random
import string
from pathlib import Path
from pinterest_dl import PinterestDL

def random_name(length=8):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def search(query, num=10):
    search_dir = Path("search")
    search_dir.mkdir(exist_ok=True)

    folder_name = random_name()
    output_dir = search_dir / folder_name
    output_dir.mkdir(exist_ok=True)

    results = []  # list of (filename, pin_url, is_video)
    try:
        client = PinterestDL.with_api()
        pins = client.search(query=query, num=int(num))
        downloaded = client.download(pins, output_dir=str(output_dir))

        for i, pin in enumerate(pins):
            pin_url = f"https://www.pinterest.com/pin/{pin.id}/" if hasattr(pin, 'id') else ""
            if i < len(downloaded) and downloaded[i]:
                fname = Path(downloaded[i]).name
                is_video = Path(fname).suffix.lower() in ['.mp4', '.mov', '.webm']
                results.append((fname, pin_url, is_video))
    except Exception as e:
        print(f"❌ خطا: {e}")
        # Fallback - no pin URLs available
        try:
            PinterestDL.with_api().search_and_download(query=query, output_dir=str(output_dir), num=int(num))
            for f in output_dir.iterdir():
                if f.is_file():
                    is_video = f.suffix.lower() in ['.mp4', '.mov', '.webm']
                    results.append((f.name, "", is_video))
        except Exception as e2:
            print(f"❌ خطای جایگزین: {e2}")

    # Update README
    update_readme(query, folder_name, results)
    print(f"✅ {len(results)} فایل در search/{folder_name} ذخیره شد")

def update_readme(query, folder, files):
    persian_msg = """
> ⚠️ اگر نتوانستید بصورت مستقیم از گیتهاب دانلود کنید بخاطر محدودیت های اینترنت است برای حل این موضوع شما میتوانید کل ریپازیتوری را از صفحه ی اصلی فورک بصورت زیپ دانلود کنید در این صورت مشکل حل شده و فایل ها درون فایل زیپ خواهد بود 📦

"""
    # README inside each search folder with images/videos
    folder_readme = Path(f"search/{folder}/README.md")
    content = f"# 🔍 {query}\n\n{persian_msg}"
    for fname, pin_url, is_video in files:
        if is_video:
            content += f"**🎬 ویدیو:** [{fname}]({fname})\n"
            if pin_url:
                content += f"📌 لینک پینترست: {pin_url}\n\n"
        else:
            content += f"![{fname}]({fname})\n"
            if pin_url:
                content += f"📌 لینک پینترست: {pin_url}\n\n"
            else:
                content += "\n"
    folder_readme.write_text(content)

    # Main search/README.md with links to searches
    main_readme = Path("search/README.md")
    link = f"- 🔍 [{query}]({folder}/)\n"
    if main_readme.exists():
        existing = main_readme.read_text()
        main_readme.write_text(existing + link)
    else:
        main_readme.write_text(f"# 📂 جستجوها\n\n{link}")

if __name__ == "__main__":
    query = sys.argv[1] if len(sys.argv) > 1 else "nature"
    num = sys.argv[2] if len(sys.argv) > 2 else "10"
    search(query, num)
