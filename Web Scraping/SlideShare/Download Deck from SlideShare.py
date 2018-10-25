# download slides on SlideShare
import os
import urllib.request

# from bs4 import BeautifulSoup
# filename = 'C:\Darren\ziqing\Merkle\Python\code\www.slideshare.net_tw_dsconf_ss-62245351.html'
# html = open(filename, encoding = 'utf-8').read()
# soup = BeautifulSoup(html, 'lxml')
# for img in soup.select('img[class="j-tooltip-thumb tooltip-thumb"]'):
#         print(img)

path = r"C:\Darren\ziqing\Merkle\Python\base\数据抓取\案例\SlideShare"
os.chdir(path)
         
folder = 'analysis-of-unstructured-data'
os.mkdir(folder)
os.chdir(folder)

slide_num = 65
url = 'https://image.slidesharecdn.com/asa2009may15-textanalytics-100301214537-phpapp02/95/analysis-of-unstructured-data-{}-728.jpg?cb=1267480025'

imglist = [url.format(str(i)) for i in range(1, slide_num+1)]

for x, imgurl in enumerate(imglist):
	urllib.request.urlretrieve(imgurl, 'slide_{}.jpg'.format(x+1))
