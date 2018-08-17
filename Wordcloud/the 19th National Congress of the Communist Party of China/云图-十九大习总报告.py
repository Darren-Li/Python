# 文件处理
import os
# 分词
import jieba.analyse
# 作图
from PIL import Image, ImageSequence  # 安装 pip install pillow
import numpy as np
import matplotlib.pyplot as plt
from wordcloud import WordCloud, ImageColorGenerator


"""
将文本文件放置在 '.\\文本'
模板图文件放置在 '.\\模板'
中文字体文件放置在 当前文件夹下
"""


def read_content(content_path):
    """
    读入所有文本文件
    :param content_path: 文件路径，应该为'.\\文本'
    :return: 文本内容
    """
    content = ''
    for f in os.listdir(content_path):
        file_fullpath = os.path.join(content_path, f)
        if os.path.isfile(file_fullpath):
            print('读入文件：{}'.format(f))
            content += open(file_fullpath, 'r', encoding='utf-8').read()
            content += '\n'
    print('文件读入完毕!')
    return content


def extra_keywords(k=1000):
    """
    提取关键字
    :param k: 关键字个数
    :return: 关键字字典
    """
    content = read_content(r'.\文本')
    result = jieba.analyse.textrank(content, topK=k, withWeight=True)
    keywords = dict()
    for i in result:
        keywords[i[0]] = i[1]
    return keywords


def img_extensions():
    """
    模板图文件后缀名收集
    :return: 模板图文件后缀名列表
    """
    extensions = ['.' + i for i in ['jpg', 'png', 'jpeg', 'jpe', 'jfif', 'bmp', 'dib', 'gif', 'tif', 'tiff']]
    print('默认模板图片后缀为：', extensions)
    add_extensions = input('如果没有包含你想要的文件后缀，请手动输入，如: "png", 输入"q"结束或不添加：')

    while add_extensions != 'q':
        extensions.append('.' + add_extensions)
        add_extensions = input()

    extensions = list(set(extensions))
    return extensions


def read_img(img_path):
    """
    读入所有模板图文件
    :param img_path: 模板路径，应该为'.\\模板'
    :return: 模板图文件名称列表
    """
    extensions = img_extensions()
    img = []
    for f in os.listdir(img_path):
        file_fullpath = os.path.join(img_path, f)
        _, extension = os.path.splitext(file_fullpath)
        if extension in extensions:
            print('读入模板：{}'.format(f))
            img.append(file_fullpath)
    print('模本读入完毕!')
    return img


def draw_wc(dpi=1024, show='off'):
    """
    生成词云图
    :param dpi: 词云图dpi, 默认为1024
    :return: None
    """
    keywords = extra_keywords()
    for imgname in read_img(r'.\模板'):
        image = Image.open(imgname)
        _, fn = os.path.split(imgname)
        graph = np.array(image)
        
        wc = WordCloud(font_path=r"simhei.ttf",  # 中文字体文件，同该python代码放置在同一文件夹
                       background_color='white', max_words=1000, mask=graph)
        
        wc.generate_from_frequencies(keywords)
        image_color = ImageColorGenerator(graph)
        plt.imshow(wc)
        plt.imshow(wc.recolor(color_func=image_color))
        plt.axis("off")
        plt.savefig('词云-'+fn, dpi=dpi)  # 如果不指定dpi且在打开之后保存图片，会得到空白图片
        plt.show() if show == 'on' else print('不打开图片')


# 执行
dpi = int(input('请输入词云图片的dpi，0表示按默认值【默认为1024】：'))
dpi = 1024 if dpi == 0 else dpi
show = input('是否在生成词云后打开，输入off或on，0表示按默认值【默认为off】：')

draw_wc(dpi=dpi, show=show)
