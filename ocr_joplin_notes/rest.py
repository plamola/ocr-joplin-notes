import json
import os

import requests

JOPLIN_TOKEN = "not-set"
if os.environ.get('JOPLIN_TOKEN') is not None:
    JOPLIN_TOKEN = "token=" + os.environ['JOPLIN_TOKEN']
else:
    print("Please set the environment variable JOPLIN_TOKEN")
    exit(1)
if os.environ.get('JOPLIN_SERVER') is not None:
    JOPLIN_SERVER = "token=" + os.environ['JOPLIN_SERVER']
else:
    JOPLIN_SERVER = "http://localhost:41184"
    print("Environment variable JOPLIN_SERVER not set, using default value: http://localhost:41184")


def rest_get(query):
    url = JOPLIN_SERVER + query + "&" + JOPLIN_TOKEN
    try:
        return requests.get(url)
    except requests.ConnectionError as e:
        print("Connection Error. URL: {}".format(url))
        exit(1)


def rest_put(query, values):
    url = JOPLIN_SERVER + query + "?" + JOPLIN_TOKEN
    try:
        return requests.put(url, data=values)
    except requests.ConnectionError as e:
        print("Connection Error. URL: {}".format(url))
        exit(1)


def rest_post(query, values):
    url = JOPLIN_SERVER + query + "?" + JOPLIN_TOKEN
    try:
        return requests.post(url, data=values)
    except requests.ConnectionError as e:
        print("Connection Error. URL: {}".format(url))
        exit(1)


def rest_post_file(query, filename, props):
    url = JOPLIN_SERVER + query + "?" + JOPLIN_TOKEN
    files = {
        "data": (json.dumps(filename), open(filename, "rb")),
        "props": (None, props),
    }
    try:
        return requests.post(url, files=files)
    except requests.ConnectionError as e:
        print("Connection Error. URL: {}".format(url))
        exit(1)


def rest_delete(query):
    url = JOPLIN_SERVER + query + "?" + JOPLIN_TOKEN
    try:
        return requests.delete(url)
    except requests.ConnectionError as e:
        print("Connection Error. URL: {}".format(url))
        exit(1)
