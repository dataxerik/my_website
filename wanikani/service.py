import re
import requests
import json
from wanikani.constants import KANJI_LEVELS,KANJI_FILE_LOCATIONS
from mysite.settings import BASE_DIR
import os

def is_valid_api_key(api_key):
    return re.fullmatch('[0-9a-zA-Z].{31}$', api_key)

def get_api_information(api_key):
    url = 'https://www.wanikani.com/api/v1.4/user/{0}/user-information'.format(api_key)
    print(url)
    r = requests.get(url)
    if r.status_code == 200:
        data = r.json()
        return data

def get_jlpt_kanji(file):
    data = ""
    with open(file, 'r', encoding='utf8') as fout:
        for line in fout:
            data += line
    return data

def gather_kanji_list():
    kanji_list = {}
    for level in KANJI_LEVELS:
        print(level)
        print(KANJI_FILE_LOCATIONS[level])
        kanji_list[level] = get_jlpt_kanji(os.path.join(BASE_DIR, KANJI_FILE_LOCATIONS[level]))
    print(kanji_list)


if __name__ == '__main__':
    gather_kanji_list()