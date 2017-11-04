import os
import sys
import time
import requests
import feedparser
import dropbox
from bs4 import BeautifulSoup

ACCESS_TOKEN = "XXXXXXXXXXXXXXXXXXXXXXX"

dbx = dropbox.Dropbox(ACCESS_TOKEN)
dbx.users_get_current_account()
entry_list = [entry.name for entry in dbx.files_list_folder('').entries]
if 'doushoko' not in entry_list:
    dbx.files_create_folder('/doushoko')
entry_list = [entry.name for entry in dbx.files_list_folder('/doushoko').entries]


def save_dropbox(image, dir_name, file_name):
    if dir_name not in entry_list:
        entry_list.append(dir_name)
        dbx.files_create_folder('/doushoko/{}'.format(dir_name))
    dbx.files_upload(
        image, '/doushoko/{0}/{1}'.format(dir_name, file_name), mute=True)


def save_local(image, dir_name, file_name):
    if not os.path.isdir('image'):
        os.mkdir('image')
    if not os.path.isdir('image/{}'.format(dir_name)):
        os.mkdir('image/{}'.format(dir_name))
    with open('image/{0}/{1}'.format(dir_name, file_name), 'wb') as f:
        f.write(image)


def download_image(image_url, cmd):
    dir_name = image_url.split('/')[-2]
    file_name = image_url[-7:]
    res = requests.get(image_url)
    image = res.content
    if cmd == '--dropbox':
        save_dropbox(image, dir_name, file_name)
    elif cmd == '--local':
        save_local(image, dir_name, file_name)
    time.sleep(1)


def get_image_url(main_url):
    url_list = []
    link = BeautifulSoup(requests.get(main_url).text, "lxml")
    time.sleep(1)
    for url in link.find_all('a'):
        if type(url.get('href')) == str and url.get('href').endswith('.jpg'):
            url_list.append(url.get('href'))
    return url_list


def get_links_from_rss(RSS_URL):
    feed = feedparser.parse(RSS_URL)
    links = []
    for result in feed.entries:
        links.append(result['link'])
    return links


def run():
    RSS_URL = "http://www.dousyoko.net/feed"
    links = get_links_from_rss(RSS_URL)
    cmd = sys.argv[1]
    for link in links:
        image_links = get_image_url(link)
        for link in image_links:
            download_image(link, cmd)


if __name__ == '__main__':
    run()
