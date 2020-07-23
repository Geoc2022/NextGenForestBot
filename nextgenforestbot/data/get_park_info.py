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
