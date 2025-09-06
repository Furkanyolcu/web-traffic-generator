#!/usr/bin/python

from __future__ import print_function
import requests
import re
import time
import random
try:
    import config
except ImportError:
    
    class ConfigClass:  
        MAX_DEPTH = 10 
        MIN_DEPTH = 3   
        MAX_WAIT = 120   
        MIN_WAIT = 5
        DEBUG = True    

        
        #ROOT_URLS = ["https://digg.com/"]
        ROOT_URLS = [
            "https://www.reddit.com",
            "https://www.yahoo.com",
            "https://www.bbc.com",
            "https://www.wikipedia.org",
	    "https://www.cnn.com",
            "https://www.theguardian.com",
            "https://www.nytimes.com",
            "https://www.wired.com",
            "https://www.nationalgeographic.com",
            "https://www.techcrunch.com",
            "https://www.sciencedaily.com",
            "https://www.howtogeek.com",
            "https://www.weather.com",
            "https://www.imdb.com",
            "https://www.furkanyolcu.com.tr",
	    "https://www.stackoverflow.com",
            "https://www.medium.com",
            "https://www.quora.com",
            "https://www.researchgate.net",
            "https://www.github.com",
            "https://www.gitlab.com",
            "https://www.npr.org",
            "https://www.forbes.com",
            "https://www.bloomberg.com",
            "https://www.aljazeera.com",
            "https://www.economist.com",
            "https://www.scientificamerican.com",
            "https://www.space.com",
            "https://www.arstechnica.com",
            "https://www.zdnet.com",
            "https://www.engadget.com",
            "https://www.slashdot.org",
            "https://www.khanacademy.org",
            "https://www.edx.org",
            "https://www.coursera.org"
        ]

        # items can be a URL "https://t.co" or simple string to check for "amazon"
        blacklist = [
            'facebook.com',
            'pinterest.com',
            't.co',
            'twitter.com',
            '.css',
            '.ico',
            '.xml',
            '.json',
            '.png',
            '.jpg',
            '.gif'
        ]

        # Different user agent list
        USER_AGENTS = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (iPad; CPU OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Android 11; Mobile; rv:68.0) Gecko/68.0 Firefox/88.0',
            'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36 OPR/77.0.4054.146'
        ]

    config = ConfigClass


class Colors:
    RED = '\033[91m'
    YELLOW = '\033[93m'
    PURPLE = '\033[95m'
    NONE = '\033[0m'


def debug_print(message, color=Colors.NONE):
    """ A method which prints if DEBUG is set """
    if config.DEBUG:
        print(color + message + Colors.NONE)


def hr_bytes(bytes_, suffix='B', si=False):
    """ A method providing a more legible byte format """

    bits = 1024.0 if si else 1000.0

    for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
        if abs(bytes_) < bits:
            return "{:.1f}{}{}".format(bytes_, unit, suffix)
        bytes_ /= bits
    return "{:.1f}{}{}".format(bytes_, 'Y', suffix)


def do_request(url):
    """ A method which loads a page """

    global data_meter
    global good_requests
    global bad_requests

    debug_print("  Requesting page...".format(url))

    # Random user agent 
    user_agent = random.choice(config.USER_AGENTS)
    headers = {'user-agent': user_agent}
    
    debug_print("  Using User-Agent: {}".format(user_agent))

    try:
        r = requests.get(url, headers=headers, timeout=5)
    except:
        time.sleep(30)
        return False

    page_size = len(r.content)
    data_meter += page_size

    debug_print("  Page size: {}".format(hr_bytes(page_size)))
    debug_print("  Data meter: {}".format(hr_bytes(data_meter)))

    status = r.status_code

    if (status != 200):
        bad_requests += 1
        debug_print("  Response status: {}".format(r.status_code), Colors.RED)
        if (status == 429):
            debug_print(
                "  We're making requests too frequently... sleeping longer...")
            config.MIN_WAIT += 10
            config.MAX_WAIT += 10
    else:
        good_requests += 1

    debug_print("  Good requests: {}".format(good_requests))
    debug_print("  Bad reqeusts: {}".format(bad_requests))

    return r


def get_links(page):
    """ A method which returns all links from page, less blacklisted links """

    pattern = r"(?:href\=\")(https?:\/\/[^\"]+)(?:\")"
    links = re.findall(pattern, str(page.content))
    valid_links = [link for link in links if not any(
        b in link for b in config.blacklist)]
    return valid_links


def recursive_browse(url, depth):
    """ A method which recursively browses URLs, using given depth """


    debug_print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    debug_print(
        "Recursively browsing [{}] ~~~ [depth = {}]".format(url, depth))

    if not depth:  

        do_request(url)
        return

    else:  

        page = do_request(url)  

        if not page:
            debug_print(
                "  Stopping and blacklisting: page error".format(url), Colors.YELLOW)
            config.blacklist.append(url)
            return

        # scrape page for links not in blacklist
        debug_print("  Scraping page for links".format(url))
        valid_links = get_links(page)
        debug_print("  Found {} valid links".format(len(valid_links)))

        # give up if no links to browse
        if not valid_links:
            debug_print("  Stopping and blacklisting: no links".format(
                url), Colors.YELLOW)
            config.blacklist.append(url)
            return

        # sleep and then recursively browse
        sleep_time = max(config.MIN_WAIT, 
                         min(config.MAX_WAIT, int(abs(random.gauss(30, 15)))))
        debug_print("  Pausing for {} seconds...".format(sleep_time))
        time.sleep(sleep_time)

        recursive_browse(random.choice(valid_links), depth - 1)


if __name__ == "__main__":

    # Initialize global variables
    data_meter = 0
    good_requests = 0
    bad_requests = 0

    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    print("Traffic generator started")
    print("https://github.com/ecapuano/web-traffic-generator")
    print("Diving between 3 and {} links deep into {} root URLs,".format(
        config.MAX_DEPTH, len(config.ROOT_URLS)))
    print("Waiting between {} and {} seconds between requests. ".format(
        config.MIN_WAIT, config.MAX_WAIT))
    print("Using {} different user agents.".format(len(config.USER_AGENTS)))
    print("This script will run indefinitely. Ctrl+C to stop.")

    while True:

        debug_print("Randomly selecting one of {} Root URLs".format(
            len(config.ROOT_URLS)), Colors.PURPLE)

        random_url = random.choice(config.ROOT_URLS)
        depth = random.choice(range(config.MIN_DEPTH, config.MAX_DEPTH))

        recursive_browse(random_url, depth)
