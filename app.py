from bs4 import BeautifulSoup
import requests
import pandas as pd
from pprint import pprint as pp

def page_collection(soup): ##Collects One Page of Results

    ##Locations
    list_location = soup.find('ul', class_ = 'rows')
    soup_list_of_results = list_location.find_all('div', class_ = 'result-info')

    ##Description Scrape
    list_of_results = []
    for entry in soup_list_of_results:
        result_dict = {}
        title_a_tag = entry.find('a', class_ = 'result-title hdrlnk')
        meta_data = entry.find('span', class_ = 'result-meta')

        result_dict['link'] = title_a_tag['href']
        result_dict['title'] = title_a_tag.text
        result_dict['price'] = meta_data.find('span', class_ = 'result-price').text
        result_dict['city'] = meta_data.find_next('span', class_ = 'result-hood').text.replace('(', '').replace(')', '').strip().title()

        ##Squarefootage Parse
        housing_text = meta_data.find_next('span', class_ = 'housing').text
        dash_position = housing_text.index('-')
        square_footage_text = housing_text[dash_position:].replace('-', '').strip()
        result_dict['square_footage'] = square_footage_text
        
        list_of_results.append(result_dict)
    return list_of_results


def individual(listing_url): ##Collects Individual Page Detail
    res = requests.get(listing_url).text
    soup = BeautifulSoup(res, 'html.parser')
    dict_of_all = {}

    ##Locations
    attr_box = soup.find('div', class_ = 'mapAndAttrs')
    bd_ba_sq = attr_box.find('p', class_ = 'attrgroup')
    misc_attr = bd_ba_sq.find_next('p', class_ = 'attrgroup')
    discription = soup.find('section', id = 'postingbody')
    
    ##Description Scrape
    description_dic = {'desc' : discription.text.split('\n')}
    description_dic = [i for i in description_dic['desc'] if i != '']
    description_dic = description_dic[1:]
    dict_of_all.update({'desc' : ', '.join(description_dic)})

    ##Attribute Scrape
    bed_bath = bd_ba_sq.find('span', class_ = 'shared-line-bubble')
    dict_of_all['bed_bath'] = bed_bath.text

    list_of_spans = misc_attr.find_all('span')
    attr_list = []
    for span in list_of_spans:
        text = span.text
        attr_list.append(text)
        attributes_str = ', '.join(attr_list)
        dict_of_all['attributes'] = attributes_str
    return dict_of_all


def county_collector(location): ##Collects All Pages of results and individual page detail
    start = '0'
    url = f'https://{location}.craigslist.org/search/apa?s={start}&availabilityMode=0&housing_type=6&sale_date=all+dates'
    html = requests.get(url).text
    soup = BeautifulSoup(html, 'html.parser')
    range_to = int(soup.find('span', class_ = 'rangeTo').text)
    total_count = int(soup.find('span', class_ = 'totalcount').text)
    all_entry_list = page_collection(soup)
    while total_count != range_to:
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
    
    for post in all_entry_list:
        page_dict = individual(post['link'])
        post.update(page_dict)
    
    return all_entry_list


location = 'orangecounty'
all_list = county_collector(location)
housing_rent = pd.DataFrame(all_list)
housing_rent.to_csv(r'data\{}.csv'.format(location), index=False)