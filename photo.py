from datetime import datetime


class Photo:
    def __init__(self, photo_id, url, likes, photo_type, date):
        self.url = url
        self.photo_id = photo_id
        self.likes = likes
        self.photo_type = photo_type
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
            "size": self.photo_type
        }
