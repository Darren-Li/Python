# 抓取墨迹天气网所有县级的天气情况，并绘图

import requests
from bs4 import BeautifulSoup
import os
import csv
import time


def get_soup(url):
    """
    获取解析好的HTML文档树
    :param url: 想要获取数据的页面链接
    :return: 解析好的HTML文档树
    """
    try:
        resp = requests.get(url)
    except requests.exceptions.ConnectionError as e:
        print(e)
        time.sleep(10)
        resp = requests.get(url)
    soup = BeautifulSoup(resp.content, 'lxml')
    return soup


def province(url):
    """
    获取所有省份名和其背后的链接
    :param url: 省份页面链接
    :return: 字典形式返回省份名及背后链接，省份名最键，链接为值
    """
    soup = get_soup(url)
    data = {}
    for div in soup.select('div[class="city clearfix"]'):
        for dl in div.select('dl[class="city_list clearfix"]'):
            for a in dl.select('a'):
                data[a.text] = 'https://tianqi.moji.com' + a.get('href')
    return data


def city_hot(dict_p):
    """
    获取热门城市名及其背后的链接
    :param dict_p: province的返回值
    :return: 以嵌套列表的形式返回省份，城市和城市背后的链接
    """
    data = []
    for k, v in dict_p.items():
        soup = get_soup(v)
        for div in soup.select('div[class="city_hot"]'):
            for a in div.select('a'):
                data.append([k, a.text, a.get('href')])
    return data


def weather_info(url):
    soup = get_soup(url)

    data = []
    for div1 in soup.select('div[class="wrap clearfix wea_info"]'):
        for div2 in div1.select('div[class="left"]'):
            try:
                for div31 in div2.select('div[class="wea_alert clearfix"]'):
                    pollution_index, pollution_segment = div31.em.text.split()
            except AttributeError as e:
                print('没有污染指标！', e, url)
                pollution_index, pollution_segment = None, None
            for div32 in div2.select('div[class="wea_weather clearfix"]'):
                temperature, weather_desc = div32.em.text, div32.b.text
            for div33 in div2.select('div[class="wea_about clearfix"]'):
                humidity, wind = div33.span.text.split()[1], div33.em.text
            for div34 in div2.select('div[class="wea_tips clearfix"]'):
                wea_tips = div34.em.text
            data.extend([pollution_index, pollution_segment, temperature, weather_desc, humidity, wind, wea_tips])

    # data1 = []
    # for div3 in soup.select('div[class="forecast clearfix"]'):
    #     for ul in div3.select('ul[class="days clearfix"]'):
    #         data2 = []
    #         for li in ul.select('li'):
    #             data2.append(li.text.strip())
    #         data1.append(data2)
    # data.extend(data1)
    return data


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
            writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(columns)
            writer.writerow(data)
    else:
        with open('{}.csv'.format(file), 'a+', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(data)


if __name__ == "__main__":
    os.chdir(r'C:\Darren\ziqing\Merkle\Python\base\数据抓取\案例\墨迹天气')

    file, columns = '墨迹天气-20180415', \
                    ['省份', '城市', '污染指数', '污染描述', '实时温度', '天气', '湿度', '风况', '提示'
                    # ,'预测_今天', '预测_明天', '预测_后天'
                     ]
    url = r'https://tianqi.moji.com/weather/china'
    c = city_hot(province(url))
    for p, c, l in c:
        data = weather_info(l)
        data.insert(0, c)
        data.insert(0, p)
        to_csv(file, data, columns, delete=False)
    print('Done!')
