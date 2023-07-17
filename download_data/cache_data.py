import os
import wget
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

def download_data():
    today = datetime.now().date()
    one_week_ago = today - timedelta(days=7)
    current_date = one_week_ago
    while current_date <= today:
        formatted_date = current_date.strftime('%d-%m-%Y')
        url = f"https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/SRAG/2023/INFLUD23-{formatted_date}.csv"
        if not os.path.exists('data'):
            os.makedirs('data')
        try:
            wget.download(url, 'data')
            print(f"Found file from {formatted_date}")
        except:
            print(f"There's no file from {formatted_date}")
        current_date += timedelta(days=1)


def create_service():
    credentials = Credentials.from_authorized_user_file('credentials.json')
    service = build('drive', 'v3', credentials=credentials)

    return service


def list_files_in_drive_folder(service, folder_id):
    response = service.files().list(q=f"parents = '{folder_id}'").execute()
    return response.get('files')


def generate_drive_service():
    gauth = GoogleAuth()
    gauth.LoadCredentialsFile('credentials.json')
    return GoogleDrive(gauth)


def upload_files(drive, files_to_be_uploaded, folder_id):
    for file in files_to_be_uploaded:
        gfile = drive.CreateFile({'parents': [{'id': folder_id}], 'title': file})
        gfile.SetContentFile(f"data/{file}")
        print(f"Uploading {file} to google drive.")
        gfile.Upload()


def upload_data_to_drive():
    folder_id = "1siqO3xH1Q05qCIiLKz6zf3PmHPCqhqdK"
    service = create_service()
    files = list_files_in_drive_folder(service, folder_id)

    files_already_in_drive = []
    for file in files:
        files_already_in_drive.append(file.get('name'))
    print(files_already_in_drive)
    files_to_be_uploaded = []

    for file in os.listdir("data"):
        if file not in files_already_in_drive:
            files_to_be_uploaded.append(file)
        else:
            print(f"File {file} downloaded but already in drive")

    drive = generate_drive_service()
    upload_files(drive, files_to_be_uploaded, folder_id)


if __name__ == "__main__":
    download_data()
    upload_data_to_drive()