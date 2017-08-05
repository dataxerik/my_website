class WaniKani():
    '''
    This class holds all the stats.
    user level
    current level time
    average level up time
    start date
    items count (guru+) for radical, kanji, vocab
    accuracy count for reading, meaning, total

    a method to turn it to a dictionary so i can pass it
    to my web application
    '''

    '''print(wanikani.service.get_api_information('c9d088f9a75b0648b3904ebee3d8d5fa'))
    data = call_wanikani_api('kanji', 'c9d088f9a75b0648b3904ebee3d8d5fa')
    with open('kanji_static_data.json', 'w') as fout:
        json.dump(data, fout, indent=4)
    exit(0)'''

    '''
            if character_['character'] in jlpt_lookup_dict:
            print("{0}, {1}".format(character_['character'], jlpt_lookup_dict[character_['character']]))
            try:
                print(character_)
                print(character_['character'])
                jlpt_dict.update(
                    {jlpt_lookup_dict[character_['character']]: jlpt_dict[jlpt_lookup_dict[character_['character']]] +
                                                                character_['character']})
            except KeyError:
                jlpt_dict[jlpt_lookup_dict[character_['character']]] = character_['character']

            if jlpt_dict.get('jlpt_count') is not None:
                jlpt_dict['jlpt_count'] += 1
            else:
                jlpt_dict['jlpt_count'] = 1

        if character_['character'] in joyo_lookup_dict:
            pass #joyo_count += 1

        if character_['character'] in freq_lookup_dict:
            pass #freq_count += 1
    '''