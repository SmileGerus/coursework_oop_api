import requests, os, json
from tqdm import tqdm
from pprint import pprint as pp


class VK:
    BASE_URL = 'https://api.vk.com/method/'

    def __init__(self, id_user):
        self.id_user = id_user

    # Постоянные параметры ссылки
    def _get_common_params(self):
        return {
            'access_token': 'vk1.a.Rsu9XTmQYUi2rjMBzk9CmpNlzZE8YcYtl4_pi4a6wYbZxCKG6wRksgU4mr_Ge_7bss-CezSArw3VXbAFWLg3FBQ88NRdqkJnLHx2fbk3SDxDIY8EqEG8WirTL5C6udNDNWZwHdqieeQ30bylC4TEALU-kInsBr-C4NSADtiBpF22BwfPO9fNDdlXKKXJCHut-CCgKyfXuV1bvfjHVpb2sw',
            'v': '5.154'
        }

    # Получаем словарь со всей информацией о фотографиях профиля
    def _get_photos_from_vk(self):
        params = self._get_common_params()
        params.update({
            'owned_id': self.id_user,
            'album_id': 'profile',
            'extended': 1,
            'photo_sizes': 1,
        })
        response = (requests.get
                    (f'{self.BASE_URL}photos.get?', params=params))
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
            file = f'C:\\Users\Steve\Desktop\courseworks\coursework_oop_api\PhotosLibery\\{name_file}.jpg'
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


def backup(user_id, token):
    result = []
    vk_client = VK(user_id)
    yandex_client = YandexDisk(token, vk_client.get_information_vk_photos())
    yandex_client.get_photos_on_directory()
    yandex_client.create_folder()
    path = 'C:\\Users\Steve\Desktop\courseworks\coursework_oop_api\PhotosLibery'
    dir_list = os.listdir(path)
    for photo in tqdm(dir_list, desc='Upload files'):
        yandex_client.upload_photo(yandex_client.get_url(photo), photo)
        result.append({'file_name': photo, 'size': 'z'})
    with open('result.json', 'w') as f:
        json.dump(result, f, indent=2)
    return len(vk_client.get_information_vk_photos())



TOKEN = 'y0_AgAAAAA3TrhxAADLWwAAAADssFkYbT5QEHQIRreFqBdntuVlj4TNIRc'
for i in tqdm(range(1), desc='Loading'):
    print(backup(440529550, TOKEN))





