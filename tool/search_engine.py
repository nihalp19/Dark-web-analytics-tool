import time
import requests
from bs4 import BeautifulSoup  # for parsing HTML
from config import SEARCH_CONFIG, ALERT_CONFIG

class SearchEngine:
    def __init__(self, db_manager, alert_system):
        self.db_manager = db_manager
        self.alert_system = alert_system
        self.session = None

    def set_proxy(self, proxy_settings=None):
        self.session = requests.Session()
        if proxy_settings:
            self.session.proxies = proxy_settings
        else:
            self.session.proxies = {'http': "socks5h://127.0.0.1:9050", 'https': "socks5h://127.0.0.1:9050"}
        print(f"[+] Proxy set: {self.session.proxies}")

    def search(self, keywords, sources=None, geo_filter=None, date_filter=None):
        if not self.session:
            print("[-] No proxy configured. Connect to Tor first.")
            return []

        print(f"[+] Searching for keywords: {', '.join(keywords)}")
        results = []

        # Get URLs from DB or crawler
        urls_to_search = self.db_manager.get_all_urls()  # You must implement this DB method

        for keyword in keywords:
            for url in urls_to_search:
                try:
                    response = self.session.get(url, timeout=SEARCH_CONFIG['timeout'])
                    response.raise_for_status()
                    soup = BeautifulSoup(response.text, "html.parser")
                    for link in soup.find_all("a", href=True):
                        if keyword.lower() in link.text.lower():
                            result = {
                                "url": link['href'],
                                "title": link.text.strip(),
                                "snippet": link.text.strip(),
                                "source": url,
                                "date": time.strftime("%Y-%m-%d")
                            }
                            if geo_filter and not self._matches_geo_filter(result, geo_filter):
                                continue
                            if date_filter and not self._matches_date_filter(result, date_filter):
                                continue
                            if sources and result['source'] not in sources:
                                continue
                            results.append(result)
                    # Store results
                    for result in results:
                        self.db_manager.store_search_result(
                            keyword, result['source'], result['url'],
                            result['title'], result['snippet'], result['date']
                        )
                    # Check alerts
                    self.alert_system.check_keyword_alerts(keyword, results)
                except Exception as e:
                    print(f"[-] Error accessing {url}: {e}")
                    continue

        # Deduplicate by URL
        unique_results = {r['url']: r for r in results}.values()
        print(f"[+] Found {len(unique_results)} results")
        return list(unique_results)

    def _matches_geo_filter(self, result, geo_filter):
        return True

    def _matches_date_filter(self, result, date_filter):
        try:
            result_date = time.strptime(result['date'], "%Y-%m-%d")
            filter_date = time.strptime(date_filter, "%Y-%m-%d")
            return result_date >= filter_date
        except:
            return True