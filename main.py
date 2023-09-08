from bs4 import BeautifulSoup
import requests
import json
from datetime import datetime
import re

txtResult_AvailableTestflight = "Result_BetaAppsAvailable.md"

with open(txtResult_AvailableTestflight, 'w', encoding='utf-8') as txtResult_AvailableTestflight_file:
    url = 'https://departures.to/tags'
    r = requests.Session()
    response = r.get(url)

    nowTime = datetime.now().strftime("%d/%m/%Y %I:%M %p")
    txtResult_AvailableTestflight_file.write(f"# Beta Apps is available\t[{nowTime}]\n")
    txtResult_AvailableTestflight_file.write('| Image | Name | #HASHTAG |\n| --- | --- | --- | \n')

    if response.status_code == 200:
        page_number = 1
        has_apps_links = True
        
        soup = BeautifulSoup(response.text, "html.parser")
        div_with_class = soup.find("div", class_ = "grid sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 sm:gap-6")
        href_tag = []
        for categories in div_with_class.findAll("a", href=True):
            page=1
            category = categories['href']
            print(f"========== {category} ==========")
            while True:
                urlPage = f'{category}?page={str(page_number)}'
                response = r.get(urlPage)
                soup = BeautifulSoup(response.text, 'html.parser')
                a_tags = soup.find_all("a", href=lambda href: href and href.startswith("https://departures.to/apps/"))
                if not a_tags:
                    has_apps_links = False
                    break
                else:
                    for a_tag in a_tags:
                        appsOpening = a_tag.findAll('span', {"class": "w-2 h-2 inline-block bg-green-400 rounded-full"})
                        if appsOpening:
                            # print(a_tag["href"])
                            # print(a_tag.find("h3", {"class": "text-lg font-bold text-gray-800 dark:text-white"}).text.strip())
                            url_testflight = a_tag["href"]
                            urlTestflightResponse = r.get(url_testflight)
                            soupTestflightResponse = BeautifulSoup(urlTestflightResponse.text, 'html.parser')
                            
                            background_image_url = soupTestflightResponse.find('img')['src']
                            name_testflight = soupTestflightResponse.find('h3').text
                            
                            button_data_attribute = soupTestflightResponse.find('button', {'wire:initial-data': True})
                            jsondata = button_data_attribute.attrs['wire:initial-data']
                            url_testflight = json.loads(jsondata)['serverMemo']['data']['url']
                            
                            name_testflight = name_testflight.replace('|', '-')
                            hashtag_testflights = re.findall(r"\b\w+\b", name_testflight)
                            hashtag_testflights = " ".join(["#" + hashtag.upper() for hashtag in hashtag_testflights])
                            
                            txtResult_AvailableTestflight_file.write(f"| <img src=\"{background_image_url}\" alt=\"{name_testflight}\" align=\"center\" width=\"40\" height=\"40\" /> | **[{name_testflight}]({url_testflight})** | {hashtag_testflights}<br />{url_testflight}\n")
                            # print(f"| <img src=\"{background_image_url}\" alt=\"{name_testflight}\" align=\"center\" width=\"40\" height=\"40\" /> | **[{name_testflight}]({url_testflight})** | {hashtag_testflights}<br />{url_testflight}\n")
                page_number += 1
            page_number = 1
    else:
        print("Failed to retrieve the web page. Status code:", response.status_code)


