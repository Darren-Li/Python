# @Time    : 07/20/2018 4:00 PM
# @Author  : 李武卿
# @Contact : wuli@merkleinc.com
# @Mobile  : (+86) 130-7253-6076


update_log = """
2018/09/01 Wuqing Li

"""


# selenium to Simulate browser behavior
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common import exceptions

# BeautifulSoup to Parse web pages
from bs4 import BeautifulSoup

# operation and time modules
import os
import time
import random
import math

# data processing and data storage
import pandas as pd
import json
import csv


def item_info(html):
    """
    :param html: html doc from browser
    :return: items information including item_id, item_name, item_url
    """
    items_info = []
    soup = BeautifulSoup(html, 'lxml')
    content_div = soup.find('div', class_="common-list-main")

    for a in content_div.select('a[class="link item-title"]'):
        item_name = a.text
        item_url = "http:" + a.get('href')
        item_others = json.loads(a.get('data-lab'))
        items_info.append({"item_id": str(item_others.get('poi_id')), "item_name": item_name, "item_url": item_url})
    return items_info


def item_details(html, item_name):
    """
    :param html: html doc from browser
    :param item_name:
    :return: items more detailed information including store info and product name
    """
    soup = BeautifulSoup(html, 'lxml')

    # 商品展示区数据
    s_c_j = {}
    for div in soup.select('div[class="details clear"]'):
        for div2 in div.select('div[class="d-left"]'):
            for div21 in div2.select('div[class="name"]'):
                s_c_j['item_name'] = div21.text
            s_c_j['item_score'], s_c_j['item_cpp'] = None, None
            try:
                for div22 in div2.select('div[class="score clear"]'):
                    s_c_j['item_score'], s_c_j['item_cpp'] = div22.p.text.replace('分', '').replace('人均￥', '').split()
            except ValueError as e:
                print(e)
                print('只获取部分信息')
            for div23 in div2.select('div[class="address"]'):
                p = div23.select('p')
                s_c_j['address'], s_c_j['contacts'], s_c_j['business_hours'] = None, None, None
                try:
                    s_c_j['address'] = p[0].text.strip('地址：')
                    s_c_j['contacts'] = p[1].text.strip('电话：')
                    s_c_j['business_hours'] = p[2].text.strip('营业时间：')
                except IndexError as e:
                    print(e)
                    print('只获取部分信息')
            others = []
            for div24 in div2.select('ul[class="tags clear"]'):
                others.append(div24.li.text)
            s_c_j['others'] = '|'.join(others)

    # 商品详情
    prod_price = {}
    for div in soup.select('div[class="recommend"]'):
        for ul in div.select('ul[class="clear"]'):
            for li in ul.select('li'):
                prod_price_txt = li.text.replace('￥', '').split()
                # print(prod_price)
                try:
                    prod_price.update(dict.fromkeys([prod_price_txt[0]], prod_price_txt[1]))
                except IndexError as e:
                    print(e)
                    prod_price.update(dict.fromkeys([prod_price_txt[0]], None))
        products = []
        for div2 in div.select('div[class="list clear"]'):
            for span in div2.select('span'):
                products.append(span.text)
        products = '|'.join(products)
        s_c_j['products'] = products

    s_c_j.update(dict.fromkeys(["prod_price"], prod_price))

    # 评论总结
    comment_summary = {}
    for div in soup.select('div[class="com-cont"]'):
        for ul in div.select('ul[class="tags clear"]'):
            for li in ul.select('li'):
                summary_text = li.text.split('(')
                try:
                    comment_summary.update(dict.fromkeys([summary_text[0]], summary_text[1].strip(')')))
                except IndexError as e:
                    print(e)
                    comment_summary.update(dict.fromkeys([summary_text[0]], None))

    s_c_j.update(dict.fromkeys(["comment_summary"], comment_summary))

    return s_c_j


def fix_JSON(json_message=None):
    """
    debug 网页返回的数据不能被直接转化为JSON格式的错误
    :param json_message:
    :return:
    """
    result = None
    try:
        result = json.loads(json_message)
    except json.decoder.JSONDecodeError as e:
        # Find the offending character index:
        idx_to_replace = int(str(e).split(' ')[-1].replace(')', ''))
        # Remove the offending character:
        json_message = list(json_message)
        json_message[idx_to_replace] = ' '
        new_message = ''.join(json_message)
        return fix_JSON(json_message=new_message)
    return result


def get_comments(item_id, offset, c):
    """
    get comments from one page
    :param item_id:
    :param offset:
    :param c: comments count on each page
    :return:
    """
    url = 'http://www.meituan.com/meishi/api/poi/getMerchantComment?' \
          '&id={}&offset={}&pageSize={}&sortType=1'.format(item_id, offset, c)
    browser.get(url)
    soup = BeautifulSoup(browser.page_source, 'lxml')
    raw_json = soup.find('body').text
    comments_json = None
    try:
        comments_json = fix_JSON(raw_json.strip('json()\n'))
        # comments_json = json.loads(raw_json.strip('json()\n'))
    except json.decoder.JSONDecodeError as e:
        print('* '*7, e, '* '*7)
    except:
        print('Other errors when parsing JSON！')

    if comments_json:
        return comments_json
    else:
        return None


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
                result[k] = len(v)
            else:
                result[k] = None
        else:
            result[k] = v
    return result


def str2time(string):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(int(string) / 1000))


def to_df(comments, item_name, item_id):
    """
    convert comments to dataframe form
    :param comments:
    :param item_name:
    :param item_id:
    :return:
    """
    df = pd.DataFrame(
        columns=['userName','userUrl', 'avgPrice', 'comment', 'merchantComment', 'picUrls', 'commentTime', 'replyCnt',
                 'zanCnt', 'readCnt', 'hilignt', 'userLevel', 'userId', 'uType', 'star', 'quality', 'alreadyZzz',
                 'reviewId', 'menu', 'did', 'dealEndtime', 'anonymous'])

    if comments:
        for comment in comments.get('data').get('comments'):
            flattened_dict = flatten_dict(comment)
            df2 = pd.DataFrame.from_dict(flattened_dict, orient='index').T
            df2['commentTime_str'] = df2['commentTime'].apply(str2time)
            df2['shop_name'] = item_name
            df2['shop_id'] = item_id
            df1 = df
            df = pd.concat([df1, df2], sort=False)
    else:
        pass
    return df


def get_all_comments(item_name, item_id, c=100):
    """
    get all comments of specific item
    :param item_name:
    :param item_id:
    :param c: comments count on each page
    :return:
    """
    comments = get_comments(item_id, 0, c)
    if comments.get('data').get('total') == 0:
        data_tmp = pd.DataFrame()
        print('{} 没有评论信息！'.format(item_name))
    else:
        i = 1
        while True:
            comments = get_comments(item_id, 0, c)
            if comments:
                if comments.get('data').get('comments') is None:
                    print(time.strftime("%Y-%m-%d %X", time.localtime()),
                          ': 你是小蜘蛛。。。(定住你 {} 秒)'.format(random.randrange(50, 60) * i))
                    time.sleep(random.randrange(50, 60) * i)
                    i += 1
                else:
                    break
            else:
                break
        data_tmp = to_df(comments, item_name, item_id)

    if comments and not data_tmp.empty:
        data = None
        data = pd.concat([data, data_tmp], sort=False)
        comment_count = comments.get('data').get('total')
        max_page = math.ceil(comment_count/c)
        print('Total comments: {2}\n\npage {0:2} of {1:2}'.format(1, max_page, comment_count))

        for page in range(2, max_page+1):
            time.sleep(random.randrange(3, 6))
            print('page {0:2} of {1:2}'.format(page, max_page))
            i = 1
            while True:
                comments = get_comments(item_id, (page-1)*c, c)
                if comments:
                    if comments.get('data').get('comments') is None:
                        print('page {0:2} of {1:2}'.format(page, max_page))
                        print(time.strftime("%Y-%m-%d %X", time.localtime()),
                              ': 你是小蜘蛛。。。(定住你 {} 秒)'.format(random.randrange(50, 60) * i))
                        time.sleep(random.randrange(50, 60) * i)
                        i += 1
                    else:
                        break
                else:
                    break
            data_tmp = to_df(comments, item_name, item_id)
            if data_tmp.empty:
                pass
            else:
                data = pd.concat([data, data_tmp], sort=False)

        file = "shop_comments_meituan.csv"
        if os.path.exists(file):
            data.to_csv(file, index=False, header=False, encoding='utf-8', mode='a+')
        else:
            data.to_csv(file, index=False, encoding='utf-8', mode='a+')
    else:
        pass


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


def items_comments(keyword, speed=1, comments=True, details=True):
    """
    get products detailed information and comments of specific seller and category
    :param keyword: keyword
    :param speed: scraping speed
    :param comments: get comments or not
    :param details: get product details or not
    :return:
    """
    search = browser.find_element_by_css_selector("input[class='header-search-input']")
    search.clear()
    # search key words
    search.send_keys(keyword)
    search.send_keys(Keys.ENTER)
    time.sleep(2)

    result_pg = 1
    while True:
        time.sleep(3*speed)
        browser.execute_script("window.scrollTo(0, 1000);")
        browser.implicitly_wait(30)

        main_page = browser.current_window_handle

        html = browser.page_source
        item_list = item_info(html)
        print(time.strftime("%Y-%m-%d %X", time.localtime()),
              '搜索关键词：“{}” 在当前页面（第{}页）共有：{}个产品！'.format(keyword, result_pg, len(item_list)))

        browser.execute_script("window.open('','_blank');")  # open a blank tab
        handles = browser.window_handles
        for handle in handles:  # 切换到产品详情窗口
            if handle != main_page:
                browser.switch_to.window(handle)
                break

        for item in item_list:
            item_name = item['item_name']
            print('\n', time.strftime("%Y-%m-%d %X", time.localtime()),
                  '正在抓取第{0:2}/{1:2}个产品：{2}'.format(item_list.index(item)+1, len(item_list), item_name))
            item_url = item['item_url']
            browser.get(item_url)  # open url in current tab

            # get product detail info here
            if details:  # True, to collect product details, else only comments are collected
                time.sleep(3*speed)
                browser.implicitly_wait(30)
                browser.execute_script("window.scrollTo(0, 400);")
                time.sleep(3*speed)
                browser.implicitly_wait(30)

                html_prod_details = browser.page_source
                prod_details = item_details(html_prod_details, item_name)
                item.pop('item_url')
                prod_details.update(item)

                columns = ['item_id', 'item_name', 'item_score', 'item_cpp', 'address', 'contacts', 'business_hours',
                           'others', 'products', 'prod_price', 'comment_summary']
                to_csv('shop_details_meituan', prod_details, columns, False)
            else:
                pass

            # get comments by requests
            item_id = item['item_id']
            if comments:  # True, to collect comments, else only product details are collected
                get_all_comments(item_name, item_id)
            else:
                pass

        browser.close()  # 关闭产品详情窗口
        browser.switch_to.window(handles[0])  # 切换回主窗口

        try:
            browser.find_element_by_css_selector("li[class='pagination-item next-btn active']").click()
            # browser.find_element_by_xpath("//a[@class='right-arrow iconfont icon-btn_right'][@href='javascript:void(0);']").click()
            result_pg += 1
        except exceptions.NoSuchElementException as e:
            print('已经是最后一页了！')
            break
        except:
            print('其他错误，跳过这一页!')
            break


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# load chrome.exe
browser = webdriver.Chrome(r'C:\Darren\ziqing\Merkle\Python\Web Scraping with Python\chromedriver.exe')
browser.maximize_window()  # 窗口最大化

# login on
browser.get(r'https://passport.meituan.com/account/unitivelogin')

username = browser.find_element_by_css_selector("input[id='login-email']")
username.clear()
# input your LinkedIn account name[email_address]
username.send_keys('13072536076')
time.sleep(2)

password = browser.find_element_by_css_selector("input[id='login-password']")
password.clear()
# your account password
password.send_keys('ziqing27')
time.sleep(2)

browser.find_element_by_css_selector('input[data-mtevent="login.normal.submit"]').click()
time.sleep(3)


# sellers and categories info
# wuli = ['西贝莜面村', '晋家门']
wuli = ['西北菜', '火锅']
# wuli = ['轻食', '星巴克']
# words = wuli[0]

for words in wuli:
    # details and comments
    items_comments(words, speed=1, comments=True, details=True)

    # details only
    # items_comments(words, speed=1, comments=False, details=True)

    # # comments only
    # items_comments(words, speed=1, comments=True, details=False)


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
browser.quit()  # close browser and chromedriver.exe
# browser.close()  # only close browser
