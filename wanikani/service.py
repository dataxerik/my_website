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
from wanikani.exceptions import InvalidAPIKeyException, BadRequestException

from mysite.settings import BASE_DIR
from collections import OrderedDict

logger = logging.getLogger("debug.log")


def is_valid_api_key(api_key):
    """A method that returns None if the given string isn't a 32 character alphanumeric string"""

    logger.info('Validating api key.')
    return True if re.fullmatch('[0-9a-zA-Z].{31}$', api_key) is not None else False


def parse_csv_file(file_):
    """A method to parse the kanji jlpt files"""

    dict_ = {}
    try:
        with open(file_, encoding='utf8') as fin:
            for line in fin:
                kanji_r, level_r = line.split(",")
                kanji = kanji_r.rstrip()
                level = level_r.rstrip()
                try:
                    dict_.update({level: dict_[level] + kanji.rstrip()})
                except KeyError:
                    dict_[level] = kanji.rstrip()
    except FileNotFoundError:
        logging.error("Couldn't find the file: {}".format(file_))

    return dict_


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


def get_count_comp(dict_, api_):
    """ A method to get the user count for a given level and total number"""

    count_dict = OrderedDict()
    for level in sorted(dict_.keys()):
        length_ = [1 for character in api_['requested_information'] if character['character'] in dict_[level]['kanji']]
        count_dict[level] = {'user_number': len(length_), 'total_number': len(dict_[level]['kanji'])}
    return count_dict


def get_count(dict_, api_):
    """ A method to get the user count for a given level and total number"""

    count_dict = OrderedDict()
    for level in sorted(dict_.keys()):
        length_ = [1 for character in api_['requested_information'] if character['character'] in dict_[level]]
        count_dict[level] = {'user_number': len(length_), 'total_number': len(dict_[level])}
    return count_dict


def gather_jlpt_list():
    """A method to read the jlpt file and parse it by the five jlpt levels"""

    file_name = os.path.join(BASE_DIR, constant.JLPT_KANJI_FILE_LOCATION)
    kanji_dic = parse_csv_file(file_name)

    return kanji_dic


def gather_frequency_list():
    """A method to read the frequency file and parse it by the five frequency levels"""

    file_name = os.path.join(BASE_DIR, constant.FREQUENCY_KANJI_FILE_LOCATION)
    kanji_dic = parse_csv_file(file_name)

    return kanji_dic


def gather_joyo_list():
    """A method to read the joyo file and parse it by the six joyo levels"""

    file_name = os.path.join(BASE_DIR, constant.JOYO_KANJI_FILE_LOCATIONS)
    kanji_dic = parse_csv_file(file_name)

    return kanji_dic


def get_jlpt_completion(api_info):
    """A method that gets the jlpt dictionary then gives the user count and total count"""

    kanji_dic = gather_jlpt_list()
    jlpt_completion_dic = get_count(kanji_dic, api_info)

    return jlpt_completion_dic


def get_joyo_completion(api_info):
    """A method that gets the joyo dictionary then gives the user count and total count"""

    kanji_dic = gather_joyo_list()
    joyo_completion_dic = get_count(kanji_dic, api_info)

    return joyo_completion_dic


def get_frequency_completion(api_info):
    """A method that gets the joyo dictionary then gives the user count and total count"""

    kanji_dic = gather_frequency_list()
    frequency_completion_dic = get_count(kanji_dic, api_info)

    return frequency_completion_dic


def get_user_completion(api_info):
    """A method that gathers the use's jlpt, joyo, frequency information"""
    t = datetime.datetime.utcnow()
    user_completion = dict()

    user_completion['jlpt'] = get_jlpt_completion(api_info)
    user_completion['joyo'] = get_joyo_completion(api_info)
    user_completion['frequency'] = get_frequency_completion(api_info)
    get_user_stats(api_info)
    print("returning user completion 1")
    print(datetime.datetime.utcnow() - t)
    return user_completion


def get_user_stats(api_info):
    unlock_dic = dict()

    wrong_meaning_count = 0
    correct_meaning_count = 0

    wrong_reading_count = 0
    correct_reading_count = 0

    character_learned = 0

    for character_ in api_info['requested_information']:
        if character_['user_specific'] is None:
            continue

        wrong_meaning_count += character_['user_specific']['meaning_incorrect']
        correct_meaning_count += character_['user_specific']['meaning_correct']

        if character_['user_specific']['reading_incorrect'] is not None:
            wrong_reading_count += character_['user_specific']['reading_incorrect']
            correct_reading_count += character_['user_specific']['reading_correct']

        if character_['user_specific']['srs'].lower() != constant.SRS_LEARNED_LEVEL:
            character_learned += 1
        else:
            pass
            # print(character_)

        if character_['level'] not in unlock_dic.keys():
            # print("adding level {}".format(character_['level']))
            unlock_dic[character_['level']] = datetime.datetime.fromtimestamp(
                character_['user_specific']['unlocked_date'])

    total_time = datetime.timedelta(0)
    for level in sorted(unlock_dic.keys()):
        print("Current time {0}".format(total_time))
        if level < len(unlock_dic):
            time_delta = unlock_dic[level + 1] - unlock_dic[level]
        else:
            time_delta = datetime.datetime.now() - unlock_dic[level]
        total_time += time_delta
        days = time_delta.days if hasattr(time_delta, 'days') else 0
        hours = round(time_delta.seconds / 3600) if hasattr(time_delta, 'seconds') else 0
        print("{0} days, {1} hours".format(days, hours))


def get_kanji_completion(api_info, user_dict_):
    jlpt_lookup_dict = parse_csv_file2(os.path.join(BASE_DIR, constant.JLPT_KANJI_FILE_LOCATION))
    joyo_lookup_dict = parse_csv_file2(os.path.join(BASE_DIR, constant.JOYO_KANJI_FILE_LOCATIONS))
    freq_lookup_dict = parse_csv_file2(os.path.join(BASE_DIR, constant.FREQUENCY_KANJI_FILE_LOCATION))

    user_dict_['kanji'] = {}
    user_dict_['kanji']['jlpt'] = {}
    user_dict_['kanji']['joyo'] = {}
    user_dict_['kanji']['freq'] = {}
    user_dict_['kanji']['meaning_oorrect'] = 0
    user_dict_['kanji']['meaning_inoorrect'] = 0
    user_dict_['kanji']['reading_oorrect'] = 0
    user_dict_['kanji']['reading_inoorrect'] = 0
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

    for character_ in api_info['requested_information']:
        check_kanji_level(character_, jlpt_lookup_dict, "jlpt", user_dict_['kanji'])
        check_kanji_level(character_, joyo_lookup_dict, "joyo", user_dict_['kanji'])
        check_kanji_level(character_, freq_lookup_dict, "freq", user_dict_['kanji'])

        if character_['user_specific'] is not None:
            user_dict_['kanji']['meaning_oorrect'] += character_['user_specific']['meaning_correct']
            user_dict_['kanji']['meaning_inoorrect'] += character_['user_specific']['meaning_incorrect']
            user_dict_['kanji']['reading_oorrect'] += character_['user_specific']['reading_correct']
            user_dict_['kanji']['reading_inoorrect'] += character_['user_specific']['reading_incorrect']
            user_dict_['kanji']['characters'].update({character_['character']:character_['user_specific']['srs']})
        else:
            user_dict_['kanji']['characters'].update({character_['character']: constant.NOTRANKED})

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

    for character_ in api_info['requested_information']:
        if character_['user_specific'] is not None:
            user_dict_['vocab']['meaning_correct'] += character_['user_specific']['meaning_correct']
            user_dict_['vocab']['meaning_incorrect'] += character_['user_specific']['meaning_incorrect']
            user_dict_['vocab']['reading_correct'] += character_['user_specific']['reading_correct']
            user_dict_['vocab']['reading_incorrect'] += character_['user_specific']['reading_incorrect']
            user_dict_['vocab']['characters'].update({character_['character']: character_['user_specific']['srs']})
        else:
            user_dict_['vocab']['characters'].update({character_['character']: constant.NOTRANKED})

    return user_dict_


def get_radical_information(api_info, user_dict_):
    user_dict_['radical'] = {}
    user_dict_['radical']['meaning_oorrect'] = 0
    user_dict_['radical']['meaning_inoorrect'] = 0
    user_dict_['radical']['total_count'] = 0
    user_dict_['radical']['characters'] = {}
    user_dict_['unlock'] = {}

    unlock_dic = dict()
    character_learned = 0

    for character_ in api_info['requested_information']:
        if character_['user_specific'] is not None:
            user_dict_['radical']['meaning_oorrect'] += character_['user_specific']['meaning_correct']
            user_dict_['radical']['meaning_inoorrect'] += character_['user_specific']['meaning_incorrect']
            user_dict_['radical']['characters'].update({character_['character']:character_['user_specific']['srs']})
            if character_['user_specific']['srs'].lower() != constant.SRS_LEARNED_LEVEL:
                character_learned += 1
            else:
                print(character_)

            if character_['level'] not in unlock_dic.keys():
                print("adding level {}".format(character_['level']))
                unlock_dic[character_['level']] = datetime.datetime.fromtimestamp(
                    character_['user_specific']['unlocked_date']).strftime('%Y-%m-%d %H:%M:%S')
        else:
            user_dict_['radical']['characters'].update({character_['character']: constant.NOTRANKED})




        user_dict_['radical']['total_count'] += 1
        print(unlock_dic)
        user_dict_['unlock'].update(unlock_dic)
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

    print(user_completion)
    print(datetime.datetime.utcnow() - t)
    return user_completion


def create_user_info(api_key):
    t = datetime.datetime.utcnow()
    user = dict()

    api_info = get_api_information(api_key, "kanji")
    user.update(get_user_completion_2(api_info, "kanji"))

    api_info = get_api_information(api_key, "radicals")
    user.update(get_user_completion_2(api_info, "radical"))

    api_info = get_api_information(api_key, "vocab")
    user.update(get_user_completion_2(api_info, "vocab"))
    print(user)
    print(datetime.datetime.utcnow() - t)
    return user


def create_offline_user_info():
    t = datetime.datetime.utcnow()
    user = dict()

    get_kanji_completion(json.load(open('../Test/kanji_static_data.json', 'r', encoding='utf-8')), user)
    get_radical_information(json.load(open('../Test/radical_static_data.json', 'r', encoding='utf-8')), user)
    get_vocab_information(json.load(open('../Test/vocabulary_static_data.json', 'r', encoding='utf-8')), user)

    print(user)
    print(datetime.datetime.utcnow() - t)
    return user


def get_api_information(api_key, service_type):
    """A method that makes the api request to wanikani"""

    if not is_valid_api_key(api_key):
        raise InvalidAPIKeyException.InvalidAPIKeyException("Invalid API Key")

    level_range = "1"
    for i in range(2, constant.LEVEL_CAP+1):
        level_range += "," + str(i)

    print(level_range)
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
    print(url)
    try:
        r = requests.get(url)
    except Exception:  # Need to check what type of exceptions requests will throw, may not be needed at all
        pass

    if r.status_code == 200:
        logger.info('successful api call with status code: {}'.format(r.status_code))
        return r.json()
    else:
        logger.error("Error while making the api call with status code: {}".format(r.status_code))
        raise BadRequestException.BadRequestException("Error while making the request")


def get_user_kanji(user_api_dic):
    """A method to create a dictionary """

    kanji_dic = {}

    for character in user_api_dic['requested_information']:
        try:
            kanji_dic[character['character']] = character['user_specific'].get('srs', 'unranked')
        except TypeError:
            kanji_dic[character['character']] = 'apprentice'
            logging.debug("Error while trying to get srs information for character: {0}".
                          format(character['character'].encode('utf8')))

    return kanji_dic


def get_jlpt_kanji(file):
    data = ""
    with open(file, 'r', encoding='utf8') as fout:
        for line in fout:
            data += line
    return data


def get_kanji_by_level():
    kanji_list = {}
    with open(os.path.join(BASE_DIR, "wanikani\static\wanikani\\kanji\\master_kanji_list.txt"),
              encoding='utf8', ) as fout:
        for line in fout.readlines():
            kanji, jlpt_level, joyo_level, frequency_level = line.strip().split(",")
            kanji_list[kanji] = {}
            kanji_list[kanji]['jlpt'] = jlpt_level
            kanji_list[kanji]['joyo'] = joyo_level
            kanji_list[kanji]['frequency'] = frequency_level

    return kanji_list


def create_user_srs_dictionary(user_api_information):
    user_srs_dic = {}

    for character_info in user_api_information['requested_information']:
        try:
            if character_info['user_specific'] is not None:
                user_srs_dic[character_info['character']] = character_info['user_specific']['srs']
            else:
                user_srs_dic[character_info['character']] = 'unranked'
        except TypeError:
            logging.error("Couldn't find srs information for {}".format(character_info['character']))

    return user_srs_dic


def gather_kanji_list(api):
    kanji_list = OrderedDict()
    for level in sorted(constant.KANJI_LEVELS, reverse=True):
        kanji_list[level] = {}
        kanji_list[level]['kanji_list'] = get_jlpt_kanji(
            os.path.join(BASE_DIR, constant.JLPT_KANJI_FILE_LOCATIONS[level]))
        kanji_list[level]['length'] = len(kanji_list[level]['kanji_list'].replace(",", ""))
        kanji_list[level]['kanji_list'] = kanji_list[level]['kanji_list'].split(",")
    user_kanji_list = get_user_kanji(api)

    for level in kanji_list:
        ranked_number = 0
        kanji_list[level]['user'] = {}
        kanji_list[level]['user']['kanji_ranking'] = {}
        for kanji in kanji_list[level]['kanji_list']:
            if kanji in user_kanji_list:
                kanji_list[level]['user']['kanji_ranking'][kanji] = user_kanji_list[kanji]
                ranked_number += 1
            else:
                kanji_list[level]['user']['kanji_ranking'][kanji] = constant.SRS_UNRANKED_LEVEL
        kanji_list[level]['user']['ranked_number'] = ranked_number
    return kanji_list


def get_user_completion_info(user_information_api):
    user_dic = create_user_srs_dictionary(user_information_api)
    type_dic = get_kanji_by_level()
    user = OrderedDict()

    for type in constant.PROGRESS_TYPES:
        user[type] = get_kanji_by_type(user_dic, type_dic, type, user_information_api)

    return user


def get_kanji_by_type(user_dic, type_dic, type, user_information_api):
    user = dict()
    user[type] = {}
    user[type] = OrderedDict()

    type_file = "{}_KANJI_LEVELS".format(type.upper())

    print(type_file)

    for level in getattr(constant, type_file):
        user[type][level] = {}
        user[type][level]['kanji'] = {}
    user[type]['na'] = {}
    user[type]['na']['kanji'] = {}

    for kanji in type_dic.keys():
        try:
            user[type][type_dic[kanji][type]]['kanji'][kanji.strip()] = user_dic.get(kanji.strip(),
                                                                                     constant.SRS_UNRANKED_LEVEL)
        except KeyError:
            logging.error("Could not find {} information for {}".format(type, kanji))
            user[type]['na']['kanji'][kanji.strip()] = constant.SRS_UNRANKED_LEVEL
    count_dic = get_count_comp(user[type], user_information_api)

    for key in count_dic.keys():
        user[type][key]['user'] = count_dic[key]

    return user


def get_complete_user_info(api_key):
    '''

    :param api_key:
    :return: a dictionary with kanji, radical, and vocabulary information
    '''

    # There is a dictionary constant to loop through each type of api: radical, kanji or vocab
    pass


if __name__ == '__main__':
    # user_information_api = get_api_information('c9d088f9a75b0648b3904ebee3d8d5fa')
    # print(get_user_completion(get_api_information('c9d088f9a75b0648b3904ebee3d8d5fa')))
    # get_user_completion_2(get_api_information("c9d088f9a75b0648b3904ebee3d8d5fa"))

    print(create_offline_user_info())
    #print(get_radical_information(json.load(open('../Test/radical_static_data.json', 'r', encoding='utf-8')), dict()))
    #print(get_kanji_completion(json.load(open('../Test/kanji_static_data.json', 'r', encoding='utf-8')), dict()))
    #print(get_vocab_information(json.load(open('../Test/vocab_static_data.json', 'r', encoding='utf-8')), dict()))
    #print(create_user_info('c9d088f9a75b0648b3904ebee3d8d5fa'))
    #get_api_information("c9d088f9a75b0648b3904ebee3d8d5fa", "kanji")
