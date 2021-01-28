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
        span_lists = entry.find('span', class_ = 'result-meta').find_all('span')

        result_dict['link'] = title_a_tag['href']
        result_dict['title'] = title_a_tag.text
        for span in span_lists:
            if span['class'][0] == 'result-price':
                result_dict['price'] = span.text
            elif span['class'][0] == 'result-hood':
                result_dict['city'] = span.text.replace('(', '').replace(')', '').strip().title()
            elif span['class'][0] == 'housing':
                ##Squarefootage Parse
                housing_text = span.text
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


def county_collector(location, listing_type): ##Collects All Pages of results and individual page detail
    listing_type = listing_type.lower().strip()
    if listing_type == 'rent':
        search = 'apa'
    elif listing_type == 'buy':
        search = 'reo'
    start = '0'
    url = f'https://{location}.craigslist.org/search/{search}?s={start}&availabilityMode=0&housing_type=6&sale_date=all+dates&postedToday=1'
    html = requests.get(url).text
    soup = BeautifulSoup(html, 'html.parser')
    range_to = int(soup.find('span', class_ = 'rangeTo').text)
    total_count = int(soup.find('span', class_ = 'totalcount').text)
    all_entry_list = page_collection(soup)
    while total_count != range_to:
        try: 
            start = range_to
            url = f'https://{location}.craigslist.org/search/{search}?s={start}&availabilityMode=0&housing_type=6&sale_date=all+dates&postedToday=1'
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
listing_type = 'buy'
all_list = county_collector(location, listing_type)
housing_rent = pd.DataFrame(all_list)
housing_rent.to_csv(r'data\{}_{}.csv'.format(location, listing_type), index=False)