from selenium.webdriver.support import expected_conditions as EC

import chromedriver_autoinstaller
from selenium import webdriver
import requests
import time

from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

url = "https://www.deu.ac.kr/www/index.do"

# -----------------------------------
#해당 링크가 유효한지 확인하는 메서드
def is_valid_url(url):
    try:
        response = requests.get(url, timeout=10)  # 타임아웃을 설정하여 응답을 기다립니다.
        if response.status_code == 200:
            return True
        else:
            return False
    except requests.exceptions.RequestException:
        # 요청 중 오류가 발생하면 유효하지 않은 URL로 처리합니다.
        return False
# -----------------------------------
def search(input_text, url):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # 브라우저 창을 띄우지 않음

    # ChromeDriverManager를 통해 드라이버 자동 설치 및 경로 설정
    service = Service(chromedriver_autoinstaller.install())
    driver = webdriver.Chrome(service=service, options=options)

    if not is_valid_url(url):
        print("해당 url을 연결할 수 없습니다.")
        driver.quit()
        return {}

    try:
        driver.get(url)

        # 페이지가 로드되기를 기다리기 위해 WebDriverWait 사용
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "input-text"))
        )

        # 요소 클릭 후 텍스트 입력
        element.click()
        element.send_keys(input_text + "\n")

        print("검색어 입력 완료")  # 검색이 정상적으로 완료되면 메시지 출력

    except Exception as e:
        print(f"오류 발생: {e}")  # 발생한 오류 출력

    finally:
        driver.quit()  # 드라이버 종료

# -----------------------------------
print("검색할 키워드를 입력하세요: ")
input_text = input()
search(input_text, url)
