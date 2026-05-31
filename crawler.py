
import requests 
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os 
from datetime import datetime 
import time

class Crawler: 
    def __init__(self):
        self.save_path = r"C:\Users\user\Downloads"
        self.visited = set() 
        self.all_links = [] 
        self.broken_links = []
        self.start_time = None
        self.domain = ""

    def get_links(self, url): 
        try: 
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, timeout=10, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            links = [] 
            for link in soup.find_all('a', href=True): 
                full_url = urljoin(url, link['href'])
                if full_url.startswith('http'): 
                    full_url = full_url.split('#')[0]
                    links.append(full_url)
            return list(set(links))
        except: 
            self.broken_links.append(url)
            return [] 
    
    def crawl(self, start_url, max_pages=20): 
        self.start_time = time.time()
        self.domain = urlparse(start_url).netloc
        to_visit = [start_url]
        count = 0 

        print(f"Starting crawl: {start_url}")

        while to_visit and count < max_pages: 
            url = to_visit.pop(0) 

            if url in self.visited:
                continue 
            
            if count > 0:
                time.sleep(0.5)
            
            links = self.get_links(url) 

            self.visited.add(url) 
            self.all_links.extend(links) 

            for link in links[:3]: 
                if link not in self.visited and link not in to_visit:
                    if urlparse(link).netloc == self.domain:
                        to_visit.append(link)
            
            count += 1 
            
            progress = (count / max_pages) * 100
            bar_length = 20
            filled = int(bar_length * count // max_pages)
            bar = '█' * filled + '░' * (bar_length - filled)
            print(f"\rProgress: |{bar}| {count}/{max_pages} pages | Links: {len(self.all_links)}", end="")

        print()  
        self.save_results()
    
    def save_results(self):
        unique_links = sorted(set(self.all_links))
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        filename = os.path.join(self.save_path, f"links_{timestamp}.txt")
        with open(filename, 'w', encoding='utf-8') as f: 
            for link in unique_links: 
                f.write(link + '\n')
        
        if self.broken_links:
            broken_file = os.path.join(self.save_path, f"broken_{timestamp}.txt")
            with open(broken_file, 'w', encoding='utf-8') as f:
                for link in self.broken_links:
                    f.write(link + '\n')
        
        elapsed = time.time() - self.start_time
        print(f"\nSaved {len(unique_links)} links to {filename}")
        print(f"Found {len(self.broken_links)} broken links")
        print(f"Time: {elapsed:.1f}s")

if __name__ == "__main__": 
    url = input("Enter URL: ")
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    max_pages = input("Enter max pages (default 20): ")
    if max_pages.strip() and max_pages.isdigit():
        max_pages = int(max_pages)
    else:
        max_pages = 20
    
    crawler = Crawler()  
    crawler.crawl(url, max_pages)
