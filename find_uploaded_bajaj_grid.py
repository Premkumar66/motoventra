import os
import time

BRAIN_DIR = r"C:\Users\rrpre\.gemini\antigravity\brain\dcf80aaa-c323-407f-888c-e29c09e9a9eb"
TEMP_DIR = r"C:\Users\rrpre\.gemini\antigravity"

print("=== Searching for uploaded Bajaj grid image ===")

found_files = []

for root_dir in [BRAIN_DIR, TEMP_DIR]:
    for dirpath, _, filenames in os.walk(root_dir):
        for f in filenames:
            if f.endswith(('.png', '.jpg', '.jpeg', '.webp')):
                fp = os.path.join(dirpath, f)
                mtime = os.path.getmtime(fp)
                found_files.append((mtime, fp, os.path.getsize(fp)))

found_files.sort(reverse=True, key=lambda x: x[0])

for mtime, fp, sz in found_files[:15]:
    time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(mtime))
    print(f"  {time_str} | {sz//1024:5} KB | {fp}")
