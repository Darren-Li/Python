# @Time    : 6/7/2018 3:30 PM
# @Author  : 李武卿, 主管高级数据分析师
# @File    : 今日头条-Search (SQLite).py
# @Software: PyCharm
# @license : Copyright(C), 美库尔信息咨询（南京）有限公司
# @Contact : wuli@merkleinc.com
# @Wechat  : wx_Darren910220


from TT_Search_Content import *

import requests
import os
import time
from tqdm import tqdm
import pandas as pd
import pandas.io.sql as sql
import sqlite3


def connect2DB(db, table, drop='Y'):
    """
    create sqlite DB and table
    :param db: DB name
    :param table: table name
    :return:
    """
    db_is_new = not os.path.exists(db)
    # create or connect to DB
    conn = sqlite3.connect(db)
    cursor = conn.cursor()

    if db_is_new:
        print('Creating DB: {}'.format(db))
    else:
        print('Database: {} exists!'.format(db))
        # test whether the table exists!
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        db_info = cursor.fetchall()
        tables = []
        for i in db_info:
            tables.append(i[0])
        exist = 'Y' if table in tables else 'N'

        if exist == 'Y' and drop == 'Y':
            print('Table: {} exists! But Dropped and Recreating now according to your instructions!'.format(table))
            cursor.execute('DROP TABLE IF EXISTS {};'.format(table))
        elif exist == 'N':
            print('Table: {} does not exist, Creating now...'.format(table))
        else:
            print('Table: {} already exists, Did NOT Dropped according to your instructions!'.format(table))

    return conn, cursor


def to_df(keyword, items, start_dt, end_dt, conn, content=True):
    """
    convert dicts to dataframe
    :param keyword:搜索关键词
    :param items:新闻列表json数据
    :param start_dt:
    :param end_dt:
    :param conn:
    :param content:
    :return:
    """
    columns = ['tag', 'title', 'abstract', 'article_url', 'comments_count',
               # 'behot_time', 'create_time',
               'datetime',
               # 'display_time', 'publish_time',
               'has_gallery', 'has_image', 'has_video', 'image_count', 'keyword',
               # 'labels',
               'large_mode', 'middle_mode', 'more_mode', 'single_mode',
               'play_effective_count', 'show_play_effective_count', 'video_duration',
               'media_name'
               ]

    df = pd.DataFrame(columns=columns)

    for i, item in enumerate(items[:-1]):
        if not item.get('article_url'):  # 排除中间的推荐新闻
            continue
        news = item.copy()
        for k in item.keys():
            if k not in columns:
                news.pop(k)
        df2 = pd.DataFrame.from_dict(news, orient='index').T
        df1 = df
        df = pd.concat([df1, df2], sort=False)

        # df2['behot_time_str'] = df2['behot_time'].apply(str2time)
        # df2['create_time_str'] = df2['create_time'].apply(str2time)
        # df2['display_time_str'] = df2['display_time'].apply(str2time)
        # df2['publish_time_str'] = df2['publish_time'].apply(str2time)

    df = df[(df.datetime < end_dt) & (df.datetime >= start_dt)]
    df.reset_index(drop=True, inplace=True)

    if content:
        df = news_contents(keyword, df)

    # 将DataFrame写入Sqlite
    sql.to_sql(df, name='toutiao', con=conn, if_exists='append', index=False)


def keyword_search(keyword, conn, start_dt, end_dt, pages=30, content=True):
    """
    遍历关键词新闻页面得到新闻内容
    :param keyword:搜索关键词
    :param conn:数据库连接
    :param start_dt:新闻起始日期
    :param end_dt:新闻结束日期
    :param pages:遍历页数
    :param content:是否返回正文内容
    :return: None
    """
    for page in range(pages):
        # print('抓取第{}页数据中。。。'.format(page+1))
        offset = page*20

        url = 'https://www.toutiao.com/search_content/?offset={}&format=json&keyword={}' \
              '&autoload=true&count=20&cur_tab=1&from=search_tab'.format(offset, keyword)

        resp_j = requests.get(url, timeout=(60, 60)).json()
        items = resp_j['data']

        # 列数
        # i = 0
        # for item in items:
        #     flattened_dict = flatten_dict(item)
        #     if len(flattened_dict) > i:
        #         i = len(flattened_dict)
        #         j = flattened_dict

        if not items:
            print('新闻页面不够多，在{}页之后提前跳出！'.format(page))
            break

        try:
            to_df(keyword, items, start_dt, end_dt, conn, content=content)
        except:
            print('第{}页出现不明错误'.format(page+1))


# connect to sqlite3
db = '..\data\public_opinion_analysis.db'
table = 'toutiao'
conn, cursor = connect2DB(db=db, table=table, drop='N')

keywords = [
    # 奶粉
    '美赞臣', '惠氏', '雀巢', '伊利', '美素佳儿', '雅培', '多美滋', '贝因美', '飞鹤', '诺优能',
    '金领冠', '爱他美', '君乐宝', '圣元', '合生元', '喜宝', '佳贝艾特', '完达山', '安满', 'a2奶粉',

    # 汽车之家热门中型车
    '大众CC', '凯美瑞', '凯迪拉克ATS-L', '博瑞GE', '名图', '君威', '君越', '天籁', '奔驰C级', '奥迪A4L', '奥迪A5',
    '宝马3系', '帕萨特', '捷豹XEL', '沃尔沃S60L', '睿骋CC', '红旗H5', '蒙迪欧', '迈腾', '迈锐宝', '迈锐宝XL', '速派',
    '阿特兹', '雅阁',

    # 纯电动车品牌
    '云度', '威马', '拜腾', '蔚来', '零跑'
]

start_dt, end_dt = '2018-01-01', '2018-08-17'  # 天或月份前的0必须添加，时间左闭右开

start = time.time()

# for keyword in keywords:
#     print('在抓取关键字：{}'.format(keyword))
#     keyword_search(keyword, file, 10)

for keyword in tqdm(keywords):
    print('\n在抓取关键字：{}'.format(keyword))
    keyword_search(keyword, conn, start_dt, end_dt, 30, content=True)

conn.close()

print('\nDone! Took {:.2f} Minutes'.format((time.time()-start)/60))
# Done! Took 113.39 minutes
