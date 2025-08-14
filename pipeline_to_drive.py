
import os, sys, io, time, requests
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

# --------- CONFIG ---------
# 1) Provide a list of part URLs (HTTP/HTTPS) accessible from Railway.
#    Tip: upload the .part files to GitHub Releases, pixeldrain, or your own host.
PART_URLS = [
    # "https://your-host/path/libil2cpp_patched_1mb.part001",
    # "https://your-host/path/libil2cpp_patched_1mb.part002",
    # ...
]

# 2) Google Drive folder ID where the final file should be saved.
DRIVE_FOLDER_ID = os.getenv("DRIVE_FOLDER_ID", "")

# 3) Service account credentials: set env var SERVICE_ACCOUNT_JSON with the JSON content,
#    or mount a file at ./service_account.json.
SERVICE_ACCOUNT_JSON = os.getenv("SERVICE_ACCOUNT_JSON", "")
SERVICE_ACCOUNT_PATH = os.getenv("SERVICE_ACCOUNT_PATH", "service_account.json")

# 4) Output filename in Drive
OUTPUT_FILENAME = os.getenv("OUTPUT_FILENAME", "libil2cpp_patched.so")

CHUNK_TIMEOUT = 120

def get_service():
    creds = None
    if SERVICE_ACCOUNT_JSON:
        import json, tempfile
        data = json.loads(SERVICE_ACCOUNT_JSON)
        with tempfile.NamedTemporaryFile("w", delete=False) as tf:
            json.dump(data, tf)
            tf.flush()
            creds = service_account.Credentials.from_service_account_file(tf.name, scopes=["https://www.googleapis.com/auth/drive.file"])
    elif os.path.exists(SERVICE_ACCOUNT_PATH):
        creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_PATH, scopes=["https://www.googleapis.com/auth/drive.file"])
    else:
        raise RuntimeError("No service account credentials provided. Set SERVICE_ACCOUNT_JSON or provide service_account.json file.")
    return build("drive", "v3", credentials=creds, cache_discovery=False)

def download_parts(urls, out_path):
    os.makedirs("parts", exist_ok=True)
    part_paths = []
    for idx, url in enumerate(urls, 1):
        name = f"parts/part{idx:03d}"
        print(f"[{idx}/{len(urls)}] Downloading {url} -> {name}", flush=True)
        with requests.get(url, stream=True, timeout=CHUNK_TIMEOUT) as r:
            r.raise_for_status()
            with open(name, "wb") as f:
                for chunk in r.iter_content(chunk_size=1<<20):
                    if chunk:
                        f.write(chunk)
        part_paths.append(name)

    print("Merging parts...", flush=True)
    with open(out_path, "wb") as out:
        for p in part_paths:
            with open(p, "rb") as pf:
                while True:
                    b = pf.read(1<<20)
                    if not b:
                        break
                    out.write(b)
    return out_path

def upload_to_drive(service, file_path, folder_id, filename):
    file_metadata = {
        "name": filename,
        "parents": [folder_id] if folder_id else None
    }
    media = MediaIoBaseUpload(io.FileIO(file_path, "rb"), mimetype="application/octet-stream", resumable=True)
    request = service.files().create(body=file_metadata, media_body=media, fields="id, name")
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Uploaded {int(status.progress() * 100)}%")
    print("Upload complete. File ID:", response.get("id"))
    return response.get("id")

def main():
    if not PART_URLS:
        print("ERROR: PART_URLS is empty. Edit pipeline_to_drive.py to add your part URLs.", file=sys.stderr)
        sys.exit(1)
    target_local = "libil2cpp_patched.so"
    print("Starting download/merge pipeline...", flush=True)
    merged = download_parts(PART_URLS, target_local)
    print("Merged file size:", os.path.getsize(merged), "bytes", flush=True)

    service = get_service()
    file_id = upload_to_drive(service, merged, DRIVE_FOLDER_ID, OUTPUT_FILENAME)
    print("Drive file ID:", file_id)

if __name__ == "__main__":
    main()
