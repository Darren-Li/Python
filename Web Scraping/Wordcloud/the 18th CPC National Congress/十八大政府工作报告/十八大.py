import os


def read_content(content_path):
    '''
    read all text files under the path
    '''
    content = ''
    for f in os.listdir(content_path):
        file_fullpath = os.path.join(content_path,f)
        if os.path.isfile(file_fullpath):
            print('loading {}'.format(file_fullpath))
            content += open(file_fullpath, 'r', encoding='utf-8').read()
            content += '\n'
    print('loading is done!')
    return content

content = read_content(r'.\文本')


import jieba.analyse

result = jieba.analyse.textrank(content,topK=1000,withWeight=True)
keywords = dict()
for i in result:
    keywords[i[0]] = i[1]


from PIL import Image, ImageSequence
import numpy as np
import matplotlib.pyplot as plt
from wordcloud import WordCloud, ImageColorGenerator

imgname = '中国地图.jpg'
imgname = '胡总.jpg'
imgname = '习大大作报告.jpg'
imgname = '人民.jpg'
imgname = '共产党.jpg'
image = Image.open(imgname)


graph = np.array(image)

wc = WordCloud(font_path=r"C:\Windows\Fonts\simhei.ttf",
               background_color='white', max_words=1000, mask=graph)
wc.generate_from_frequencies(keywords)
image_color = ImageColorGenerator(graph)

plt.imshow(wc)
plt.imshow(wc.recolor(color_func=image_color))
plt.axis("off")
# plt.savefig(imgname, dpi=1024)
plt.show()
