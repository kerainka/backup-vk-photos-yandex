import requests


class VkApi:
    def __init__(self, token, api_url, api_version):
        self.token = token
        self.api_url = api_url
        self.api_version = api_version
        self.params = {
            "access_token": self.token,
            "v": self.api_version
        }

    def get_user_id(self, user_id_or_nickname):
        id_url = self.api_url + "users.get"
        id_params = {"user_ids": user_id_or_nickname}
        res = requests.get(id_url, params={**self.params, **id_params})
        res.raise_for_status()
        return res.json()

    def get_photos(self, owner_id, album_id, count):
        photos_url = self.api_url + "photos.get"
        photos_params = {
            "owner_id": owner_id,
            "album_id": album_id,
            "photo_sizes": 1,
            "count": count
            }
        res = requests.get(photos_url, params={**self.params, **photos_params})
        res.raise_for_status()
        return res.json()

    def get_likes(self, owner_id, item_id):
        likes_url = self.api_url + "likes.getList"
        likes_params = {
            "type": "photo",
            "owner_id": owner_id,
            "item_id": item_id,
        }
        res = requests.get(likes_url, params={**self.params, **likes_params})
        res.raise_for_status()
        return res.json()