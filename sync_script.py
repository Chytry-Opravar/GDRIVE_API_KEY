import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io

# KONFIGURACE
# ID složky "Šikana MB" (z tvého odkazu)
FOLDER_IDS = [
    '10UhJDi-5Y7wnJht-fhKrGrfFphavKTPI',
    '1MqG4fQOzOGM7tt-EcZx9pQczPzHq0jx9',
    '1w-FyAt5RGM5d2z_g9hkZEetzW1_gNZKN'
]
SCOPES = ['https://www.googleapis.com/auth/drive']
LOCAL_DIR = 'drive_data'  # Kam to uložit na GitHubu

def authenticate():
    """Přihlášení pomocí klíče z GitHub Secrets."""
    creds_json = os.environ.get('GDRIVE_API_KEY')
    if not creds_json:
        raise ValueError("Chybí tajný klíč GDRIVE_API_KEY!")
    
    creds_dict = json.loads(creds_json)
    creds = service_account.Credentials.from_service_account_info(
        creds_dict, scopes=SCOPES)
    return creds

def download_files():
    """Stáhne soubory z více Google Drive složek."""
    creds = authenticate()
    service = build('drive', 'v3', credentials=creds)

    for folder_id in FOLDER_IDS:
        print(f"📁 Synchronizuji složku: {folder_id}")
        results = service.files().list(
            q=f"'{folder_id}' in parents and trashed=false",
            fields="files(id, name, mimeType)").execute()
        files = results.get('files', [])

        if not files:
            print(" -- Složka je prázdná nebo robot nemá přístup.")
            continue

        folder_dir = os.path.join(LOCAL_DIR, folder_id)
        if not os.path.exists(folder_dir):
            os.makedirs(folder_dir)

        for file in files:
            file_id = file['id']
            file_name = file['name']

            if file['mimeType'] == 'application/vnd.google-apps.document':
    print(f" -- Exportuji Google Doc jako DOCX: {file_name}")
    request = service.files().export_media(fileId=file_id, mimeType='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    fh = io.FileIO(os.path.join(folder_dir, file_name + '.docx'), 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
    continue

            print(f"Stahuji: {file_name}...")
            if 'google-apps' in file['mimeType']:
                print(f" -- Přeskakuji Google Doc formát: {file_name}")
                continue

            request = service.files().get_media(fileId=file_id)
fh = io.FileIO(os.path.join(folder_dir, file_name), 'wb')
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
            print(f" -- Hotovo.")

if __name__ == '__main__':
    download_files()
