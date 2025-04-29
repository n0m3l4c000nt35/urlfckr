import argparse
import requests
from bs4 import BeautifulSoup as bs
import tldextract
from urllib.parse import urlparse, urlsplit, urlunsplit
import sys
import signal

RED = "\033[0;31m"
GREEN = "\033[0;32m"
BLUE = "\033[0;34m"
PURPLE = "\033[0;35m"
END = "\033[0m"

subdomains = []
urls_to_visit = []
visited_urls = []

ascii_art = """
                                  ..                           ..                   
                            x .d88"     oec :            < .z@8"`                   
   x.    .        .u    .    5888R     @88888             !@88E           .u    .   
 .@88k  z88u    .d88B :@8c   '888R     8"*88%        .    '888E   u     .d88B :@8c  
~"8888 ^8888   ="8888f8888r   888R     8b.      .udR88N    888E u@8NL  ="8888f8888r 
  8888  888R     4888>'88"    888R    u888888> <888'888k   888E`"88*"    4888>'88"  
  8888  888R     4888> '      888R     8888R   9888 'Y"    888E .dN.     4888> '    
  8888  888R     4888>        888R     8888P   9888        888E~8888     4888>      
  8888 ,888B .  .d888L .+     888R     *888>   9888        888E '888&   .d888L .+   
 "8888Y 8888"   ^"8888*"     .888B .   4888    ?8888u../   888E  9888.  ^"8888*"    
  `Y"   'YP        "Y"       ^*888%    '888     "8888P'  '"888*" 4888"     "Y"      
                               "%       88R       "P'       ""    ""                
                                        88>                                         
                                        48                                          
                                        '8
                                        """


def signal_handler(sig, frame):
    print(f"\n[{RED}SEE YA{END}]")
    sys.exit(0)


def get_args():
    parser = argparse.ArgumentParser(prog="urlfckr", description="Extract subdomains from source code of a website", epilog="https://github.com/n0m3l4c000nt35/urlfckr")
    parser.add_argument("-u", "--url", type=str, dest="url", help="Base URL", required=True)
    args = parser.parse_args()
    return args.url


def main():
    signal.signal(signal.SIGINT, signal_handler)
    url = get_args()

    if not urlparse(url).scheme:
        print("No scheme provided. Please include 'http://' or 'https://' in the URL.")
        sys.exit(1)
    
    splited_href = urlsplit(url)
    urlready = urlunsplit((splited_href.scheme, splited_href.netloc, "","",""))
    urls_to_visit.append(urlready)

    print(ascii_art)

    while urls_to_visit:
        try:
            url_to_visit = urls_to_visit.pop()
            print(f"[{BLUE}ANALYZING{END}] {url_to_visit}")
            response = requests.get(url_to_visit, timeout=3)
        except requests.exceptions.MissingSchema as e:
            print("No scheme provided. Please include 'http://' or 'https://' in the URL.")
        except requests.exceptions.Timeout as e:
            print("Request timed out. Please check the URL or your internet connection.")

        if response.status_code == 200:
            soup = bs(response.text, "html.parser")

            for link in soup.find_all('a'):
                href = link.get("href")
                splited_href = urlsplit(href)
                urlready = urlunsplit((splited_href.scheme, splited_href.netloc, "","",""))
                if href is not None:
                    href_extracted = tldextract.extract(href)
                    url_domain = tldextract.extract(url_to_visit).domain
                    if href_extracted.domain == url_domain and href_extracted.subdomain != "www":
                        if urlready not in subdomains:
                            subdomains.append(urlready)
                            print(f"[{GREEN}SUBDOMAIN FOUND{END}] {urlready}")
                            if urlready not in visited_urls:
                                urls_to_visit.append(urlready)
            visited_urls.append(url_to_visit)
        else:
            print(f"[{RED}ERROR{END}] {response.status_code} - {url_to_visit}")
    else:
        print(f"\n[{PURPLE}DONE{END}]")


if __name__ == "__main__":
    main()