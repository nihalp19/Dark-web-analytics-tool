import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from config import SEARCH_CONFIG

class DarkWebCrawler:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.proxy_settings = None
        self.visited_urls = set()

    def set_proxy(self, proxy_settings):
        self.proxy_settings = proxy_settings

    def crawl(self, urls=None, depth=1, max_pages=50):
        if not self.proxy_settings:
            print("[-] No proxy settings configured. Connect to Tor first.")
            return []

        print("[+] Starting crawl operation...")
        if not urls:
            urls = ["http://directory123.onion", "http://darkwebwiki.i2p", "http://freenetproject.org"]

        crawled_data = []
        for url in urls:
            print(f"[+] Crawling: {url}")
            site_data = self._crawl_site(url, depth, max_pages)
            crawled_data.extend(site_data)

            for page in site_data:
                self.db_manager.store_website(
                    page['url'], page['title'], page['content'],
                    page['type'], page['geo_location'], page.get('risk_level', 0)
                )

        print(f"[+] Crawl completed. Found {len(crawled_data)} items.")
        return crawled_data

    def _crawl_site(self, base_url, depth, max_pages):
        to_crawl = [(base_url, 0)]
        crawled_data = []
        self.visited_urls.clear()

        while to_crawl and len(crawled_data) < max_pages:
            url, current_depth = to_crawl.pop(0)
            if url in self.visited_urls or current_depth > depth:
                continue

            try:
                page_data = self._fetch_page(url)
                if page_data:
                    crawled_data.append(page_data)
                    self.visited_urls.add(url)

                    if current_depth < depth:
                        links = self._extract_links(page_data['content'], base_url)
                        for link in links:
                            if link not in self.visited_urls:
                                to_crawl.append((link, current_depth + 1))

                time.sleep(1)  # polite delay
            except Exception as e:
                print(f"[-] Error crawling {url}: {str(e)}")
                continue

        return crawled_data

    def _fetch_page(self, url):
        try:
            session = requests.session()
            if self.proxy_settings:
                session.proxies = self.proxy_settings

            response = session.get(url, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.title.string if soup.title else "No Title"
            content = soup.get_text()
            page_type = self._determine_page_type(url, content)
            geo_location = "Unknown"

            return {'url': url, 'title': title, 'content': content, 'type': page_type, 'geo_location': geo_location}
        except Exception as e:
            print(f"[-] Error fetching {url}: {str(e)}")
            return None

    def _extract_links(self, content, base_url):
        soup = BeautifulSoup(content, 'html.parser')
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            absolute_url = urljoin(base_url, href)
            if (absolute_url.startswith('http://') or absolute_url.startswith('https://')) and \
               ('.onion' in absolute_url or '.i2p' in absolute_url):
                links.append(absolute_url)
        return links

    def _determine_page_type(self, url, content):
        if 'product' in url.lower() or 'listing' in url.lower() or 'shop' in url.lower():
            return 'marketplace'
        elif 'forum' in url.lower() or 'discussion' in url.lower():
            return 'forum'
        elif 'blog' in url.lower():
            return 'blog'
        elif 'chat' in url.lower() or 'message' in url.lower():
            return 'chat'
        else:
            return 'website'
