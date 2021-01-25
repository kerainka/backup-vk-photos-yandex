import requests


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

