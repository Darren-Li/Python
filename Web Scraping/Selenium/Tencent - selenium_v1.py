# @Time    : 06/07/2018 4:00 PM
# @Author  : 李武卿, 主管高级数据分析师
# @File    : Tencent - selenium_v1.py
# @Software: PyCharm Community Edition
# @license : Copyright(C), 美库尔信息咨询（南京）有限公司
# @Contact : wuli@merkleinc.com
# @Mobile  : (+86) 130-7253-6076

# update log


# selenium to Simulate browser behavior
from selenium import webdriver
from selenium.common import exceptions

# BeautifulSoup to Parse web pages
from bs4 import BeautifulSoup

# operation and time modules
import os
import time
import datetime
# import random

# data processing and data storage
# import pandas as pd
# import json
import csv

import requests
from bs4 import BeautifulSoup
import re

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# load chrome.exe
browser = webdriver.Chrome(r'C:\Darren\ziqing\Merkle\Python\Web Scraping with Python\chromedriver.exe')
browser.maximize_window()  # 窗口最大化


def start_end_date(start_date, end_date):
    year, month, day = list(map(int, start_date.split('-')))
    start_tm = datetime.datetime(year, month, day)
    year, month, day = list(map(int, end_date.split('-')))
    end_tm = datetime.datetime(year, month, day) + datetime.timedelta(days=1)
    return start_tm, end_tm


def blog_list(category, start_tm, end_tm, headers, year='2018'):
    """
    :param category: 新闻频道
    :param start_tm: 想抓取的文章的起始发布时间, 如 '2017-06-24'
    :param end_tm: 想抓取的文章的结束发布时间, 如 '2017-06-26'
    :return: 各新闻频道文章列表
    """
    data = []
    i = False

    while True:
        html = browser.page_source
        soup = BeautifulSoup(html, 'lxml')

        # 没有文章页面自动跳出
        if soup.select('div[class="article-tips"]'):
            print('{}类页没有文章！'.format(category))
            break
        # 查询等待
        if soup.find('正在查询'):
            print('正在查询，请耐心等待。。。')
            time.sleep(10)
            continue

        for div in soup.select('div[id="artContainer"]'):
            for ul in div.select('ul'):
                for li in ul.select('li'):
                    post_tm = year + '-' + li.select('span[class="t-time"]')[0].text
                    sub_category = li.select('span[class="t-tit"]')[0].text.strip('[]')
                    href = li.a.get('href')
                    title = li.a.text
                    post_tm = datetime.datetime.strptime(post_tm, "%Y-%m-%d %H:%M")

                    if start_tm <= post_tm < end_tm:
                        content = get_content(href, headers)
                        data_t = [category, sub_category, title, href, post_tm]
                        data_t.extend(content)
                        data.append(data_t)
                    elif post_tm < end_tm:
                        i = True

        # 不在指定时间范围内的页面自动跳出
        if i:
            break

        try:
            next = browser.find_element_by_css_selector('a[onclick="nextPage();"]')
            next.click()
        except exceptions.StaleElementReferenceException as e:
            time.sleep(10)
        except exceptions.NoSuchElementException as e:
            print('{}：抓取完毕'.format(category))
            break

        time.sleep(3)
        browser.implicitly_wait(5)

    return data


# 将数据写入CSV,如果文件存在直接覆盖
def to_csv_rows(filename, header, data, delete='N'):
    # filename: 文件名，总是以.csv结尾
    # header  : 表头,list格式
    # data    : 数据,list格式
    # del     : 文件存在时是否删除
    if os.path.exists(filename) and delete == 'N':
        f = open(filename, 'a', newline="\n", encoding="utf-8")
        writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerows(data)
        f.close()
    else:
        f = open(filename, 'w', newline="\n", encoding="utf-8")
        writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(header)
        writer.writerows(data)
        f.close()


def loop_categories(filename, header, start_date, end_tm_date, headers):
    start_tm, end_tm = start_end_date(start_date, end_tm_date)
    for xpath in ['//*[@id="iBody"]/div[1]/div[4]/div[1]/div[2]/div/div[5]/a[{}]'.format(i) for i in range(1, 14)]:
        # print(xpath)
        cate = browser.find_element_by_xpath(xpath)
        category = cate.text
        print('开始抓取** {} **类'.format(category))
        cate.click()
        time.sleep(5)
        browser.implicitly_wait(5)
        data = blog_list(category, start_tm, end_tm, headers)
        to_csv_rows(filename, header, data)


def get_content(url, headers):
    """
    发起请求访问网页并解析返回内容，最终返回解析过的网页内容
    :param url:
    :param headers:
    :return:
    """
    catalog, source, cmtNum, abstract = None, None, None, None
    try:
        resp = requests.get(url, headers=headers)
        soup = BeautifulSoup(resp.content, 'lxml')
        # print(url)

        for div in soup.select('div[class="qq_article"]'):
            for info in div.select('div[class="a_Info"]'):
                for info in div.select('span[class="a_catalog"]'):
                    catalog = info.text
                for info in div.select('span[class="a_source"]'):
                    source = info.text

            for content in div.select('div[id="Cnt-Main-Article-QQ"]'):
                if content.select('p[class="titdd-Article"]'):
                    for p in content.select('p[class="titdd-Article"]'):
                        abstract = p.text
                else:
                    abstract = []
                    for p in content.select('p[style*="TEXT-INDENT"]')[:5]:
                        abstract.append(p.text.strip())
                    abstract = [i for i in abstract if i != '']

                    if not abstract:
                        abstract = content.text.strip()

        if catalog:
            cmt_id = re.findall(r'\d+', re.findall(r'cmt_id = \d+;', resp.text)[0])[0]
            url_comm = 'http://coral.qq.com/article/{}/commentnum'.format(cmt_id)
            resp = requests.get(url_comm, headers=headers)
            resp_j = resp.json()
            cmtNum = int(resp_j['data']['commentnum'])
    except:
        print("requests error")

    content = [catalog, source, cmtNum, abstract]

    return content

# url = 'https://news.qq.com/a/20180607/014362.htm'
# get_content(url, headers)

# 进入新闻滚动页面
browser.get(r'http://roll.house.qq.com/#')

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/'
                         '66.0.3359.181 Safari/537.36'}

loop_categories(filename='腾讯新闻.csv', header=['category', 'sub_category', 'title', 'href', 'post_tm',
                                               'catalog', 'source', 'cmtNum', 'abstract'],
                start_date='2018-06-05', end_tm_date='2018-06-06', headers=headers)


browser.quit()   # close browser and chromedriver.exe
# browser.close()  # only close browser
