import requests
from bs4 import BeautifulSoup
import json

start_url = 'https://ipsi.deu.ac.kr/submenu.do?menuUrl=54Mm3BQ0IOZq%2b7x%2bQeXT8w%3d%3d&'
# 유효한 URL을 검사하는 함수
def is_valid_url(url):
    try:
        response = requests.get(url, timeout=10)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

#2025년도 등록금 정보 가져오는 함수
def get_tution():
    start_url = 'https://ipsi.deu.ac.kr/submenu.do?menuUrl=54Mm3BQ0IOZq%2b7x%2bQeXT8w%3d%3d&'
    response = requests.get(start_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # college_tag는 <td> 태그로 구성된 리스트
    college_tag = [td for td in soup.find_all('td') if
                   td.find('p') and '원' not in td.find('p').text or not td.find('p')]
    # college 리스트에 대학 이름만 추출
    college = [college_tag[i].text.strip() for i in range(len(college_tag))]
    #print("College list:", college)

    # tution_tag는 <p class='center'> 태그로 구성된 리스트
    tution_tag = soup.find_all('p', attrs={'class': 'center'})
    #print("Tution tags:", tution_tag)

    college_tution = {}
    # tution_tag에서 학비 정보를 2개씩 묶어서 college와 짝지어 저장
    j = 0
    for i in range(0, len(college), 1): #9
        if j + 1 < len(tution_tag):  # j+1이 유효한 인덱스인지 확인
            college_tution[college[i]] = [
                tution_tag[j].text.strip(),  # tution_tag[j]의 값
                tution_tag[j + 1].text.strip()  # tution_tag[j+1]의 값
            ]
            j += 2  # 2개씩 이동

    print(len(tution_tag))
    print(len(college))
    print(len(college_tution))
    print(college_tution)
    return college_tution

#-----------------------------------------
# 대학 이름을 분리하고 튜션 가격을 그대로 유지하는 함수
def split_and_create_tuition_dict(college_tution):
    """
    대학 이름을 콤마(,)를 기준으로 분리하여 새로운 키-값 쌍을 생성하는 함수
    """
    new_tuition_data = {}

    # 각 대학 이름이 하나로 묶여 있는 데이터를 분리하여 새로운 dict 생성
    for colleges, tuition_prices in college_tution.items():
        college_names = colleges.split(",")  # 콤마로 대학 이름 분리

        # 각 분리된 대학 이름에 대해 동일한 튜션 가격을 매칭
        for college_name in college_names:
            college_name = college_name.strip()  # 앞뒤 공백 제거
            new_tuition_data[college_name] = tuition_prices  # 동일한 튜션 가격을 사용

    print(new_tuition_data)

    return new_tuition_data

# 최종 결과를 저장할 딕셔너리
college_tuition_dict = {}

def set_json(new_tuition_data):
    path = 'university.json'
    with open(path, "r", encoding='utf-8') as json_file:
        json_data = json.load(json_file)

    college_list = json_data["college_info"].get("college", [])

    for college_group in college_list:
        for college_data in college_group:
            college_name = college_data["name"]
            departments = college_data["departments"]

            # 대학 이름이 tuition_data에 존재하는지 확인
            if college_name in new_tuition_data:
                tuition_prices = new_tuition_data[college_name]
                tuition_info = {}

                # 학과별로 1-1, 1-2, 2-1, 2-2, ... 형식으로 가격을 추가
                for i, department in enumerate(departments):
                    department_name = department["name"]

                    # 각 학과마다 1-1, 1-2, 2-1, 2-2, ... 형식으로 매핑
                    if i == 0:
                        tuition_info[f"{i + 1}-1"] = tuition_prices[0]  # 첫 번째 학과는 1-1에 첫 번째 가격
                        tuition_info[f"{i + 1}-2"] = tuition_prices[1]  # 첫 번째 학과는 1-2에 두 번째 가격
                    elif i == 1:
                        tuition_info[f"{i + 1}-1"] = tuition_prices[1]  # 두 번째 학과부터는 2-1에 두 번째 가격
                        tuition_info[f"{i + 1}-2"] = tuition_prices[1]  # 두 번째 학과는 2-2에 두 번째 가격
                    elif i == 2:
                        tuition_info[f"{i + 1}-1"] = tuition_prices[1]  # 세 번째 학과부터는 3-1에 두 번째 가격
                        tuition_info[f"{i + 1}-2"] = tuition_prices[1]  # 세 번째 학과는 3-2에 두 번째 가격
                    elif i == 3:
                        tuition_info[f"{i + 1}-1"] = tuition_prices[1]  # 네 번째 학과부터는 4-1에 두 번째 가격
                        tuition_info[f"{i + 1}-2"] = tuition_prices[1]  # 네 번째 학과는 4-2에 두 번째 가격
                    elif i==4:
                        # 이후 학과들도 1-1부터 차례대로 가격을 추가
                        tuition_info[f"{i + 1}-1"] = tuition_prices[1]
                        tuition_info[f"{i + 1}-2"] = tuition_prices[1]

                # 대학 이름에 해당하는 데이터를 college_tuition_dict에 추가
                college_tuition_dict[college_name] = tuition_info

    # 결과 출력
    print(college_tuition_dict)
    return college_tuition_dict

#-----------------------------------------
def write_json(college_tuition_dict):
    json_file = 'tuition.json'
    with open(json_file, 'w', encoding='utf-8') as outfile:
        json.dump(college_tuition_dict, outfile, ensure_ascii=False, indent=4)
#-----------------------------------------
#main
college_tution = get_tution()
new_tuition_data = split_and_create_tuition_dict(college_tution)
college_tuition_dict = set_json(new_tuition_data)
write_json(college_tuition_dict)