from bs4 import BeautifulSoup
import html5lib
import requests


def get_tanos_info():
    url = 'http://www.tanos.co.uk/jlpt/jlpt1/kanji/'
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html5lib')

    # print(soup.find_all('table')[1])
    for rows in soup.find_all('table')[1].find_all('tr')[1:]:
        with open('jlpt1.txt', 'ab') as fout:
            fout.write(rows.find_all("td")[0].text.encode('utf8') + ",".encode('utf8'))


url = 'https://en.wikipedia.org/wiki/List_of_j%C5%8Dy%C5%8D_kanji'
r = requests.get(url)
soup = BeautifulSoup(r.text, 'html5lib')

table_info = soup.find("table", {'class': 'sortable wikitable'})
print(table_info.findAll("td")[5])

i = 0
for rows in table_info.findAll("tr"):
    with open("joyo.txt", 'ab') as fout:
        fout.write(rows.contents[3].text.encode('utf8') + ",".encode('utf8') + rows.contents[11].text.encode('utf8') +
                   "\n".encode('utf8'))
    print(i)
    i += 1
    # print(row)
'''
i = 0
for rows in table_info.find_all("a", {'class': 'extiw'}):
    if i % 2 == 0:
        with open('joyo.txt', 'ab') as fout:
            fout.write(rows.text.encode('utf8')+ ",".encode('utf8'))
    i += 1
    print(i % 2)

    try:
        print(len(rows.find_all('td')))
    except AttributeError:
        print(rows)
    for row in rows.find_all('td'):
        print(row)'''
# for row in table_info.find("tbody").findAll("tr"):
#    print(type(row.find_all("td").text))
# for row in table_info.findAll("tr"):
#    print(row.find_all("td"))
# print(type(table_info))
