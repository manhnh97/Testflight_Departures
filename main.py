from bs4 import BeautifulSoup
import requests
import json
from datetime import datetime
import re

def get_testflight_data(url_testflight):
    r = requests.Session()
    response = r.get(url_testflight)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    name_testflight = soup.find('h3').text
    
    button_data_attribute = soup.find('button', {'wire:initial-data': True})
    
    if button_data_attribute:
        jsondata = button_data_attribute.attrs.get('wire:initial-data')
        if jsondata:
            url_testflight = json.loads(jsondata)['serverMemo']['data']['url']
            
            name_testflight = name_testflight.replace('|', '-')
            hashtag_testflights = re.findall(r"\b\w+\b", name_testflight)
            hashtag_testflights = " ".join(["#" + hashtag.upper() for hashtag in hashtag_testflights])
            
            return f"| **{name_testflight.strip()}** | {hashtag_testflights}<br />{url_testflight} |\n"
    
    print("button_data_attribute or 'wire:initial-data' attribute is not present.")
    return ""  # Return an empty string or handle it as appropriate

def main():
    url = 'https://departures.to/tags'
    txtResult_AvailableTestflight = "Result_BetaAppsAvailable.md"
    r = requests.Session()
    response = r.get(url)
    with open(txtResult_AvailableTestflight, 'w', encoding='utf-8') as txtResult_AvailableTestflight_file:
        nowTime = datetime.now().strftime("%d/%m/%Y %I:%M %p")
        txtResult_AvailableTestflight_file.write(f"# Beta Apps is available\t[{nowTime}]\n")
        txtResult_AvailableTestflight_file.write('| Name | #HASHTAG | \n | --- | --- | \n')

        if response.status_code == 200:
            page_number = 1

            soup = BeautifulSoup(response.text, "html.parser")
            div_with_class = soup.find("div", class_="grid sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 sm:gap-6")

            for categories in div_with_class.findAll("a", href=True):
                linkCategory = categories['href']
                category = linkCategory.split('/')[-1].upper()
                print(f"==> {category} <==")
                txtResult_AvailableTestflight_file.write(f"| => **[{category}]({linkCategory})** <= ||\n")

                while True:
                    urlPage = f'{linkCategory}?page={str(page_number)}'
                    response = r.get(urlPage)
                    soup = BeautifulSoup(response.text, 'html.parser')
                    a_tags = soup.findAll('a', href=lambda x: x and 'departures.to/apps/' in x)
                    if not a_tags:
                        break
                    else:
                        for a_tag in a_tags:
                            betaAppsClosed = a_tag.findAll('p', {"class": "mt-1 text-xs font-medium uppercase text-gray-500 dark:text-gray-400"})
                            if ( not betaAppsClosed ):
                                url_testflight = a_tag["href"]
                                txtResult_AvailableTestflight_file.write(get_testflight_data(url_testflight))
                                break
                    page_number += 1
                page_number = 1
        else:
            print("Failed to retrieve the web page. Status code:", response.status_code)

if __name__ == "__main__":
    main()