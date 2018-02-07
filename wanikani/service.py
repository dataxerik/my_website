from collections import OrderedDict
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
    def create_dict_for_kanji_type():
        temp = {}

        for kanji in constant.PROGRESS_KANJI_LEVELS:
            type = kanji.split('_')[0]
            temp[type] = OrderedDict()
            for level in getattr(constant, kanji):
                temp[type][level] = ""
        return temp

    def convert_to_tuple(progess_dict):
        return [(k, v) for k, v in progess_dict.items()]

    def check_kanji_level(character_, character_lookup_dict, lookup_type, user_dict):
        if character_['character'] in character_lookup_dict:
            #sys.exit(0)
            level = character_lookup_dict[character_['character']]
            try:
                user_dict[lookup_type].update(
                    OrderedDict({level: user_dict[lookup_type][character_lookup_dict[
                        character_['character']]] +
                                                                     character_['character']}))
            except KeyError:
                user_dict[lookup_type][level] = character_['character']

            if user_dict['counts'].get(lookup_type + '_total') is not None:
                user_dict['counts'][lookup_type + '_total'] += 1
            else:
                user_dict['counts'][lookup_type + '_total'] = 1

            try:
                if character_['user_specific']['srs'] in constant.SRS_LEARNED_LEVEL:
                    user_dict['counts'][lookup_type][level]['learned'] += 1
            except TypeError:
                pass

            user_dict['counts'][lookup_type][level]['total'] += 1

    def create_progress_count():
        temp = {}
        for kanji in constant.PROGRESS_KANJI_LEVELS:
            type = kanji.split('_')[0]
            temp[type] = {}
            for level in getattr(constant, kanji):
                temp[type][level] = {}
                temp[type][level]['total'] = 0
                temp[type][level]['learned'] = 0

        return temp

    jlpt_lookup_dict = parse_csv_file2(os.path.join(BASE_DIR, constant.JLPT_KANJI_FILE_LOCATION))
    joyo_lookup_dict = parse_csv_file2(os.path.join(BASE_DIR, constant.JOYO_KANJI_FILE_LOCATIONS))
    freq_lookup_dict = parse_csv_file2(os.path.join(BASE_DIR, constant.FREQUENCY_KANJI_FILE_LOCATION))

    user_dict_['kanji'] = {}
    user_dict_['kanji'] = create_dict_for_kanji_type()
    user_dict_['kanji']['meaning_correct'] = 0
    user_dict_['kanji']['meaning_incorrect'] = 0
    user_dict_['kanji']['reading_correct'] = 0
    user_dict_['kanji']['reading_incorrect'] = 0
    user_dict_['kanji']['total_count'] = 0
    user_dict_['kanji']['characters'] = {}
    user_dict_['kanji']['counts'] = create_progress_count()

    user_dict_['user'] = {}
    user_dict_['user']['name'] = api_info['user_information']['username']
    user_dict_['user']['level'] = api_info['user_information']['level']

    character_learned = 0

    for character_ in api_info['requested_information']:
        for progress, lookup_dict in zip(constant.PROGRESS_TYPES, [jlpt_lookup_dict, joyo_lookup_dict, freq_lookup_dict]):
            check_kanji_level(character_, lookup_dict, progress, user_dict_['kanji'])

        if character_['user_specific'] is not None:
            for count_item in ['meaning_correct', 'meaning_incorrect', 'reading_correct', 'reading_incorrect']:
                user_dict_['kanji'][count_item] += \
                    character_['user_specific'][count_item] if character_['user_specific'][count_item] is not None else 0
                #user_dict_['kanji']['meaning_incorrect'] += character_['user_specific']['meaning_incorrect']
                #user_dict_['kanji']['reading_correct'] += character_['user_specific']['reading_correct']
                #user_dict_['kanji']['reading_incorrect'] += character_['user_specific']['reading_incorrect']
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

    for type in constant.PROGRESS_TYPES:
        user_dict_['kanji'][type] = convert_to_tuple(user_dict_['kanji'][type])
    return user_dict_


def get_vocab_information(api_info, user_dict_):
    user_dict_['vocab'] = {}
    user_dict_['vocab']['meaning_correct'] = 0
    user_dict_['vocab']['meaning_incorrect'] = 0
    user_dict_['vocab']['reading_correct'] = 0
    user_dict_['vocab']['reading_incorrect'] = 0
    user_dict_['vocab']['total_count'] = 0
    user_dict_['vocab']['characters'] = {}

    unlock_dic = dict()
    character_learned = 0

    for character_ in api_info['requested_information']:
        if character_['user_specific'] is not None:
            for count_item in ['meaning_correct', 'meaning_incorrect', 'reading_correct', 'reading_incorrect']:
                user_dict_['vocab'][count_item] += \
                    character_['user_specific'][count_item] if character_['user_specific'][count_item] is not None else 0
            #user_dict_['vocab']['meaning_correct'] += character_['user_specific']['meaning_correct']
            #user_dict_['vocab']['meaning_incorrect'] += character_['user_specific']['meaning_incorrect']
            #user_dict_['vocab']['reading_correct'] += character_['user_specific']['reading_correct']
            #user_dict_['vocab']['reading_incorrect'] += character_['user_specific']['reading_incorrect']
            user_dict_['vocab']['characters'].update({character_['character']: character_['user_specific']['srs']})
            if character_['user_specific']['srs'].lower() in constant.SRS_LEARNED_LEVEL:
                character_learned += 1
            else:
                pass
                #logger.debug(character_)

            if character_['level'] not in unlock_dic.keys():
                unlock_dic[character_['level']] = []
            if character_['user_specific']['unlocked_date'] is not None:
                unlock_dic[character_['level']].append(character_['user_specific']['unlocked_date'])
        else:
            user_dict_['vocab']['characters'].update({character_['character']: constant.NOTRANKED})

    user_dict_['vocab']['characters_learned'] = character_learned


    return unlock_dic


def get_radical_information(api_info, user_dict_):
    user_dict_['radical'] = {}
    user_dict_['radical']['meaning_correct'] = 0
    user_dict_['radical']['meaning_incorrect'] = 0
    user_dict_['radical']['total_count'] = 0
    user_dict_['radical']['characters'] = {}
    #user_dict_['unlock'] = {}
    #user_dict_['unlock']['date'] = {}

    unlock_dic = dict()
    #unlock_dic['date'] = dict()
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
            for count_item in ['meaning_correct', 'meaning_incorrect']:
                user_dict_['radical'][count_item] += \
                    character_['user_specific'][count_item] if character_['user_specific'][count_item] is not None else 0
            #user_dict_['radical']['meaning_correct'] += character_['user_specific']['meaning_correct']
            #user_dict_['radical']['meaning_incorrect'] += character_['user_specific']['meaning_incorrect']
            user_dict_['radical']['characters'].update({character_['character']: character_['user_specific']['srs']})
            #print(character_['user_specific']['srs'].lower()  in constant.SRS_LEARNED_LEVEL)
            if character_['user_specific']['srs'].lower() in constant.SRS_LEARNED_LEVEL:
                character_learned += 1
            else:
                pass
                #logger.debug(character_)


            if character_['level'] not in unlock_dic.keys():
                #logger.debug("adding level {}".format(character_['level']))
                unlock_dic[character_['level']] = datetime.datetime.fromtimestamp(
                    character_['user_specific']['unlocked_date']) if character_['user_specific']['unlocked_date'] is not None else None  # .strftime('%Y-%m-%d %H:%M:%S')
        else:
            user_dict_['radical']['characters'].update({character_['character']: constant.NOTRANKED})

        user_dict_['radical']['total_count'] += 1
        #@logger.debug(unlock_dic)

        #user_dict_['unlock'].update(unlock_dic)

    user_dict_['radical']['characters_learned'] = character_learned
    #get_user_unlock_time(user_dict_)

    return unlock_dic


def get_user_unlock_time(user_dict, radical_unlock_data, vocab_unlock_data):

    user_dict['unlock']['date'] = {}
    user_dict['unlock']['timespent'] = {}
    print("user unlock time")

    total_average_time = datetime.timedelta(0)
    for level in sorted(radical_unlock_data.keys()):
        if radical_unlock_data.get(level) is not None and radical_unlock_data.get(level + 1) is None:
            user_dict['unlock']['timespent']["{0}_unlock".format(level)] = str(
                datetime.datetime.now() - radical_unlock_data[level])
            total_average_time += datetime.datetime.now() - radical_unlock_data[level]
            user_dict['unlock']['date'].update(
                {level: radical_unlock_data[level].strftime('%Y-%m-%d %H:%M:%S')})
        elif radical_unlock_data.get(level) is not None:
            total_average_time += radical_unlock_data[level + 1] - radical_unlock_data[level]
            user_dict['unlock']['timespent']["{0}_unlock".format(level)] = str(
                radical_unlock_data[level + 1] - radical_unlock_data[level])
            user_dict['unlock']['date'].update(
                {level: radical_unlock_data[level].strftime('%Y-%m-%d %H:%M:%S')})
        else:
            time_value = datetime.datetime.fromtimestamp(vocab_unlock_data[level][int(len(vocab_unlock_data) * .3)])
            if radical_unlock_data.get(level+1) is None:
                time_value_2 = datetime.datetime.fromtimestamp(vocab_unlock_data[level+1][int(len(vocab_unlock_data) * .3)])
                total_average_time += time_value_2 - time_value
                user_dict['unlock']['timespent']["{0}_unlock".format(level)] = str(
                    time_value_2 - time_value)
                user_dict['unlock']['date'].update(
                    {level: time_value.strftime('%Y-%m-%d %H:%M:%S')})
            else:
                total_average_time += radical_unlock_data[level + 1] - time_value
                user_dict['unlock']['timespent']["{0}_unlock".format(level)] = str(
                    radical_unlock_data[level + 1] - time_value)
                user_dict['unlock']['date'].update(
                    {level: time_value.strftime('%Y-%m-%d %H:%M:%S')})


    user_dict['unlock']['average'] = str(total_average_time / len(radical_unlock_data.keys()))


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
        user['unlock'] = {}

        start_date = datetime.datetime.fromtimestamp(api_info['user_information']['creation_date'])
        start_date = start_date.strftime('%Y-%m-%d %H:%M:%S') + \
                     " (" + str((datetime.datetime.now() - start_date).days) + " days ago)"
        user['unlock']['start_date'] = start_date

        r_info = get_radical_information(get_api_information(api_key, "radicals"), {})
        v_info = get_vocab_information(get_api_information(api_key, "vocab"), {})
        get_user_unlock_time(user, r_info, v_info)
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
    datetime.datetime.now()

    return user
def test_vocab_list():
    url = "https://www.wanikani.com/api/v1.4/user/c9d088f9a75b0648b3904ebee3d8d5fa/vocabulary/33"
    info = requests.get(url).json()
    time = {}
    for character_ in info['requested_information']:
        if character_['user_specific'] is not None:
            if character_['level'] not in time.keys():
                time[character_['level']] = []
            time[character_['level']].append(datetime.datetime.fromtimestamp(character_['user_specific']['unlocked_date']))
    #print(time)
    for t in sorted(time[33]):
        print(t)



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
        if r.status_code == 200:
            logger.info('successful api call with status code: {}'.format(r.status_code))
            return r.json()
        else:
            logger.error("Error while making the api call with status code: {}".format(r.status_code))
            raise BadRequestException("Error while making the request")
    except Exception:  # Need to check what type of exceptions requests will throw, may not be needed at all
        pass



if __name__ == '__main__':
    #test_vocab_list()
    get_user_unlock_time({},{1: None, 2: None, 3: datetime.datetime(2016, 5, 6, 18, 56, 1), 4: datetime.datetime(2016, 5, 22, 0, 33, 27), 5: datetime.datetime(2016, 6, 16, 15, 59, 52), 6: datetime.datetime(2016, 7, 2, 11, 27, 49), 7: datetime.datetime(2016, 7, 17, 19, 6, 27), 8: datetime.datetime(2016, 7, 31, 19, 40, 21), 9: datetime.datetime(2016, 8, 15, 20, 32, 35), 10: datetime.datetime(2016, 9, 3, 11, 47, 25), 11: datetime.datetime(2016, 9, 15, 22, 12, 8), 12: datetime.datetime(2016, 9, 28, 18, 28, 7), 13: datetime.datetime(2016, 10, 10, 23, 44), 14: datetime.datetime(2016, 10, 22, 14, 15, 35), 15: datetime.datetime(2016, 11, 2, 17, 18, 51), 16: datetime.datetime(2016, 11, 16, 14, 32, 47), 17: datetime.datetime(2016, 11, 26, 17, 0, 42), 18: datetime.datetime(2016, 12, 9, 0, 29, 32), 19: datetime.datetime(2016, 12, 21, 21, 23, 14), 20: datetime.datetime(2017, 1, 9, 18, 21, 19), 21: datetime.datetime(2017, 1, 26, 20, 56, 42), 22: datetime.datetime(2017, 2, 11, 20, 25, 44), 23: datetime.datetime(2017, 2, 28, 16, 5, 24), 24: datetime.datetime(2017, 3, 29, 23, 38, 11), 25: datetime.datetime(2017, 4, 13, 1, 9, 51), 26: datetime.datetime(2017, 5, 4, 22, 33, 18), 27: datetime.datetime(2017, 5, 14, 11, 26, 10), 28: datetime.datetime(2017, 5, 26, 1, 43, 1), 29: datetime.datetime(2017, 6, 14, 19, 46, 9), 30: datetime.datetime(2017, 7, 11, 23, 5, 17), 31: datetime.datetime(2017, 7, 28, 1, 0, 45), 32: datetime.datetime(2017, 8, 17, 0, 10, 8), 33: datetime.datetime(2017, 9, 2, 11, 8, 39), 34: datetime.datetime(2017, 9, 23, 14, 39, 31), 35: datetime.datetime(2017, 12, 11, 22, 20, 54), 36: datetime.datetime(2017, 12, 29, 22, 54, 7), 37: datetime.datetime(2018, 1, 11, 13, 9, 24), 38: datetime.datetime(2018, 1, 20, 23, 54, 51), 39: datetime.datetime(2018, 1, 29, 12, 55, 26)},
                         {1: [1461564168, 1461474798, 1461638257, 1461638257, 1461474745, 1461474757, 1461474798,
                              1461474822, 1461474822, 1461474906, 1461474906, 1461474906, 1461474906, 1461474906,
                              1461474906, 1461474700, 1461474745, 1461474757, 1461474768, 1461474700, 1461474798,
                              1461474787, 1461474798, 1461474868, 1461474881, 1461474906, 1461474906, 1461638257,
                              1461638257, 1461638808, 1461638938, 1461638938, 1461807368, 1461807367, 1461807368,
                              1461474804, 1461474787, 1461474881, 1461474700, 1461474805, 1461474868, 1461638506],
                          2: [1462407365, 1462573987, 1462574827, 1462574707, 1462334461, 1462574737, 1462563172,
                              1462574737, 1462563162, 1462575360, 1462334563, 1462574827, 1462576028, 1461969485,
                              1462563172, 1462563162, 1462575190, 1461638938, 1461807368, 1461896037, 1461896037,
                              1461896263, 1461896263, 1461896037, 1461896263, 1461969485, 1461969485, 1461969505,
                              1461969176, 1461969485, 1461969485, 1461969485, 1461969485, 1461969505, 1462161214,
                              1462407365, 1462562676, 1462562682, 1462562682, 1462562682, 1462562682, 1462562656,
                              1462562656, 1462562682, 1462562706, 1462562706, 1462574827, 1462575335, 1462575335,
                              1462575360, 1462575360, 1462574652, 1462574713, 1462574737, 1462574707, 1462574827,
                              1462574827, 1462575187, 1462575241, 1462575241, 1462575298, 1462575360, 1462836614,
                              1463100032, 1461969287, 1461969485, 1461969485, 1462334563, 1462334563, 1462562616,
                              1462563183, 1462563162, 1462563183, 1462573849, 1462573849, 1462573854, 1462573987,
                              1462574652, 1462574652, 1462574827, 1462574652, 1462574737, 1462574827, 1462575204,
                              1462575190, 1462575190, 1462575190, 1462575204, 1462836614],
                          3: [1463632547, 1463182245, 1463632980, 1463632980, 1463632679, 1463537993, 1463632581,
                              1463632735, 1463632843, 1463632547, 1463632747, 1463632987, 1463632679, 1463182006,
                              1463632581, 1463182006, 1463268188, 1462575361, 1462575361, 1462575361, 1463158211,
                              1463158211, 1463158496, 1463158517, 1463181277, 1463181378, 1463181277, 1463181277,
                              1463181277, 1463182006, 1463182212, 1463182212, 1463182271, 1463264273, 1463268188,
                              1463268188, 1463891777, 1463891777, 1463892586, 1462575361, 1463158211, 1463158517,
                              1463181378, 1463181277, 1463181378, 1463182007, 1463264159, 1463264159, 1463264159,
                              1463268188, 1463538024, 1463538066, 1463538066, 1463537985, 1463538024, 1463538079,
                              1463538079, 1463538102, 1463632547, 1463632547, 1463632528, 1463632547, 1463632679,
                              1463632747, 1463632735, 1463632735, 1463632747, 1463632917, 1463632986, 1463891606,
                              1463891777, 1463891777],
                          4: [1465616344, 1465597724, 1465872364, 1466219399, 1465265554, 1465265598, 1465265573,
                              1466814382, 1466633958, 1466633958, 1466633958, 1465616275, 1466107192, 1465265598,
                              1466814383, 1466814383, 1466814383, 1465695229, 1465597664, 1465597633, 1463891607,
                              1465265649, 1465779979, 1465690856, 1465695229, 1465616344, 1465616344, 1465265598,
                              1465265684, 1465695229, 1465265598, 1463891607, 1463891607, 1463891607, 1463891607,
                              1463891607, 1465265566, 1465265514, 1465265514, 1465265630, 1465265649, 1465597664,
                              1465597744, 1465616275, 1465616344, 1465690856, 1465695229, 1465695229, 1465779979,
                              1465779801, 1465953467, 1465953629, 1465953614, 1465953568, 1466107192, 1466814383,
                              1466814383, 1466814383, 1466814382, 1463891607, 1465265573, 1465265573, 1465265573,
                              1465265573, 1465265598, 1465265598, 1465265649, 1465265649, 1465265649, 1465265649,
                              1465265554, 1465265566, 1465265649, 1465265684, 1465265740, 1465349280, 1465597633,
                              1465597692, 1465597724, 1465597697, 1465597692, 1465597724, 1465597697, 1465616275,
                              1465616275, 1465616344, 1465616361, 1465690989, 1465695229, 1465695229, 1465779678,
                              1465779747, 1465779801, 1465779977, 1465779979, 1465780076, 1465780076, 1465872364,
                              1465872364, 1465953467, 1465953629, 1465953568, 1466814383, 1466814382, 1466814383],
                          5: [1467331530, 1467164552, 1467164609, 1467216706, 1467164552, 1467330770, 1466730648,
                              1466730632, 1466730649, 1466730429, 1466730640, 1467164634, 1467164581, 1467164581,
                              1467164559, 1466730433, 1467164637, 1467164637, 1467164608, 1467164608, 1467164553,
                              1467164553, 1467330770, 1467330770, 1467330770, 1466905675, 1466730654, 1466814753,
                              1466814753, 1466814753, 1466730654, 1467216885, 1467642751, 1466730654, 1467164553,
                              1466107192, 1467330770, 1466730461, 1467473827, 1466730447, 1469056289, 1467164552,
                              1467216885, 1467164615, 1466107192, 1466905506, 1466905675, 1466905674, 1466905675,
                              1467164664, 1466107192, 1466107192, 1466107192, 1466730398, 1466730461, 1466730670,
                              1466730654, 1466730461, 1466730461, 1466730670, 1466730670, 1466814272, 1466814272,
                              1466814272, 1466814383, 1466814517, 1466814517, 1466814753, 1466814517, 1467164552,
                              1467164576, 1467164609, 1467164576, 1467164552, 1467164552, 1467164576, 1467164581,
                              1467164576, 1467164609, 1467164615, 1467164615, 1467164664, 1467164660, 1467164664,
                              1467164689, 1467164615, 1467216406, 1467216406, 1467216406, 1467216706, 1467330714,
                              1467330714, 1467330770, 1467330770, 1467330770, 1467331530, 1467473268, 1467473827,
                              1467474629, 1467642751, 1467642751, 1469056289, 1466107192, 1466107192, 1466107192,
                              1466107192, 1466107192, 1466107192, 1466730398, 1466730427, 1466730447, 1466730632,
                              1466730634, 1466730634, 1466730640, 1466730670, 1466814517, 1466814671, 1466814753,
                              1466814753, 1466814753, 1467164552, 1467164637, 1467216406, 1467216885, 1467164615],
                          6: [1468538920, 1467473268, 1468023146, 1468281617, 1468538862, 1468195953, 1468538868,
                              1468538868, 1468023336, 1469055346, 1468023272, 1468023271, 1468023109, 1468023272,
                              1468023109, 1468023109, 1468023272, 1468023109, 1468796786, 1468195953, 1468195953,
                              1468195953, 1468796786, 1468195852, 1468796552, 1468796552, 1468195912, 1468538746,
                              1468195912, 1468538868, 1468195912, 1468723850, 1468154684, 1468023336, 1467473268,
                              1468538920, 1468154684, 1468023146, 1468195953, 1468976997, 1467473268, 1467474629,
                              1468195953, 1468195953, 1468154684, 1467473269, 1467473269, 1467473269, 1467473268,
                              1467473268, 1467473268, 1467473268, 1467473268, 1467473268, 1467473268, 1467473268,
                              1468022888, 1468022888, 1468023032, 1468023199, 1468023200, 1468022888, 1468022888,
                              1468023032, 1468023200, 1468023249, 1468023336, 1468023249, 1468023431, 1468154147,
                              1468154174, 1468154684, 1468154684, 1468154684, 1468154877, 1468195826, 1468195912,
                              1468195953, 1468195953, 1468281617, 1468538840, 1468538620, 1468538840, 1468538862,
                              1468538920, 1468538868, 1468647663, 1468723838, 1468723850, 1468723833, 1468723833,
                              1468796537, 1468796537, 1468796626, 1468796781, 1468796781, 1468796867, 1468796781,
                              1468796786, 1468796867, 1469055689, 1469055346, 1469055689, 1467473268, 1467473268,
                              1468023199, 1468023147, 1468154147, 1468154147, 1468154877, 1468195852, 1468538620,
                              1468538816, 1468538920, 1468796719, 1468796719, 1468796867, 1468796867],
                          7: [1469666811, 1468796787, 1498685320, 1469586177, 1469586177, 1469401243, 1469919828,
                              1469315538, 1468796787, 1470008388, 1470196971, 1469401204, 1469578319, 1469919828,
                              1470008368, 1470008388, 1470008419, 1469672431, 1470008419, 1469315538, 1468796787,
                              1468796787, 1469665339, 1470538949, 1468796787, 1470018251, 1468796787, 1468796787,
                              1468796787, 1470196971, 1468796787, 1468796787, 1469666811, 1469672423, 1469672423,
                              1469672431, 1469672468, 1469672470, 1469672468, 1469672470, 1469578533, 1468796787,
                              1468796787, 1468796787, 1468796787, 1468796787, 1468796787, 1468796787, 1468796787,
                              1468796787, 1468796787, 1468796787, 1468796787, 1468796787, 1468796787, 1469315379,
                              1469315484, 1469315396, 1469315396, 1469315396, 1469315379, 1469315538, 1469315538,
                              1469315538, 1469320591, 1469320662, 1469397958, 1469397958, 1469401223, 1469401301,
                              1469401223, 1469401243, 1469401301, 1469401301, 1469578533, 1469578533, 1469578319,
                              1469578533, 1469665154, 1469665154, 1469665501, 1469665501, 1469665339, 1469665501,
                              1469665501, 1469666736, 1469666736, 1469752635, 1469752635, 1469752739, 1469752635,
                              1469753192, 1470008368, 1470008368, 1470538949, 1468796787, 1468796787, 1468796787,
                              1469315538, 1469315484, 1469315484],
                          8: [1470661356, 1470660915, 1471488101, 1471307741, 1471307554, 1471307554, 1471307741,
                              1471307741, 1471307741, 1471307741, 1471307741, 1470008420, 1470008421, 1470661407,
                              1471051921, 1470008420, 1470008420, 1471052025, 1471052025, 1471052093, 1470008421,
                              1470661356, 1470008421, 1470921027, 1470660968, 1471052124, 1470661356, 1470661356,
                              1471488101, 1471488101, 1470660915, 1470920122, 1471052124, 1470921027, 1471051871,
                              1470008420, 1471051899, 1470008420, 1470627077, 1470660887, 1470008421, 1470008420,
                              1470661116, 1471488101, 1470627077, 1470965569, 1470964991, 1471488101, 1471052093,
                              1470661116, 1470008421, 1470008421, 1470008421, 1470008421, 1470008420, 1470008420,
                              1470008420, 1470008420, 1470008420, 1470008420, 1470008420, 1470008420, 1470008420,
                              1470008420, 1470008420, 1470008420, 1470008420, 1470008420, 1470008420, 1470008420,
                              1470008420, 1470008420, 1470627077, 1470660887, 1470660893, 1470660893, 1470660915,
                              1470660915, 1470660915, 1470660949, 1470660949, 1470660968, 1470660887, 1470660949,
                              1470660949, 1470661116, 1470661116, 1470661116, 1470661356, 1470661407, 1470661356,
                              1470661407, 1470661407, 1470661435, 1470705565, 1470705565, 1470705472, 1470705565,
                              1470920122, 1470920122, 1470920122, 1470920283, 1470920122, 1470920122, 1470920122,
                              1470920283, 1470964992, 1470964992, 1470965569, 1470964991, 1470965207, 1470965207,
                              1471051921, 1471052063, 1471052063, 1471052105, 1471052124, 1471052124, 1471051899,
                              1471051921, 1471052063, 1471052124, 1471306901, 1471306901, 1471307554, 1471307957,
                              1471488101, 1471488101, 1471307554, 1470008421, 1470008420, 1470008420, 1470660968,
                              1470964991, 1471052093, 1470705565],
                          9: [1472085346, 1471307555, 1472918806, 1471307555, 1472914069, 1471828205, 1471828205,
                              1471828278, 1471883895, 1472084754, 1472085034, 1472085697, 1471307555, 1471307555,
                              1471307555, 1471828285, 1471883895, 1471883895, 1471884196, 1471884196, 1471884015,
                              1471884035, 1472085346, 1472914363, 1472918579, 1472341473, 1472341470, 1472914069,
                              1472085034, 1472737872, 1472913952, 1472918806, 1472918806, 1472919784, 1472919784,
                              1472914363, 1472914069, 1472914069, 1471307555, 1472918579, 1471307555, 1472919784,
                              1471884196, 1472341360, 1472085486, 1472085486, 1471307555, 1471307555, 1472341331,
                              1472737872, 1471883895, 1471883895, 1472085034, 1472914363, 1471307555, 1471883901,
                              1472738036, 1471883901, 1472084754, 1471884197, 1472738036, 1471884196, 1472914069,
                              1472341473, 1472737872, 1472918579, 1471307555, 1471828199, 1472914363, 1472341360,
                              1471307555, 1472341360, 1472341360, 1472341360, 1472341473, 1472341473, 1472341473,
                              1471884267, 1472914363, 1472918806, 1471307555, 1471307555, 1471307555, 1471307555,
                              1471307555, 1471307555, 1471828100, 1471828240, 1471828240, 1471828254, 1471828278,
                              1471884197, 1471883895, 1471883895, 1471884035, 1471884035, 1471884267, 1472085066,
                              1472085697, 1472084754, 1472339289, 1472339289, 1472341335, 1472339289, 1472341360,
                              1472341470, 1472914363, 1472914363, 1472914363, 1472914363, 1472917644, 1472918806,
                              1472919784, 1472918806, 1472914363, 1471884035, 1471884035, 1472341335, 1471828285],
                          10: [1473567378, 1474225999, 1473566919, 1473784537, 1473907101, 1472917645, 1473907350,
                               1473462871, 1472917645, 1473463109, 1473991744, 1473991717, 1473463109, 1473463109,
                               1473463109, 1473463109, 1473463109, 1473567019, 1473784078, 1473784078, 1473784078,
                               1474125126, 1472917645, 1472917645, 1473463109, 1472917645, 1473566919, 1473462819,
                               1473826262, 1473567292, 1473900200, 1473871603, 1475101580, 1473567378, 1473991744,
                               1472917645, 1473991623, 1473567292, 1472917645, 1473991812, 1473991927, 1473463109,
                               1473566953, 1472917645, 1473991812, 1473991927, 1473784078, 1475101580, 1473991812,
                               1473826069, 1472917645, 1472917645, 1472917645, 1472917645, 1472917645, 1472917645,
                               1472917645, 1472917645, 1472917645, 1472917645, 1472917645, 1473462819, 1473463164,
                               1473463164, 1473462819, 1473462871, 1473463022, 1473463022, 1473463022, 1473567019,
                               1473567292, 1473567378, 1473566749, 1473567019, 1473567292, 1473567292, 1473567378,
                               1473826069, 1473826069, 1473826069, 1473826069, 1473826262, 1473826262, 1473871424,
                               1473900327, 1473900327, 1473900200, 1473900327, 1473907101, 1473907350, 1473991623,
                               1473991537, 1473991537, 1473991579, 1473991579, 1473991623, 1473991656, 1473991656,
                               1473991717, 1473991656, 1473991717, 1473991717, 1473991717, 1473991744, 1473991789,
                               1473991914, 1473991927, 1473991914, 1475101580, 1475101580, 1472917645, 1472917645,
                               1472917645, 1473566747, 1473566747, 1473566747, 1473566747],
                          11: [1474850314, 1474650045, 1474840333, 1474511968, 1475101170, 1473991927, 1473991927,
                               1473991927, 1473991928, 1473991928, 1473991927, 1473991928, 1473991927, 1474850183,
                               1475015853, 1474840282, 1474840282, 1474840282, 1474840282, 1474840418, 1475773820,
                               1475100945, 1475101170, 1474511655, 1475773821, 1474850314, 1473991927, 1474511693,
                               1475101170, 1474840282, 1474511751, 1475252484, 1474511751, 1475101686, 1475101686,
                               1474840327, 1473991927, 1473991928, 1474840288, 1474650836, 1474511347, 1474650039,
                               1474650045, 1474650039, 1474650045, 1474650096, 1474850160, 1474940127, 1498683747,
                               1475252484, 1474511693, 1473991927, 1473991927, 1474511347, 1474650836, 1474511347,
                               1473991928, 1475100945, 1474840333, 1473991928, 1475015853, 1474650836, 1475100945,
                               1474850151, 1474940268, 1473991927, 1474650040, 1473991928, 1473991928, 1474840236,
                               1475101452, 1475101170, 1474940268, 1474850152, 1475101686, 1474511430, 1473991927,
                               1473991927, 1475773820, 1473991927, 1475100945, 1473991928, 1473991927, 1473991927,
                               1473991927, 1473991927, 1473991927, 1473991927, 1473991927, 1474511347, 1474511347,
                               1474511656, 1474511395, 1474511347, 1474511791, 1474511656, 1474512193, 1474674178,
                               1474840327, 1474840236, 1474840236, 1474840236, 1474850314, 1474850160, 1474850362,
                               1475101218, 1475101218, 1475101218, 1475101452, 1475101989, 1475101989, 1475773820,
                               1473991928, 1474511347, 1474511693, 1474650039, 1474650039, 1474650039, 1474674178,
                               1474674029, 1474674029, 1474840236, 1475015853, 1475252484, 1473991927, 1475101452],
                          12: [1476058782, 1476625788, 1475101687, 1475786600, 1475972215, 1475101687, 1476058782,
                               1475715216, 1475715375, 1475101687, 1475101687, 1475715231, 1475715216, 1475715231,
                               1475972215, 1476058883, 1476228346, 1475714833, 1475786600, 1475860031, 1475814436,
                               1476058782, 1475786600, 1475814586, 1498682260, 1475786700, 1475101687, 1475715375,
                               1475714708, 1475714708, 1475693596, 1475972215, 1475101687, 1475101687, 1475101687,
                               1476228346, 1475693314, 1475693327, 1475687160, 1475687160, 1475705987, 1475705986,
                               1475714856, 1475786600, 1475786700, 1476058955, 1476047111, 1476047172, 1476047210,
                               1476047210, 1476047210, 1475714915, 1475786600, 1476227567, 1475786700, 1475101687,
                               1476625788, 1475714833, 1476058883, 1475693643, 1475714856, 1475714833, 1476058883,
                               1475972239, 1475101687, 1476625788, 1476227567, 1475693327, 1475693596, 1476058959,
                               1475101687, 1475786700, 1475860031, 1475693314, 1476047172, 1475687160, 1475693327,
                               1476047485, 1476138361, 1475714833, 1475101687, 1475101687, 1475101687, 1475101687,
                               1475101687, 1475101687, 1475101687, 1475101687, 1475101687, 1475101687, 1475101687,
                               1475101687, 1475101687, 1475101687, 1475101687, 1475705987, 1475705986, 1475705987,
                               1475693327, 1475693447, 1475693327, 1475693354, 1475693447, 1475714708, 1475714833,
                               1475714833, 1475715084, 1475715084, 1475714914, 1475715216, 1475715084, 1475715375,
                               1475814436, 1475814586, 1475814586, 1475972239, 1475972239, 1475972239, 1475972276,
                               1476058782, 1476058955, 1476157439, 1475101687, 1475101687, 1475101687, 1475714708,
                               1475715216, 1475101687, 1476138361],
                          13: [1477070782, 1477159829, 1476157439, 1477003083, 1476808246, 1477160493, 1476157439,
                               1476808146, 1477069717, 1476764533, 1477773388, 1476882428, 1477422495, 1476157439,
                               1476674408, 1476674408, 1476808610, 1477002966, 1477098905, 1477098905, 1477098864,
                               1477098864, 1476660033, 1476808610, 1476882428, 1477003083, 1476918807, 1476157439,
                               1476157439, 1477069717, 1476808246, 1477002867, 1476157439, 1476157439, 1477070782,
                               1476660046, 1476659761, 1476659761, 1476674682, 1476674667, 1476674667, 1476808167,
                               1476808167, 1476808350, 1476808350, 1476882428, 1477069717, 1476764386, 1477070764,
                               1477070782, 1477160135, 1477160117, 1476808167, 1477773388, 1477422495, 1477159976,
                               1476674667, 1476157439, 1476157440, 1476157439, 1477002966, 1477159829, 1477069717,
                               1477160009, 1477098864, 1477069717, 1477070782, 1476157439, 1477773388, 1476808246,
                               1476808350, 1476157439, 1476157439, 1476764386, 1476157440, 1476157440, 1476157440,
                               1476157440, 1476157439, 1476157439, 1476157439, 1476660033, 1476674408, 1476674408,
                               1476674682, 1476674689, 1476764533, 1476808547, 1476808146, 1476808350, 1476808610,
                               1476882428, 1476918807, 1477002966, 1477003083, 1477003083, 1477070596, 1477070764,
                               1477070782, 1477069717, 1477069717, 1477069849, 1477070782, 1477098864, 1477159994,
                               1477160117, 1477160493, 1476157439, 1476659761, 1477002867, 1477002867, 1477069717,
                               1477070764, 1477159976, 1476157439],
                          14: [1477160135, 1477160135, 1477755450, 1478121118, 1477722770, 1477160135, 1477755255,
                               1478121568, 1477722770, 1478886243, 1477755657, 1477755557, 1478121568, 1477723201,
                               1478119352, 1477864982, 1477722770, 1477160135, 1477755644, 1477723598, 1477160135,
                               1477160135, 1477932184, 1477864982, 1477865955, 1477865619, 1477160135, 1478121529,
                               1477160135, 1477160135, 1477722881, 1477932573, 1477160135, 1477160135, 1477160135,
                               1477160135, 1477865582, 1477865619, 1477160135, 1477723598, 1478121529, 1477723659,
                               1477755644, 1477755644, 1478121118, 1478053892, 1477723659, 1477160135, 1478121568,
                               1477723659, 1477755255, 1477755644, 1477755644, 1478121365, 1477932185, 1477723623,
                               1477932573, 1477932573, 1477160135, 1478121118, 1477160135, 1478121365, 1477865955,
                               1477723201, 1478121365, 1478119352, 1478525575, 1478121365, 1477160135, 1477160135,
                               1478121365, 1478525575, 1477755657, 1477160135, 1477160135, 1478886243, 1477160135,
                               1477723659, 1477755255, 1477932184, 1477755709, 1478525575, 1478525575, 1477864982,
                               1477160135, 1478119341, 1477160135, 1477865955, 1477160135, 1477865619, 1477755450,
                               1478121349, 1477160135, 1477160135, 1477160135, 1477160135, 1477160135, 1477160135,
                               1477160135, 1477722770, 1477722770, 1477723203, 1477723598, 1477723201, 1477723201,
                               1477723623, 1477723658, 1477864982, 1477932573, 1478119341, 1477160135, 1477160135,
                               1477723040, 1477723623, 1477755644, 1477932185],
                          15: [1478121530, 1478121530, 1478979724, 1478979724, 1478121531, 1478121531, 1478121530,
                               1479456227, 1478979468, 1478121531, 1478979476, 1478939118, 1478939118, 1478939118,
                               1478939342, 1478980066, 1479070879, 1479324766, 1479070542, 1478121531, 1478979468,
                               1478980066, 1479183703, 1478121531, 1478979724, 1478979476, 1479456227, 1478939286,
                               1478939118, 1478939127, 1478939193, 1498678956, 1478121531, 1478121531, 1478884123,
                               1478121530, 1478121530, 1478979854, 1478121530, 1478121531, 1478121530, 1478121531,
                               1478884123, 1478939066, 1478939118, 1478979476, 1478979653, 1478979476, 1478979476,
                               1478979724, 1478979724, 1479069606, 1479324766, 1479324748, 1479324748, 1479350185,
                               1478979476, 1479662290, 1478121530, 1478979724, 1478939342, 1478979787, 1478979717,
                               1479662290, 1478121531, 1478979724, 1478979476, 1479456227, 1478121531, 1478884123,
                               1478884868, 1478979468, 1478979787, 1478121530, 1478884298, 1478885633, 1478884298,
                               1478979787, 1478979468, 1479070917, 1478939286, 1479324766, 1478121531, 1478939278,
                               1478939342, 1478979717, 1479324766, 1478939342, 1478884868, 1478939161, 1478939286,
                               1478939342, 1478979476, 1479070542, 1479070917, 1479324766, 1478980058, 1478980058,
                               1478980058, 1479069992],
                          16: [1479832105, 1479831618, 1479857138, 1479324767, 1479832139, 1479324766, 1479324767,
                               1479831353, 1479831618, 1479919246, 1480186229, 1479324767, 1479324767, 1479832105,
                               1479832105, 1479858188, 1479858188, 1479919246, 1480125585, 1480186475, 1479831352,
                               1479857138, 1479832374, 1479935969, 1479857138, 1480186475, 1479324767, 1479919246,
                               1479832857, 1479324766, 1480186229, 1479324767, 1479831448, 1479324767, 1479935969,
                               1479919246, 1479831618, 1479324767, 1479324767, 1479324767, 1479324767, 1479858188,
                               1479832720, 1479324767, 1480186174, 1479832105, 1479324766, 1479746552, 1479749180,
                               1479831446, 1479831544, 1479832720, 1479832816, 1479857138, 1480197640, 1479324767,
                               1479832374, 1479832318, 1479831618, 1479324767, 1479324767, 1480306020, 1479831353,
                               1480186174, 1479324767, 1479324767, 1480306020, 1479919246, 1479746552, 1479832915,
                               1479857138, 1479832161, 1479831618, 1479832720, 1479832915, 1479832562, 1479832161,
                               1479832720, 1479832816, 1479832562, 1479831352, 1479935969, 1479324767, 1479832355,
                               1479919246, 1480197735, 1479832105, 1479324767, 1480186474, 1479324767, 1479749729,
                               1479832857, 1479832915, 1479831352, 1479832105, 1479832105, 1479832139, 1480186132,
                               1480186174, 1480197735, 1480197734, 1480304167, 1480304167, 1480306020, 1479749180,
                               1479831352, 1479832139, 1479832915, 1479832915, 1479857138, 1480186474, 1480186474,
                               1480186474, 1480186474, 1479858188, 1480186474, 1479831618],
                          17: [1481480557, 1481480557, 1480752364, 1481222082, 1480752364, 1480870408, 1480917868,
                               1480753124, 1480197641, 1480958772, 1480784842, 1480752321, 1480752522, 1480752522,
                               1480752522, 1480752992, 1480752992, 1480753125, 1480752992, 1480870049, 1480917429,
                               1480917592, 1480917868, 1480958619, 1481222081, 1481261623, 1480784842, 1480752522,
                               1480752992, 1480784842, 1480784842, 1480784842, 1480784842, 1480917592, 1480917592,
                               1480958771, 1481221774, 1480870796, 1480752104, 1481221334, 1480197641, 1481155412,
                               1480871736, 1480752104, 1481221334, 1481221774, 1480784842, 1480197641, 1480197641,
                               1480197641, 1480197641, 1480917429, 1481480557, 1480752321, 1481068860, 1480751728,
                               1481068860, 1480784426, 1480784426, 1480197641, 1480751728, 1480870049, 1480917868,
                               1481261838, 1480917429, 1480752522, 1481221334, 1480197641, 1480197641, 1480197641,
                               1480197641, 1480197641, 1480752522, 1480752522, 1480752992, 1480753124, 1480753124,
                               1480753124, 1480752522, 1480752992, 1480820655, 1480820655, 1480871741, 1480870408,
                               1480871736, 1480917592, 1480917868, 1480958771, 1480958619, 1480958619, 1481068965,
                               1481068945, 1481068965, 1481155288, 1481155412, 1481221334, 1481221334, 1481221774,
                               1481221774, 1481221334, 1481221774, 1481261838, 1481261838, 1481261370, 1480958619,
                               1480197641, 1480197641, 1480197641, 1480197641, 1480820655, 1480870796, 1480958771,
                               1481068861, 1481221334, 1481221334, 1481221334, 1481221334, 1481261838, 1481261838,
                               1481155412, 1480197641, 1480871736, 1480784842, 1481222082],
                          18: [1481950294, 1481951070, 1481261372, 1481950732, 1481865338, 1482373393, 1481950231,
                               1482943613, 1481950790, 1481865338, 1482334343, 1481864689, 1481261372, 1481261371,
                               1481261371, 1481261371, 1481865338, 1481950518, 1482116043, 1481865338, 1482056898,
                               1481950518, 1482373393, 1482373339, 1481950804, 1481864548, 1481865338, 1482116043,
                               1482373463, 1481261371, 1482373393, 1481261371, 1481261371, 1481261371, 1481261371,
                               1482943613, 1481261371, 1481261371, 1481864690, 1481864689, 1482372552, 1482373136,
                               1482254843, 1481261371, 1482373463, 1481261371, 1482373027, 1481261372, 1482116043,
                               1482373027, 1481261371, 1481950790, 1482372852, 1482254843, 1482115968, 1482373463,
                               1481950790, 1481261371, 1482204314, 1482373393, 1482372752, 1482373464, 1482373136,
                               1481864689, 1481261372, 1482056898, 1482373393, 1481261371, 1481261372, 1482116043,
                               1481261371, 1482115424, 1482204314, 1482372752, 1482372752, 1482115969, 1482288452,
                               1481864334, 1481261372, 1481261371, 1481261371, 1481261371, 1481261371, 1481864548,
                               1481950231, 1481950732, 1481950732, 1481950231, 1481950231, 1481950294, 1481950732,
                               1481950790, 1481950791, 1482115424, 1482115424, 1482204314, 1482254843, 1482334343,
                               1482334343, 1482334188, 1482334189, 1482372552, 1482372552, 1482373136, 1482373393,
                               1482373393, 1482373463, 1481261372, 1481261372, 1481261372, 1481261372, 1481261372,
                               1481261371, 1481261371, 1481261371, 1481261371, 1481261371, 1481261371, 1481261371,
                               1481950790, 1481950804, 1481951070, 1482056898, 1482288452, 1482334188, 1482334343,
                               1482334343, 1482334343, 1482373136, 1482373339, 1482373339, 1482943613, 1482943613,
                               1482334189, 1482373339],
                          19: [1484780740, 1482944935, 1482373393, 1484004080, 1482373393, 1482943657, 1483802535,
                               1482943964, 1483378225, 1483385429, 1484003457, 1482944935, 1482373393, 1482945362,
                               1482373393, 1483803505, 1482373393, 1482373393, 1482943696, 1483378225, 1483930540,
                               1482944229, 1482943964, 1483385073, 1482373393, 1483628613, 1483628613, 1483628613,
                               1483680766, 1483802064, 1483802064, 1483802535, 1483802535, 1483929417, 1483929417,
                               1483929417, 1483929417, 1483929417, 1483930539, 1483384303, 1484004080, 1484005339,
                               1483680766, 1484780740, 1483378225, 1484523306, 1484003457, 1483378734, 1482944056,
                               1484005339, 1483384303, 1483802535, 1483802064, 1483385429, 1482943734, 1483378734,
                               1482373393, 1483385073, 1482944935, 1482944056, 1482943964, 1482373393, 1482373393,
                               1483385073, 1484523306, 1482943657, 1483985885, 1483929417, 1484004081, 1483378225,
                               1484005339, 1483929417, 1483628613, 1484003457, 1483929417, 1483384303, 1483680766,
                               1483628613, 1484005339, 1482943657, 1482945008, 1482373393, 1482373393, 1482373393,
                               1482944229, 1482943734, 1482944935, 1483384303, 1483803505, 1484003457, 1482944307,
                               1482944307, 1482944307, 1482944307, 1482945007, 1482945007, 1483385429, 1483985885,
                               1482944057, 1482944057, 1482944056, 1482944307, 1482945273, 1483628613, 1483628613,
                               1482943954],
                          20: [1485102876, 1484955264, 1485396500, 1485396500, 1485629634, 1484955088, 1485833774,
                               1485208899, 1484884216, 1485102778, 1484882597, 1484884739, 1484004079, 1484004079,
                               1484004079, 1484004079, 1484004079, 1484004079, 1486088376, 1485833774, 1485629634,
                               1485102828, 1484885158, 1484004079, 1486088376, 1484785850, 1484786624, 1484786735,
                               1484786774, 1484882598, 1484884216, 1484884233, 1484884738, 1484884739, 1484885141,
                               1484885158, 1485833774, 1484955088, 1484955272, 1484955272, 1485102778, 1485102778,
                               1485102828, 1485102828, 1485102828, 1485103484, 1484004079, 1485102876, 1485394095,
                               1485394095, 1485394095, 1485394095, 1485833774, 1484884193, 1482943613, 1486088376,
                               1485396500, 1485833774, 1485394095, 1484785850, 1485629634, 1484884316, 1484785850,
                               1486088376, 1486088376, 1484004079, 1484786624, 1484884216, 1485103484, 1485482203,
                               1485629634, 1484955088, 1484884316, 1485102876, 1484884216, 1485482203, 1484885155,
                               1485102778, 1485102877, 1484786774, 1485103484, 1484955273, 1485102876, 1484884739,
                               1484955272, 1484781439, 1484004079, 1484786624, 1484882597, 1484955272, 1486088376,
                               1485208899, 1484785850, 1485305583, 1484786736, 1484004079, 1484004079, 1484004079,
                               1484004079, 1484004079, 1484004079, 1484004079, 1484004079, 1485629634, 1484004079,
                               1484004079, 1484781439, 1484781439, 1484882597, 1484884193, 1486088376, 1485102778,
                               1484955272, 1484786774],
                          21: [1486862902, 1485482202, 1486848279, 1486604812, 1486840032, 1486847133, 1486605102,
                               1486862836, 1485482202, 1486603198, 1486598333, 1486848249, 1486862745, 1486489970,
                               1486603103, 1485482202, 1485482202, 1485482202, 1485482202, 1485482202, 1485482202,
                               1486862902, 1486429535, 1485482202, 1485482202, 1486431517, 1486598333, 1486604812,
                               1485482202, 1485482202, 1486848279, 1485482202, 1486431517, 1485482202, 1486269672,
                               1486221979, 1486223128, 1485482202, 1486848249, 1486423899, 1486423899, 1486429535,
                               1486429535, 1486430617, 1486430617, 1486489825, 1486598333, 1485482202, 1486840635,
                               1486848279, 1486862745, 1486862745, 1487129737, 1485482202, 1486848280, 1486862837,
                               1486840032, 1486490070, 1486848250, 1486489969, 1486269864, 1486862837, 1486269672,
                               1486839938, 1486848279, 1486489961, 1486269864, 1486490070, 1486223128, 1485482202,
                               1486848249, 1485482202, 1486847231, 1486862837, 1486848279, 1486598333, 1486603198,
                               1486862745, 1486223128, 1487129737, 1486598333, 1486269354, 1485482202, 1485482202,
                               1486489825, 1486840635, 1486862902, 1486430617, 1486489970, 1486490070, 1486603103,
                               1486848249, 1485482202, 1486269354, 1486839938, 1485482202, 1485482202, 1485482202,
                               1486846807, 1486429535, 1486840032, 1486840032, 1485482202, 1486598333, 1486846807,
                               1486603198, 1486598333, 1486269672],
                          22: [1487902827, 1487723257, 1487871072, 1487810370, 1488226507, 1488315924, 1488226549,
                               1487483401, 1488744011, 1487723411, 1487573567, 1488315861, 1487574775, 1487573935,
                               1487723318, 1486862744, 1487574775, 1486862744, 1488740742, 1488744011, 1487483401,
                               1487785895, 1487573357, 1487573358, 1486862744, 1488955360, 1487723411, 1487573357,
                               1486862744, 1487723411, 1486862744, 1488740742, 1487574775, 1486862744, 1486862744,
                               1486862744, 1486862744, 1488226507, 1486862744, 1488744011, 1487573974, 1488744011,
                               1487724044, 1487574259, 1487574493, 1486862744, 1487809806, 1487573567, 1486862744,
                               1486862744, 1488744011, 1488226549, 1487871072, 1487810370, 1486862744, 1487723318,
                               1487483401, 1488226507, 1488226549, 1487785588, 1486862744, 1487573567, 1487809490,
                               1487573358, 1487723411, 1488955360, 1487573974, 1487573936, 1487574259, 1487574259,
                               1486862744, 1488226549, 1487809806, 1487574775, 1487785895, 1487573936, 1487723318,
                               1487809806, 1488740742, 1486862744, 1486862744, 1487723256, 1487810370, 1488744011,
                               1487483401, 1488315861, 1486862744, 1487573357, 1488315861, 1487723318, 1487902827,
                               1487573959, 1487573567, 1486862744, 1487785588, 1487793402, 1487723256, 1487724044,
                               1487573935, 1486862744, 1486862744, 1487809806, 1488744011, 1487574775, 1488226549,
                               1487724044, 1488955360, 1487789900, 1487785895, 1486862744, 1484884193, 1486862744,
                               1487712596, 1487712596, 1487483401, 1487573358],
                          23: [1490845091, 1490550163, 1488315924, 1491283576, 1490845068, 1488315924, 1490549156,
                               1490548838, 1491283576, 1488315924, 1490845068, 1490549591, 1490845091, 1490762832,
                               1490762909, 1491532949, 1490762646, 1488315924, 1490549591, 1490762832, 1490550653,
                               1490762646, 1488315924, 1491788388, 1488315924, 1488315924, 1490550966, 1490845068,
                               1490547592, 1488315924, 1488315924, 1490550966, 1490762942, 1490550966, 1490547845,
                               1490547845, 1488315924, 1490240864, 1490240864, 1488315924, 1488315924, 1490547845,
                               1488315924, 1490763250, 1488315924, 1490550679, 1490546441, 1490547845, 1490549665,
                               1490762942, 1490762909, 1490550820, 1490761296, 1491532949, 1490845068, 1488315924,
                               1490546441, 1491283576, 1490550653, 1490845068, 1490763250, 1490550820, 1488315924,
                               1490240864, 1490547846, 1490761296, 1490546340, 1490550653, 1490845068, 1488315924,
                               1490845091, 1490240262, 1488315924, 1490845091, 1490322448, 1488315924, 1490239755,
                               1490240864, 1490322448, 1490322448, 1490240864, 1490240864, 1490547846, 1490548838,
                               1488315924, 1490550543, 1490546340, 1490549156, 1490550820, 1490762832, 1490549665,
                               1490762832, 1490550679, 1490550966, 1490550966, 1490845068, 1491788388, 1491532949,
                               1490549665],
                          24: [1492057651, 1491786871, 1491789363, 1491789248, 1491787033, 1491786883, 1492060191,
                               1491788893, 1491786871, 1491530963, 1491532660, 1490845091, 1491531523, 1491786871,
                               1491788640, 1492793885, 1491532660, 1492793886, 1492057650, 1492060521, 1490845091,
                               1491786634, 1491671098, 1491788953, 1492060521, 1491671067, 1492793886, 1492057701,
                               1491788729, 1492060321, 1491787718, 1492057651, 1491532661, 1492793886, 1492793886,
                               1491671067, 1490845091, 1491531523, 1490845091, 1491533148, 1491788893, 1491788907,
                               1491789248, 1492060521, 1491787718, 1492057701, 1491671098, 1491533148, 1491789363,
                               1490845091, 1490845091, 1491671098, 1491787718, 1492058091, 1491671067, 1491788907,
                               1491788640, 1490845091, 1490845091, 1492058266, 1490845091, 1491671067, 1492058091,
                               1491533148, 1490845091, 1491532661, 1491788198, 1491786882, 1491786634, 1491789363,
                               1490845091, 1492060521, 1490845091, 1492058266, 1491671067, 1490845091, 1492060321,
                               1492057651, 1492057702, 1490845091, 1492060191, 1491789133, 1490845091, 1491789248,
                               1492057651, 1491789248, 1490845091, 1491788640, 1492058091, 1491788953, 1491789363,
                               1491788907, 1491533148, 1490845091, 1492057651, 1491787107, 1491530963, 1491788953,
                               1491533148, 1490845091, 1490845091, 1491787033, 1492060192, 1492793885, 1491533148,
                               1492058266, 1491788913, 1491530963, 1492793885, 1492793886, 1491786882, 1491787036,
                               1492060192, 1491530963, 1491788892, 1491531523, 1490845091, 1491788640, 1490845091,
                               1492057650, 1491789133],
                          25: [1492060190, 1493692508, 1493691480, 1492060190, 1493434619, 1493257519, 1493259482,
                               1493075577, 1493258241, 1493618789, 1493692508, 1493692508, 1494118453, 1493434619,
                               1493331525, 1493331421, 1493259482, 1493830424, 1494118453, 1493331642, 1493692004,
                               1493434619, 1492060190, 1493951599, 1493052978, 1493618740, 1493692508, 1493331076,
                               1493691358, 1493257757, 1493332342, 1493691357, 1492060190, 1493618740, 1493436840,
                               1493331642, 1493331642, 1493830543, 1493436840, 1493435958, 1493436503, 1493331421,
                               1493829444, 1493332147, 1492060190, 1493951642, 1493691357, 1493052238, 1493692508,
                               1492060190, 1493436840, 1493436840, 1494262939, 1493258241, 1492060190, 1493692004,
                               1494118453, 1493258241, 1493435344, 1493258241, 1493951642, 1493257757, 1493258241,
                               1493436884, 1493436840, 1493618789, 1493258241, 1493691480, 1493691480, 1493691481,
                               1492060190, 1493331076, 1493331525, 1493257519, 1492060190, 1493436884, 1493331076,
                               1493829444, 1493692004, 1493435958, 1492060190, 1493332147, 1493434619, 1493436503,
                               1492060190, 1493435958, 1493829443, 1492060190, 1493951598, 1492060190, 1492060190,
                               1492060190, 1494262939, 1493258241, 1493259482, 1493052238, 1493075576, 1493830543,
                               1492060190, 1492060190, 1493052978],
                          26: [1493951598, 1494380630, 1494435953, 1494436671, 1493951598, 1493951598, 1493951598,
                               1494436460, 1494436460, 1494436703, 1495209535, 1493951598, 1495209535, 1494605371,
                               1494535131, 1494535131, 1493951598, 1493951598, 1493951598, 1494436526, 1494435953,
                               1493951598, 1493951598, 1494722176, 1494434924, 1494434924, 1494435953, 1494435207,
                               1494436671, 1494435429, 1494435953, 1494436739, 1494521930, 1494523370, 1494522468,
                               1494535130, 1493951598, 1494721904, 1493951598, 1493951598, 1494605844, 1494380388,
                               1494380603, 1494436739, 1494535130, 1493951598, 1494436526, 1493951598, 1494435953,
                               1493951598, 1494380603, 1494436739, 1498677438, 1494436739, 1495209535, 1494380603,
                               1494436526, 1494605371, 1494436671, 1494436739, 1494380630, 1494435429, 1494775570,
                               1494535062, 1493951598, 1493951598, 1494380388, 1494521930, 1494434789, 1494605212,
                               1495209535, 1494535130, 1494722176, 1493951598, 1493951598, 1493951598, 1493951598,
                               1493951598, 1493951598, 1493951598, 1494535062, 1494436170, 1494721904, 1494435429,
                               1495209535, 1494436671, 1494380630, 1494434924, 1494775571, 1494722176, 1494605212,
                               1494606317, 1494605212, 1494521930, 1493951598, 1494436349, 1494436170, 1494606317,
                               1494380603, 1494605844, 1494435953, 1494436460, 1494436671, 1494436703, 1494436703,
                               1494436739, 1494436739, 1494434554, 1494434604, 1494434604, 1494434924, 1494435429,
                               1494523221, 1494953116, 1494953115, 1495209535, 1495209535, 1495209535, 1495298383,
                               1495298383, 1494434789, 1494605211, 1494605371, 1493951598, 1494523221],
                          27: [1494775569, 1496025434, 1495559303, 1495848845, 1495301007, 1495559303, 1496025434,
                               1495777381, 1495299934, 1495300653, 1495559023, 1495298256, 1495672677, 1495472458,
                               1495473844, 1495558913, 1494775569, 1494775569, 1494775569, 1494775569, 1494775569,
                               1494775569, 1494775569, 1495673131, 1494775569, 1494775569, 1494775569, 1495672676,
                               1495383797, 1495472458, 1495300653, 1494775569, 1494775569, 1495298256, 1495559023,
                               1495559322, 1494775569, 1495849165, 1495558131, 1495673131, 1495473844, 1495558132,
                               1494775569, 1494775569, 1494775569, 1495472193, 1495849165, 1495777381, 1495777381,
                               1495559303, 1494775569, 1494775569, 1494775569, 1494775569, 1494775569, 1495301007,
                               1495472193, 1495849165, 1494775569, 1494775569, 1495849165, 1495473945, 1495383797,
                               1495299920, 1495299934, 1495473844, 1495777381, 1495559474, 1494775569, 1495473945,
                               1495299771, 1495298256, 1494775569, 1495473167, 1494775569, 1495672677, 1495299771,
                               1495299920, 1495301007, 1495384218, 1495385234, 1495472923, 1495473844, 1495473945,
                               1495474181, 1495474181, 1495558428, 1495558427, 1495558912, 1495559303, 1495559322,
                               1495559474, 1495559474, 1495672676, 1495673013, 1495673131, 1495777381, 1495672676,
                               1495473167, 1495848845, 1495848845, 1494775569, 1495559023, 1495559474, 1495472923,
                               1495301007, 1495473945],
                          28: [1496967147, 1495777380, 1497662438, 1496714833, 1497459302, 1496683105, 1496291299,
                               1496712455, 1495777380, 1495777380, 1495777380, 1495777380, 1497662438, 1496292311,
                               1496356754, 1496713501, 1497402038, 1496714833, 1496682649, 1497402038, 1496683105,
                               1496967147, 1495777380, 1495777380, 1495777380, 1496292067, 1495777380, 1495777380,
                               1496356465, 1496292601, 1495777380, 1497402038, 1497662438, 1495777380, 1497459302,
                               1496500425, 1496682649, 1495777380, 1496682649, 1496291299, 1495777380, 1495777380,
                               1496292067, 1496713501, 1497705182, 1495777380, 1496336248, 1495777380, 1496967147,
                               1495777380, 1496290401, 1496292332, 1497705182, 1496713501, 1496289644, 1496289716,
                               1495777380, 1496272821, 1496289779, 1496289780, 1496289780, 1496291286, 1496292335,
                               1496682649, 1496336248, 1496500370, 1496292332, 1496683105, 1496292601, 1496289644,
                               1496292601, 1496292067, 1495777380, 1495777380, 1495777380, 1495777380, 1496272821,
                               1496272820, 1496272821, 1496289716, 1496290401, 1496290988, 1496292311, 1496292332,
                               1496292332, 1496292335, 1496292601, 1496336481, 1496336481, 1496336501, 1496356754,
                               1496712455, 1496713501, 1496713501, 1497662438, 1497705181, 1496500370, 1497483971,
                               1497483971, 1496289716, 1496290988, 1496290988, 1496291286, 1496291299, 1496291299,
                               1496336248, 1496336249, 1496336480, 1496336501, 1496356754, 1496712455, 1495777380,
                               1496292067, 1496682649, 1496292335, 1495777380, 1495777380, 1496967147],
                          29: [1497483967, 1498627231, 1498063683, 1497483967, 1498627230, 1498627233, 1498627415,
                               1498627439, 1498627439, 1498090573, 1498090568, 1498627146, 1498627439, 1498627286,
                               1498627146, 1499615512, 1498627146, 1499053020, 1498151873, 1498627415, 1497483967,
                               1498091554, 1500059781, 1498627255, 1498627286, 1499445413, 1498091554, 1498627321,
                               1498962098, 1498627255, 1499053020, 1498627321, 1498627233, 1498090575, 1499616030,
                               1499137984, 1499615512, 1499616030, 1498627321, 1498091554, 1498090573, 1498090386,
                               1498090568, 1499746259, 1498090486, 1499615512, 1498090486, 1500059238, 1498090595,
                               1499828717, 1498151873, 1499826884, 1499826884, 1498090573, 1498090575, 1499447307,
                               1499445413, 1499746260, 1499826884, 1500059781, 1498090568, 1498090568, 1499053020,
                               1499746259, 1499137984, 1498090595, 1498090595, 1498627262, 1497483967, 1500059237,
                               1498151873, 1498627234, 1498627286, 1499447307, 1497483967, 1497483967, 1497483967,
                               1497483967, 1497483967, 1497483967, 1497483967, 1497483967, 1497483967, 1497483967,
                               1497483967, 1497709561, 1497483967, 1497483967, 1497483967, 1497483967, 1497483967,
                               1497483967, 1497483967, 1497483967, 1497483967, 1497483967, 1497483967, 1497483967,
                               1497483967, 1499137984, 1498090568, 1499447307, 1497483967, 1498627286, 1497483967,
                               1497483967, 1498962098, 1498090486],
                          30: [1500863611, 1499828717, 1500745812, 1500862416, 1500865119, 1501087784, 1500655438,
                               1500864784, 1500655438, 1500655438, 1500747483, 1500745725, 1500745795, 1500747483,
                               1500745725, 1500745795, 1500747483, 1500745795, 1500745872, 1500862732, 1500862732,
                               1500864784, 1500864858, 1500863611, 1500745725, 1500862416, 1500862416, 1500656440,
                               1500745871, 1500745674, 1501108594, 1501174249, 1501174249, 1501108594, 1500676542,
                               1501217771, 1501857949, 1501857236, 1501087784, 1501087667, 1501450584, 1501450584,
                               1501217772, 1501450584, 1500864784, 1499828717, 1500745470, 1500863611, 1500655438,
                               1499828717, 1501218046, 1501087975, 1501218046, 1501087667, 1500864922, 1500865119,
                               1500745725, 1500745674, 1501087784, 1501087667, 1500655438, 1500865119, 1501450584,
                               1501087975, 1500864858, 1500745674, 1500864858, 1499828717, 1501087759, 1500864921,
                               1500865119, 1501857949, 1501087759, 1500745871, 1501087759, 1500864784, 1499828717,
                               1500864921, 1500915234, 1501087667, 1501857237, 1500915234, 1499828717, 1499828717,
                               1499828717, 1500954441, 1501857236, 1501857949, 1499828717, 1499828717, 1499828717,
                               1499828717, 1499828717, 1499828717, 1499828717, 1500864858, 1501217771, 1499828717,
                               1500655571, 1500747483, 1500915234, 1499828717, 1501218046],
                          31: [1503319801, 1501218045, 1501218045, 1502243267, 1503167409, 1502668099, 1502245435,
                               1502549051, 1502470230, 1502552901, 1502246065, 1502244225, 1502242556, 1502246065,
                               1502551888, 1501218045, 1502552714, 1502246018, 1502943009, 1502552179, 1501218045,
                               1502244225, 1502549051, 1502668099, 1502245126, 1502549051, 1502552179, 1502243366,
                               1502246018, 1502943009, 1502729743, 1501218045, 1502729743, 1502943010, 1503319801,
                               1501218045, 1502044228, 1502774338, 1501218045, 1502246147, 1502551888, 1502242705,
                               1502728594, 1501218045, 1501218045, 1502055500, 1502244112, 1502044228, 1501218045,
                               1502242976, 1502244225, 1502244225, 1502243433, 1502243433, 1502245126, 1502245290,
                               1502245360, 1502246065, 1502549255, 1502243267, 1502242557, 1502242394, 1502243366,
                               1502246147, 1502245435, 1502245360, 1502942940, 1502942940, 1502943009, 1502943010,
                               1502246065, 1502943131, 1502728594, 1502728594, 1502729743, 1502942940, 1501218045,
                               1502552901, 1502549255, 1502728594, 1502243267, 1501218045, 1502943131, 1502242705,
                               1503319801, 1502242976, 1502055500, 1502668099, 1501218045, 1502245069, 1501218045,
                               1502242705, 1503167409, 1502245360, 1501218045, 1502242394, 1502549051, 1501218045,
                               1502245290, 1502245126, 1502243366, 1501218045, 1502470230, 1502243366, 1501218045,
                               1502552715, 1502774338, 1501218045, 1501218045, 1501218045, 1501218045, 1501218045,
                               1501218045],
                          32: [1504045968, 1504045968, 1504098226, 1504098226, 1504098226, 1500745725, 1500915234,
                               1504098138, 1501087667, 1501087975, 1503542071, 1503541951, 1504098226, 1501174249,
                               1503871694, 1503682688, 1500862417, 1504306637, 1503594575, 1501218046, 1501087667,
                               1503617876, 1503595068, 1500745725, 1503595068, 1503594575, 1504306637, 1504306637,
                               1503542071, 1504306637, 1503682431, 1503541951, 1503682704, 1501087784, 1503871236,
                               1501857949, 1501087759, 1503528408, 1503873918, 1503871357, 1503871357, 1503871376,
                               1503871376, 1503871376, 1503872803, 1504364924, 1503874042, 1503874042, 1503873918,
                               1503682578, 1503595068, 1503542071, 1500863611, 1503871669, 1503872803, 1503871669,
                               1503873481, 1503871694, 1503682688, 1501087667, 1503873918, 1504330373, 1503873015,
                               1504630874, 1503617876, 1504664770, 1504664770, 1503542071, 1503542071, 1504098138,
                               1503682430, 1503873481, 1503682704, 1503870742, 1503542071, 1503617876, 1503595067,
                               1503595069, 1504098226, 1503871356, 1503873055, 1503617876, 1501108594, 1503873918,
                               1503682704, 1504664770, 1503542071, 1503682688, 1503871236, 1501218046, 1504630874,
                               1504330373, 1503873015, 1503594361, 1503871376, 1503617876, 1504306637, 1500747483,
                               1503872803, 1503874042, 1501217772, 1501108594, 1501857237, 1501857237, 1501857949,
                               1503871236, 1503872680, 1503873015, 1503874042, 1504666770, 1496712456, 1503872680],
                          33: [1505839778, 1505839778, 1505839778, 1505839778, 1503319802, 1505582913, 1505407980,
                               1502668099, 1504980116, 1505839778, 1502552715, 1502470230, 1502668099, 1502668099,
                               1505149075, 1505148665, 1505235437, 1506101423, 1502055500, 1505221405, 1502942940,
                               1502245435, 1505149075, 1505221073, 1505221404, 1505135167, 1502244225, 1504980116,
                               1505320818, 1505320818, 1505321517, 1505321517, 1505321517, 1505321698, 1505322329,
                               1505321799, 1505322329, 1505321951, 1502245126, 1502245126, 1505321951, 1502245126,
                               1506191973, 1505321698, 1505407980, 1505408162, 1505408574, 1505408574, 1505494675,
                               1504980116, 1505575944, 1505575944, 1506101423, 1505494676, 1505221073, 1505582913,
                               1499615512, 1505494550, 1505754654, 1505754654, 1502470230, 1505321066, 1506193366,
                               1505322329, 1506193366, 1505321066, 1505320817, 1505408574, 1505754654, 1505320818,
                               1505575944, 1505321698, 1505149075, 1505235437, 1505408412, 1505147695, 1505575944,
                               1506711221, 1505494610, 1505321698, 1506707387, 1506707387, 1506707387, 1506707387,
                               1505321698, 1505494550, 1505321799, 1502942940, 1502943010, 1505235437, 1505408162,
                               1505575944, 1505754654, 1505408412, 1506191973, 1502245069, 1505407980, 1506193366,
                               1505221117, 1506711221, 1505135167, 1506711221, 1505135167],
                          34: [1512668647, 1503871694, 1510427990, 1508015621, 1512614380, 1510427990, 1510427990,
                               1511744529, 1508078168, 1508078169, 1508298478, 1508298478, 1508298478, 1508344391,
                               1508344365, 1503542071, 1511804572, 1508079242, 1508298478, 1513571138, 1508344391,
                               1511744530, 1508015621, 1508110483, 1503594361, 1501174250, 1503873918, 1508078168,
                               1513571138, 1508110483, 1508431831, 1507741216, 1511973324, 1511973324, 1511973383,
                               1511973383, 1511973383, 1511973383, 1501174249, 1508431831, 1503873918, 1508079242,
                               1512094766, 1512094767, 1512094766, 1512094767, 1512100507, 1512100507, 1512100507,
                               1507826879, 1503528408, 1512333931, 1512410335, 1512410335, 1512410336, 1512497455,
                               1512497455, 1512497455, 1512497455, 1512668647, 1512668647, 1512613194, 1512614379,
                               1512614379, 1512614379, 1512614380, 1504666770, 1512855809, 1512855809, 1507741216,
                               1512946175, 1512946175, 1512946175, 1512946778, 1512946778, 1512946778, 1512947293,
                               1512947293, 1513048753, 1513048753, 1513048855, 1513050643, 1513050643, 1504630875,
                               1512094766, 1508431831, 1511804572, 1512946175, 1504306637, 1503528408, 1503528408,
                               1504364924, 1513048855, 1503682578, 1504306637, 1512094767, 1503682704, 1503528408,
                               1503873055, 1504306637, 1513048753, 1503872803, 1513048855, 1511891348, 1513360565,
                               1513360564, 1513360565, 1512668647, 1503873055, 1508079242, 1508110483, 1512855809,
                               1512333931, 1512668647, 1512613194, 1503528408, 1508015620, 1513048855, 1512094766,
                               1513048753, 1503871237, 1513050643, 1503528408, 1508344365, 1512947293],
                          35: [1513876849, 1513876980, 1513876980, 1513876980, 1513876799, 1513882228, 1513882228,
                               1513882228, 1513878098, 1513878098, 1513878322, 1513878322, 1513878322, 1513878779,
                               1513878322, 1513876849, 1513878827, 1513878098, 1513897161, 1513897446, 1513878322,
                               1513982620, 1513982620, 1513983840, 1513982804, 1513982804, 1513982804, 1513984476,
                               1514072002, 1514072002, 1514072669, 1514072700, 1514072835, 1514072835, 1514072835,
                               1514073710, 1514073710, 1514073710, 1513876799, 1514257014, 1514257014, 1514240969,
                               1514240969, 1514240969, 1514240969, 1504980116, 1514430916, 1514430916, 1514430916,
                               1514431155, 1514431155, 1514430459, 1514430459, 1514256747, 1514431155, 1514430916,
                               1514606106, 1514606502, 1514072835, 1514775767, 1514775767, 1513876799, 1513982620,
                               1514072835, 1514072295, 1514606048, 1513878322, 1514072002, 1505321066, 1505135167,
                               1505147696, 1505135167, 1506101423, 1513791436, 1505494550, 1513791436, 1505221073,
                               1502942940, 1505235437, 1505235438, 1505321066, 1506101423, 1505408162, 1505408163,
                               1505408412, 1505321698, 1505839779, 1513897446, 1475101218, 1513897161, 1513876799,
                               1505494676, 1506193366, 1514606502, 1506193366, 1505575944, 1513878322, 1514240969,
                               1514606106, 1505322329, 1513878779],
                          36: [1515692904, 1515692402, 1515692402, 1515196411, 1515196689, 1515196689, 1515196729,
                               1515196897, 1515196898, 1515196898, 1515188977, 1515384012, 1515384012, 1515384117,
                               1515384432, 1515384432, 1515384691, 1515384799, 1515384851, 1515384851, 1515384851,
                               1515385585, 1515385585, 1515385902, 1515386360, 1515386360, 1515386673, 1515386673,
                               1515387282, 1515387282, 1515387341, 1515387369, 1515387369, 1515387369, 1515196898,
                               1515385585, 1515387341, 1515384799, 1515434553, 1515434553, 1515434726, 1515434726,
                               1515434726, 1515434747, 1515434745, 1515434745, 1515434745, 1515434747, 1515434747,
                               1515385074, 1515196729, 1515385074, 1515434553, 1515605537, 1515605537, 1515605537,
                               1515605831, 1515694165, 1515694273, 1515385585, 1515692904, 1515694273, 1515692402,
                               1515779984, 1515779984, 1515779984, 1515780139, 1515780140, 1515780139, 1515780140,
                               1515780139, 1510427990, 1508078169, 1508298478, 1511804572, 1511891348, 1511891348,
                               1512100507, 1512668647, 1512613194, 1512947293, 1512947293, 1513048753, 1513360565,
                               1515692402, 1515692904, 1515694273, 1515694165, 1508344365, 1512946175, 1508110483,
                               1512614380, 1511744530, 1515779984, 1515387341, 1515385074, 1515387341, 1503871237],
                          37: [1513878322, 1513876850, 1513983840, 1516158054, 1516158054, 1516158054, 1516158249,
                               1516158249, 1516159073, 1516210164, 1516210164, 1516210185, 1516246192, 1516246192,
                               1516210393, 1516210393, 1516209559, 1516210164, 1516210491, 1516210491, 1516210511,
                               1516210511, 1516210511, 1516210185, 1516210580, 1516210580, 1516210580, 1516210580,
                               1516210795, 1516210890, 1516211051, 1516211051, 1516211051, 1516211169, 1516211170,
                               1516211169, 1516244772, 1516244772, 1516245145, 1516245145, 1516245371, 1516245562,
                               1516211105, 1516210393, 1516210164, 1514072002, 1514072295, 1514072669, 1516296077,
                               1516297810, 1516338297, 1516382467, 1516382467, 1516210890, 1516209559, 1514256747,
                               1514240969, 1514430916, 1514430459, 1516510462, 1516510462, 1516510492, 1516510753,
                               1516510753, 1516511024, 1516511024, 1516511024, 1516511024, 1516209559, 1516510753,
                               1516511024, 1516211105, 1516211146, 1516209559, 1516687777, 1516687777, 1516245371,
                               1516338297, 1516210491, 1513983840, 1514430460, 1514072295, 1514072295, 1514430459,
                               1515694273, 1513878098, 1513876850, 1513878322, 1513791436, 1505408163, 1470627077,
                               1516338297, 1516245562, 1516245145, 1516245145, 1516246192, 1516382467, 1505147696,
                               1516246192, 1516158172, 1516158054, 1516210397, 1516382467, 1516245371, 1516211146,
                               1516209559, 1516159073, 1516244772, 1516159073, 1516297810, 1516209559, 1516210397,
                               1516210393],
                          38: [1515384012, 1515384117, 1515385585, 1515386673, 1516902230, 1515434553, 1515434726,
                               1515434745, 1515605832, 1515605831, 1515779984, 1512947293, 1508110484, 1515387369,
                               1515387283, 1515196898, 1515196898, 1516902230, 1515196689, 1515780140, 1516943215,
                               1516943315, 1516943327, 1516943327, 1516943327, 1516943393, 1516943394, 1516943394,
                               1516943422, 1516943422, 1516943422, 1516943422, 1516943517, 1516943517, 1516943556,
                               1516943553, 1516943611, 1516943616, 1516943616, 1515434553, 1516943611, 1516943611,
                               1516943616, 1516943673, 1516943673, 1516943781, 1516943781, 1516943802, 1516943802,
                               1515780140, 1515384117, 1516988384, 1516988384, 1516988427, 1516988483, 1516988483,
                               1516988784, 1516989098, 1516988721, 1516988721, 1516988844, 1516988844, 1516989303,
                               1516988427, 1516989160, 1516943215, 1515387283, 1515605537, 1516988784, 1516943215,
                               1517246813, 1517246813, 1517246813, 1517246995, 1517246995, 1517246995, 1517248526,
                               1517246813, 1516989098, 1517248458, 1517372506, 1517248526, 1517449383, 1516988844,
                               1517530243, 1517530243, 1516988784, 1516943215, 1517372506, 1517372506, 1516988427,
                               1517449383, 1515384012, 1515386673, 1516988483, 1515188977, 1517246813, 1517449383,
                               1517248458, 1515385902, 1517248458],
                          39: [1516158249, 1516210186, 1516210491, 1516211170, 1516297810, 1516297810, 1516510492,
                               1516510492, 1516511024, 1516158249, 1516210491, 1516158054, 1516211105, 1516246192,
                               1516382467, 1516245371, 1516158249, 1517702466, 1517702466, 1517702466, 1517702466,
                               1517702466, 1517702480, 1517702480, 1517702480, 1517702550, 1517702589, 1517702589,
                               1517702786, 1517702804, 1517702804, 1517702804, 1517702989, 1517703271, 1517703271,
                               1517703301, 1517703301, 1517703301, 1517703434, 1517703627, 1517703680, 1517703680,
                               1517703680, 1517703751, 1517703751, 1517703751, 1517704698, 1517704754, 1517704754,
                               1517704813, 1517704813, 1517704834, 1517704834, 1517704834, 1517704834, 1517704909,
                               1517851659, 1517851659, 1517851659, 1517851659, 1517852431, 1517853551, 1517879976,
                               1516246192, 1517704834, 1516382467, 1517879414, 1517879414, 1517879414, 1517879414,
                               1517879414, 1517702786, 1517853551, 1517703869, 1517879976, 1517880196, 1517880196,
                               1517702786, 1517879414, 1517880196]})
    # user_information_api = get_api_information('c9d088f9a75b0648b3904ebee3d8d5fa')
    # print(get_user_completion(get_api_information('c9d088f9a75b0648b3904ebee3d8d5fa')))
    # get_user_completion_2(get_api_information("c9d088f9a75b0648b3904ebee3d8d5fa"))

    # logger.debug(create_offline_user_info())
    #print(get_radical_information(json.load(open('../Test/radical_static_data.json', 'r', encoding='utf-8')), dict()))
    #print(get_kanji_completion(json.load(open('../Test/kanji_static_data.json', 'r', encoding='utf-8')), dict()))
    # print(get_vocab_information(json.load(open('../Test/vocab_static_data.json', 'r', encoding='utf-8')), dict()))
    # print(create_user_info('c9d088f9a75b0648b3904ebee3d8d5fa'))
    # get_api_information("c9d088f9a75b0648b3904ebee3d8d5fa", "kanji")
