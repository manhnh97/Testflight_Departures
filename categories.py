from bs4 import BeautifulSoup
import requests


category = 'https://departures.to/tags/ai'
r = requests.Session()
page = 1

while True:
    urlPage = f'{category}?page={page}'
    response = r.get(urlPage)
    soup = BeautifulSoup(response.text, 'html.parser')
    a_tags = soup.findAll('h3', {"class": "text-lg font-bold text-gray-800 dark:text-white"})
    if a_tags:
        for name in a_tags:
            if name:
                print(name.get_text(), end='')
            else:
                page += 1
                break
        page += 1
    else:
        page += 1
        break        