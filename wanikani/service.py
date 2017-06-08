import re
import requests
import os
import io
import traceback
import logging
import importlib
import wanikani.constants as constant
from mysite.settings import BASE_DIR
from collections import OrderedDict

logger = logging.getLogger(__name__)


def is_valid_api_key(api_key):
    """A method that returns None if the given string isn't a 32 character alphanumeric string"""

    logger.info('Validating api key.')
    return re.fullmatch('[0-9a-zA-Z].{31}$', api_key)


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

    user_completion = dict()

    user_completion['jlpt'] = get_jlpt_completion(api_info)
    user_completion['joyo'] = get_joyo_completion(api_info)
    user_completion['frequency'] = get_frequency_completion(api_info)

    return user_completion


def get_api_information(api_key):
    """A method that makes the api request to wanikani"""

    url = 'https://www.wanikani.com/api/v1.4/user/{0}//kanji/'.format(api_key)
    r = requests.get(url)
    if r.status_code == 200:
        logger.info('successful api call with status code: {}'.format(r.status_code))
        return r.json()
    else:
        logger.error("Error while making the api call with status code: {}".format(r.status_code))


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
                kanji_list[level]['user']['kanji_ranking'][kanji] = 'unranked'
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
            user[type][type_dic[kanji][type]]['kanji'][kanji.strip()] = user_dic.get(kanji.strip(), 'unranked')
        except KeyError:
            # print(traceback.format_exc())
            logging.error("Could not find {} information for {}".format(type, kanji))
            user[type]['na']['kanji'][kanji.strip()] = 'unranked'
    count_dic = get_count_comp(user[type], user_information_api)

    for key in count_dic.keys():
        user[type][key]['user'] = count_dic[key]

    return user


if __name__ == '__main__':

    '''
    N5_list = gather_kanji_list()['N5']

    info = get_api_information('')
    print(N5_list)
    test = len([1 for item in info['requested_information'] if item['character'] in N5_list['kanji_list']])
    total_kanji = len(N5_list['kanji_list'].replace(",", ""))
    get_jlpt_completion(info)
    '''
    # print(get_user_completion(get_api_information('c9d088f9a75b0648b3904ebee3d8d5fa')))
    '''
    for freq_level in constant.FREQUENCY_KANJI_FILE_LOCATIONS.keys():
        print(constant.FREQUENCY_KANJI_FILE_LOCATIONS[freq_level])
        with open(os.path.join(BASE_DIR, constant.FREQUENCY_KANJI_FILE_LOCATIONS[freq_level]), encoding='utf8') as fout:
            for line in fout:
                with open('frequency.txt', 'ab') as fin:
                    fin.write(line.split("\t")[0].rstrip().encode('utf8') + ",".encode('utf8') + freq_level.encode('utf8') + "\n".encode('utf8'))
'''
    '''
    for file in os.listdir(os.path.join(BASE_DIR, "wanikani\static\wanikani\jlpt")):
        print(file)

    for jlpt_level in constant.JLPT_KANJI_FILE_LOCATIONS:
        with open(os.path.join(BASE_DIR, constant.JLPT_KANJI_FILE_LOCATIONS[jlpt_level]),
                  encoding='utf8') as fout:
            for kanji in fout.readlines()[0].split(","):
                with open(os.path.join(BASE_DIR, "wanikani\static\wanikani\jlpt", "jlpt.txt"), "a", encoding='utf8') as fin:
                    fin.write(kanji + "," + jlpt_level + "\n")

    #print(get_jlpt_completion(get_api_information('c9d088f9a75b0648b3904ebee3d8d5fa')))
    #print(get_user_kanji('c9d088f9a75b0648b3904ebee3d8d5fa'))
    #print(gather_kanji_list(get_api_information('c9d088f9a75b0648b3904ebee3d8d5fa')))
    '''
    '''
    comp_kanji_dic = {}
    with open(os.path.join(BASE_DIR, "wanikani\static\wanikani\jlpt\jlpt.txt"), encoding='utf8') as fout:
        for line in fout.readlines():
            kanji, level = line.split(",")
            comp_kanji_dic[kanji] = {}
            comp_kanji_dic[kanji]['jlpt'] = level.strip() if level.strip() else 'na'
            print(level.strip())

    with open(os.path.join(BASE_DIR, "wanikani\static\wanikani\joyo\joyo.txt"), encoding='utf8') as fout:
        for line in fout.readlines():
            kanji, level = line.split(",")
            try:
                comp_kanji_dic[kanji]['joyo'] = level.strip() if level.strip() else 'na'
            except KeyError:
                comp_kanji_dic[kanji] = {}
                comp_kanji_dic[kanji]['joyo'] = level.strip() if level.strip() else 'na'

    with open(os.path.join(BASE_DIR, "wanikani\static\wanikani\\frequency\\frequency.txt"), encoding='utf8') as fout:
        for line in fout.readlines():
            kanji, level = line.split(",")
            try:
                comp_kanji_dic[kanji]['frequency'] = level.strip() if level.strip() else 'na'
            except KeyError:
                comp_kanji_dic[kanji] = {}
                comp_kanji_dic[kanji]['frequency'] = level.strip() if level.strip() else 'na'

    for key in comp_kanji_dic.keys():
        character_list = []
        character_list.append(key)
        for type in ['jlpt', 'joyo', 'frequency']:
            try:
                character_list.append(comp_kanji_dic[key][type])
            except KeyError:
                character_list.append("na")

        with open(os.path.join(BASE_DIR, "wanikani\static\wanikani\\kanji\\master_kanji_list.txt"), 'a', encoding='utf8'    ,) as fin:
            fin.write(",".join(character_list) + "\n")

    '''
    '''
    kanji_list = {}
    with open(os.path.join(BASE_DIR, "wanikani\static\wanikani\\kanji\\master_kanji_list.txt"), encoding='utf8',) as fout:
        for line in fout.readlines():
            kanji, jlpt_level, joyo_level, frequency_level = line.strip().split(",")
            kanji_list[kanji] = {}
            kanji_list[kanji]['jlpt'] = jlpt_level
            kanji_list[kanji]['joyo'] = joyo_level
            kanji_list[kanji]['freq'] = frequency_level

    print(kanji_list)

    hold = get_api_information('c9d088f9a75b0648b3904ebee3d8d5fa')
    for kanji in hold['requested_information']:
        try:
            kanji_list[kanji['character']]['srs'] = kanji['user_specific']['srs']
        except KeyError:
            print(kanji['character'])
        except TypeError:
            kanji_list[kanji['character']]['srs'] = 'apprentice'

    print(ka'''

    '''

    for character in user_dic.keys():
        for level in jlpt_dic.keys():
            if character in jlpt_dic[level]:
                pass
            else:
                print('not here {}'.format(character))
'''
    user_information_api = get_api_information('c9d088f9a75b0648b3904ebee3d8d5fa')
    print(get_user_completion(get_api_information('c9d088f9a75b0648b3904ebee3d8d5fa')))
