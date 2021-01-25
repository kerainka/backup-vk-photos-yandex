import json
from vk_client import VkApi
from yandex_client import YandexApi
from photo import Photo

YANDEX_API_URL = "https://cloud-api.yandex.net/"
YANDEX_API_VERSION = "v1"

VK_API_URL = "https://api.vk.com/method/"
VK_API_VERSION = "5.126"


class User:
    def __init__(self, user_id_or_nickname, vk_token, yandex_token):
        self.vk_client = VkApi(vk_token, VK_API_URL, VK_API_VERSION)
        self.yandex_client = YandexApi(yandex_token, YANDEX_API_URL, YANDEX_API_VERSION)
        self.user_id = self.get_user_id(user_id_or_nickname)

    def get_user_id(self, user_id_or_nickname):
        response = self.vk_client.get_user_id(user_id_or_nickname)["response"]
        return int(response[0]["id"])

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
            photo_id = item["id"]
            likes = self.get_photo_likes(photo_id)
            url = item["sizes"][-1]["url"]
            photo_type = item["sizes"][-1]["type"]
            date = item["date"]
            photo = Photo(photo_id, url, likes, photo_type, date)
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
            print("Загружаю {} в Yandex Disk. Путь к фото: {}".format(photo.photo_id, path))
            self.yandex_client.upload(path, url)

    def save_photos_to_json(self, file_name, photos):
        print("Сохраняю отчет в {}".format(file_name))
        output = []
        for photo in photos:
            output.append(photo.to_dict())
        with open(file_name, "w") as f:
            json.dump(output, f)

