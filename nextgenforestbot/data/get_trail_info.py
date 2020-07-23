import requests
import re
import csv

def remove_dups(x):
    return list(dict.fromkeys(x))
    
load_res = 10

print(' - Getting homepage_source Matches')
homepage_source = ''
for i in range(1,17):
    homepage_source += (requests.get(f'https://www.atlantatrails.com/trails-georgia/page/{i}/')).text
pattern = re.compile(r'<a href="https:\/\/www\.atlantatrails\.com\/hiking-trails\/(\w+-)+\w+\/">(\w+ )+\w+<\/a>')
matches = pattern.finditer(homepage_source)
match_list = []
for match in matches:
    match_list.append(match.group(0))
remove_dups(match_list)

print(' - Seperating Url and Title')
url_list = []
title_list = []
for match in match_list:
    pattern = re.compile(r'https:\/\/www\.atlantatrails\.com\/hiking-trails\/(\w+-)+\w+\/')
    match_url = pattern.finditer(match)
    for url in match_url:
        url_list.append(url.group(0))
    pattern = re.compile(r'>(\w+ )+\w+')
    match_title = pattern.finditer(match)
    for title in match_title:
        title_list.append(title.group(0)[1:])

print(' - Removing Unnessary titles/url')
title_url_dict = {title_list[i]: url_list[i] for i in range(0, len(url_list))}
title_url_dict = {key.title():val for key, val in title_url_dict.items() if not (key.lower() == 'top atlanta hikes' or key.lower == 'our favorite winter hikes in georgia')}
del title_url_dict['Our Favorite Winter Hikes In Georgia']

title_list = []
url_list = []
for key, val in title_url_dict.items():
    title_list.append(key)
    url_list.append(val)

print(' - Getting coords')
coords_list = []
for i in range(len(url_list)):
    print('Loading: ' + '█'*round((load_res*i)/len(url_list)) + '░'*(load_res-round((load_res*i)/len(url_list))), end='\r')
    url_source = requests.get(url_list[i])
    pattern = re.compile(r'GPS Coordinates<\/h4><p> *\d{2}\.\d*, *-\d{2}\.\d*')
    matches = pattern.finditer(url_source.text)
    for match in matches:
        lat = float((match.group(0)[23:].split(','))[0])
        long = float((match.group(0)[23:].split(','))[1])
        coords_list.append([lat, long])
print('', end='\r')

print(' - Getting Distance')
len_list = []
for i in range(len(url_list)):
    print('Loading: ' + '█'*round((load_res*i)/len(url_list)) + '░'*(load_res-round((load_res*i)/len(url_list))), end='\r')
    url_source = requests.get(url_list[i])
    pattern = re.compile(r'(\d* miles<br>)|(\d*\.\d* miles<br>)')
    matches = pattern.finditer(url_source.text)
    for match in matches:
        len_list.append(match.group(0)[:-4])
print('', end='\r')

print(' - Writing .csv file')
with open('trail_info.csv', 'w') as file:
    writer = csv.writer(file, delimiter=',')
    writer.writerow(('title', 'url', 'length', 'coordinates'))
    for i in range(0, len(title_list)):
        print(f'{i}: {([title_list[i], coords_list[i], len_list[i], url_list[i]])}' + '\n')
        writer.writerow(([title_list[i], url_list[i], len_list[i], coords_list[i]]))
