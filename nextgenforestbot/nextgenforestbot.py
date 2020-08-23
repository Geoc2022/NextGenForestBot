#@NextGenForestB1

import tweepy
import time
import sys
import csv
import math
import re
import geocoder
from pyowm import OWM
from keys import *

# NOTE: flush=True is just for running this script
# with PythonAnywhere's always-on task.
# More info: https://help.pythonanywhere.com/pages/AlwaysOnTasks/

# = setup =
print('Running...')

CONSUMER_KEY = ''
CONSUMER_SECRET = ''
ACCESS_KEY = ''
ACCESS_SECRET = ''

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth)

mapbox_key = 'pk.eyJ1IjoiZ2VvY2giLCJhIjoiY2tjZ3M5OTh6MDJlbjJxbWhwZHI1MXVoaiJ9.qpy6TD5rCJovweLIeE7DbA'

FILE_NAME = 'last_seen_id.txt'

def retrieve_last_seen_id(file_name):
    f_read = open(file_name, 'r')
    last_seen_id = int(f_read.read().strip())
    f_read.close()
    return last_seen_id

def store_last_seen_id(last_seen_id, file_name):
    f_write = open(file_name, 'w')
    f_write.write(str(last_seen_id))
    f_write.close()
    return
    

# = functions =
#Remove dups
def remove_dups(x):
    return list(dict.fromkeys(x))


#Distance Between Coords
def dist_coord(c1, c2):
    R = 6371*(10**3)
    φ1, φ2 = (c1[0] * math.tau/360), (c2[0] * math.tau/360)
    Δφ, Δλ = ((c2[0]-c1[0]) * math.tau/360), ((c2[1]-c1[1]) * math.tau/360)

    a = math.sin(Δφ/2) * math.sin(Δφ/2) + math.cos(φ1) * math.cos(φ2) * math.sin(Δλ/2) * math.sin(Δλ/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = R * c
    return d


#Search Location
def search_location(text_to_search):
    global mapbox_key
    patterns = [
    '((1?\d{0,2})(\.\d+)?)°?\s?([NSns]),?\s+((1?\d{0,2})(\.\d+)?)°?\s?([WEwe])',
    '(1?\d{0,2})°\s?((\d{0,2})\'\s?)?((\d{0,2}\.?\d*)\"\s?)?([NSns]),?\s+(1?\d{0,2})°\s?((\d{0,2})\'\s?)?((\d{0,2}\.?\d*)\"\s?)?([WEwe])',
    '(-?1?\d{0,2})°\s?((\d{0,2})\'\s?)?((\d{0,2}\.?\d*)\'\'\s?)?([NSns]),?\s+(-?1?\d{0,2})°\s?((\d{0,2})\'\s?)?((\d{0,2}\.?\d*)\'\'\s?)?([WEwe])',
    '((-?1?\d{1,2})(\.\d+)?),?\s+((-?1?\d{1,2})(\.\d+)?)',
    '([A-z]\w+),\s?([A-Z]\w+)']
    
    match_list = []
    for i, pattern_text in enumerate(patterns):
        pattern = re.compile(pattern_text)
        matches = pattern.finditer(text_to_search)
        for match in matches:
            mg = []
            for j in range(len(match.groups())):
                try:
                    mg.append(float(match.groups()[j]))
                except:
                    if match.groups()[j]:
                        mg.append((match.groups()[j]).lower())
                    else:
                        mg.append(0)
            if i == 0:
                match_lat = mg[0]*(1 if mg[3] == "n" else -1)
                match_long = mg[4]*(1 if mg[7] == "e" else -1)
            elif i == 1:
                match_lat = (mg[0]+(mg[2]/60)+(mg[4]/3600))*(1 if mg[5] == "n" else -1)
                match_long = (mg[6]+(mg[8]/60)+(mg[10]/3600))*(1 if mg[11] == "e" else -1)
            elif i == 2:
                match_lat = (mg[0]+(mg[2]/60)+(mg[4]/3600))*(1 if mg[5] == "n" else -1)
                match_long = (mg[6]+(mg[8]/60)+(mg[10]/3600))*(1 if mg[11] == "e" else -1)
            elif i == 3:
                match_lat = mg[0]
                match_long = mg[3]
            else:
                match_lat = (geocoder.mapbox(f'{mg[0]}, {mg[1]}', key=mapbox_key).latlng)[0]
                match_long = (geocoder.mapbox(f'{mg[0]}, {mg[1]}', key=mapbox_key).latlng)[1]
            match_list.append([match_lat, match_long])
    
    match_text = []
    match_text = remove_dups([f'{match[0]}, {match[1]}' for match in match_list])
    match_list = [coord.split(', ') for coord in match_text]
    match_list = [[float(coord[0]), float(coord[1])] for coord in match_list]
    
    match_list.append([0,0])
    
    return match_list
    
# Search Activity/Area/Length/Date/tbm/link/nearby
def search_fun(text_to_search):
    search_input_dict = {}
    pattern_types = [['title', 'name'], ['activity', 'act'], ['area', 'size'], ['length', 'len'], ['link', 'call'],
                     ['nearbyparks', 'nearbytrails'], ['nearbypark', 'nearbytrail'], ['nearby', 'nearbys']]
    for i, search_term in enumerate(pattern_types):
        if (i == 0):
            patterns = [f'{search_term[0]}\((([^$.*+?,|]?\w+,?\s*)+)\)', f'{search_term[1]}\((([^$.*+?,|]?\w+,?\s*)+)\)']
        elif (i == 1) or (i == 4):
            patterns = [f'{search_term[0]}\(((\w+,?\s*)+)\)', f'{search_term[1]}\(((\w+,?\s*)+)\)']
        elif (i == 2) or (i == 3):
            patterns = [f'{search_term[0]}\(((([<>]?\d+(\.\d+)?(\w+\^?\d?)?[<>]?)-?,?\s*)+)\)',
                        f'{search_term[1]}\(((([<>]?\d+(\.\d+)?(\w+\^?\d?)?[<>]?)-?,?\s*)+)\)']
        else:
            patterns = [f'{search_term[0]}\((-?\d+)\)', f'{search_term[1]}\((-?\d+)\)']

        match_list = []
        for pattern_text in patterns:
            pattern = re.compile(pattern_text)
            matches = pattern.finditer(text_to_search)
            for match in matches:
                match_list.extend(re.split(r'[,.]\s*|\s+', (match.group(1)).lower()))

        match_list = remove_dups(match_list)
        search_input_dict.update({str(search_term[0]): match_list})

    return search_input_dict


# Check Activity/Area/Length/Date/tbm/link/nearby in Files
def check_fun_csv(search_input, t_p):
    global user_location
    file_title_list = []
    file_link_list = []
    file_latlong_list = []
    if t_p == 'park_info':
        file_area_list = []
        file_activity_list = []
        file_activitylink_list = []
    else:
        file_len_list = []
    with open(f'data/{t_p}.csv', 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        next(csv_reader)
        for line in csv_reader:
            file_title_list.append(line[0])
            file_link_list.append(line[1])
            if t_p == 'park_info':
                file_area_list.append(line[3])
                file_activitylink_list.append(line[6])
                file_activity_list.append(line[7])
                file_latlong_list.append([line[4], line[5]])
            else:
                file_len_list.append(line[2])
                file_latlong_list.append((line[3][1:-1]).split(', '))

    for i, coord in enumerate(file_latlong_list):
        file_latlong_list[i] = [float(file_latlong_list[i][0]), float(file_latlong_list[i][1])]

    if t_p == 'park_info':
        for i in range(len(file_activity_list)):
            file_activity_list[i] = (file_activity_list[i][2:-2]).split("\', \'")
            file_activitylink_list[i] = (file_activitylink_list[i][2:-2]).split("\', \'")
        search_results = {
            file_title_list[i]: [file_link_list[i], file_area_list[i], file_latlong_list[i], file_activitylink_list[i], file_activity_list[i]] for i in range(len(file_title_list))}
        sifted_search_results = {}
        for title in search_results.keys():
            sifted_search_results.update({title: {'activity': {}, 'link': {}}})

    if t_p == 'trail_info':
        search_results = {file_title_list[i]: [file_link_list[i], file_len_list[i], file_latlong_list[i]] for i in
                          range(len(file_title_list))}

    for search_type, search_terms in search_input.items():
        temp_search_results = {}
        if (search_type == 'title') and search_terms:
            for title, values in search_results.items():
                for search_term in search_terms:
                    if re.match(search_term, title.lower()):
                        temp_search_results.update({title: search_results[title]})
            search_results = temp_search_results
        elif (search_type == 'activity') and search_terms and t_p == 'park_info':
            for title, values in search_results.items():
                temp_activity_search_results = {}
                for search_term in search_terms:
                    temp_activity_search_results.update({search_term: []})
                for i, activity_str in enumerate(values[-1]):
                    for search_term in search_terms:
                        if search_term in activity_str.lower():
                            temp_search_results.update({title: search_results[title]})
                            (temp_activity_search_results[search_term]).append(
                                [activity_str, search_results[title][-2][i][8:]])
                sifted_search_results[title]['activity'] = temp_activity_search_results
            search_results = temp_search_results
        elif (search_type == 'area') and search_terms and t_p == 'park_info':
            for title, values in search_results.items():
                for search_term in search_terms:

                    area_unit_dict = {
                        'mi2': 1 / 2.59,
                        'miles2': 1 / 2.59,
                        'mi^2': 1 / 2.59,
                        'miles^2': 1 / 2.59,
                        'y2': 1.196 * (10 ** 6),
                        'yard2': 1.196 * (10 ** 6),
                        'y^2': 1.196 * (10 ** 6),
                        'yard^2': 1.196 * (10 ** 6),
                        'hectare': 100,
                        'ha': 100
                    }

                    area_unit = ''
                    if 'acres' in search_term:
                        area_unitized = float(((values[1][:-5]).split(' acres ('))[0])
                        area_unit = 'acres'
                    else:
                        for unit_name, unit_conversion in area_unit_dict.items():
                            if f'{unit_name}' in search_term:
                                area_unitized = (float(((values[1][:-5]).split(' acres ('))[1])) * unit_conversion
                                area_unit = f'{unit_name}'
                        if not area_unit:
                            area_unitized = float(((values[1][:-5]).split(' acres ('))[1])

                    search_term = search_term.replace(f'{area_unit}', '')

                    if re.fullmatch('\d+(\.\d+)?', search_term):
                        if round(float(search_term)) == round(area_unitized):
                            temp_search_results.update({title: search_results[title]})
                    if re.fullmatch('\d+(\.\d+)?-\d+(\.\d+)?', search_term):
                        if float((search_term.split('-'))[0]) < area_unitized < float((search_term.split('-'))[1]):
                            temp_search_results.update({title: search_results[title]})
                    if re.fullmatch('>\d+(\.\d+)?', search_term):
                        if float(search_term[1:]) < area_unitized:
                            temp_search_results.update({title: search_results[title]})
                    if re.fullmatch('\d+(\.\d+)?<', search_term):
                        if float(search_term[:-1]) < area_unitized:
                            temp_search_results.update({title: search_results[title]})
                    if re.fullmatch('<\d+(\.\d+)?', search_term):
                        if float(search_term[1:]) > area_unitized:
                            temp_search_results.update({title: search_results[title]})
                    if re.fullmatch('\d+(\.\d+)?>', search_term):
                        if float(search_term[:-1]) > area_unitized:
                            temp_search_results.update({title: search_results[title]})
            search_results = temp_search_results
        elif (search_type == 'length') and search_terms and t_p == 'trail_info':
            for title, values in search_results.items():
                for search_term in search_terms:

                    len_unit_dict = {
                        'km': 1.609,
                        'kilometer': 1.609,
                        'y': 1760,
                        'yard': 1760,
                        'f': 5280,
                        'feet': 5280
                    }

                    len_unit = ''
                    for unit_name, unit_conversion in len_unit_dict.items():
                        if f'{unit_name}' in search_term:
                            len_unitized = (float(values[1][:-6])) * unit_conversion
                            len_unit = f'{unit_name}'
                    if not len_unit:
                        len_unitized = float(values[1][:-6])

                    search_term = search_term.replace(f'{len_unit}', '')

                    if re.fullmatch('\d+(\.\d+)?', search_term):
                        if round(float(search_term)) == round(len_unitized):
                            temp_search_results.update({title: search_results[title]})
                    if re.fullmatch('\d+(\.\d+)?-\d+(\.\d+)?', search_term):
                        if float((search_term.split('-'))[0]) < len_unitized < float((search_term.split('-'))[1]):
                            temp_search_results.update({title: search_results[title]})
                    if re.fullmatch('>\d+(\.\d+)?', search_term):
                        if float(search_term[1:]) < len_unitized:
                            temp_search_results.update({title: search_results[title]})
                    if re.fullmatch('\d+(\.\d+)?<', search_term):
                        if float(search_term[:-1]) < len_unitized:
                            temp_search_results.update({title: search_results[title]})
                    if re.fullmatch('<\d+(\.\d+)?', search_term):
                        if float(search_term[1:]) > len_unitized:
                            temp_search_results.update({title: search_results[title]})
                    if re.fullmatch('\d+(\.\d+)?>', search_term):
                        if float(search_term[:-1]) > len_unitized:
                            temp_search_results.update({title: search_results[title]})
            search_results = temp_search_results
        elif (search_type == 'link') and search_terms and t_p == 'park_info':
            for title, values in search_results.items():
                temp_link_search_results = {}
                for search_term in search_terms:
                    temp_link_search_results.update({search_term: []})
                for i, link_str in enumerate(values[-1]):
                    for search_term in search_terms:
                        if search_term in link_str.lower():
                            temp_search_results.update({title: search_results[title]})
                            (temp_link_search_results[search_term]).append(
                                [link_str, search_results[title][-2][i][8:]])
                sifted_search_results[title]['link'] = temp_link_search_results
        elif ((search_type == 'nearbyparks') or (search_type == 'nearbypark') or (search_type == 'nearby')) and search_terms:
            dist_user_parktrail_dict = {}
            for title, values in search_results.items():
                dist_user_parktrail_dict.update({title: dist_coord(user_location, values[2])})
                sort_dist_list = sorted(dist_user_parktrail_dict, key=dist_user_parktrail_dict.__getitem__)
            if int(search_terms[0]) > 0:
                nearby_parktrail_list = sort_dist_list[:int(search_terms[0])]
            else:
                nearby_parktrail_list = sort_dist_list[int(search_terms[0]):]
                nearby_parktrail_list.reverse()
            for parktrail in nearby_parktrail_list:
                temp_search_results.update({parktrail: search_results[parktrail]})
            search_results = temp_search_results
            
    if t_p == 'park_info':
        sifted_search_results = {k:sifted_search_results[k] for k in search_results.keys()}

#    if t_p == 'park_info':
#        for k, v in search_results.items():
#            print(f'\n{k}: \n{v[0][12:]} \n{v[1]} \n{v[2]}')
#            for i in range(len(v[3])):
#                print(f'\t{v[4][i]}: {v[3][i][39:]}')
#            print('\n')
#        for k, v in sifted_search_results.items():
#            print(f'\n{k}:\n {v}')
#    else:
#        for k, v in search_results.items():
#            print(f'\n{k}: \n{v[0]} \n{v[1]} \n{v[2]}')
            
    if t_p == 'park_info':
        return search_results, sifted_search_results
    else:
        return search_results
    

#Print Weather
def print_weather(placetitle, weather_stored_dict, items):
    weather_text_list = [
    f"\n{placetitle} - {weather_stored_dict['Status']} {weather_stored_dict['Emoji']}  ({weather_stored_dict['Details']})\nTemperature: {weather_stored_dict['Temperature']['temp']}\n    max: {weather_stored_dict['Temperature']['temp_max']}\n    min: {weather_stored_dict['Temperature']['temp_min']}\n    feels like: {weather_stored_dict['Temperature']['feels_like']}\nWind: {weather_stored_dict['Wind'][0]}, {weather_stored_dict['Wind'][1]}\nUV Exposure: {(weather_stored_dict['UV Exposure']).title()}",
    f"\n{placetitle} - {weather_stored_dict['Status']} {weather_stored_dict['Emoji']}  ({weather_stored_dict['Details']})"]

    try:
        return [weather_text_list[int(item)] for item in items]
    except:
        return [weather_text_list[1]]


#Convert to Tweet Text
def convert_tweet_text():
    global park_or_trail
    global search_results
    global user_tweet_text
    parktrail_text_list = []
    for title in search_results.keys():
        parktrail_weather = get_weather(search_results[title][2])
        
        if park_or_trail == 'park':
            parktrail_text = f"- {title}: {parktrail_weather['Emoji']} {search_results[title][0][12:]}\ngoogle.com/maps/search/?api=1&query={title.replace(' ','+')}+National+Park"
            for i, act_term in enumerate((sifted_search_results[title]['activity']).keys()):
                if sifted_search_results[title]['activity'][act_term]:
                    parktrail_text += f"\n{act_term.title()}:"
                    if not i > 5:
                        for j, act_actlink in enumerate(sifted_search_results[title]['activity'][act_term]):
                            if not j > 3:
                                parktrail_text += f"\n{act_actlink[1][4:]}"
            
            for i, link_term in enumerate((sifted_search_results[title]['link']).keys()):
                if sifted_search_results[title]['link'][link_term]:
                    parktrail_text += f"\n{link_term}: {sifted_search_results[title]['link'][link_term][0][1][4:]}"
        else:
            parktrail_text = f"- {title}: {parktrail_weather['Emoji']} {search_results[title][0][12:]}\ngoogle.com/maps/search/?api=1&query={title.replace(' ','+')}"

        if 'very' in (parktrail_weather['UV Exposure']).lower() or 'extreme' in (parktrail_weather['UV Exposure']).lower():
            parktrail_text += f"\nUV Exposure: {(parktrail_weather['UV Exposure']).title()}"
        parktrail_text_list.append(parktrail_text)
        
        if re.search('weather\((\d[,\s]?)*\)', user_tweet_text.lower()):
            pattern = re.compile('weather\((\d[,\s]?)*\)')
            matches = pattern.finditer(user_tweet_text.lower())
            weather_search_list = []
            for match in matches:
                weather_search_list.extend(re.split(r',\s*|\s+', (match.group(1)).lower()))
            parktrail_text_list.extend(print_weather(title, parktrail_weather, weather_search_list))
        
    return parktrail_text_list


#Get Weather
def get_weather(location):
    owm = OWM('aea60db634c1cdfb77cdd2153c4f9591')
    uv_mgr = owm.uvindex_manager()
    weather_mgr = owm.weather_manager()

    weather = weather_mgr.weather_at_coords(location[0], location[1]).weather
    uvi = uv_mgr.uvindex_around_coords(location[0], location[1])
    wind_dict_in_meters_per_sec = weather.wind()

    temp_keys = []
    temp_values = []
    for kf, f in (weather.temperature('fahrenheit')).items():
        temp_keys.append(kf)
        temp_values.append(f'{f}°F')
    for i, (kf, c) in enumerate((weather.temperature('celsius')).items()):
        temp_values[i] += f', {c}°C'
    temp_dict = {temp_keys[i]: temp_values[i] for i in range(len(temp_keys)-1)}

    if weather.status == 'Thunderstorm':
        if weather.detailed_status in ['thunderstorm with light rain','light thunderstorm','thunderstorm with light drizzle','thunderstorm with drizzle','thunderstorm with heavy drizzle]']:
            weather_emoji = '🌩️'
        else:
            weather_emoji = '⛈️'
    elif weather.status == 'Drizzle':
        weather_emoji = '🌦️'
    elif weather.status == 'Rain':
        if weather.detailed_status == 'freezing rain':
            weather_emoji = '🌨️'
        else:
            weather_emoji = '🌧️'
    elif weather.status == 'Snow':
        weather_emoji = '❄️'
    elif weather.status in ['Mist','Smoke','Haze','Dust','Fog','Sand','Dust','Ash','Squall','Tornado']:
        weather_emoji = '🌫️'
    elif weather.status == 'Clear':
        weather_emoji = '☀️'
    elif weather.status == 'Clouds':
        if weather.detailed_status == 'few clouds':
            weather_emoji = '🌤️'
        elif weather.detailed_status == 'scattered clouds':
            weather_emoji = '⛅'
        else:
            weather_emoji = '☁️'
    else:
        weather_emoji = ' '

    weather_dict = {
    'Status': weather.status,
    'Details': weather.detailed_status,
    'Temperature': temp_dict,
    'Wind': [f"{wind_dict_in_meters_per_sec['speed']}m/s", f"{float('{:.2f}'.format((wind_dict_in_meters_per_sec['speed'])*(3660/1609)))}mi/h", ],
    'UV Exposure': uvi.get_exposure_risk(),
    'Emoji': weather_emoji
    }

    return weather_dict


# = running script =
def reply_to_tweets():
    global search_results
    global sifted_search_results
    global park_or_trail
    global user_location
    global user_tweet_text
    print(time.strftime("%c") + ': retrieving and replying to tweets...')
    last_seen_id = retrieve_last_seen_id(FILE_NAME)
    mentions = api.mentions_timeline(
                        last_seen_id,
                        tweet_mode='extended')
    for mention in reversed(mentions):
        print('\n ' + str(mention.id) + ' - ' + mention.full_text)
        last_seen_id = mention.id
        store_last_seen_id(last_seen_id, FILE_NAME)
        if '#helloworld' in mention.full_text.lower():
            print('found #helloworld')
            print('responding back...')
            api.update_status('@' + mention.user.screen_name + ' HelloWorld', mention.id)
        elif 'park' in mention.full_text.lower() or 'trail' in mention.full_text.lower():
            user_tweet_text = (mention.full_text.replace('\n',' ')).replace('\r',' ')
            
            park_or_trail = 'trail' if 'trail' in mention.full_text.lower() else 'park'
            print(f'found #{park_or_trail}')
            
            print(user_tweet_text.lower())
            
            user_location = (search_location(user_tweet_text))[0]
            
            if park_or_trail == 'park':
                search_results, sifted_search_results = check_fun_csv(search_fun(user_tweet_text.lower()), 'park_info')
            else:
                search_results = sifted_search_results = check_fun_csv(search_fun(user_tweet_text.lower()), 'trail_info')
            
            print('responding back...')
            if user_location == [0,0]:
                api.update_status('@' + mention.user.screen_name + ' Error - Location?', mention.id)
            
            tweet_replies_list = convert_tweet_text()
            for i, tweet_text in enumerate(tweet_replies_list[:10]):
                api.update_status('@' + mention.user.screen_name + tweet_text, mention.id)
            print('completed\n')
        
        elif 'help' in mention.full_text.lower():
            print('found #help')
            print('responding #help...')
            api.update_status('@' + mention.user.screen_name +
                    '\nname(abc park)\nnearby(5) -add location-\n\nParks:\nactivity: act(bike)\narea: size(5, 1-2.5, >7) -mi2, acres-\n link(info, maps, permits, conditions)\n\nTrails:\nlen(*same as size*) -km, mi-\ntwitter.com/NextGenForestB1/status/1286073084362010624?s=20', mention.id)
        elif 'lnt' in mention.full_text.lower() or 'trace' in mention.full_text.lower():
            api.update_status('@' + mention.user.screen_name + 'lnt.org', mention.id)
        elif 'covid' in mention.full_text.lower() or '19' in mention.full_text.lower() or 'corona' in mention.full_text.lower() or 'health' in mention.full_text.lower():
            api.update_status('@' + mention.user.screen_name + 'https://www.nps.gov/aboutus/news/public-health-update.htm', mention.id)
        elif 'essentials' in mention.full_text.lower() or 'pack' in mention.full_text.lower():
            api.update_status('@' + mention.user.screen_name + 'https://www.nps.gov/articles/10essentials.htm', mention.id)
        elif 'planning' in mention.full_text.lower() or 'guide' in mention.full_text.lower():
            api.update_status('@' + mention.user.screen_name + 'https://www.nationalparks.org/connect/blog/how-findyourpark-beginners-guide', mention.id)

def testing(t):
    if t == 1:
        exit = input('Test: ')
        if exit == 'exit':
            sys.exit('Exit')
            
def sleep_load(sec):
    for i in range(sec):
        print('Loading: ', end='')
        time.sleep(1)
        print('■'*i, end='\r')
    print('', end='\r')

while True:
    reply_to_tweets()
#    sleep_load(15)
    testing(1)
