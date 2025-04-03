import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from collections import deque

class WebDriver:
    def __init__(self, headless=True):
        self.options = webdriver.ChromeOptions()
        if headless:
            self.options.add_argument('--headless')  # 브라우저 창을 띄우지 않음
        self.service = Service(chromedriver_autoinstaller.install())
        self.driver = webdriver.Chrome(service=self.service, options=self.options)

    def open_page(self, url):
        self.driver.get(url)
        time.sleep(2)  # 페이지 로딩 대기

    def find_element(self, by, value):
        return self.driver.find_element(by, value)

    def wait_for_element(self, by, value, timeout=10):
        return WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((by, value)))

    def quit(self):
        self.driver.quit()


class SearchPage:
    def __init__(self, driver, url):
        self.driver = driver
        self.url = url

    def search_keyword(self, keyword):
        self.driver.open_page(self.url)
        input_element = self.driver.find_element(By.ID, 'schKeyword')
        input_element.clear()
        input_element.send_keys(keyword)

        search_button = self.driver.wait_for_element(By.CSS_SELECTOR, 'input[type="submit"]')
        search_button.click()

        time.sleep(10)
        self.search_btn()

    def search_btn(self):
        btn_element = self.driver.find_element(By.CLASS_NAME, 'btn-base')
        btn_element.click()

    def get_search_results(self):
        self.driver.wait_for_element(By.CLASS_NAME, 'con-box')

        # 페이지 소스를 가져옵니다.
        page_source = self.driver.driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')

        # 'content' ID를 가진 요소를 찾습니다.
        content_element = soup.find(id='content')

        # 찾은 요소의 텍스트만 반환합니다.
        if content_element:
            return content_element.get_text()
        else:
            return "Content not found"

    def get_search_links(self):
        GetLinks.crawl(self.url, max_depth=3)

class GetLinks:
    @staticmethod
    def get_links(url):
        """ 주어진 URL 페이지에서 모든 링크를 추출합니다. """
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        links = set()

        for link in soup.find_all('a', href=True):
            full_url = urljoin(url, link['href'])
            links.add(full_url)
        return links


    @staticmethod
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
                    for link in GetLinks.get_links(current_url):  # 클래스에서 메서드 호출 시 클래스 이름을 명시해야 함
                        if link not in visited:
                            queue.append((link, depth + 1))
                except requests.exceptions.RequestException as e:
                    print(f"Error fetching {current_url}: {e}")

        print("Crawling finished.")

def main():
    url = 'https://www.deu.ac.kr/www/search.do'  # 기본 검색 URL
    driver = WebDriver()  # WebDriver 객체 생성
    search_page = SearchPage(driver, url)  # SearchPage 객체 생성

    keyword = input("검색어를 입력하세요: ")

    # 검색어 입력 및 검색 결과 추출
    search_page.search_keyword(keyword)
    #search_page.search_btn()
    search_results = search_page.get_search_results()

    #해당 페이지의 검색 결과 더보기 버튼 클릭 후 결과 추출

    # 결과 출력
    print(search_results)
    search_page.get_search_links()

    # 브라우저 종료
    driver.quit()


if __name__ == "__main__":
    main()