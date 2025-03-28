import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from collections import deque

def is_valid_url(base_url, url):
    """ 동일 도메인 내의 URL인지 검사하고, 유효한 링크인지 확인합니다. """
    parsed_base = urlparse(base_url)
    parsed_url = urlparse(url)
    if parsed_base.netloc != parsed_url.netloc:
        return False
    if not parsed_url.scheme.startswith('http'):
        return False
    return True

def get_links(url):
    """ 주어진 URL 페이지에서 모든 링크를 추출합니다. """
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    links = set()
    for link in soup.find_all('a', href=True):
        full_url = urljoin(url, link['href'])
        if is_valid_url(url, full_url):
            links.add(full_url)
    return links

def crawl(start_url, max_depth=3):
    """ 너비 우선 탐색(BFS)을 사용하여 웹 크롤링을 실행합니다. """
    visited = set()
    queue = deque([(start_url, 0)])  # URL과 현재 깊이를 저장합니다.

    while queue:
        current_url, depth = queue.popleft()
        if depth > max_depth:
            break
        if current_url not in visited:
            visited.add(current_url)
            print(f"Visiting: {current_url} at depth {depth}")
            try:
                for link in get_links(current_url):
                    if link not in visited:
                        queue.append((link, depth + 1))
            except requests.exceptions.RequestException as e:
                print(f"Error fetching {current_url}: {e}")

    print("Crawling finished.")

# 시작 URL 설정
start_url = 'https://ipsi.deu.ac.kr/universityDetail.do'
crawl(start_url, max_depth=3)