# @Time    : 10/27/2017 10:43 AM
# @Author  : 李武卿, 高级数据分析师
# @File    : 豆瓣读书-书籍内容简介.py.py
# @Software: PyCharm Community Edition
# @Desc    : Python3 基础课程
# @license : Copyright(C), 美库尔信息咨询（南京）有限公司
# @Contact : wuli@merkleinc.com

"""
目标：
1. 抓取所有豆瓣读书页面的书籍简介
2. 可以指定数据大类
3. 可以指定书籍子类中书本个数
"""

import requests
from bs4 import BeautifulSoup
import os
import time


loginUrl = 'http://accounts.douban.com/login'

formData = {
    "redir": "http://movie.douban.com/mine?status=collect",
    "form_email": 13072536076,
    "form_password": 'ziqing27',
    "login": '登录'
}

headers = {"Referer": "https://www.douban.com/accounts/login?source=book",
           "User-Agent": 'Mozilla/5.0 (Windows NT 6.1)\AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36'}

# create session
session_requests = requests.session()

r = session_requests.post(loginUrl, data=formData, headers=headers)
print('登陆状态：', r.status_code)


def get_soup(url):
    """
    解析 html
    :param url: url
    :return: soup
    """
    #resp = requests.get(url)  #  在非登录状态下访问
    resp = session_requests.get(url)  #  在登录状态下访问
    soup = BeautifulSoup(resp.text, 'lxml')
    return soup


def has_href(tag):
    """
    返回有 href属性的 tag
    :param tag: html tag
    :return: 有 href属性的 tag
    """
    return tag.has_attr('href')


def has_href_title(tag):
    """
    返回有 href和 title属性的 tag
    :param tag: html tag
    :return: 有 href和 title属性的 tag
    """
    return tag.has_attr('href') and tag.has_attr('title')


def sub_category_url(url, category):
    """
    :param url: 豆瓣图书标签页面url
    :param category: 图书大类，如 “文化”， “文学”
    :return: 大类中各子类所对应的页面url
    """
    soup = get_soup(url)

    def specific_name(tag):
        return tag.has_attr('name') and tag.get('name') == category

    specific_category = soup.find(specific_name)
    sub_category = {}

    for e in specific_category.next_siblings:
        if e == '\n':
            pass
        else:
            for a in e.find_all(has_href):
                sub_category[a.get_text()] = 'https://book.douban.com/' + a.get('href')

    return sub_category


def write_text(category, sub_category, book, text):
    """
    将文本输出到text文档，并指定名字
    :param category: 大类名
    :param sub_category: 子类名
    :param book: 书名
    :param text: 文本
    :return: None
    """
    illegal_chars = list('?、\/*"<>|:')
    for c in illegal_chars:
        if c in book:
            book = book.replace(c, '')
    with open('{0}/{0}-{1}_{2}.txt'.format(category, sub_category, book), 'w', encoding='utf-8') as f:
        f.write(text)


def get_text(url, category, sub_category, book):
    """
    返回简介
    :param url: 书所在页面的 url
    :param category: 大类名
    :param sub_category: 子类名
    :param book: 书名
    :return: 简介
    """
    soup = get_soup(url)
    try:
        instro = soup.select('div[class="intro"]')[0].text.strip()
        #write_text(category, sub_category, book, instro)
    except IndexError:
        print('No intro for book {}, its url is: {}'.format(book, url))


def create_dir(directory):
    """在当前路径下创建一个文件夹"""
    if not os.path.exists(directory):
        print('创建文件夹： ' + directory)
        os.mkdir(directory)
    else:
        print('文件夹已经存在!')


def main(url, category, num=1000):
    """
    主函数，调用了上面的函数，遍历拿到子类中每一类的前1000本书，然后拿到简介，
    实际上网站只能最多返回前50页，也就是前1000本书。
    :param url: 主页面 url
    :param category: 大类名
    :param num: 书的数量，当num<20时，返回20本。
    :return: None
    """
    create_dir(category)

    sub_category = sub_category_url(url, category)
    print('\n共{}个子类！'.format(len(sub_category)), end='\n')

    for k, v in sub_category.items():
        print('downloading intro for: ', k)
        url = v
        i = 0

        while True:
            soup = get_soup(url)

            if i == 0:
                try:
                    paginator = int(soup.select('div[class="paginator"]')[0].select('a')[-2].text)
                except IndexError:
                    print('No paginator category, its url is: {}'.format(k, url))
                    break
                paginator = int(num/20) if paginator > int(num/20) else paginator

            for a in soup.find_all(has_href_title):
                if a == '\n':
                    pass
                else:
                    get_text(a.get('href'), category, k, a.get('title'))

            i += 1
            url = 'https://book.douban.com/tag/{}?start={}&type=T'.format(k, i * 20)

            if i > paginator-1:
                break
        time.sleep(60)


def main2(url, category, num=1000):
    """
    主函数，调用了上面的函数，遍历拿到子类中每一类的前1000本书，然后拿到简介，
    实际上网站只能最多返回前50页，也就是前1000本书。在子类书籍页面遍历中在当前页自动获取下一页链接
    :param url: 主页面 url
    :param category: 大类名
    :param num: 书的数量，当num<20时，返回20本。
    :return: None
    """
    create_dir(category)

    sub_category = sub_category_url(url, category)
    print('\n共{}个子类！'.format(len(sub_category)), end='\n')

    for k, v in sub_category.items():
        print('downloading intro for: ', k)
        url = v
        i = 0

        while True:
            soup = get_soup(url)
            time.sleep(3)
            if soup.select('span[class="next"]'):
                # 如果没有遍历完，在获取下页链接
                url = 'https://book.douban.com' + soup.select('span[class="next"]')[0].select('a')[0].get('href')
            else:
                break

            # 判断是否遍历完毕，若遍历完毕在下一页会出现标签“<p class="pl2">没有找到符合条件的图书</p>”
            if soup.select('p[class="p12"]'):
                break
                print('All pages have been scraped')

            for a in soup.find_all(has_href_title):
                if a == '\n':
                    pass
                else:
                    get_text(a.get('href'), category, k, a.get('title'))

            # 记录页数
            i += 1
            # 如果页数达到指定页数则跳出
            if i > int(num / 20)-1:
                break
        time.sleep(60)


if __name__ == '__main__':
    douban_book_labels = 'https://book.douban.com/tag/?view=type&icn=index-sorttags-all'

    # 下载豆瓣读书指定大类(如：文化)的指定页面数的书籍简介
    # main(douban_book_labels, '文化', 100)
    # main(douban_book_labels, '经管', 100)
    # main2(douban_book_labels, '文学', 10)

    for cate in ['文学', '流行', '文化', '生活', '经管', '科技']:
        main2(douban_book_labels, cate, 100)
        time.sleep(120)
        
