from __future__ import print_function

import requests, os, json, sys
from tqdm import tqdm
from PyQt5 import QtWidgets
from PyQt5.QtGui import QIcon
from design import Ui_MainWindow
from time import sleep
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload


# Работает кривовато, но я пытался :)
class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.backup = backup
        self.setWindowIcon(QIcon('web.png'))
        self.setWindowTitle('BackUP+')

        self.ui.label_3.setText('')
        self.ui.pushButton.clicked.connect(self.push_b)

    def push_b(self):
        self.progres_start()
        self.start_backup()
        self.progres_bar()
        self.progres_end()

    def start_backup(self):
        token = self.ui.lineEdit.text()
        vk_id = self.ui.lineEdit_2.text()
        print(self.backup(token, vk_id))

    def progres_start(self):
        self.ui.label_3.setText("Загрузка")

    def progres_end(self):
        self.ui.label_3.setText("Завершено")

    def progres_bar(self):
        for i in range(101):
            sleep(0.2)
            self.ui.progressBar.setValue(i)


class VK:
    BASE_URL = 'https://api.vk.com/method/'

    def __init__(self, id_user):
        self.id_user = id_user

    # Постоянные параметры ссылки
    def _get_common_params(self):
        return {
            'access_token': 'vk1.a.qb_pYaRfkQQP80ICdJ7D6WJtyXPtuaQhHVWmBMhk_UxNPAG31x5W9JBIGgNzbUFfXoSUo1UOJtiCb7XR0EhE1xxj2DPYg0ntAjUbsJkTYJUKiq8jYXce-sIfTJkLKzNUbkR-_nT9mtBnnHPwjjHzqLp8MavXPttHCZ17BeGsVHVVx1jokkOt1V3iEF9o-RkK',
            'v': '5.150'
        }

    # Получаем словарь со всей информацией о фотографиях профиля
    def _get_photos_from_vk(self):
        params = self._get_common_params()
        params.update({
            'owned_id': self.id_user,
            'extended': 1,
            'photo_sizes': 1,
        })
        response = (requests.get
                    (f'{self.BASE_URL}photos.getAll?', params=params))
        return response.json()

    # Получаем нужную нам информацию о фотографиях для дальнейших манипуляций
    def get_information_vk_photos(self):
        information_vk_photos = {}
        data_vk = self._get_photos_from_vk()
        for inf in data_vk['response']['items']:
            information_vk_photos[inf['id']] = dict(
                likes=inf['likes']['count'],
                date=inf['date'],
                link=inf['sizes'][-1]['url'],
                type=inf['sizes'][-1]['type'])
        return information_vk_photos


class YandexDisk:
    BASE_URL = 'https://cloud-api.yandex.net/'

    def __init__(self, token, info_photos):
        self.token = token
        self.info_photos = info_photos

    # Устанавливаем стандартный headers
    def _get_common_headers(self):
        return {
            'Authorization': self.token
        }

    # Получаем на компьютер фотографии для загрузки на диск.
    # В info_photos нужно поместить get_information_vk_photos
    def get_photos_on_directory(self):
        for photo in self.info_photos.values():
            response = requests.get(photo['link'])
            name_file = str(photo["likes"])
            file = f'{os.getcwd()}\PhotosLibery\\{name_file}.jpg'
            if os.path.isfile(file):
                name_file += f"_{photo['date']}"
            with open(f'PhotosLibery\{name_file}.jpg', 'bw') as f:
                f.write(response.content)

    # Создает папку и возвращает статус для проверки создания
    def create_folder(self):
        headers = self._get_common_headers()
        params = {
            'path': 'BackupImages'
        }
        response = requests.put(f'{self.BASE_URL}v1/disk/resources',
                                headers=headers, params=params)
        return response.raise_for_status()

    # Генерируем URL для загрузки файла в Яндекс Диск
    def get_url(self, name_file):
        params = {
            'path': f'BackupImages/{name_file}'
        }
        headers = self._get_common_headers()
        response = requests.get(f'{self.BASE_URL}v1/disk/resources/upload',
                                headers=headers, params=params)
        return response.json()['href']

    # Загружаем фото на Яндекс Диск
    def upload_photo(self, href, name_file):
        with open(f'PhotosLibery\\{name_file}', 'rb') as f:
            response = requests.put(href, files={'file': f})
        return response


class GoogleDrive:
    def __init__(self):
        # If modifying these scopes, delete the file token.json.
        self.SCOPES = ['https://www.googleapis.com/auth/drive.file']
        self.creds = None

    def auth(self):
        """Shows basic usage of the Drive v3 API.
        Prints the names and ids of the first 10 files the user has access to.
        """
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.json'):
            self.creds = Credentials.from_authorized_user_file('token.json', self.SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self.SCOPES)
                self.creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(self.creds.to_json())
        return self.creds

    def create_folder(self):
        try:
            # create drive api client
            service = build('drive', 'v3', credentials=self.auth())
            file_metadata = {
                'name': 'BackupImages',
                'mimeType': 'application/vnd.google-apps.folder'
            }

            # pylint: disable=maybe-no-member
            file = service.files().create(body=file_metadata, fields='id'
                                          ).execute()
            # print(F'Folder ID: "{file.get("id")}".')
            return file.get('id')

        except HttpError as error:
            print(F'An error occurred: {error}')
            return None

    def upload_photos(self, folder_id, name_photo):
        try:
            # create drive api client
            service = build('drive', 'v3', credentials=self.auth())

            file_metadata = {
                'name': name_photo,
                'parents': [folder_id]
            }
            media = MediaFileUpload('web.png',
                                    mimetype='image/png', resumable=True)
            # pylint: disable=maybe-no-member
            file = service.files().create(body=file_metadata, media_body=media,
                                          fields='id').execute()
            # print(F'File ID: "{file.get("id")}".')
            return file.get('id')

        except HttpError as error:
            print(F'An error occurred: {error}')
            return None


def backup(token, vk_id):
    result = []
    vk_client = VK(vk_id)
    drive_client = GoogleDrive()
    yandex_client = YandexDisk(token, vk_client.get_information_vk_photos())
    yandex_client.get_photos_on_directory()
    yandex_client.create_folder()
    folder_id = drive_client.create_folder()
    path = f'{os.getcwd()}\PhotosLibery'
    dir_list = os.listdir(path)
    for photo in tqdm(dir_list, ncols=85,
                      position=0, unit=' photos', desc='Loading'):
        yandex_client.upload_photo(yandex_client.get_url(photo), photo)
        drive_client.upload_photos(folder_id, photo)
        result.append({'file_name': photo, 'size': 'z'})
    with open('result.json', 'w') as f:
        json.dump(result, f, indent=2)
    for photo in dir_list:
        os.remove(os.path.join(path, photo))
    return len(vk_client.get_information_vk_photos())


if __name__ == '__main__':
    # backup('y0_AgAAAAA3TrhxAADLWwAAAADssFkYbT5QEHQIRreFqBdntuVlj4TNIRc', 440529550)
    app = QtWidgets.QApplication([])
    w = Ui()
    w.show()
    sys.exit(app.exec())
