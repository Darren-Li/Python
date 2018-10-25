import requests
from bs4 import BeautifulSoup
import time


url = 'http://fund.eastmoney.com/allfund.html'

# 直接抓取
resp = requests.get(url)
soup = BeautifulSoup(resp.text, 'lxml')  # 乱码
print(soup.prettify())

# .content 二进制的形式返回响应内容
soup = BeautifulSoup(resp.content, 'lxml')
print(soup.prettify())


def get_soup(url):
    while True:
        try:
            resp = requests.get(url)
        except:
            print('Other errors!')
            time.sleep(60)
        else:
            if resp.status_code == 200:
                break
    
    # check the encoding, in some cases, it is not consitent with
    # what you see in its html file.
    # print(resp.encoding)
    # 解决乱码问题
    if resp.encoding == 'ISO-8859-1':
        encodings = requests.utils.get_encodings_from_content(resp.text)
        if encodings:
            encoding = encodings[0]
        else:
            encoding = resp.apparent_encoding
    else:
        encoding = resp.apparent_encoding
    encode_content = resp.content.decode(encoding, 'replace')
    # 解析网页
    soup = BeautifulSoup(encode_content, 'lxml')
    # print(soup.prettify())
    return soup


# 处理乱码
soup = get_soup(url)
print(soup.prettify())
