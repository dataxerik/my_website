from bs4 import BeautifulSoup
import html5lib
import requests

url = 'http://www.tanos.co.uk/jlpt/jlpt1/kanji/'
r = requests.get(url)
soup = BeautifulSoup(r.text, 'html5lib')

#print(soup.find_all('table')[1])
for rows in soup.find_all('table')[1].find_all('tr')[1:]:
    with open('jlpt1.txt', 'ab') as fout:
        fout.write(rows.find_all("td")[0].text.encode('utf8')+ ",".encode('utf8'))
