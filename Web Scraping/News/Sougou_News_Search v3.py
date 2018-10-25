# @Time    : 7/26/2018 8:40 PM
# @Author  : 李武卿, 主管高级数据分析师
# @File    : Sougou_News_Search.py
# @Software: PyCharm
# @license : Copyright(C), 美库尔信息咨询（南京）有限公司
# @Contact : wuli@merkleinc.com
# @Wechat  : wx_Darren910220

"""
搜索模式抓取搜狗新闻搜索引擎上的指定关键系相关的新闻

mob下，异步加载模式返回数据，缺少abstract
"""


import requests
from bs4 import BeautifulSoup
from DBcreator import create_sqlite_db_table
import datetime


def time2date(time_str):
    """
    将新闻发布时间为换为当天时间 YYYY-MM-DD HH:MM:SS 格式
    :param time_str:
    :return:
    """
    time_str = time_str.strip()
    now = datetime.datetime.today()
    if '分钟前' in time_str:
        minute = int(time_str[:-3])
        return (now - datetime.timedelta(minutes=minute)).strftime('%Y-%m-%d %X')
    elif '小时前' in time_str:
        hours = int(time_str[:-3])
        return (now - datetime.timedelta(hours=hours)).strftime('%Y-%m-%d %X')
    else:
        return datetime.datetime.strptime(time_str, '%Y-%m-%d').strftime('%Y-%m-%d %X')


def get_soup(url):
    """
    发起请求访问网页并解析返回内容，最终返回解析过的网页内容
    :param url:
    :return:
    """
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, 'lxml')
    return soup


def new_list(keyword, url, site, start_dt, end_dt):
    soup = get_soup(url)

    br = False
    data = []
    for li in soup.select('li'):
        article_url = li.a.get('href')
        abstract = None
        for h4 in li.select('h4[class="clamp2"]'):
            title = h4.text
        for div2 in li.select('div[class="citeurl ellipsis"]'):
            source = div2.span.text
            publish_time = div2.time.text
            publish_time = time2date(publish_time)

        if start_dt <= publish_time < end_dt:
            data.append([title, abstract, publish_time, source, article_url, site, keyword])
        elif publish_time < start_dt:
            br = True
            break
    return br, data


def sougou_news(keyword, site, start_dt, end_dt, table, pages=50):
    sites = {'腾讯': 'site:qq.com',
             '搜狐': 'site:sohu.com',
             '新浪': 'site:sina.com.cn',
             '凤凰': 'site:ifeng.com',
             '网易': 'site:163.com'
             }
    site_id = sites.get(site)
    if not site_id:
        print('输入的网站名称错误，请参考{}，\n重新输入：'.format(sites))

    url = 'http://news.sogou.com/news/wap/searchlist_ajax.jsp?mode=1&media=&query={}+{}' \
          '&time=0&clusterId=&sort=1&p=42230305&dp=1&from=ajax&page={}'.format(site_id, keyword, 1)
    soup = get_soup(url)
    if soup.p:
        pages = int(soup.p.text.split(',')[0])
    else:
        pages = pages
        print('Pags={}【自己指定的】'.format(pages))

    data_tmp = []
    for page in range(1, pages+1):
        url = 'http://news.sogou.com/news/wap/searchlist_ajax.jsp?mode=1&media=&query={}+{}' \
              '&time=0&clusterId=&sort=1&p=42230302&dp=1&from=ajax&page={}'.format(site_id, keyword, page)

        br, data = new_list(keyword, url, site, start_dt, end_dt)

        if data == data_tmp:
            print('在{}页已经遍历完毕，跳出'.format(page))
            break
        data_tmp = data

        cursor.executemany("INSERT INTO {} VALUES (?, ?, ?, ?, ?, ?, ?)".format(table), data)
        conn.commit()

        # if br:  # 如果严格按时间排序，这里可以使得程序提前跳出
        #     print('新闻发布时间早于{}，在{}页跳出'.format(start_dt, page))
        #     break


if __name__ == '__main__':
    keywords = ['美赞臣', '美素佳儿', '雀巢', '惠氏', '雅培',
                '疫苗', '长生生物',
                '瑞虎8', '哈弗h6', '汉兰达', '奥迪q5', 'rav4']

    sites = ['腾讯', '搜狐', '新浪', '凤凰', '网易']
    start_dt, end_dt = '2018-07-01', '2018-08-03'  # 必须是 YYYY-MM-DD 格式

    db = '..\data\public_opinion_analysis.db'
    table = 'sougou'
    create_script = '''CREATE TABLE {} (title text, abstract text, publish_time text, source text, article_url text,
     site text, keyword text)'''.format(table)

    # connect to sqlite3 and create a table for storing the data scraping form the corresponding account
    conn, cursor = create_sqlite_db_table(db=db, table=table, create_script=create_script, drop='N')

    for keyword in keywords:
        for site in sites:
            print('\n正在抓取 "{}" 网上 "{}" 相关新闻\n'.format(site, keyword), "* "*30)
            sougou_news(keyword, site, start_dt, end_dt, table, pages=50)

    conn.close()
