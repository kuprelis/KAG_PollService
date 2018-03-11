import html

import firebase_admin
from firebase_admin import credentials, messaging
import requests
from json import JSONDecoder
import json

cred = credentials.Certificate('service_key.json')
app = firebase_admin.initialize_app(cred)


def get_json_obj(url):
    resp = requests.get(url, headers={'User-Agent': ''})
    text = resp.content.decode('utf-8')
    text = html.unescape(text)
    return JSONDecoder().decode(text)


def send_message(title, body, topic):
    config = messaging.AndroidConfig(ttl=12*60*60)
    msg = messaging.Message(data={'title': title, 'body': body}, android=config, topic=topic)
    return messaging.send(msg, False, app)


timestamps = {}
try:
    with open('timestamps.json') as file:
        timestamps = JSONDecoder().decode(file.read())
except FileNotFoundError:
    pass

obj = get_json_obj('http://azuolynogimnazija.lt/json/svarbu')
if 'alerts' in timestamps and obj['updated_at'] > timestamps['alerts'] or 'alerts' not in timestamps:
    timestamps['alerts'] = obj['updated_at']
    print(send_message(obj['title'], obj['text'], 'alerts'))

obj = get_json_obj('http://azuolynogimnazija.lt/json/news?perpage=1')
item = obj['data'][0]
if 'news' in timestamps and item['created_at'] > timestamps['news'] or 'news' not in timestamps:
    timestamps['news'] = item['created_at']
    print(send_message(item['title'], item['primarytext'], 'news'))

with open('timestamps.json', 'w') as file:
    json.dump(timestamps, file)
