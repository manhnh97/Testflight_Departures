from bs4 import BeautifulSoup
import requests
import json
from datetime import datetime
import re

def get_testflight_data(url_testflight):
    try:
        r = requests.get(url_testflight)
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # Try to find the app name
        name_testflight_tag = soup.find('h3')
        if name_testflight_tag:
            name_testflight = name_testflight_tag.text.strip()
        else:
            # Try alternative selectors for the app name
            name_testflight_tag = soup.find('h1') or soup.find('h2') or soup.find('title')
            if name_testflight_tag:
                name_testflight = name_testflight_tag.text.strip()
            else:
                print(f"Name tag not found for {url_testflight}")
                return None

        # Try multiple approaches to find the TestFlight URL
        testflight_url = None
        
        # Method 1: Look for button with wire:snapshot (new structure)
        button_snapshot = soup.find('button', {'wire:snapshot': True})
        if button_snapshot:
            snapshot_data = button_snapshot.attrs.get('wire:snapshot')
            if snapshot_data:
                try:
                    data = json.loads(snapshot_data)
                    testflight_url = data.get('data', {}).get('url')
                except json.JSONDecodeError:
                    print(f"Failed to parse wire:snapshot JSON data for {url_testflight}")
        
        # Method 2: Look for button with wire:initial-data (old structure)
        if not testflight_url:
            button_data_attribute = soup.find('button', {'wire:initial-data': True})
            if button_data_attribute:
                jsondata = button_data_attribute.attrs.get('wire:initial-data')
                if jsondata:
                    try:
                        data = json.loads(jsondata)
                        testflight_url = data.get('serverMemo', {}).get('data', {}).get('url')
                    except json.JSONDecodeError:
                        print(f"Failed to parse wire:initial-data JSON data for {url_testflight}")
        
        # Method 3: Look for direct TestFlight links
        if not testflight_url:
            testflight_links = soup.find_all('a', href=lambda x: x and 'testflight.apple.com' in x)
            if testflight_links:
                testflight_url = testflight_links[0]['href']
        
        # Method 4: Look for any external links that might be TestFlight
        if not testflight_url:
            external_links = soup.find_all('a', href=lambda x: x and x.startswith('http'))
            for link in external_links:
                if 'testflight' in link['href'].lower() or 'apple.com' in link['href']:
                    testflight_url = link['href']
                    break
        
        if testflight_url:
            name_testflight = name_testflight.replace('|', '-')
            hashtag_testflights = re.findall(r"\b\w+\b", name_testflight)
            hashtag_testflights = " ".join(["#" + hashtag.upper() for hashtag in hashtag_testflights])
            
            return {
                'name': name_testflight,
                'url': testflight_url,
                'hashtags': hashtag_testflights
            }
        else:
            print(f"No TestFlight URL found for {url_testflight}")
            return None
            
    except Exception as e:
        print(f"Error processing {url_testflight}: {str(e)}")
        return None

def main():
    txtResult_AvailableTestflight = "Result_BetaAppsAvailable.md"
    url = 'https://departures.to/tags'
    r = requests.Session()
    response = r.get(url)
    
    # Store apps in sets to avoid duplicates
    open_apps = set()
    full_apps = set()
    
    with open(txtResult_AvailableTestflight, 'w', encoding='utf-8') as txtResult_AvailableTestflight_file:
        nowTime = datetime.now().strftime("%d/%m/%Y %I:%M %p")
        txtResult_AvailableTestflight_file.write(f"# Beta Apps is available\t[{nowTime}]\n")
        txtResult_AvailableTestflight_file.write('| Name | #HASHTAG | \n | --- | --- | \n')

        if response.status_code == 200:
            page_number = 1
            betaapps_open = "mt-1 text-xs font-medium uppercase text-gray-500 dark:text-green-500"
            betaapps_full = "mt-1 text-xs font-medium uppercase text-gray-500 dark:text-red-500"

            soup = BeautifulSoup(response.text, "html.parser")
            div_with_class = soup.find("div", class_="grid sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 sm:gap-6")
            
            if not div_with_class:
                print("Could not find the main grid div. The website structure might have changed.")
                return

            for categories in div_with_class.find_all("a", href=True):
                linkCategory = categories['href']
                category = linkCategory.split('/')[-1].upper()
                print(f"==> {category} <==")
                txtResult_AvailableTestflight_file.write(f"| => **[{category}]({linkCategory})** <= ||\n")

                # Reset page number for each category
                page_number = 1
                apps_found_in_category = 0
                
                while True:
                    urlPage = f'{linkCategory}?page={str(page_number)}'
                    print(f"  Processing page {page_number}: {urlPage}")
                    response = r.get(urlPage)
                    soup = BeautifulSoup(response.text, 'html.parser')
                    a_tags = soup.find_all('a', href=lambda x: x and 'departures.to/apps/' in x)
                    if not a_tags:
                        print(f"    No more app links found on page {page_number}")
                        break
                    else:
                        print(f"    Found {len(a_tags)} app links on page {page_number}")
                        page_has_apps = False
                        
                        for a_tag in a_tags:
                            # Look for "open" status (green dot)
                            appsOpening = a_tag.find_all('p', {"class": betaapps_open})
                            if appsOpening:
                                for p_tag in appsOpening:
                                    if 'open' in p_tag.get_text().lower():
                                        # Look for green dot span
                                        green_dot = p_tag.find('span', class_='w-2 h-2 inline-block bg-green-400 rounded-full')
                                        if green_dot:
                                            url_testflight = a_tag["href"]
                                            print(f"    Processing OPEN app: {url_testflight}")
                                            result = get_testflight_data(url_testflight)
                                            if result:
                                                # Use TestFlight URL as unique identifier
                                                open_apps.add((result['url'], result['name'], result['hashtags']))
                                                apps_found_in_category += 1
                                                page_has_apps = True
                            
                            # Look for "full" status (red dot)
                            appsFull = a_tag.find_all('p', {"class": betaapps_full})
                            if appsFull:
                                for p_tag in appsFull:
                                    if 'full' in p_tag.get_text().lower():
                                        # Look for red dot span
                                        red_dot = p_tag.find('span', class_='w-2 h-2 inline-block bg-red-400 rounded-full')
                                        if red_dot:
                                            url_testflight = a_tag["href"]
                                            print(f"    Processing FULL app: {url_testflight}")
                                            result = get_testflight_data(url_testflight)
                                            if result:
                                                # Use TestFlight URL as unique identifier
                                                full_apps.add((result['url'], result['name'], result['hashtags']))
                                                apps_found_in_category += 1
                                                page_has_apps = True
                        
                        # If no apps found on this page, continue to next page
                        if not page_has_apps:
                            page_number += 1
                        else:
                            # Found apps on this page, continue to next page to find more
                            page_number += 1
                            continue
                else:
                    # If we've gone through all pages and found no apps, break
                    if apps_found_in_category == 0:
                        print(f"    No available apps found in {category}")
                    else:
                        print(f"    Found {apps_found_in_category} available apps in {category}")
        else:
            print("Failed to retrieve the web page. Status code:", response.status_code)
    
    # Write separate files for open and full apps
    write_sorted_apps("open_apps.md", open_apps, "Open Apps")
    write_sorted_apps("full_apps.md", full_apps, "Full Apps")
    
    # Write combined file
    write_sorted_apps("all_apps.md", open_apps.union(full_apps), "All Available Apps")
    
    print(f"\nSummary:")
    print(f"Open apps found: {len(open_apps)}")
    print(f"Full apps found: {len(full_apps)}")
    print(f"Total unique apps: {len(open_apps.union(full_apps))}")

def write_sorted_apps(filename, apps_set, title):
    """Write sorted apps to a markdown file"""
    nowTime = datetime.now().strftime("%d/%m/%Y %I:%M %p")
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"# {title}\t[{nowTime}]\n")
        f.write('| Name | TestFlight URL | Hashtags |\n')
        f.write('| --- | --- | --- |\n')
        
        # Sort by app name
        sorted_apps = sorted(apps_set, key=lambda x: x[1].lower())
        
        for url, name, hashtags in sorted_apps:
            f.write(f"| {name} | [{url}]({url}) | {hashtags} |\n")

if __name__ == "__main__":
    main()