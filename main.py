import requests
from datetime import datetime
import json

VK_API_URL = "https://api.vk.com/method/"
VK_API_VERSION = "5.126"

YANDEX_API_URL = "https://cloud-api.yandex.net/"
YANDEX_API_VERSION = "v1"


class VkApi:
    def __init__(self, token, api_url, api_version):
        self.token = token
        self.api_url = api_url
        self.api_version = api_version
        self.params = {
            "access_token": self.token,
            "v": self.api_version
        }

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


class YandexApi:
    def __init__(self, token, api_url, api_version):
        self.token = token
        self.api_url = api_url + api_version
        self.api_version = api_version
        self.headers = {"Authorization": f"OAuth {self.token}"}

    def upload(self, path, url):
       response = requests.post(self.api_url + "/disk/resources/upload",
                               params={"path": path, "url": url}, headers=self.headers)
       response.raise_for_status()
       return response.json()

    def create_folder(self, path):
        response = requests.put(self.api_url + "/disk/resources",
                                params={"path": path}, headers=self.headers)
        is_already_exists_error = response.status_code == 409
        if not is_already_exists_error:
            response.raise_for_status()
        return response.json()


class Photo:
    def __init__(self, id, url, likes, type, date):
        self.url = url
        self.id = id
        self.likes = likes
        self.type = type
        self.date = date
        self.use_date_in_file_name = False

    def get_file_name(self):
        if self.use_date_in_file_name:
            return "{}_{}.jpg".format(self.likes, self.get_formatted_date())
        else:
            return "{}.jpg".format(self.likes)

    def get_formatted_date(self):
        return datetime.utcfromtimestamp(self.date).strftime('%Y-%m-%d_%H-%M-%S')

    def to_dict(self):
        return {
            "file_name": self.get_file_name(),
            "size": self.type
        }


class User:
    def __init__(self, user_id, vk_token, yandex_token):
        self.vk_client = VkApi(vk_token, VK_API_URL, VK_API_VERSION)
        self.yandex_client = YandexApi(yandex_token, YANDEX_API_URL, YANDEX_API_VERSION)
        self.user_id = user_id

    def backup_profile_photos(self, count=5, backup_folder="user_photos"):
        photos = self.get_profile_photos(count)
        self.upload_photos_yandex(photos, backup_folder)
        self.save_photos_to_json("output.json", photos)

    def get_profile_photos(self, count):
        print("Скачиваю {} фотографии с профиля".format(count))
        response = self.vk_client.get_photos(self.user_id, "profile", count)["response"]
        items = response["items"]
        photos = []
        likes_dict = {}
        for item in items:
            id = item["id"]
            likes = self.get_photo_likes(id)
            url = item["sizes"][-1]["url"]
            type = item["sizes"][-1]["type"]
            date = item["date"]
            photo = Photo(id, url, likes, type, date)
            photos.append(photo)
            if likes not in likes_dict:
                likes_dict[likes] = []
            likes_dict[likes].append(photo)
        for likes, like_photos in likes_dict.items():
            if len(like_photos) > 1:
                for like_photo in like_photos:
                    like_photo.use_date_in_file_name = True
        return photos

    def get_photo_likes(self, item_id):
        print("Запрашиваю количество лайков для {}".format(item_id))
        response = self.vk_client.get_likes(self.user_id, item_id)["response"]
        return response["count"]

    def upload_photos_yandex(self, photos, backup_folder):
        print("Создаю папку {} в Yandex Disk".format(backup_folder))
        self.yandex_client.create_folder(backup_folder)
        for photo in photos:
            path = backup_folder + "/" + photo.get_file_name()
            url = photo.url
            print("Загружаю {} в Yandex Disk. Путь к фото: {}".format(photo.id, path))
            self.yandex_client.upload(path, url)

    def save_photos_to_json(self, file_name, photos):
        print("Сохраняю отчет в {}".format(file_name))
        output = []
        for photo in photos:
            output.append(photo.to_dict())
        with open(file_name, "w") as f:
            json.dump(output, f)


id = int(input("Введите id: "))
vk_token = input("Введите Vk Token: ")
yandex_token = input("Введите Yandex Token: ")
backup_folder = input("Введите название папки: ")
photos_count = int(input("Введите количество фотографии для резервного копирования: "))
user = User(id, vk_token, yandex_token)
user.backup_profile_photos(photos_count, backup_folder)
