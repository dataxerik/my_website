import re
import requests
import os
import wanikani.constants as constant
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
        completion_numbers[level]['total_number'] = len(total_number_dict[level]['kanji_list'].replace(",", ""))

    return completion_numbers


def gather_joyo_list():
    kanji_dic = {}
    with open(os.path.join(BASE_DIR, constant.JOYO_KANJI_FILE_LOCATIONS), encoding='utf8') as fin:
        for line in fin:
            kanji_r, level_r = line.split(",")
            kanji = kanji_r.rstrip()
            level = level_r.rstrip()
            try:
                kanji_dic.update({level: kanji_dic[level] + kanji.rstrip()})
            except KeyError:
                kanji_dic[level] = kanji.rstrip()
    return kanji_dic


def get_joyo_completion(api_info):
    joyo_completion_dic = OrderedDict()
    kanji_dic = gather_joyo_list()
    for level in sorted(kanji_dic.keys()):
        length_ = [1 for character in api_info['requested_information'] if character['character'] in kanji_dic[level]]
        joyo_completion_dic["G" + level] = {'user_number': len(length_), 'total_number': len(kanji_dic[level])}
    return joyo_completion_dic

def get_user_completion(api_info):
    user_completion = {}
    user_completion['jlpt'] = get_jlpt_completion(api_info)
    user_completion['joyo'] = get_joyo_completion(api_info)

    return user_completion

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
    for level in sorted(constant.KANJI_LEVELS, reverse=True):
        kanji_list[level] = {}
        kanji_list[level]['kanji_list'] = get_jlpt_kanji(
            os.path.join(BASE_DIR, constant.JLPT_KANJI_FILE_LOCATIONS[level]))
        kanji_list[level]['length'] = len(kanji_list[level]['kanji_list'].replace(",", ""))

    return kanji_list


if __name__ == '__main__':
    '''
    N5_list = gather_kanji_list()['N5']

    info = get_api_information('c9d088f9a75b0648b3904ebee3d8d5fa')
    print(N5_list)
    test = len([1 for item in info['requested_information'] if item['character'] in N5_list['kanji_list']])
    total_kanji = len(N5_list['kanji_list'].replace(",", ""))
    get_jlpt_completion(info)
    '''
    #print(get_user_completion(get_api_information('c9d088f9a75b0648b3904ebee3d8d5fa')))
    with open(os.path.join(BASE_DIR, constant.FREQUENCY_KANJI_FILE_LOCATIONS), encoding='utf8') as fout:
        for line in fout:
            with open('frequency1.txt', 'ab') as fin:
                #fin.write(line.split("\t")[0].rstrip().encode('utf8') + ",F1\n".encode('utf8'))
