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
    """Stáhne soubory z Google Drive složky."""
    creds = authenticate()
    service = build('drive', 'v3', credentials=creds)

    # 1. Zjistit seznam souborů ve složce
    results = service.files().list(
        q=f"'{FOLDER_ID}' in parents and trashed=false",
        fields="files(id, name, mimeType)").execute()
    files = results.get('files', [])

    if not files:
        print("Složka je prázdná nebo robot nemá přístup.")
        return

    if not os.path.exists(LOCAL_DIR):
        os.makedirs(LOCAL_DIR)

    # 2. Stahování
    for file in files:
        file_id = file['id']
        file_name = file['name']
        
        # Přeskočit složky (pro zjednodušení stahujeme jen soubory)
        if file['mimeType'] == 'application/vnd.google-apps.folder':
            continue

        print(f"Stahuji: {file_name}...")
        
        # Ignorovat Google Docs formáty (nejdou stáhnout přímo, musely by se konvertovat do PDF)
        # Zde stahujeme PDF, obrázky, Word atd.
        if 'google-apps' in file['mimeType']:
            print(f" -- Přeskakuji Google Doc formát: {file_name}")
            continue

        request = service.files().get_media(fileId=file_id)
        fh = io.FileIO(os.path.join(LOCAL_DIR, file_name), 'wb')
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
        print(f" -- Hotovo.")

if __name__ == '__main__':
    download_files()
