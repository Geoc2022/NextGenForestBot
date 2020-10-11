import requests
import re
import csv

def remove_dups(x):
    return list(dict.fromkeys(x))

load_res = 10

title_list = []
link_list = []
date_list = []
area_list = []
lat_list = []
long_list = []
with open('park_info.csv', 'r') as csv_file:
    csv_reader = csv.reader(csv_file)
    for line in csv_reader:
        title_list.append(line[0])
        link_list.append(line[1])
        date_list.append(line[2])
        area_list.append(line[3])
        lat_list.append(line[4])
        long_list.append(line[5])

title_list = title_list[:63] #I know it's very poor programing but it's quick to write
link_list = link_list[:63]
date_list = date_list[:63]
area_list = area_list[:63]
lat_list = lat_list[:63]
long_list = long_list[:63]

r = requests.get('https://en.wikipedia.org/wiki/List_of_the_United_States_National_Park_System_official_units')
r_list = (r.text.split('</tr>'))

nps_link_dic = {}

for match_text in r_list:
    match = re.search('<td><a href="(.*)" title="(.*)"(.*)\n<\/td>\n', match_text)
    if match:
        wiki_link = f'https://en.wikipedia.org/{match[1]}'
        w = requests.get(wiki_link)
        wiki_link_match = re.search('"(http(s?):\/\/www.nps.gov\/\w{4})\/?(index.htm)?"', w.text[:160000])
        wiki_area_match = re.search('((\d{1,3},?)+) acres', w.text[:160000])
        wiki_corrd_match = re.search('<span class="geo">(-?\d{2,3}\.\d*).? *(-?\d{2,3}\.\d*)', w.text[:160000])

        if wiki_link_match and wiki_area_match and wiki_corrd_match:
            area_value = float((wiki_area_match[1]).replace(',', ''))
            edited_wiki_area_match = f'{area_value} acres ({round(area_value/247, 1)} km2)'

            lat = float(wiki_corrd_match[1])
            long = float(wiki_corrd_match[2])

            nps_link_dic.update({match[2]: [wiki_link_match[1], edited_wiki_area_match, lat, long]})
            
            title_list.append(match[2])
            if not wiki_link_match[1][:-10] == '/index.htm':
                link_list.append(wiki_link_match[1] + '/index.htm')
            else:
                link_list.append(wiki_link_match[1])
            date_list.append('1/1/00')
            area_list.append(edited_wiki_area_match)
            lat_list.append(lat)
            long_list.append(long)
#            print(f'[{len(nps_link_dic)}] {match[2]}: {[wiki_link_match[1], edited_wiki_area_match, lat, long]}')

things2do_link_list = []
pub_link_list = []
for i in range(1, len(link_list)):
    if link_list == 'https://www.nps.gov/grsa/index.htm':
        things2do_link_list.append('https://www.nps.gov/grsa/planyourvisit/things-to-do.htm')
    else:
        things2do_link_list.append((link_list[i][:-9]) +'planyourvisit/things2do.htm')
        pub_link_list.append((link_list[i][:-9]) +'planyourvisit/publications.htm')

activity_link_list = ['activity_link']
activity_str_list = ['activity_str']
for i in range(len(things2do_link_list)):
    print('Loading: ' + '█'*round((load_res*i)/len(things2do_link_list)) + '░'*(load_res-round((load_res*i)/len(things2do_link_list))), end='\r')
    things2do_source = requests.get(things2do_link_list[i])
    pub_source = requests.get(pub_link_list[i])
    pattern = re.compile(r'href="\/([a-z]{4})\/planyourvisit\/([^/\r\n]+)\.htm"')
    matches = pattern.finditer(things2do_source.text + pub_source.text)
    activity_link_list.append((['https://www.nps.gov' + match.group(0)[6:-1] for match in matches]))
    matches = pattern.finditer(things2do_source.text + pub_source.text)
    activity_str_list.append(([match.group(2) for match in matches]))
print('', end='\r')

for i in range(1, len(activity_link_list)):
    activity_link_list[i] = remove_dups(activity_link_list[i])
    activity_str_list[i] = remove_dups(activity_str_list[i])

print(' - Writing .csv file')
with open('park_info.csv', 'w') as csv_file:
    writer = csv.writer(csv_file, delimiter=',')
    for i in range(0, len(title_list)):
        print(f'{i}: {([title_list[i], link_list[i], date_list[i], area_list[i], lat_list[i], long_list[i], activity_link_list[i], activity_str_list[i]])}\n')
        writer.writerow(([title_list[i], link_list[i], date_list[i], area_list[i], lat_list[i], long_list[i], activity_link_list[i], activity_str_list[i]]))
