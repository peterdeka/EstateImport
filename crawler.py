import requests
from bs4 import BeautifulSoup
#import pprint
import re
import JomestateImporter as ji


#pp = pprint.PrettyPrinter(indent=4)
#debug=False
MAIN_URLS='http://www.cortinarent.com'
IMAGE_URLS='http://www.cortinarent.com/data/frontImages/vacationrentals/vacationrentals_image/'
payload={'take':'100','skip':'0','page':'1','pageSize':'100'}

#fetch page
def fetch_page(url):
    r = requests.get(url)
    if r.status_code != requests.codes.ok:
        print "Error fetching {0}".format(url)
        return None
    r.encoding = 'utf-8'

    return r.text.replace(u'\xa0',u' ')

def fetch_post_aptlist(url):
    r = requests.post(url,data=payload)
    if r.status_code != requests.codes.ok:
        print "Error fetching {0}".format(url)
        exit()
    return r.json()

#apre la voce di menu per un determinato indirizzo
def parse_address(c):
    url=MAIN_URLS+c
    print url
    p=fetch_post_aptlist(url)
    for apt in p['data_result']:
        parse_apt(c, apt)

def parse_apt(address,apt):
    print apt['vacationrentals_name']


mainpage=fetch_page(MAIN_URLS)
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

for c in hrefs:
    parse_address(c)

#for j in range(4,len(categories)):
 #   parse_category(categories[j],[])

#for li in categories:
 #   parse_category(li,[])

#fvariationserr.close()
#fmanuerr.close()
