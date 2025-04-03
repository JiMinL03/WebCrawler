import chromedriver_autoinstaller
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin


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
        self.open_search_page()
        self.enter_search_keyword(keyword)
        self.click_search_button()
        self.wait_for_results()

    def open_search_page(self):
        self.driver.open_page(self.url)

    def enter_search_keyword(self, keyword):
        input_element = self.driver.find_element(By.ID, 'schKeyword')
        input_element.clear()
        input_element.send_keys(keyword)

    def click_search_button(self):
        search_button = self.driver.wait_for_element(By.CSS_SELECTOR, 'input[type="submit"]')
        search_button.click()

    def wait_for_results(self):
        time.sleep(5)
        self.click_additional_search_button()

    def click_additional_search_button(self):
        btn_element = self.driver.find_element(By.CLASS_NAME, 'btn-base')
        btn_element.click()

    def get_search_results(self):
        self.driver.wait_for_element(By.CLASS_NAME, 'con-box')
        page_source = self.driver.driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')

        content_element = self.extract_content_by_id(soup, 'content')
        self.print_content(content_element)

        div_elements = self.extract_div_elements_by_class(soup, 'board-subject')
        self.print_links(div_elements)

    def extract_content_by_id(self, soup, id):
        return soup.find(id=id)

    def print_content(self, content_element):
        if content_element:
            print(content_element.get_text())
        else:
            print("Content not found")

    def extract_div_elements_by_class(self, soup, class_name):
        return soup.find_all('div', attrs={'class': class_name})

    def print_links(self, div_elements):
        base_url = 'https://www.deu.ac.kr/'
        if div_elements:
            for div in div_elements:
                link_elements = div.find_all('a', href=True)
                for link in link_elements:
                    full_url = urljoin(base_url, link['href'])
                    response = requests.get(full_url)
                    soup = BeautifulSoup(response.text, 'html.parser')
                    print(soup.get_text())
                    return full_url
        else:
            print("Div elements not found")


def main():
    url = 'https://www.deu.ac.kr/www/search.do'  # 기본 검색 URL
    driver = WebDriver()  # WebDriver 객체 생성
    search_page = SearchPage(driver, url)  # SearchPage 객체 생성

    keyword = input("검색어를 입력하세요: ")

    # 검색어 입력 및 검색 결과 추출
    search_page.search_keyword(keyword)
    search_page.get_search_results()

    # 브라우저 종료
    driver.quit()


if __name__ == "__main__":
    main()
