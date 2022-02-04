import json

import requests


class RestApi:
    def __init__(self, server, token):
        self.token = token
        self.server = server

    def __create_url(self, path):
        return self.server + path + "?" + self.token

    def rest_get(self, path, params: dict = None):
        try:
            return requests.get(self.__create_url(path), params=params)
        except requests.ConnectionError as e:
            print("** Connection Error.")
            exit(1)

    def rest_put(self, path, values):
        try:
            return requests.put(self.__create_url(path), data=values)
        except requests.ConnectionError as e:
            print("** Connection Error.")
            exit(1)

    def rest_post(self, path, data=None, files=None):
        try:
            return requests.post(self.__create_url(path), data=data, files=files)
        except requests.ConnectionError as e:
            print("** Connection Error.")
            exit(1)

    def rest_delete(self, path):
        try:
            return requests.delete(self.__create_url(path))
        except requests.ConnectionError as e:
            print("** Connection Error.")
            exit(1)
