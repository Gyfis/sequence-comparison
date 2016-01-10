import requests
import os

__author__ = 'Gyfis'


def download_file(url_string, filename, path):
    filepath = path + os.sep + filename

    if not os.path.isdir(path):
        os.mkdir(path)
    if not os.path.exists(filepath):
        f = open(filepath, 'wb')
        f.write(requests.get(url_string).content)
        f.close()
    return filepath
