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

    results = []
    try:
        client = PinterestDL.with_api()
        pins = client.search(query=query, num=int(num))
        downloaded = client.download(pins, output_dir=str(output_dir))

        for f in output_dir.iterdir():
            if f.is_file():
                results.append(f.name)
    except Exception as e:
        print(f"Error: {e}")
        # Fallback
        try:
            PinterestDL.with_api().search_and_download(query=query, output_dir=str(output_dir), num=int(num))
            for f in output_dir.iterdir():
                if f.is_file():
                    results.append(f.name)
        except Exception as e2:
            print(f"Fallback error: {e2}")

    # Update README
    update_readme(query, folder_name, results)
    print(f"Downloaded {len(results)} files to search/{folder_name}")

def update_readme(query, folder, files):
    # README inside each search folder with images/videos
    folder_readme = Path(f"search/{folder}/README.md")
    content = f"# {query}\n\n"
    for f in files:
        ext = Path(f).suffix.lower()
        if ext in ['.mp4', '.mov', '.webm']:
            content += f"- 🎬 [{f}]({f})\n"
        else:
            content += f"![{f}]({f})\n\n"
    folder_readme.write_text(content)

    # Main search/README.md with links to searches
    main_readme = Path("search/README.md")
    link = f"- [{query}]({folder}/)\n"
    if main_readme.exists():
        existing = main_readme.read_text()
        main_readme.write_text(existing + link)
    else:
        main_readme.write_text(f"# Searches\n\n{link}")

if __name__ == "__main__":
    query = sys.argv[1] if len(sys.argv) > 1 else "nature"
    num = sys.argv[2] if len(sys.argv) > 2 else "10"
    search(query, num)
