import json

import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import chromedriver_autoinstaller

start_url = "https://ipsi.deu.ac.kr/universityDetail.do"

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
def get_colleges(url):
    # 웹 페이지 요청 및 파싱
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # "strong" 태그를 찾아 텍스트에 "대학"이 포함된 요소만 필터링
    college = [
        element.get_text().strip()  # get_text()로 텍스트 추출 후 앞뒤 공백과 개행 문자 제거
        for element in soup.find_all("strong")
        if "대학" in element.get_text()
    ]

    # 필요 없는 공백이나 특수문자를 추가로 제거하기
    college = [text.replace("\r", "").replace("\n", "").replace("\t", "") for text in college]

    # 불필요한 항목(고교-대학연계, 대학안내 등) 삭제
    del college[:2]  # 고교-대학연계, 대학안내 데이터 삭제
    return college


# -----------------------------------
# 단대 하위 경로 url 추출 (동적 웹페이지라서 selenium 이용)
def get_departments(url, college_names):
    """ 주어진 URL 페이지에서 <div class="department-box"> 내의 <ul><li> 내의 <a> 태그의 href만 추출합니다. """
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # 브라우저 창을 띄우지 않음

    # ChromeDriverManager를 통해 드라이버 자동 설치 및 경로 설정
    service = Service(chromedriver_autoinstaller.install())
    driver = webdriver.Chrome(service=service, options=options)

    # URL 유효성 검사
    if not is_valid_url(url):
        print(f"Invalid URL: {url}")
        return {}

    driver.get(url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    links_by_college = {}  # 대학별 링크를 저장할 딕셔너리

    # 대학 이름마다 링크 추출
    for college in college_names:
        links_by_college[college] = []  # 해당 대학에 대한 링크 리스트 초기화

        try:
            # 해당 college 이름이 포함된 <strong> 태그 찾기
            strong = soup.find('strong', string=lambda text: text and college in text.strip())

            if strong:
                # 'strong' 태그가 있으면, 그 부모나 관련 요소에서 <div class="department-box"> 찾기
                department_area = strong.find_parent('div', class_='department-area')

                if department_area:
                    # department_area 내에서 <div class="department-box"> 찾기
                    department_box = department_area.find('div', class_='department-box')

                    if department_box:
                        # department_box 내에서 <ul> 태그 찾기
                        ul_elements = department_box.find_all('ul')

                        for ul in ul_elements:
                            # <ul> 내에서 모든 <li> 태그 찾기
                            li_elements = ul.find_all('li')

                            for li in li_elements:
                                # <li> 내에서 <a> 태그의 href 속성 찾기
                                a_tag = li.find('a', href=True)
                                if a_tag:
                                    # 상대 URL을 절대 URL로 변환
                                    full_url = urljoin(url, a_tag['href'])
                                    links_by_college[college].append(full_url)
                                    # links_by_college 딕셔너리를 사용하여 대학 이름을 키로, 그에 해당하는 링크들을 리스트로 저장
            else:
                print(f"Could not find a 'strong' tag with the text '{college}'.")

        except Exception as e:
            # 오류가 발생하면 해당 college의 처리를 건너뜁니다.
            print(f"Error processing {college}: {e}")
            continue  # 계속해서 다음 college로 넘어갑니다.

    return links_by_college  # 각 대학별 링크들을 포함하는 딕셔너리 반환

# -----------------------------------

def get_department(department_url):
    # URL 유효성 검사
    if not is_valid_url(department_url):
        print(f"Invalid URL: {department_url}")
        return {}

    response = requests.get(department_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # '학부' 또는 '학과'가 포함된 텍스트를 가진 span 태그 찾기
    department = soup.find('span', string=lambda text: text and (
            ('학부' in text or '학과' in text or '대학' in text or '전공' in text) and '학과소개' not in text))

    department_name = department.get_text().strip() if department else ''
    return department_name

# -----------------------------------

def get_facultys(department_url):
    # URL 유효성 검사
    if not is_valid_url(department_url):
        print(f"Invalid URL: {department_url}")
        return {}

    response = requests.get(department_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    #<a>교수소개</a> 태그 찾기
    faculty_url = soup.find('a', title=lambda title: title and '교수소개' in title)
    if faculty_url:
        # href 속성만 추출
        faculty_page_url = urljoin(department_url, faculty_url.get('href'))
        #https://koreanl.deu.ac.kr + /koreanl/sub02_02.do
        return faculty_page_url

# -----------------------------------

def get_faculty(faculty_url):
    # URL 유효성 검사
    if not is_valid_url(faculty_url):
        print(f"Invalid URL: {faculty_url}")
        return {}

    response = requests.get(faculty_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    teach_list = soup.find_all('div', class_='teachList')
    professors_data = []
    if teach_list:
        # 각 교수 정보 <dl> 태그 찾기
        for dl in soup.find_all('dl'):
            professor = {}

            # 교수 이름과 연구 분야 추출
            dt = dl.find('dt')
            professor['name'] = dt.find('p').text.strip() if dt.find('p') else '정보없음'
            professor['research_field'] = dt.find('span').text.strip() if dt.find('span') else '정보없음'

            # 교수의 연구실, 연락처, 이메일 추출
            dd = dl.find('dd')
            ul = dd.find('ul')

            professor['room'] = ul.find_all('li')[0].text.split('연구실')[1].strip() if len(
                ul.find_all('li')) > 0 else ''
            professor['phone'] = ul.find_all('li')[1].text.split('연락처')[1].strip() if len(
                ul.find_all('li')) > 1 else ''

            # 이메일은 <a> 태그 안에 있음
            email_tag = ul.find_all('li')[2].find('a') if len(ul.find_all('li')) > 2 else None
            professor['email'] = email_tag.text.strip() if email_tag else '정보없음'

            professors_data.append(professor)
    return professors_data

# -----------------------------------
# 실행 코드(main)
college_names = get_colleges(start_url)  # 대학명 리스트 가져오기
links_by_college = get_departments(start_url, college_names)  # 대학별 링크 추출

# 결과 저장할 변수
college_data = []

# 대학 학과 출력
for college, links in links_by_college.items():
    college_info = {"name": college, "departments": []}
    for link in links:
        department_name = get_department(link)  # 각 링크에 대해 학과 이름 가져오기
        faculty_page_url = get_facultys(link)  # 교수소개 페이지 URL 얻기
        faculty_data = []

        if faculty_page_url:
            # 교수소개 페이지 URL과 기본 URL을 합쳐서 전체 URL을 만든 후 get_faculty 호출
            full_url = urljoin('https://koreanl.deu.ac.kr', faculty_page_url)
            faculty_data = get_faculty(full_url)

        # 학과 정보 추가
        college_info["departments"].append({
            "name": department_name,
            "website": link,
            "faculty": faculty_data
        })

    # 대학 정보 추가
    college_data.append(college_info)
# -----------------------------------
# JSON 파일에 데이터를 저장하는 부분
json_file = 'university.json'

data_to_save = {
    "college": [college_data]
}

data_to_dict = {
    "university": {
        "name": "동의대학교",
        "location": "부산광역시 부산진구 엄광로 176",
        "contact_info": {
            "phone": "051-890-1114",
            "birthday": "1976년 12월 31일",
            "website": "https://www.deu.ac.kr/www/index.do"
        }
    }
}
# 두 데이터를 하나의 딕셔너리로 합치기
combined_data = {
    "university_info": data_to_dict,
    "college_info": data_to_save
}
with open(json_file, 'w', encoding='utf-8') as outfile:
    json.dump(combined_data, outfile, ensure_ascii=False, indent=4)