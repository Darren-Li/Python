# @Time    : 10/19/2018 10:17 AM
# @Author  : 李武卿, 数据分析经理
# @File    : 华东师范大学.py
# @Software: PyCharm
# @Wechat  : wx_Darren910220


"""
https://zsb.ecnu.edu.cn/webapp/scoreSearch-new2.jsp?id=2&pid=931&year=2018&moduleId=31

"""


import requests
from bs4 import BeautifulSoup
import sqlite3


def get_soup(url):
    """
    发起请求访问网页并解析返回内容，最终返回解析过的网页内容
    :param url: url
    :return: soup
    """
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, 'lxml')
    return soup


def get_data(url, year, province):
    soup = get_soup(url)
    table = soup.select('table[id="score-table"]')[0]

    data = []
    for tr in table.select('tr'):
        if '暂时没有数据' in tr.text:
            print('!!! {}年 在 {} 暂时没有数据'.format(year, province))
            i = 1
        else:
            i = 0
        body = []
        for td in tr.select('td'):
            body.append(td.text.strip())
        data.append(body)
    if i == 0:
        return data
    else:
        return None


def insert_data(cursor, tbname, data):
    if data:
        # test whether the table exists!
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        db_info = cursor.fetchall()
        tables = []
        for i in db_info:
            tables.append(i[0])
        exist = 'Y' if tbname in tables else 'N'

        if exist == 'N':
            # create table
            cursor.execute('create table {} ({})'.format(tbname, ', '.join(data[0]).replace('/', "_")))

        # insert data
        cursor.executemany("INSERT INTO {} VALUES (?{})".format(tbname, ",?"*(len(data[0])-1)), data[1:])

    else:
        pass


def main(url, cursor, tbname, year=None, province=None):
    data = get_data(url, year, province)
    insert_data(cursor, tbname, data)


def get_province_index(province_html):
    soup = BeautifulSoup(province_html, 'lxml')

    province_index = {}

    for div in soup.select('div[id="province11"]'):
        keys = []
        for label in div.select('label'):
            keys.append([label.get('for'), label.text])
        values = []
        for input in div.select('input'):
            values.append([input.get('id'), input.get('value')])

    for i, j in keys:
        for m, n in values:
            if i == m:
                province_index[j] = n
    return province_index


province_html = """<div id="province11" class="col-sm-11 controls">
                                    <input id="radio1" name="recruit-province" value="911" type="radio"> <label class="radio-inline" for="radio1">北京 </label><input id="radio2" name="recruit-province" value="912" type="radio"> <label class="radio-inline" for="radio2">天津 </label><input id="radio3" name="recruit-province" value="913" type="radio"> <label class="radio-inline" for="radio3">河北 </label><input id="radio4" name="recruit-province" value="914" type="radio"> <label class="radio-inline" for="radio4">山西 </label><input id="radio5" name="recruit-province" value="915" type="radio"> <label class="radio-inline" for="radio5">内蒙古 </label><input id="radio6" name="recruit-province" value="921" type="radio"> <label class="radio-inline" for="radio6">辽宁 </label><input id="radio7" name="recruit-province" value="922" type="radio"> <label class="radio-inline" for="radio7">吉林 </label><input id="radio8" name="recruit-province" value="923" type="radio"> <label class="radio-inline" for="radio8">黑龙江 </label><input id="radio9" name="recruit-province" value="931" type="radio" checked="checked"> <label class="radio-inline" for="radio9">上海 </label><input id="radio10" name="recruit-province" value="932" type="radio"> <label class="radio-inline" for="radio10">江苏 </label><input id="radio11" name="recruit-province" value="933" type="radio"> <label class="radio-inline" for="radio11">浙江 </label><input id="radio12" name="recruit-province" value="934" type="radio"> <label class="radio-inline" for="radio12">安徽 </label><input id="radio13" name="recruit-province" value="935" type="radio"> <label class="radio-inline" for="radio13">福建 </label><input id="radio14" name="recruit-province" value="936" type="radio"> <label class="radio-inline" for="radio14">江西 </label><input id="radio15" name="recruit-province" value="937" type="radio"> <label class="radio-inline" for="radio15">山东 </label><input id="radio16" name="recruit-province" value="941" type="radio"> <label class="radio-inline" for="radio16">河南 </label><input id="radio17" name="recruit-province" value="942" type="radio"> <label class="radio-inline" for="radio17">湖北 </label><input id="radio18" name="recruit-province" value="943" type="radio"> <label class="radio-inline" for="radio18">湖南 </label><input id="radio19" name="recruit-province" value="944" type="radio"> <label class="radio-inline" for="radio19">广东 </label><input id="radio20" name="recruit-province" value="945" type="radio"> <label class="radio-inline" for="radio20">广西 </label><input id="radio21" name="recruit-province" value="946" type="radio"> <label class="radio-inline" for="radio21">海南 </label><input id="radio22" name="recruit-province" value="950" type="radio"> <label class="radio-inline" for="radio22">重庆 </label><input id="radio23" name="recruit-province" value="951" type="radio"> <label class="radio-inline" for="radio23">四川 </label><input id="radio24" name="recruit-province" value="952" type="radio"> <label class="radio-inline" for="radio24">贵州 </label><input id="radio25" name="recruit-province" value="953" type="radio"> <label class="radio-inline" for="radio25">云南 </label><input id="radio26" name="recruit-province" value="954" type="radio"> <label class="radio-inline" for="radio26">西藏 </label><input id="radio27" name="recruit-province" value="961" type="radio"> <label class="radio-inline" for="radio27">陕西 </label><input id="radio28" name="recruit-province" value="962" type="radio"> <label class="radio-inline" for="radio28">甘肃 </label><input id="radio29" name="recruit-province" value="963" type="radio"> <label class="radio-inline" for="radio29">青海 </label><input id="radio30" name="recruit-province" value="964" type="radio"> <label class="radio-inline" for="radio30">宁夏 </label><input id="radio31" name="recruit-province" value="965" type="radio"> <label class="radio-inline" for="radio31">新疆 </label><input id="radio32" name="recruit-province" value="966" type="radio"> <label class="radio-inline" for="radio32">港澳台联招 </label></div>
                                    """
province_index = get_province_index(province_html)


db = "历年高考录取分数线"
conn = sqlite3.connect(db)
cursor = conn.cursor()

years = [2015, 2016, 2017, 2018]

tbname = 'score_provinces'  # id=1
print('正在抓取 华东师范大学 近几年在各省的录取分数线')
for province, index in province_index.items():
    url = 'https://zsb.ecnu.edu.cn/webapp/scoreSearch-new2.jsp?id=1&pid={}&moduleId=31'.format(index)
    main(url, cursor, tbname, year=None, province=province)

tbname = 'score_art'  # id=3
for year in years:
    url = 'https://zsb.ecnu.edu.cn/webapp/scoreSearch-new2.jsp?id=3&year={}&moduleId=31'.format(year)
    print('正在抓取 华东师范大学 在 {}年 的艺术类专业分数线'.format(year))
    main(url, cursor, tbname, year=year, province=None)

for tbname, i in [['score_majors', 2], ['score_plan', 4]]:
    for year in years:
        print('正在抓取 华东师范大学 {}年 在各省份的分数线'.format(year))
        for province, index in province_index.items():
            url = 'https://zsb.ecnu.edu.cn/webapp/scoreSearch-new2.jsp?id={}&pid={}&year={}&moduleId=31'\
                .format(i, index, year)
            main(url, cursor, tbname, year=year, province=province)

conn.commit()
conn.close()
