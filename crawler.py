import requests
from bs4 import BeautifulSoup
#import pprint
import re
import JomestateImporter as ji
import consts as cc

#pp = pprint.PrettyPrinter(indent=4)
#debug=False

processed=0
#fetch page
def fetch_page(url):
    r = requests.get(url)
    if r.status_code != requests.codes.ok:
        print "Error fetching {0}".format(url)
        return None
    r.encoding = 'utf-8'

    return r.text.replace(u'\xa0',u' ')

def fetch_post_aptlist(url):
    r = requests.post(url,data=cc.payload)
    if r.status_code != requests.codes.ok:
        print "Error fetching {0}".format(url)
        exit()
    return r.json()

#apre la voce di menu per un determinato indirizzo
def parse_address(c):
    url=cc.MAIN_URL+c
    print url
    p=fetch_post_aptlist(url)
    for apt in p['data_result']:
        ji.add_apt(apt)
        global processed
        processed+=1
    

mainpage=fetch_page(cc.MAIN_URL)
if not mainpage:
    exit()
mainsoup = BeautifulSoup(mainpage)
menus=mainsoup.select('.dm-menu > li')
print len(menus),'menu voices'
aptli=menus[2]
categories=aptli.select('li a')
print len(categories),'addresses found'
hrefs=[x.get('href') for x in categories]
print hrefs
if len(hrefs)<1:
    print "Error can't find addresses"
    exit()

#for c in hrefs:
 #   parse_address(c)
parse_address('/All-Apartments')
global processed
print processed, "apts stolen"
