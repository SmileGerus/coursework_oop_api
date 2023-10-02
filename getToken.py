import requests
from urllib.parse import urlencode
from pprint import pprint


def get_token():
    APP_ID = '51755935'
    OAUTH_BASE_URL = 'https://oauth.vk.com/authorize'
    params = {
        'client_id': APP_ID,
        'redirect_ur': 'https://oauth.vk.com/blank.html',
        'display': 'page',
        'scope': 'photos',
        'response_type': 'token'
    }

    oauth_url = f'{OAUTH_BASE_URL}?{urlencode(params)}'
    print(oauth_url)


class VK:
    BASE_URL = 'https://api.vk.com/method/'

    def __init__(self, id_user):
        self.id_user = id_user

    # Постоянные параметры ссылки
    def _get_common_params(self):
        return {
            'access_token': 'vk1.a.QER8LT0u0mPFBnUCjE6yLjgYY_sjZa_8CQiQ0e_5_qDyCHud-I2aW-kS4nC3-10ClwBPWwWtTj0syYDlUpx2c2XWPfGdz11paJ_GFY1jsOa4-Ht2nQ60WsgVAoGwS2LjHYh2GCtEaoSf6JpMMrKxFkVyRhAl1iaIkaZ0KO7iFDpcZBKTguUg5ymAIRi24das',
            'v': '5.150'
        }

    # Получаем словарь со всей информацией о фотографиях профиля
    def _get_photos_from_vk(self) -> object:
        params = self._get_common_params()
        params.update({
            'owned_id': self.id_user,
            'extended': 0,
            'photo_sizes': 1,
            'no_service_albums': 0
        })
        response = (requests.get
                    (f'{self.BASE_URL}photos.getAll?', params=params))
        return response.json()


vk = VK(440529550)

get_token()
