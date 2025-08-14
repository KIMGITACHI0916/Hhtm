import os
import requests
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account

# 1️⃣ Replace "YOUR_HOST_URL" with the actual domain/path where your .part files are hosted
# Make sure these are DIRECT download links (not HTML pages)
PART_URLS = [
    "https://YOUR_HOST_URL/libil2cpp_patched.part001",
    "https://YOUR_HOST_URL/libil2cpp_patched.part002",
    "https://YOUR_HOST_URL/libil2cpp_patched.part003",
    "https://YOUR_HOST_URL/libil2cpp_patched.part004",
    "https://YOUR_HOST_URL/libil2cpp_patched.part005",
    "https://YOUR_HOST_URL/libil2cpp_patched.part006",
    "https://YOUR_HOST_URL/libil2cpp_patched.part007",
    "https://YOUR_HOST_URL/libil2cpp_patched.part008",
    "https://YOUR_HOST_URL/libil2cpp_patched.part009",
    "https://YOUR_HOST_URL/libil2cpp_patched.part010",
    "https://YOUR_HOST_URL/libil2cpp_patched.part011",
    "https://YOUR_HOST_URL/libil2cpp_patched.part012",
    "https://YOUR_HOST_URL/libil2cpp_patched.part013",
    "https://YOUR_HOST_URL/libil2cpp_patched.part014",
    "https://YOUR_HOST_URL/libil2cpp_patched.part015",
    "https://YOUR_HOST_URL/libil2cpp_patched.part016"
]

OUTPUT_FILENAME = os.getenv("OUTPUT_FILENAME", "libil2cpp_patched.so")
SERVICE_ACCOUNT_JSON = os.getenv("SERVICE_ACCOUNT_JSON")
DRIVE_FOLDER_ID = os.getenv("DRIVE_FOLDER_ID", None)

if not PART_URLS or "YOUR_HOST_URL" in PART_URLS[0]:
    raise SystemExit("ERROR: PART_URLS not updated with real download links.")

# 2️⃣ Download and merge parts
print(f"Downloading {len(PART_URLS)} parts...")
merged_data = bytearray()
for i, url in enumerate(PART_URLS, start=1):
    print(f"Downloading part {i}/{len(PART_URLS)}: {url}")
    r = requests.get(url, stream=True)
    r.raise_for_status()
    for chunk in r.iter_content(chunk_size=8192):
        merged_data.extend(chunk)

with open(OUTPUT_FILENAME, "wb") as f:
    f.write(merged_data)
print(f"Merged file saved as {OUTPUT_FILENAME} ({len(merged_data)} bytes)")

# 3️⃣ Upload to Google Drive
print("Uploading to Google Drive...")
creds = service_account.Credentials.from_service_account_info(
    eval(SERVICE_ACCOUNT_JSON), scopes=["https://www.googleapis.com/auth/drive"]
)
service = build("drive", "v3", credentials=creds)

file_metadata = {"name": OUTPUT_FILENAME}
if DRIVE_FOLDER_ID:
    file_metadata["parents"] = [DRIVE_FOLDER_ID]

media = MediaFileUpload(OUTPUT_FILENAME, resumable=True)
file = service.files().create(body=file_metadata, media_body=media, fields="id").execute()
print(f"✅ Uploaded to Google Drive with file ID: {file.get('id')}")
