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
        title = soup.title.string.strip() if soup.title else "No Title"
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

            results.append(self._extract_info(content, url))
            
            if depth < max_depth:
                for link in self._extract_links(content, url):
                    if link not in visited:
                        if not same_domain_only or urlparse(link).netloc == initial_domain:
                            queue.append((link, depth + 1))
        return results


class DFSDeepCrawlStrategy(DeepCrawlStrategy):
    def crawl(self, start_url, max_depth, max_pages, fetcher, same_domain_only):
        results = []
        visited = set()
        initial_domain = urlparse(start_url).netloc
        self._dfs(start_url, 0, max_depth, max_pages, fetcher, same_domain_only, initial_domain, visited, results)
        return results

    def _dfs(self, url, depth, max_depth, max_pages, fetcher, same_domain_only, initial_domain, visited, results):
        if len(results) >= max_pages or depth > max_depth or url in visited:
            return

        visited.add(url)
        content = fetcher.fetch(url)
        if not content:
            return

        results.append(self._extract_info(content, url))

        if depth < max_depth:
            for link in self._extract_links(content, url):
                if not same_domain_only or urlparse(link).netloc == initial_domain:
                    self._dfs(link, depth + 1, max_depth, max_pages, fetcher, same_domain_only, initial_domain, visited, results)

class CrawlerRunConfig:
    def __init__(self, deep_crawl_strategy: DeepCrawlStrategy, max_depth=2, max_pages=50,
                 same_domain_only=True, timeout=10.0, headers=None):
        self.deep_crawl_strategy = deep_crawl_strategy
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.same_domain_only = same_domain_only
        self.timeout = timeout
        self.headers = headers or {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }


class PageFetcher:
    def __init__(self, user_agent=None, timeout=5):
        self.user_agent = user_agent or "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        self.timeout = timeout

    def fetch(self, url):
        try:
            request = urllib.request.Request(url, headers={"User-Agent": self.user_agent})
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                if response.status == 200:
                    return response.read()
        except urllib.error.HTTPError as error:
            print(f"[HTTP Error] {url} -> {error.code}")
        except urllib.error.URLError as error:
            print(f"[URL Error] {url} -> {error.reason}")
        except Exception as error:
            print(f"[Fetch Error] {url} -> {error}")
        return None

class WebCrawler:
    def run(self, url: str, config: CrawlerRunConfig) -> list[dict]:
        fetcher = PageFetcher(
            user_agent=config.headers.get("User-Agent"),
            timeout=config.timeout
        )
        
        return config.deep_crawl_strategy.crawl(
            start_url=url,
            max_depth=config.max_depth,
            max_pages=config.max_pages,
            fetcher=fetcher,
            same_domain_only=config.same_domain_only
        )

if __name__ == "__main__":
    entry_url = "https://chiaki.vn/"
    
    bfs_strategy = BFSDeepCrawlStrategy()
    config_bfs = CrawlerRunConfig(deep_crawl_strategy=bfs_strategy, max_depth=1, max_pages=5)
    
    crawler = WebCrawler()
    print(f"--- Đang cào {entry_url} với chiến lược BFS ---")
    results_bfs = crawler.run(entry_url, config_bfs)
    for res in results_bfs:
        print(f"- {res['url']} | Tiêu đề: {res['title']}")

    # dfs_strategy = DFSDeepCrawlStrategy()
    # config_dfs = CrawlerRunConfig(deep_crawl_strategy=dfs_strategy, max_depth=1, max_pages=5)
    
    # # print(f"\n--- Đang cào {entry_url} với chiến lược DFS ---")
    # # results_dfs = crawler.run(entry_url, config_dfs)
    # # for res in results_dfs:
    # #     print(f"- {res['url']} | Tiêu đề: {res['title']}")
