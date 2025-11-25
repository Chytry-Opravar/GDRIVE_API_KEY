import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io

# KONFIGURACE
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

    # Vytvoř kořenovou složku, pokud neexistuje
    if not os.path.exists(LOCAL_DIR):
        os.makedirs(LOCAL_DIR)

    for folder_id in FOLDER_IDS:
        print(f"📁 Synchronizuji složku: {folder_id}")

        # Získání souborů ve složce
        results = service.files().list(
            q=f"'{folder_id}' in parents and trashed=false",
            fields="files(id, name, mimeType)"
        ).execute()
        files = results.get('files', [])

        if not files:
            print(" -- Složka je prázdná nebo robot nemá přístup.")
            continue

        # Podsložka pro dané folder_id
        folder_dir = os.path.join(LOCAL_DIR, folder_id)
        if not os.path.exists(folder_dir):
            os.makedirs(folder_dir)

        for file in files:
            file_id = file['id']
            file_name = file['name']
            mime = file['mimeType']

            # Export Google Docs → DOCX
            if mime == 'application/vnd.google-apps.document':
                print(f" -- Exportuji Google Doc jako DOCX: {file_name}")
                request = service.files().export_media(
                    fileId=file_id,
                    mimeType='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                )
                fh = io.FileIO(os.path.join(folder_dir, file_name + '.docx'), 'wb')
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()
                print(" -- Hotovo (DOCX).")
                continue

            # Export Google Sheets → XLSX
            if mime == 'application/vnd.google-apps.spreadsheet':
                print(f" -- Exportuji Google Sheet jako XLSX: {file_name}")
                request = service.files().export_media(
                    fileId=file_id,
                    mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                fh = io.FileIO(os.path.join(folder_dir, file_name + '.xlsx'), 'wb')
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()
                print(" -- Hotovo (XLSX).")
                continue

            # Export Google Slides → PPTX
            if mime == 'application/vnd.google-apps.presentation':
                print(f" -- Exportuji Google Slides jako PPTX: {file_name}")
                request = service.files().export_media(
                    fileId=file_id,
                    mimeType='application/vnd.openxmlformats-officedocument.presentationml.presentation'
                )
                fh = io.FileIO(os.path.join(folder_dir, file_name + '.pptx'), 'wb')
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()
                print(" -- Hotovo (PPTX).")
                continue

            # Přeskočit ostatní Google Apps typy (Drawings, Forms, atd.)
            if 'google-apps' in mime:
                print(f" -- Přeskakuji nepodporovaný Google Apps formát: {file_name} ({mime})")
                continue

            # Standardní stahování binárních/ostatních souborů (PDF, MP3, HTML, DOC/DOCX uložené jako soubory)
            print(f"Stahuji: {file_name}...")
            request = service.files().get_media(fileId=file_id)
            fh = io.FileIO(os.path.join(folder_dir, file_name), 'wb')
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
            print(" -- Hotovo.")

if __name__ == '__main__':
    download_files()
