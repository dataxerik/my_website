import re
import requests
import os
import io
import traceback
import logging
import importlib
import datetime
import sys
import json
import wanikani.constants as constant
from wanikani.exceptions.BadRequestException import BadRequestException
from wanikani.exceptions.InvalidAPIKeyException import InvalidAPIKeyException

from mysite.settings import BASE_DIR
from collections import OrderedDict

logger = logging.getLogger(__name__)


def is_valid_api_key(api_key):
    """
    A simple method to validate a user's api key. The key is a 31 alphanumeric key.
    :param api_key: a string
    :return: Return True if key is a full match or False else.
    """

    logger.info('Validating api key.')
    return True if re.fullmatch('[0-9a-zA-Z].{31}$', api_key) is not None else False

def parse_csv_file2(file_):
    """A method to parse the kanji jlpt files"""

    dict_ = {}
    try:
        with open(file_, encoding='utf8') as fin:
            for line in fin:
                kanji_r, level_r = line.split(",")
                kanji = kanji_r.rstrip()
                level = level_r.rstrip()
                try:
                    dict_.update({kanji: level.rstrip()})
                except KeyError:
                    dict_[kanji] = level.rstrip()
    except FileNotFoundError:
        logging.error("Couldn't find the file: {}".format(file_))

    return dict_


def get_kanji_completion(api_info, user_dict_):
    jlpt_lookup_dict = parse_csv_file2(os.path.join(BASE_DIR, constant.JLPT_KANJI_FILE_LOCATION))
    joyo_lookup_dict = parse_csv_file2(os.path.join(BASE_DIR, constant.JOYO_KANJI_FILE_LOCATIONS))
    freq_lookup_dict = parse_csv_file2(os.path.join(BASE_DIR, constant.FREQUENCY_KANJI_FILE_LOCATION))

    user_dict_['kanji'] = {}
    user_dict_['kanji']['jlpt'] = {}
    user_dict_['kanji']['joyo'] = {}
    user_dict_['kanji']['freq'] = {}
    user_dict_['kanji']['meaning_correct'] = 0
    user_dict_['kanji']['meaning_incorrect'] = 0
    user_dict_['kanji']['reading_correct'] = 0
    user_dict_['kanji']['reading_incorrect'] = 0
    user_dict_['kanji']['total_count'] = 0
    user_dict_['kanji']['characters'] = {}

    def check_kanji_level(character_, character_lookup_dict, lookup_type, user_dict):
        if character_['character'] in character_lookup_dict:
            try:
                user_dict[lookup_type].update(
                    {character_lookup_dict[character_['character']]: user_dict[lookup_type][character_lookup_dict[
                        character_['character']]] +
                                                                     character_['character']})
            except KeyError:
                user_dict[lookup_type][character_lookup_dict[character_['character']]] = character_['character']

            if user_dict[lookup_type].get(lookup_type + '_count') is not None:
                user_dict[lookup_type][lookup_type + '_count'] += 1
            else:
                user_dict[lookup_type][lookup_type + '_count'] = 1

    user_dict_['user'] = {}
    user_dict_['user']['name'] = api_info['user_information']['username']
    user_dict_['user']['level'] = api_info['user_information']['level']
    character_learned = 0

    for character_ in api_info['requested_information']:
        check_kanji_level(character_, jlpt_lookup_dict, "jlpt", user_dict_['kanji'])
        check_kanji_level(character_, joyo_lookup_dict, "joyo", user_dict_['kanji'])
        check_kanji_level(character_, freq_lookup_dict, "freq", user_dict_['kanji'])

        if character_['user_specific'] is not None:
            user_dict_['kanji']['meaning_correct'] += character_['user_specific']['meaning_correct']
            user_dict_['kanji']['meaning_incorrect'] += character_['user_specific']['meaning_incorrect']
            user_dict_['kanji']['reading_correct'] += character_['user_specific']['reading_correct']
            user_dict_['kanji']['reading_incorrect'] += character_['user_specific']['reading_incorrect']
            user_dict_['kanji']['characters'].update({character_['character']: character_['user_specific']['srs']})
            if character_['user_specific']['srs'].lower() in constant.SRS_LEARNED_LEVEL:
                character_learned += 1
            else:
                pass
                #logger.debug(character_)
        else:
            user_dict_['kanji']['characters'].update({character_['character']: constant.NOTRANKED})

        user_dict_['kanji']['characters_learned'] = character_learned
        user_dict_['kanji']['total_count'] += 1
    return user_dict_


def get_vocab_information(api_info, user_dict_):
    user_dict_['vocab'] = {}
    user_dict_['vocab']['meaning_correct'] = 0
    user_dict_['vocab']['meaning_incorrect'] = 0
    user_dict_['vocab']['reading_correct'] = 0
    user_dict_['vocab']['reading_incorrect'] = 0
    user_dict_['vocab']['total_count'] = 0
    user_dict_['vocab']['characters'] = {}
    character_learned = 0

    for character_ in api_info['requested_information']:
        if character_['user_specific'] is not None:
            user_dict_['vocab']['meaning_correct'] += character_['user_specific']['meaning_correct']
            user_dict_['vocab']['meaning_incorrect'] += character_['user_specific']['meaning_incorrect']
            user_dict_['vocab']['reading_correct'] += character_['user_specific']['reading_correct']
            user_dict_['vocab']['reading_incorrect'] += character_['user_specific']['reading_incorrect']
            user_dict_['vocab']['characters'].update({character_['character']: character_['user_specific']['srs']})
            if character_['user_specific']['srs'].lower() in constant.SRS_LEARNED_LEVEL:
                character_learned += 1
            else:
                pass
                #logger.debug(character_)
        else:
            user_dict_['vocab']['characters'].update({character_['character']: constant.NOTRANKED})

    user_dict_['vocab']['characters_learned'] = character_learned

    return user_dict_


def get_radical_information(api_info, user_dict_):
    user_dict_['radical'] = {}
    user_dict_['radical']['meaning_correct'] = 0
    user_dict_['radical']['meaning_incorrect'] = 0
    user_dict_['radical']['total_count'] = 0
    user_dict_['radical']['characters'] = {}
    user_dict_['unlock'] = {}
    user_dict_['unlock']['date'] = {}

    unlock_dic = dict()
    unlock_dic['date'] = dict()
    character_learned = 0

    def get_user_unlock_time(levels_):
        user_dict_['unlock']['timespent'] = {}
        print("user unlock time")
        total_average_time = datetime.timedelta(0)
        for level in sorted(levels_['unlock']['date'].keys()):
            if levels_['unlock']['date'].get(level + 1) is None:
                user_dict_['unlock']['timespent']["{0}_unlock".format(level)] = str(
                    datetime.datetime.now() - levels_['unlock']['date'][level])
                #total_average_time += datetime.datetime.now() - levels_['unlock']['date'][level]
                user_dict_['unlock']['date'].update(
                    {level: user_dict_['unlock']['date'][level].strftime('%Y-%m-%d %H:%M:%S')})
                break
            total_average_time += levels_['unlock']['date'][level + 1] - levels_['unlock']['date'][level]
            user_dict_['unlock']['timespent']["{0}_unlock".format(level)] = str(
                levels_['unlock']['date'][level + 1] - levels_['unlock']['date'][level])
            user_dict_['unlock']['date'].update(
                {level: user_dict_['unlock']['date'][level].strftime('%Y-%m-%d %H:%M:%S')})
        levels_['unlock']['average'] = str(total_average_time / len(levels_['unlock']['date'].keys()))

    for character_ in api_info['requested_information']:
        if character_['user_specific'] is not None:
            user_dict_['radical']['meaning_correct'] += character_['user_specific']['meaning_correct']
            user_dict_['radical']['meaning_incorrect'] += character_['user_specific']['meaning_incorrect']
            user_dict_['radical']['characters'].update({character_['character']: character_['user_specific']['srs']})
            #print(character_['user_specific']['srs'].lower()  in constant.SRS_LEARNED_LEVEL)
            if character_['user_specific']['srs'].lower() in constant.SRS_LEARNED_LEVEL:
                character_learned += 1
            else:
                pass
                #logger.debug(character_)

            if character_['level'] not in unlock_dic.keys():
                #logger.debug("adding level {}".format(character_['level']))
                unlock_dic['date'][character_['level']] = datetime.datetime.fromtimestamp(
                    character_['user_specific']['unlocked_date'])  # .strftime('%Y-%m-%d %H:%M:%S')
        else:
            user_dict_['radical']['characters'].update({character_['character']: constant.NOTRANKED})

        user_dict_['radical']['total_count'] += 1
        #@logger.debug(unlock_dic)

        user_dict_['unlock'].update(unlock_dic)

    user_dict_['radical']['characters_learned'] = character_learned
    get_user_unlock_time(user_dict_)

    return user_dict_


def get_user_completion_2(api_info, type):
    t = datetime.datetime.utcnow()
    user_completion = dict()

    if type == "kanji":
        get_kanji_completion(api_info, user_completion)
    elif type == "radical":
        get_radical_information(api_info, user_completion)
    elif type == "vocab":
        get_vocab_information(api_info, user_completion)
    else:
        raise ValueError("Invalid type requested")

    logger.debug(datetime.datetime.utcnow() - t)
    return user_completion


def create_user_info(api_key):
    t = datetime.datetime.utcnow()
    user = dict()

    try:
        api_info = get_api_information(api_key, "kanji")
        user.update(get_user_completion_2(api_info, "kanji"))

        api_info = get_api_information(api_key, "radicals")
        user.update(get_user_completion_2(api_info, "radical"))

        api_info = get_api_information(api_key, "vocab")
        user.update(get_user_completion_2(api_info, "vocab"))
    except BadRequestException:
        return 'error'

    #logger.debug(user)
    logger.debug(datetime.datetime.utcnow() - t)
    return user


def create_offline_user_info():
    t = datetime.datetime.utcnow()
    user = dict()

    get_kanji_completion(json.load(open('../Test/kanji_static_data.json', 'r', encoding='utf-8')), user)
    get_radical_information(json.load(open('../Test/radical_static_data.json', 'r', encoding='utf-8')), user)
    get_vocab_information(json.load(open('../Test/vocabulary_static_data.json', 'r', encoding='utf-8')), user)

    logger.debug(user)
    logger.debug(datetime.datetime.utcnow() - t)
    return user


def get_api_information(api_key, service_type):
    """
    A method to get the user information
    :param api_key: a 31 character alphanumeric string
    :param service_type: There are three kind of information one can get: Radical, Kanji, and Vocabulary
    :return:
    """

    # This seems kind of redundant
    if not is_valid_api_key(api_key):
        raise InvalidAPIKeyException("Invalid API Key")

    level_range = "1"
    for i in range(2, constant.LEVEL_CAP + 1):
        level_range += "," + str(i)
    logger.debug(level_range)

    base_url = 'https://www.wanikani.com/api/v1.4/user/{0}/'
    if service_type.lower() == 'kanji':
        base_url += 'kanji/'
    elif service_type.lower() == 'radicals':
        base_url += 'radicals/'
    elif service_type.lower() == 'vocab':
        base_url += 'vocabulary/'
    else:
        raise ValueError("Unrecognized service type")

    base_url += level_range
    url = base_url.format(api_key)

    try:
        r = requests.get(url)
    except Exception:  # Need to check what type of exceptions requests will throw, may not be needed at all
        pass

    if r.status_code == 200:
        logger.info('successful api call with status code: {}'.format(r.status_code))
        return r.json()
    else:
        logger.error("Error while making the api call with status code: {}".format(r.status_code))
        raise BadRequestException("Error while making the request")



if __name__ == '__main__':
    # user_information_api = get_api_information('c9d088f9a75b0648b3904ebee3d8d5fa')
    # print(get_user_completion(get_api_information('c9d088f9a75b0648b3904ebee3d8d5fa')))
    # get_user_completion_2(get_api_information("c9d088f9a75b0648b3904ebee3d8d5fa"))

    # logger.debug(create_offline_user_info())
    print(get_radical_information(json.load(open('../Test/radical_static_data.json', 'r', encoding='utf-8')), dict()))
    # print(get_kanji_completion(json.load(open('../Test/kanji_static_data.json', 'r', encoding='utf-8')), dict()))
    # print(get_vocab_information(json.load(open('../Test/vocab_static_data.json', 'r', encoding='utf-8')), dict()))
    # print(create_user_info('c9d088f9a75b0648b3904ebee3d8d5fa'))
    # get_api_information("c9d088f9a75b0648b3904ebee3d8d5fa", "kanji")
