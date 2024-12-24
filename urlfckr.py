import argparse
from urllib.parse import urlparse, urljoin
import requests
from bs4 import BeautifulSoup as bs
import tldextract
import signal
import sys


RED = "\033[0;31m"
GREEN = "\033[0;32m"
BLUE = "\033[0;34m"
PURPLE = "\033[0;35m"
END = "\033[0m"

urls_to_visit = set()
visited_urls = set()
relative_urls = set()
subdomains = set()

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
    print_results()
    sys.exit(0)


def get_args():
    parser = argparse.ArgumentParser(description="URLFCKR")
    parser.add_argument("-u", "--url", type=str, dest="url", help="Base URL", required=True)
    args = parser.parse_args()
    return args.url


def validate_url(url):
    try:
        url_parsed = urlparse(url)
        if url_parsed.scheme not in ["http", "https"]:
            raise ValueError(
                f"Scheme '{url_parsed.scheme}' isn't valid. "
                "URL must begin with 'http' or 'https'"
            )
        return True
    except ValueError as e:
        print(f"[{RED}ERROR{END}] {str(e)}")


def get_html(url):
    try:
        response = requests.get(url)
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"[{RED}ERROR{END}] {str(e)}")


def get_hrefs(html):
    try:
        soup = bs(html, "html.parser")
        return [a.get("href") for a in soup.find_all("a")]
    except Exception as e:
        print(f"[{RED}ERROR{END}] {str(e)}")


def get_valid_hrefs(hrefs, url_base):
    for href in hrefs:
        if href and not href.startswith("#"):
            href_parsed = urlparse(href)
            if href_parsed.scheme in ["http", "https"] and is_subdomain(url_base, href):
                subdomains.add(urljoin(href_parsed.scheme + "://" + href_parsed.netloc, "/"))
                if urljoin(url_base, href) not in visited_urls:
                    urls_to_visit.add(urljoin(url_base, href))
            elif not href_parsed.scheme:
                relative_urls.add(urljoin(url_base, href))
                if urljoin(url_base, href) not in visited_urls:
                    urls_to_visit.add(urljoin(url_base, href))


def is_subdomain(base_url, url):
    base_info = tldextract.extract(base_url)
    base_domain = f"{base_info.domain}.{base_info.suffix}"
    
    url_info = tldextract.extract(url)
    url_domain = f"{url_info.domain}.{url_info.suffix}"
    
    return url_domain == base_domain and url_info.subdomain != ""


def print_results():
    print()
    print(f"[{BLUE}RELATIVE URLS{END}][{PURPLE}{len(relative_urls)}{END}]\n{"\n".join(map(str, sorted(relative_urls)))}" + ("\n" if len(relative_urls) > 0 else ""))
    print(f"[{BLUE}SUBDOMAINS{END}][{PURPLE}{len(subdomains)}{END}]\n{"\n".join(map(str, sorted(subdomains)))}" + ("\n" if len(subdomains) > 0 else ""))
    print(f"[{BLUE}VISITED URLS{END}][{PURPLE}{len(visited_urls)}{END}]\n{"\n".join(map(str, sorted(visited_urls)))}" + ("\n" if len(visited_urls) > 0 else ""))


def main():
    
    signal.signal(signal.SIGINT, signal_handler)
    
    url_base = get_args()

    print(ascii_art)

    if validate_url(url_base):
        urls_to_visit.add(url_base)
        while urls_to_visit:
            url_to_visit = urls_to_visit.pop()
            visited_urls.add(url_to_visit)
            print(f"[{GREEN}ANALIZING{END}] {url_to_visit}")
            html = get_html(url_to_visit)
            hrefs = get_hrefs(html)
            get_valid_hrefs(hrefs, url_to_visit)


    print_results()


if __name__ == "__main__":
    main()