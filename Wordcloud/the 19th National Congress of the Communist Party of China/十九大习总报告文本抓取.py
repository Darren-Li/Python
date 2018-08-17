import os
import requests
from bs4 import BeautifulSoup

url = 'http://www.china.com.cn/cppcc/2017-10/18/content_41752399.htm'


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
    
    ## check the encoding, in some cases, it is not consitent with
    ## what you see in its html file.
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
    encode_content = resp.content.decode(encoding, 'replace').encode('utf-8', 'replace')
    # 解析网页
    soup = BeautifulSoup(encode_content, 'lxml')
    # print(soup.prettify())
    return soup

def writeout(text):
	with open('文本\\党的十九大报告.txt', 'a', encoding='utf-8') as f:
		f.write(text + '\n')


soup = get_soup(url)

os.mkdir('文本')

with open('文本\\党的十九大报告.txt', 'w', encoding='utf-8') as f:
		pass

for div in soup.select('div[class="center_box"]'):
	for p in div.select('p[style="TEXT-INDENT: 30px; MARGIN: 0px 3px 15px"]')[1:-5]:
		writeout(p.text)
