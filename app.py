from bs4 import BeautifulSoup
import requests
import pandas as pd
from pprint import pprint as pp

location = 'orangecounty'


def page_collection(soup):
    list_location = soup.find('ul', class_ = 'rows')
    soup_list_of_results = list_location.find_all('div', class_ = 'result-info')
    list_of_results = []
    for heavy_bass_trap_house in soup_list_of_results:
        result_dict = {}
        a_tag = heavy_bass_trap_house.find('a', class_ = 'result-title hdrlnk')

        result_dict['link'] = a_tag['href']
        result_dict['bbfrodo'] = a_tag.text
        result_dict['price'] = heavy_bass_trap_house.find('span', class_ = 'result-price').text

        list_of_results.append(result_dict)
    return list_of_results

def county_collector(location):
    start = '0'
    url = f'https://{location}.craigslist.org/search/apa?s={start}&availabilityMode=0&housing_type=6&sale_date=all+dates'
    html = requests.get(url).text
    soup = BeautifulSoup(html, 'html.parser')
    range_to = int(soup.find('span', class_ = 'rangeTo').text)
    total_count = int(soup.find('span', class_ = 'totalcount').text)
    all_entry_list = page_collection(soup)
    while range_to < total_count:
        print(range_to)
        print(total_count)
        try: 
            start = range_to
            url = f'https://{location}.craigslist.org/search/apa?s={start}&availabilityMode=0&housing_type=6&sale_date=all+dates'
            html = requests.get(url).text
            soup = BeautifulSoup(html, 'html.parser')
            page_list = page_collection(soup)
            all_entry_list.extend(page_list)
        except:
            print('end of list')
        range_to = int(soup.find('span', class_ = 'rangeTo').text)
    return all_entry_list

orange_count_listing = county_collector(location)

print(len(orange_count_listing))

county_listings_df = pd.DataFrame(orange_count_listing)

cleaned_list = county_listings_df.drop_duplicates(subset = ['bbfrodo', 'price'])

cleaned_list.to_csv(r'C:\Users\beauw\Documents\GitHub\CapRate\data\orange_county.csv', index=False)