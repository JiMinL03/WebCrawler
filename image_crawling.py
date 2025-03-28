import requests
from bs4 import BeautifulSoup
from PIL import Image, ImageEnhance
from io import BytesIO
import pytesseract

# Tesseract 경로 설정
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# 실제 URL을 start_url에 할당
start_url = "https://www.deu.ac.kr/www/deu-notice.do?mode=view&articleNo=65607"

# start_url 변수 사용하여 GET 요청
response = requests.get(start_url)

# HTML 파싱
soup = BeautifulSoup(response.content, 'html.parser')

# 모든 이미지 태그 찾기
img_tags = soup.find_all("img")

# 각 이미지 URL을 가져와서 Base64로 인코딩
for img_tag in img_tags:
    img_url = img_tag.get("src")

    # 상대 경로일 경우 절대 경로로 변환
    if img_url.startswith("/"):
        img_url = "https://www.deu.ac.kr" + img_url

    # 이미지 다운로드
    img_data = requests.get(img_url).content

    # BytesIO로 이미지 데이터 래핑
    img = Image.open(BytesIO(img_data))

    # 이미지 전처리 (그레이스케일 + 이진화)
    img = img.convert('L')  # 그레이스케일 변환
    img = img.point(lambda x: 0 if x < 143 else 255)  # 이진화 (임계값 143)

    # 이미지에서 텍스트 추출 (페이지 분할 모드 지정)
    text = pytesseract.image_to_string(img, config='--psm 6')

    # 추출된 텍스트 출력
    print("추출된 텍스트:")
    print(text)
