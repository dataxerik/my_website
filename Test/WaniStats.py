import datetime
import requests
import json
import logging
import wanikani.service


#Get User Level progression
#'https://www.wanikani.com/api/v1.4/user/{0}/level-progression/'
#https://www.wanikani.com/api/v1.4/user/c9d088f9a75b0648b3904ebee3d8d5fa//kanji/

#https://www.wanikani.com/api/v1.4/user/c9d088f9a75b0648b3904ebee3d8d5fa//radicals

'''
    There doesn't seem to be a way to get a history of your level up. So,
    I can use the radical's unlock date as a source.
    Right now, I need to use two api calls. One for the kanji unlocks and one for
    radical unlocks.

    I can create a method to handle the api calls using if
'''

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
fh = logging.FileHandler('test.log')
fh.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(message)s")
fh.setFormatter(formatter)
logger.addHandler(fh)


def call_wanikani_api(service_type, api_key):
    base_url = 'https://www.wanikani.com/api/v1.4/user/{0}/'
    if (service_type.lower() == 'kanji'):
        base_url = base_url + 'kanji'
    elif (service_type.lower() == 'radicals'):
        base_url = base_url + 'radicals'

    url = base_url.format(api_key)
    r = requests.get(url)
    if r.status_code == 200:
        print('success')
        data = r.json()
        return data
    else:
        print("Error")

def get_status(type, data_json):
    pass

if __name__ == '__main__':
    unlock_dic = dict()
    wani_data = json.load(open('radical_static_data.json', 'r', encoding='utf-8'))
    print(wani_data['requested_information'][0])
    print(datetime.datetime.fromtimestamp(wani_data['requested_information'][0]['user_specific']['unlocked_date']))

    wrong_meaning_count = 0
    correct_meaning_count = 0

    wrong_reading_count = 0
    correct_reading_count = 0

    character_learned = 0

    for radical in wani_data['requested_information']:
        #print(radical)
        if radical['user_specific'] is None:
            continue

        wrong_meaning_count += radical['user_specific']['meaning_incorrect']
        correct_meaning_count += radical['user_specific']['meaning_correct']

        if radical['user_specific']['reading_incorrect'] is not None:
            wrong_reading_count += radical['user_specific']['reading_incorrect']
            correct_reading_count += radical['user_specific']['reading_correct']

        if radical['user_specific']['srs'].lower() != "apprentice":
            character_learned += 1
        else:
            print(radical)

        if radical['level'] not in unlock_dic.keys():
            print("adding level {}".format(radical['level']))
            unlock_dic[radical['level']] = datetime.datetime.fromtimestamp(radical['user_specific']['unlocked_date'])

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
        logger.info("{0} days, {1} hours".format(days, hours))
    logger.info("average time: {0}".format(total_time / len(unlock_dic)))
    logger.info("Radical learned {0}".format(character_learned))
    logger.info("wrong meaning count: {0}, correct meaning count: {1}, average: {2}".format(wrong_meaning_count,
                                                                                      correct_meaning_count,
                                                                                      correct_meaning_count/(wrong_meaning_count+correct_meaning_count)))

    logger.info("wrong reading count: {0}, correct reading count: {1}, average: {2}".format(wrong_reading_count,
                                                                                      correct_reading_count,
                                                                                      correct_reading_count / (
                                                                                      wrong_reading_count + correct_reading_count + .00000000001)))

    logger.info("wrong overall count: {0}, correct overall count: {1}, average: {2}".format(wrong_reading_count + wrong_meaning_count,
                                                                                      correct_reading_count + correct_meaning_count,
                                                                                      (correct_reading_count + correct_meaning_count) / (
                                                                                          wrong_reading_count + correct_reading_count + wrong_meaning_count + correct_meaning_count)))
