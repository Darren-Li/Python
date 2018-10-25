# @Time    : 7/24/2018 6:54 PM
# @Author  : 李武卿, 主管高级数据分析师
# @File    : 今日头条-Search（新闻正文）.py
# @Software: PyCharm
# @license : Copyright(C), 美库尔信息咨询（南京）有限公司
# @Contact : wuli@merkleinc.com
# @Wechat  : wx_Darren910220


import requests
from bs4 import BeautifulSoup
import re
import json
import pandas as pd


"""
视频网页
http://www.365yg.com/a6581237704757871112/#mid=6976379136
头条站内网页
    网页：
    https://www.toutiao.com/a6581373017606062595/
    图集：
    https://www.toutiao.com/a6581224243839631880/
站外网页
https://m.haiwainet.cn/ttc/3541092/2018/0723/content_31359485_1.html
"""


header_m = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko)"
                  " Version/11.0 Mobile/15A372 Safari/604.1",
    # "user-agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
    #               "Chrome/67.0.3396.99 Safari/537.36",
}

header_w = {"user-agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/68.0.3440.84 Safari/537.36"
            }


def content_snippets(keyword, contents, text_len=50):
    """
    :param keyword: 搜索关键词
    :param contents: 清洗过的正文内容
    :param text_len: 关键词前后字长上限
    :return: 关键词在正文中的片段列表
    """
    content = []
    target_contents = re.finditer(keyword, contents, re.I)

    u, u0 = 0, 0
    for i in target_contents:
        l0 = i.span()[0]
        if u0 != 0 and l0 - u0 < text_len:
            u0 = i.span()[1]
        else:
            u0 = i.span()[1]
            l = max(l0 - text_len, 0, u)
            u = u0 + text_len
            content.append(contents[l:u])
    return content


def toutiao_news(url, keyword, text_len=50, abstract_num=5):
    """
    获取头条站内新闻内容
    :param url: 新闻链接
    :param keyword: 搜索关键词
    :param text_len: 关键词前后字长上限
    :param abstract_num: 摘取关键词段个数
    :return: 列表，新闻标签和关键词段
    """
    resp = requests.get(url, headers=header_w, timeout=(60, 60))
    tags, content, data = None, [], []

    tags1 = re.search(r"tags: \[{.+}\],", resp.text)
    if tags1:
        tags2 = tags1.group()[6:-1]
        tags = []
        for tag in json.loads(tags2):
            tags.append(tag.get('name'))
        tags = '|'.join(tags)

    content1 = re.search(r"content: '.+',", resp.text)
    if content1:
        content2 = content1.group()[10:-2]
        content2 = re.sub(r'/+', '', content2)
        content2 = re.sub(r'[a-z]*[&a-z]+;', '', content2)
        content2 = re.sub(r'div [&#A-Za-z0-9 -_;]+', '', content2)
        content2 = re.sub(r'inline[&#A-Za-z0-9 -_;]+', '', content2)

        content = content_snippets(keyword, content2, text_len=text_len)

    data.append(tags)
    data.extend(content[:abstract_num])
    return data


def toutiao_photos(url, abstract_num=5):
    """
    获取头条站内图集内容
    :param url: 新闻链接
    :param abstract_num: 图集描述个数
    :return: 列表，新闻标签和图集描述
    """
    resp = requests.get(url, headers=header_w, timeout=(60, 60))
    labels, sub_abstracts, data = None, None, []

    labels1 = re.search(r'labels.+],\\"sub_abstracts', resp.text)
    if labels1:
        labels2 = labels1.group()[10:-17]
        labels3 = labels2.replace('\\\\', '\\')
        labels4 = labels3.encode().decode('unicode-escape')
        labels = labels4.replace('","', '|').replace('"', '')

    sub_abstracts1 = re.search(r'sub_abstracts.+],\\"sub_titles', resp.text)
    if sub_abstracts1:
        sub_abstracts2 = sub_abstracts1.group()[20:-14]
        sub_abstracts3 = sub_abstracts2.replace('\\\\', '\\')
        sub_abstracts = sub_abstracts3.encode().decode('unicode-escape')

    data.append(labels)
    data.extend(sub_abstracts.split('","')[:abstract_num])
    return data


def other_sites(url, keyword, text_len=50, abstract_num=5):
    """
    获取头条站外新闻内容
    :param url:新闻链接
    :param keyword:搜索关键词
    :param text_len:关键词前后字长上限
    :param abstract_num:摘取关键词段个数
    :return: 列表，新闻标签和关键词段
    """
    resp = requests.get(url, headers=header_m, timeout=(60, 60))
    soup = BeautifulSoup(resp.content, 'lxml')
    content, data = [], []

    content1 = soup.body.text
    content2 = re.sub(r'\s', '', content1)
    if content2:
        content = content_snippets(keyword, content2, text_len=text_len)

    data.append(None)
    data.extend(content[:abstract_num])
    return data


def news_contents(keyword, df, abstract_num=5):
    """
    获取头条新闻正文
    :param keyword:搜索关键词
    :param df:DataFrame，新闻列表
    :param abstract_num: 摘取关键词段个数
    :return:DataFrame，新闻全部内容
    """
    data = []

    for i in range(df.shape[0]):
        a_url = df.iloc[i]['article_url']
        try:
            if a_url.startswith('http://toutiao.com/group/'):
                a_url = a_url.replace('http://toutiao.com/group/', 'https://www.toutiao.com/a')

                if df.iloc[i]['has_gallery']:
                    content = toutiao_photos(a_url)
                elif df.iloc[i]['has_video']:
                    content = [None] * (abstract_num + 1)
                else:
                    content = toutiao_news(a_url, keyword)
            elif a_url.startswith('http://toutiao.com/preview_article/'):
                content = [None] * (abstract_num + 1)
            else:
                content = other_sites(a_url, keyword)
        except:
            print('抓取正文出错')
            content = [None] * (abstract_num+1)

        if len(content) < abstract_num+1:
            content.extend([None]*(abstract_num+1-len(content)))

        data.append(content)

    col_names = ['contents{}'.format(str(i)) for i in range(1, abstract_num+1)]
    col_names.insert(0, 'tags')

    df = df.merge(pd.DataFrame(data, columns=col_names), left_index=True, right_index=True)
    return df


if __name__ == "__main__":
    keyword = '疫苗'
    keyword = '长生生物'

    url = 'https://www.toutiao.com/a6581606476865864195/'  # 头条站内新闻
    url = 'https://www.toutiao.com/a6581082992163160580/'
    url = 'https://www.toutiao.com/a6581684803806953992/'
    url = 'https://www.toutiao.com/a6578631507793936909/'
    url = 'https://www.toutiao.com/a6582001007885025796/'
    toutiao_news(url, keyword)

    url = 'https://www.toutiao.com/a6581224243839631880/'  # 头条图集
    url = 'https://www.toutiao.com/a6575718893917045261/'
    url = 'https://www.toutiao.com/a6581774947641721351/'
    toutiao_photos(url, abstract_num=3)

    url = 'https://m.haiwainet.cn/ttc/3541092/2018/0723/content_31359485_1.html'  # 站外新闻
    url = 'http://m.gmw.cn/toutiao/2018-07/24/content_121388960.htm'
    url = 'http://m.cnwest.com/toutiao/data/content/15905779.html'
    url = 'https://wap.egsea.com/detail/article?id=271182'
    url = 'http://www.xinhuanet.com/fortune/2018-07/16/c_129914303.htm'
    url = 'https://www.toutiao.com/a6581082992163160580/'  # 站内也适用
    url = 'http://36kr.com/newsflash/coop/128700.html'
    url = 'https://www.zhitongcaijing.com/content/detail/139811.html'
    other_sites(url, keyword)

    url = 'https://www.toutiao.com/a6581383092387185159/'
    # news_contents(keyword, df)
