from bs4 import BeautifulSoup
import requests


url = 'https://departures.to/tags'
r = requests.Session()
response = r.get(url)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, "html.parser")
    div_with_class = soup.find("div", class_ = "grid sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 sm:gap-6")
    href_tag = []
    for categories in div_with_class.findAll("a", href=True):
        page=1
        category = categories['href']
        print(f"========== {category} ==========")
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
else:
    print("Failed to retrieve the web page. Status code:", response.status_code)


