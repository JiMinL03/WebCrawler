import requests
from bs4 import BeautifulSoup

start_url = 'https://ipsi.deu.ac.kr/submenu.do?menuUrl=54Mm3BQ0IOZq%2b7x%2bQeXT8w%3d%3d&'
# 유효한 URL을 검사하는 함수
def is_valid_url(url):
    try:
        response = requests.get(url, timeout=10)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

#2025년도 등록금 정보 가져오는 함수
def get_tution(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # college_tag는 <td> 태그로 구성된 리스트
    college_tag = [td for td in soup.find_all('td') if
                   td.find('p') and '원' not in td.find('p').text or not td.find('p')]
    # college 리스트에 대학 이름만 추출
    college = [college_tag[i].text.strip() for i in range(len(college_tag))]
    print("College list:", college)

    # tution_tag는 <p class='center'> 태그로 구성된 리스트
    tution_tag = soup.find_all('p', attrs={'class': 'center'})
    print("Tution tags:", tution_tag)

    # college_tution 딕셔너리 초기화
    college_tution = {}
    # tution_tag에서 학비 정보를 2개씩 묶어서 college와 짝지어 저장
    j = 0  # tution_tag 인덱스를 추적하는 변수
    for i in range(len(college)):
        # 학비 정보가 2개 이상 있을 경우
        if j + 1 < len(tution_tag):
            college_tution[college[i]] = [
                tution_tag[j].text.strip(),
                tution_tag[j + 1].text.strip()
            ]
            j += 2  # 2개씩 이동
        elif j < len(tution_tag):  # 하나만 남았을 경우
            college_tution[college[i]] = [tution_tag[j].text.strip()]
            j += 1  # 하나만 이동
        else:  # 학비 정보가 없을 경우
            college_tution[college[i]] = ["정보 없음"]  # 학비 정보가 없을 때 처리
    print("College Tuition Data:", college_tution)

#-----------------------------------------
#main
get_tution(start_url)

