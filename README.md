
# Chunk Download → Google Drive Pipeline (Railway/GitHub)

This repo downloads many small `.part` files, merges them into `libil2cpp_patched.so`, and uploads to **Google Drive** using a **Service Account**.

## Quick Setup

1. **Upload the `.part` files** to a host Railway can access (e.g., GitHub Releases, Pixeldrain, or any HTTP server).  
2. Edit `pipeline_to_drive.py` → fill `PART_URLS` with your hosted part links in order.
3. Create a **Google Cloud service account** with Drive API access:
   - Enable Google Drive API in your project.
   - Create a Service Account and download the JSON key.
   - Share your Drive **folder** (or a subfolder) with the **service account email**.
4. Set Railway variables:
   - `SERVICE_ACCOUNT_JSON` = contents of the JSON key (paste entire JSON).
   - `DRIVE_FOLDER_ID` = your Drive folder ID (optional; root if empty).
   - `OUTPUT_FILENAME` = `libil2cpp_patched.so` (or your desired name).

## Local Test

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
python pipeline_to_drive.py
```

## Railway Deploy

Push these files to GitHub, then on Railway:
- New Project → Deploy from GitHub → Select this repo.
- Set variables as above.
- Deploy.
- Start the **worker** process.

## Notes

- `PART_URLS` must be HTTP/HTTPS URLs reachable by Railway; the chat download links here are not accessible from Railway.
- If you prefer OAuth user auth instead of a service account, replace `get_service()` accordingly.
