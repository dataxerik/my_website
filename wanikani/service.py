import re
import requests
import os
from wanikani.constants import KANJI_LEVELS, KANJI_FILE_LOCATIONS
from mysite.settings import BASE_DIR
from collections import OrderedDict


def is_valid_api_key(api_key):
    return re.fullmatch('[0-9a-zA-Z].{31}$', api_key)


def get_jlpt_completion(api_info):
    completion_numbers = {}
    total_number_dict = gather_kanji_list()
    for level in total_number_dict:
        completion_numbers[level] = {}
        completion_numbers[level]['user_number'] = len([1 for item in api_info['requested_information']
                                                        if item['character'] in total_number_dict[level]['kanji_list']])
        completion_numbers[level]['total_numbers'] = len(total_number_dict[level]['kanji_list'].replace(",", ""))

    return completion_numbers


def get_api_information(api_key):
    url = 'https://www.wanikani.com/api/v1.4/user/{0}//kanji/'.format(api_key)
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
    kanji_list = OrderedDict()
    for level in sorted(KANJI_LEVELS, reverse=True):
        kanji_list[level] = {}
        kanji_list[level]['kanji_list'] = get_jlpt_kanji(os.path.join(BASE_DIR, KANJI_FILE_LOCATIONS[level]))
        kanji_list[level]['length'] = len(kanji_list[level]['kanji_list'].replace(",", ""))

    return kanji_list


if __name__ == '__main__':
    N5_list = gather_kanji_list()['N5']

    info = get_api_information('c9d088f9a75b0648b3904ebee3d8d5fa')
    print(N5_list)
    test = len([1 for item in info['requested_information'] if item['character'] in N5_list['kanji_list']])
    total_kanji = len(N5_list['kanji_list'].replace(",", ""))
    get_jlpt_completion(info)
