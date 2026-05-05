import urllib.request
import urllib.error
from urllib.parse import urljoin, urlparse, urldefrag
from bs4 import BeautifulSoup
from collections import deque
from abc import ABC, abstractmethod


class DeepCrawlStrategy(ABC):
    @abstractmethod
    def crawl(self, start_url, max_depth, max_pages, fetcher, same_domain_only) -> list[dict]:
        pass

    def _extract_links(self, html_content, base_url):
        links = []
        soup = BeautifulSoup(html_content, "html.parser")

        for a_tag in soup.find_all("a", href=True):
            normalized = urljoin(base_url, a_tag["href"])
            normalized, _ = urldefrag(normalized)

            parsed = urlparse(normalized)

            if parsed.scheme in {"http", "https"} and parsed.netloc:
                links.append(normalized)
        return links

    def _extract_info(self, html_content, url):
        soup = BeautifulSoup(html_content, "html.parser")
        if soup.title:
            title = soup.title.string.strip()
        else: 
            title = "No Title" 
            
        return {"url": url, "title": title}     

class BFSDeepCrawlStrategy(DeepCrawlStrategy):
    def crawl(self, start_url, max_depth, max_pages, fetcher, same_domain_only):
        results = []
        visited = set()
        queue = deque([(start_url, 0)])
        initial_domain = urlparse(start_url).netloc

        while queue and len(results) < max_pages:
            url, depth = queue.popleft()

            if url in visited or depth > max_depth:
                continue

            visited.add(url)
            content = fetcher.fetch(url)

            if not content:
                continue

            results.append(self._extract_info(content,url))

            if depth < max_depth:
                for link in self._extract_links(content,url):
                    if link not in visited:
                        if not same_domain_only or urlparse(link).netloc == initial_domain:
                            queue.append((link, depth + 1)) 

        return results

class DFSDeepCrawlStrategy(DeepCrawlStrategy):
    def crawl(self, start_url, max_depth, max_pages, fetcher, same_domain_only):
        results = []
        visited = set()
        initial_domain = urlparse(start_url).netloc

    def _dfs(self, url, depth, max_depth, max_pages, fetcher, same_domain_only, initial_domain, visited, results):
        if len(results) > max_pages or depth > max_depth or url in visited:
            return
        
        visited.add(url)
        content = fetcher.fetch(url)

        if not content:
            return
        
        results.append(self._extract_info(content,url))

        if depth < max_depth:
            for link in self._extract_links(content,url):
                if link not in visited:
                    if not same_domain_only or urlparse(link).netloc == initial_domain:
                        self._dfs(link, depth + 1, max_depth, max_pages, fetcher, same_domain_only, initial_domain, visited, results)

class PageFetcher:
    def __init__(self, timeout = 5, user_agent="Mozilla/5.0"):
        self.user_agent = user_agent
        self.timeout = timeout


    def fetch(self, url):
        try:
            request = urllib.request.Request(url, headers = {"User-Agent": self.user_agent})
            with urllib.request.urlopen(request, timeout = self.timeout) as response:
                if response.getcode() == 200:
                    return response.read()
        
        except urllib.error.HTTPError as error:
            print(f"[HTTP Error] {url} -> {error.code}")
        except urllib.error.URLError as error:
            print(f"[URL Error] {url} -> {error.reason}")
        except Exception as error:
            print(f"[Fetch Error] {url} -> {error}")
            
        return None 

if __name__ == "__main__":
    start_url = "http://books.toscrape.com/"
    
    dfs_strategy = DFSDeepCrawlStrategy()
    fetcher = PageFetcher()

    results = dfs_strategy.crawl(
        start_url=start_url,
        max_depth=1,        
        max_pages=10,      
        fetcher=fetcher,
        same_domain_only=True
    )

    for item in results:
        print(item)
