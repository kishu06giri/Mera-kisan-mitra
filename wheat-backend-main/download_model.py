# download_model.py (robust, write-first-to-/tmp then try to move/copy)
import os, sys, shutil, re, time
from urllib.parse import urlparse, parse_qs

GDRIVE_ENV = os.environ.get("GDRIVE_ID", "").strip()
MODEL_PATH_ENV = os.environ.get("MODEL_PATH", "").strip()  # optional user-specified final path
# final preferred path (if set), else we'll use /tmp
DEFAULT_TMP = "/tmp/wheat_classifier.pth"

def extract_id(val):
    if not val:
        return None
    val = val.strip()
    # if it's a full url, try to extract id
    import re
    m = re.search(r"/d/([a-zA-Z0-9_-]+)", val)
    if m:
        return m.group(1)
    parsed = urlparse(val)
    qs = parse_qs(parsed.query)
    if "id" in qs:
        return qs["id"][0]
    if re.fullmatch(r"[a-zA-Z0-9_-]{10,}", val):
        return val
    return None

gdrive_id = extract_id(GDRIVE_ENV)
if not gdrive_id:
    print("GDRIVE_ID not provided or not valid. Value was:", repr(GDRIVE_ENV))
    print("Set environment variable GDRIVE_ID to either the file id or a full share URL.")
    sys.exit(0)

url = f"https://drive.google.com/uc?id={gdrive_id}"
print("Attempting to download Google Drive file id:", gdrive_id)
print("Download URL used:", url)

try:
    import gdown
except Exception as e:
    print("gdown not installed:", e)
    print("Add gdown to requirements.txt")
    sys.exit(1)

TMP_PATH = DEFAULT_TMP
print("Temporary download path:", TMP_PATH)

# Try download with retries
successful = False
for attempt in range(1,4):
    try:
        print(f"gdown attempt {attempt} ...")
        # fuzzy=True helps with some Drive URL forms
        gdown.download(url, TMP_PATH, quiet=False, fuzzy=True)
        if os.path.exists(TMP_PATH) and os.path.getsize(TMP_PATH) > 1024:
            print("Downloaded to tmp path:", TMP_PATH)
            successful = True
            break
        else:
            print("Downloaded file missing or too small:", os.path.exists(TMP_PATH), os.path.getsize(TMP_PATH) if os.path.exists(TMP_PATH) else None)
    except Exception as e:
        print("gdown raised:", repr(e))
    time.sleep(1)

if not successful:
    print("\nERROR: Failed to download model from Google Drive using gdown.")
    print("Check: file is shared as 'Anyone with the link' and GDRIVE_ID is correct.")
    sys.exit(1)

# If user provided MODEL_PATH, try to copy there, otherwise keep in /tmp
final_path = MODEL_PATH_ENV if MODEL_PATH_ENV else "/app/wheat_classifier.pth"
print("Requested final path:", final_path)

# Try move -> fallback to copy -> fallback to leave in /tmp
try:
    os.makedirs(os.path.dirname(final_path), exist_ok=True)
    shutil.move(TMP_PATH, final_path)
    print("Moved model to:", final_path)
    print("Done.")
    sys.exit(0)
except PermissionError as e:
    print("PermissionError moving to final path:", e)
    try:
        shutil.copy2(TMP_PATH, final_path)
        print("Copied model to final path (copy2 successful):", final_path)
        sys.exit(0)
    except Exception as e2:
        print("Copy also failed:", e2)
        # keep the file in TMP and print instructions
        print("Keeping model at tmp:", TMP_PATH)
        print("You can set MODEL_PATH to", TMP_PATH, "in Render environment variables and redeploy so the app uses it.")
        sys.exit(0)
except Exception as e:
    print("Unexpected error while moving model:", e)
    print("Keeping tmp file at:", TMP_PATH)
    sys.exit(0)

