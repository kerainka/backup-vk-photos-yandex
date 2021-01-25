from user import User

if __name__ == '__main__':
    user_id_or_nickname = input("Введите id/nickname: ")
    vk_token = input("Введите Vk Token: ")
    yandex_token = input("Введите Yandex Token: ")
    backup_folder = input("Введите название папки: ")
    photos_count = int(input("Введите количество фотографии для резервного копирования: "))
    user = User(user_id_or_nickname, vk_token, yandex_token)
    user.backup_profile_photos(photos_count, backup_folder)
