# @Time    : 6/7/2018 3:30 PM
# @Author  : 李武卿, 主管高级数据分析师
# @File    : 今日头条.py
# @Software: PyCharm Community Edition
# @Desc    : Python3 基础课程
# @license : Copyright(C), 美库尔信息咨询（南京）有限公司
# @Contact : wuli@merkleinc.com
# @Wechat  : wx_Darren910220


import requests
import csv
import time
import os
import pandas as pd


def flatten_dict(d):
    """
    Flatten an nested Dict object
    :param d: Dict
    :return: Flattened Dict
    """
    result = dict()
    for k, v in d.items():
        if isinstance(v, dict):
            result.update(flatten_dict(v))
        elif isinstance(v, list):
            if v:
                for i in range(len(v)):
                    result[k+'_'+str(i)] = v[i]
            else:
                result[k] = None
        else:
            result[k] = v
    return result


def str2time(string):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(int(string) / 1000))


def to_csv(file, data, columns, delete=False):
    """
    write data to csv
    :param file: file name
    :param data: data you want to write out
    :param columns: column names
    :param delete: if delete the file if exits
    :return:
    """
    if not os.path.exists('{}.csv'.format(file)) or delete:
        with open('{}.csv'.format(file), 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=columns)
            writer.writeheader()
            writer.writerow(data)
    else:
        with open('{}.csv'.format(file), 'a+', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=columns)
            writer.writerow(data)


def to_df(items, keyword, file):
    """
    convert comments to dataframe form
    :param comments:
    :return:
    """
    l = ['abstract', 'article_url', 'comment_count', 'comments_count', 'create_time', 'datetime',
         'display_time', 'has_gallery', 'has_image', 'has_video', 'image_count', 'middle_mode', 'more_mode',
         'play_effective_count', 'publish_time', 'single_mode', 'tag','video_duration', 'video_duration_str']

    df = pd.DataFrame(columns=l)

    for i, item in enumerate(items[:-1]):
        # print(i)
        if not item.get('abstract'):
            continue
        news = item.copy()
        for k in item.keys():
            if k not in l:
                news.pop(k)
        # print(news)
        # flattened_dict = flatten_dict(item)
        df2 = pd.DataFrame.from_dict(news, orient='index').T
        # df2['behot_time_str'] = df2['behot_time'].apply(str2time)
        # df2['create_time_str'] = df2['create_time'].apply(str2time)
        # df2['display_time_str'] = df2['display_time'].apply(str2time)
        # df2['publish_time_str'] = df2['publish_time'].apply(str2time)
        df2['keyword'] = keyword
        df1 = df
        df = pd.concat([df1, df2])

    if os.path.exists(file):
        df.to_csv(file, index=False, header=False, encoding='utf-8', mode='a+')
    else:
        df.to_csv(file, index=False, encoding='utf-8', mode='a+')


def keyword_search(keyword, file, pages=50):
    for page in range(pages):
        print('第{}页'.format(page+1))
        offset = page*20

        url = 'https://www.toutiao.com/search_content/?offset={}&format=json&keyword={}' \
              '&autoload=true&count=20&cur_tab=1&from=search_tab'.format(offset, keyword)

        resp_j = requests.get(url).json()
        items = resp_j['data']

        # 列数
        # i = 0
        # for item in items:
        #     flattened_dict = flatten_dict(item)
        #     if len(flattened_dict) > i:
        #         i = len(flattened_dict)
        #         j = flattened_dict

        try:
            to_df(items, keyword, file)
        except:
            print('不明错误')


file = "今日头条-Search.csv"
keywords = ['高考', 'Python', '大数据']
for keyword in keywords:
    print('在抓取关键字：{}'.format(keyword))
    keyword_search(keyword, file, 10)
