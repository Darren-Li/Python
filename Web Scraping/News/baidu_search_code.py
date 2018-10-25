"""
抓取百度搜索结果
"""

# import packages that will be used for below web scrawling
import datetime
import requests
from bs4 import BeautifulSoup
from requests.exceptions import RequestException
import csv
import re


# -----------------------------------------Part1: run below codes one time after opening the code file-----------------

# define the headers
headers = {
    # 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
    #               'Chrome/67.0.3396.99 Safari/537.36',
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) '
                  'Version/11.0 Mobile/15A372 Safari/604.1',
}


def article_date_transfer(time_str):
    """
    将网页不规范的时间格式转换为 YYYY-MM-DD 时间格式
    :param time_str:网页发布时间
    :return:YYYY-MM-DD格式的网页时间
    """
    time_str = time_str.strip()
    now = datetime.datetime.today()
    if '分钟前' in time_str:
        minute = int(time_str[:-3])
        return (now - datetime.timedelta(minutes=minute)).strftime('%Y-%m-%d')
    elif '小时前' in time_str:
        hours = int(time_str[:-3])
        return (now - datetime.timedelta(hours=hours)).strftime('%Y-%m-%d')
    elif '天前' in time_str:
        days = int(time_str[:-2])
        return (now - datetime.timedelta(days=days)).strftime('%Y-%m-%d')
    else:
        return datetime.datetime.strptime(time_str, '%Y年%m月%d日').strftime('%Y-%m-%d')


def get_url(url, header=headers):
    """
    访问关键词搜索的百度网页
    :param url:关键词搜索的百度网址
    :return:百度搜索页面的内容
    """
    try:
        resp = requests.get(url, header)
        soup = BeautifulSoup(resp.content, 'lxml')
        if resp.status_code == 200:
            return soup
        else:
            return None
    except RequestException:
        print("页面请求索引出错")
        return None


def get_detailed_url(url, header=headers):
    """
    访问每条关键词的详细页面
    :param url:每条关键词详细页面的网址
    :return:每条关键词详细页面的内容
    """
    try:
        resp = requests.get(url, header)
        soup = BeautifulSoup(resp.content, 'lxml')
        if resp.status_code == 200:
            return soup
        else:
            return None
    except RequestException:
        print("详细页面请求索引出错")
        return None


def get_page_search(keyword, page_num, file):
    """
    获取每条关键词详细页面的信息
    :param keyword:要搜索的关键词
    :param page_num:每条关键词最大访问的页数
    :param file:输出的csv文件名
    :return:返回每条关键词详细页面的搜索内容包括：标题，时间，摘要，具体内容
    """

    t = 0
    start_url = 'https://baidu.com/s?word=' + keyword + '&pn=' + str(t)  # 关键词搜索返回的第一页网址
    item_num = 1  # 抓取的关键词条数
    item = get_url(start_url)

    while t <= (page_num - 1) * 10:
        for i in item.select("div[class='result c-container ']"):
            try:
                item_url = i.h3.a.get("href")  # 每条关键词详细页面的网址
            except:
                item_url = None

            try:
                item_title = i.h3.a.text.strip()  # 每条关键词详细页面的标题
            except:
                item_title = None
            try:
                item_time = i.select("span[class=' newTimeFactor_before_abs m']")[0].text.strip().split()[0]
                item_time = article_date_transfer(item_time)  # 每条关键词详细页面的发布时间
            except:
                item_time = None
            try:
                item_abstract = i.select("div[class='c-abstract']")[0].text.strip().split()[-1]  # 每条关键词详细页面的摘要
            except:
                item_abstract = None
            try:
                item_detail = get_detailed_url(item_url)
                if item_detail:
                    item_content = [e.text.strip() for e in item_detail.find_all("p")]
                    item_content = "".join(item_content).strip()
                    item_content = re.sub(r'\s', '', item_content)  # 每条关键词详细页面的具体内容
            except:
                item_content = None

            if item_title or item_url or item_content:
                list_value = [item_num, keyword, item_title, item_time, item_url, item_abstract, item_content]
                with open(file, 'a', encoding='utf-8', newline="") as f:
                    # 打开一个csv文件用于追加。如果该文件已存在，文件指针将会放在文件的结尾。也就是说，
                    # 新的内容将会被写入到已有内容之后。如果该文件不存在，创建新文件进行写入。
                    writer = csv.writer(f)
                    writer.writerow(list_value)  # 返回搜索关键词的记录数，关键词，标题，时间，网址，摘要，详细内容
                item_num += 1
                print('正在访问"{}"第 "{}" 页 (共"{}" 页)相关内容'.format(keyword,
                                                              item.select("span[class='fk fk_cur']")[0].next_sibling.text.strip(),
                                                              page_num),
                      list_value)
        t += 10
        start_url = 'https://baidu.com/s?word=' + keyword + '&pn=' + str(t)  # 关键词搜索页面的下一页网址
        item = get_url(start_url)
        if not item or t > (page_num - 1) * 10:
            print('\n"{}"所有页面访问结束, 共访问了前 "{}" 页相关内容\n'.format(keyword,
                                                              int(item.select("span[class='fk fk_cur']")[0].next_sibling.text.strip()) - 1),
                  "* " * 30)
            break
    f.close()


# -----------------------------------------Part2: run below codes every time with changing input values---------------

"""
输入：
1.keywords的值:需要搜索的关键词，可以单个也可以多个（多个时用逗号隔开）
2.page_num的值;每个关键词要访问的最大页数 (一个关键词获取前10页内容约1分钟，时间：keyword个数*page_num/10*1分钟）
输出: 返回一个名为“百度搜索”的csv文件，里面存了一个或多个关键词的爬虫内容。每次重run code，文件内容会被totally refresh
爬虫结束提示：当出现"keywords"所有页面访问结束, 共访问了前 "page_num" 页相关内容"提示时，说明爬虫过程已经结束

"""

keywords = ['爱他美','美素佳儿']  # 输入1：需要搜索的关键词，可以单个也可以多个（多个时用逗号隔开）
page_num = 2  # 输入2：每个关键词要访问的最大页面数

file_name = "百度搜索.csv"   # 输出：csv文件
with open(file_name, 'w', encoding='utf-8', newline='') as f:
    # 打开一个csv文件只用于写入。如果该文件已存在则将其覆盖。如果该文件不存在，创建新文件。
    writer = csv.writer(f)
    writer.writerow(['序号', '关键词', '标题', '时间', '网址', '摘要', '详细内容'])

for keyword in keywords:
    print('\n正在抓取百度上 "{}" 相关新闻\n'.format(keyword), "* " * 30)
    get_page_search(keyword, page_num, file=file_name)
