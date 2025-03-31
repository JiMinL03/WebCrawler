import json
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import chromedriver_autoinstaller
import schedule
import time

START_URL = "https://ipsi.deu.ac.kr/universityDetail.do"

# -----------------------------------
# 유효한 URL을 검사하는 함수
def is_valid_url(url):
    try:
        response = requests.get(url, timeout=10)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

# -----------------------------------
# 대학 목록을 가져오는 함수
def get_colleges(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    college_names = [
        element.get_text().strip()
        for element in soup.find_all("strong")
        if "대학" in element.get_text()
    ]

    # 불필요한 특수문자 및 공백 제거
    college_names = [text.replace("\r", "").replace("\n", "").replace("\t", "") for text in college_names]
    del college_names[:2]  # 고교-대학연계, 대학안내 항목 제거

    return college_names

# -----------------------------------
# 각 대학에 대한 학과 링크를 추출하는 함수
def get_departments(url, college_names):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # 브라우저 창을 띄우지 않음
    service = Service(chromedriver_autoinstaller.install())
    driver = webdriver.Chrome(service=service, options=options)

    if not is_valid_url(url):
        print(f"Invalid URL: {url}")
        return {}

    driver.get(url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    links_by_college = {}
    for college in college_names:
        links_by_college[college] = extract_college_links(soup, college)

    return links_by_college

# 대학 이름을 기준으로 학과 링크를 추출하는 함수
def extract_college_links(soup, college_name):
    links = []
    try:
        strong = soup.find('strong', string=lambda text: text and college_name in text.strip())
        if strong:
            department_area = strong.find_parent('div', class_='department-area')
            if department_area:
                department_box = department_area.find('div', class_='department-box')
                if department_box:
                    ul_elements = department_box.find_all('ul')
                    for ul in ul_elements:
                        for li in ul.find_all('li'):
                            a_tag = li.find('a', href=True)
                            if a_tag:
                                full_url = urljoin(START_URL, a_tag['href'])
                                links.append(full_url)
    except Exception as e:
        print(f"Error processing {college_name}: {e}")
    return links

# -----------------------------------
# 학과 이름을 추출하는 함수
def get_department(department_url):
    if not is_valid_url(department_url):
        return ""
    response = requests.get(department_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    department = soup.find('span', string=lambda text: text and ('학부' in text or '학과' in text or '대학' in text) and '학과소개' not in text)
    return department.get_text().strip() if department else ""

# -----------------------------------
# 교수소개 페이지 URL을 추출하는 함수
def get_facultys(department_url):
    if not is_valid_url(department_url):
        return None
    response = requests.get(department_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    faculty_url = soup.find('a', title=lambda title: title and '교수소개' in title)
    return urljoin(department_url, faculty_url.get('href')) if faculty_url else None

# -----------------------------------
# 교수 정보를 추출하는 함수
def get_faculty(faculty_url):
    if not is_valid_url(faculty_url):
        return []
    response = requests.get(faculty_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    professors_data = []

    for dl in soup.find_all('dl'):
        professor = extract_professor_info(dl)
        professors_data.append(professor)

    return professors_data

# 교수 정보를 추출하는 함수
def extract_professor_info(dl):
    professor = {}
    dt = dl.find('dt')
    professor['name'] = dt.find('p').text.strip() if dt.find('p') else '정보없음'
    professor['research_field'] = dt.find('span').text.strip() if dt.find('span') else '정보없음'

    dd = dl.find('dd')
    ul = dd.find('ul')

    professor['room'] = extract_room(ul)
    professor['phone'] = extract_phone(ul)
    professor['email'] = extract_email(ul)

    return professor

# 교수의 연구실 정보를 추출하는 함수
def extract_room(ul):
    return ul.find_all('li')[0].text.split('연구실')[1].strip() if len(ul.find_all('li')) > 0 else ''

# 교수의 연락처를 추출하는 함수
def extract_phone(ul):
    return ul.find_all('li')[1].text.split('연락처')[1].strip() if len(ul.find_all('li')) > 1 else ''

# 교수의 이메일을 추출하는 함수
def extract_email(ul):
    email_tag = ul.find_all('li')[2].find('a') if len(ul.find_all('li')) > 2 else None
    return email_tag.text.strip() if email_tag else '정보없음'

# -----------------------------------
# 전체 데이터를 수집하고 저장하는 함수
def job():
    college_names = get_colleges(START_URL)
    links_by_college = get_departments(START_URL, college_names)

    college_data = []
    for college, links in links_by_college.items():
        college_info = {"name": college, "departments": []}
        for link in links:
            department_name = get_department(link)
            faculty_page_url = get_facultys(link)
            faculty_data = []

            if faculty_page_url:
                faculty_data = get_faculty(faculty_page_url)

            college_info["departments"].append({
                "name": department_name,
                "website": link,
                "faculty": faculty_data
            })

        college_data.append(college_info)

    save_to_json(college_data)

# 데이터를 JSON 파일로 저장하는 함수
def save_to_json(college_data):
    json_file = 'university.json'
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

    combined_data = {
        "university_info": data_to_dict,
        "college_info": {"college": [college_data]}
    }

    with open(json_file, 'w', encoding='utf-8') as outfile:
        json.dump(combined_data, outfile, ensure_ascii=False, indent=4)

# -----------------------------------
# 스케줄러 설정 매일 23 : 59
schedule.every().day.at("23:59").do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
