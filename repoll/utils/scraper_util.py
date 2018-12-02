import re
import requests
from bs4 import BeautifulSoup


def get_first_url(text):
    urls = re.findall('https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', text)
    return urls[0]


def url_exists(text):
    url = None
    try:
        url = get_first_url(text)[0]
    except Exception as e:
        return False
    else:
        return True

def get_page_thumb_title_desc(url):
    browser = webdriver.Firefox()
    #req = requests.get(url, stream=True, verify='/home/cranium/Documents/prod/repoll/localhost.crt')
 #   headers = {'User-Agent': 'Mozilla/5'}   
    browser.get(url)
    cotent = browser.page_source
    
    
    soup = BeautifulSoup(content, 'html.parser')
    title = soup.title.string
    thumb = soup.find('meta', property='og:image')['content']
    description = soup.find('meta', property='og:description')['content']
    return thumb, title, description


def get_page_desc(url):
    req = requests.get(url)
    soup = BeautifulSoup(req.text)
    desc = soup.find('meta', property='og:description')
    if desc: 
        return desc['content']
    else: 
        return ''

def get_page_thumb(url):
    req = requests.get(url)
    soup = BeautifulSoup(req.text)
    thumb = soup.find('meta', property='og:image')
    thumb_content = ''
    if thumb: 
        thumb_content = thumb['content']

    return thumb_content
