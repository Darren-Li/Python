# @Time    : 07/23/2018 4:00 PM
# @Author  : 李武卿, 主管数据分析师
# @File    : JD 青汁 -selenium_v1.py
# @Software: PyCharm Community Edition
# @license : Copyright(C), 美库尔信息咨询（南京）有限公司
# @Contact : wuli@merkleinc.com
# @Mobile  : (+86) 130-7253-6076


update_log = """
2018/07/23 Wuqing Li

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
import re

# data processing and data storage
import pandas as pd
import json
import csv


def item_info(html):
    """
    :param html: html doc from browser
    :return: items information including item_name, item_url, price, sales_month, comments, shop_name, shop_url倒数从左至右
    """
    items_info = []
    soup = BeautifulSoup(html, 'lxml')

    for ul in soup.select('ul[class="gl-warp clearfix"]'):
        for li in ul.select('li[class="gl-item"]'):
            item_id = li.get('data-sku')
            # item_spu = li.get('data-spu')
            # item_pid = li.get('data-pid')
            for div in li.select('div[class="p-price"]'):
                price = div.strong.i.text
            for div in li.select('div[class="p-name p-name-type-2"]'):
                item_name = div.a.em.text
                promo_words = div.a.i.text
                item_url = 'https:' + div.a.get('href')
            for div in li.select('div[class="p-shop"]'):
                for a in div.select('a[class="curr-shop"]'):
                    shop_name = a.text
                    shop_url = 'https:' + a.get('href')
            for div in li.select('div[class="p-commit"]'):
                comments = div.a.text
            for div in li.select('div[class="p-icons"]'):
                icons = ''
                for i in div.select('i'):
                    icons += i.text + ' |'
                icons = icons.strip(' |')
            items_info.append({"item_id": item_id, "item_name": item_name, "promo_words": promo_words,
                               "item_url": item_url, "price": price,
                               "comments": comments, "icons": icons,
                               "shop_name": shop_name, "shop_url": shop_url})
    return items_info


def item_details(html, item_name):
    """
    :param html: html doc from browser
    :return: items more detailed information including product name, country of origin, brand, trade name
                                                       weight and so on
    """
    soup = BeautifulSoup(html, 'lxml')

    # 商品详情
    contents = {}
    for ul in soup.select('ul[class*="parameter2"]'):
        for li in ul.select('li'):
            try:
                _ = li.text.split('：')[1]
                contents.update(dict.fromkeys([li.text.split('：')[0]], li.get('title').strip('\xa0')))
            except IndexError:
                contents.update(dict.fromkeys([li.text.split('：')[0]], li.get('title').strip('\xa0')))

    # contents.keys()
    # update lookup dict if need
    lookup = {
              '商品名称': 'Production_Name', '商品编号': 'ArticleNum',
              '主要成分': 'Ingredients',
              '蓝帽标识': 'Blue_hat_logo',
              '商品毛重': 'Gross_weight',
              '国产/进口': 'Domestic_imported',
              '价位': 'Price_band',
              '适用人群': 'Target_user',
              '商品产地': 'Production_Place',
              }

    contents_out = {}
    if contents:
        for k in contents.keys():
            if k in lookup.keys():
                contents_out.update(dict.fromkeys([lookup.pop(k)], contents[k]))

        # if len(contents_out) != len(contents):
        #     print('Please note that len(contents_out) != len(contents) for {}'.format(item_name))
    else:
        print("“{}” 没有商品详情".format(item_name))

    return contents_out


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


def get_comments(item_id, page):
    """
    get comments from one page
    :param seller_id:
    :param item_id:
    :param page:
    :return:
    """
    # 所有在该产品页在卖的产品
    # url = 'https://club.jd.com/comment/productPageComments.action?callback=fetchJSON_comment98vv12723' \
    #       '&productId={}&score=0&sortType=5&page={}&pageSize=10&isShadowSku=0&rid=0&fold=1'.format(item_id, page)
    # 当前产品评论
    url = 'https://club.jd.com/comment/productPageComments.action?callback=fetchJSON_comment98vv12723' \
          '&productId={}&score=0&sortType=5&page={}&pageSize=10&isShadowSku=0&rid=0&fold=1'.format(item_id, page)
    browser.get(url)
    soup = BeautifulSoup(browser.page_source, 'lxml')
    raw_json = soup.find('body').text
    comments_json = None
    try:
        comments_json = fix_JSON(raw_json.strip('fetchJSON_comment98vv12723()\n'))
    except json.decoder.JSONDecodeError as e:
        print('* '*7, e, '* '*7)
    except:
        print('Other errors when parsing JSON！')

    if comments_json:
        return comments_json
    else:
        return None


def flatten_dict2(d):
    """
    Flatten an nested Dict object
    :param d: Dict
    :return: Flattened Dict
    """
    result = dict()
    for k, v in d.items():
        if isinstance(v, dict):
            result.update(flatten_dict2(v))
        elif isinstance(v, list):
            if v:
                result[k] = len(v)
            else:
                result[k] = None
        else:
            result[k] = v
    return result


def to_df(comments):
    """
    convert comments to dataframe form
    :param comments:
    :return:
    """
    columns = ['nickname', 'firstCategory', 'creationTime', 'score', 'userImage', 'userImageUrl', 'title',
               'userLevelId', 'replyCount2', 'content', 'isTop', 'productSales', 'referenceName', 'referenceTypeId',
               'mobileVersion', 'topped', 'isReplyGrade', 'thirdCategory', 'guid', 'productSize', 'viewCount',
               'referenceType', 'anonymousFlag', 'secondCategory', 'referenceId', 'productColor', 'replies',
               'userLevelName', 'userProvince', 'referenceTime', 'recommend', 'afterDays', 'usefulVoteCount',
               'integral', 'referenceImage', 'plusAvailable', 'userLevelColor', 'id', 'days', 'orderId',
               'userClientShow', 'userClient', 'isMobile', 'replyCount', 'userImgFlag', 'uselessVoteCount', 'status'
               ]
    df = pd.DataFrame(columns=columns)

    if comments:
        for comment in comments.get('comments'):
            flattened_dict = flatten_dict2(comment)
            df2 = pd.DataFrame.from_dict(flattened_dict, orient='index').T
            df1 = df
            df = pd.concat([df1, df2])
    else:
        pass
    return df


def get_all_comments(item_id, file):
    """
    get all comments of specific item
    :param search_words:
    :param item_id:
    :return:
    """
    i = 1
    while True:
        comments = get_comments(item_id, 0)
        if comments:
            if comments.get('productCommentSummary') is None:
                print(time.strftime("%Y-%m-%d %X", time.localtime()),
                      ': 你是小蜘蛛。。。(定住你 {} 秒)'.format(random.randrange(50, 60) * i))
                time.sleep(random.randrange(50, 60) * i)
                i += 1
            else:
                break
        else:
            break
    data_tmp = to_df(comments)

    if comments and not data_tmp.empty:
        data = None
        data = pd.concat([data, data_tmp])
        print('productCommentSummary:', comments.get('productCommentSummary'), '\n'
              'maxPage:', comments.get('maxPage'))
        lastPage = int(comments.get('maxPage'))

        for page in range(1, lastPage):
            time.sleep(random.randrange(3, 6))
            # print('page {0:2} of {1:2}'.format(page, lastPage))
            i = 1
            while True:
                comments = get_comments(item_id, page)
                if comments:
                    if comments.get('productCommentSummary') is None:
                        print('page {0:2} of {1:2}'.format(page, lastPage))
                        print(time.strftime("%Y-%m-%d %X", time.localtime()),
                              ': 你是小蜘蛛。。。(定住你 {} 秒)'.format(random.randrange(50, 60) * i))
                        time.sleep(random.randrange(50, 60) * i)
                        i += 1
                    else:
                        break
                else:
                    break
            data_tmp = to_df(comments)
            if data_tmp.empty:
                pass
            else:
                data = pd.concat([data, data_tmp])

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


def items_comments(search_words, speed=1, comments=True, details=True):  # from_cate_pg=1, from_comm_pg=1
    """
    get products detailed information and comments of specific seller and category
    :param search_words:
    :param speed: scraping speed
    :param comments: get comments or not
    :param details: get product details or not
    :return:
    """
    search = browser.find_element_by_css_selector("input[id='key']")
    search.clear()
    # search key words
    search.send_keys(search_words)
    search.send_keys(Keys.ENTER)
    time.sleep(2)

    while True:
        time.sleep(3*speed)
        browser.execute_script("window.scrollTo(0, 4000);")
        time.sleep(5 * speed)
        browser.execute_script("window.scrollTo(0, 6000);")
        browser.implicitly_wait(30)

        main_page = browser.current_window_handle

        html = browser.page_source
        item_list = item_info(html)
        print(time.strftime("%Y-%m-%d %X", time.localtime()),
              '搜索关键词：“{}” 在当前页面共有：{}个产品！'.format(search_words, len(item_list)))

        browser.execute_script("window.open('','_blank');")  # open a blank tab
        handles = browser.window_handles
        for handle in handles:  # 切换到产品详情窗口
            if handle != main_page:
                browser.switch_to_window(handle)
                break

        for item in item_list:
            print('\n', time.strftime("%Y-%m-%d %X", time.localtime()),
                  '正在抓取第{0:2}/{1:2}个产品：{2}'.format(item_list.index(item)+1, len(item_list), item['item_name']))
            item_url = item['item_url']
            # shop_id = item['shop_id']
            browser.get(item_url)  # open url in current tab

            # get product detail info here
            if details:  # True, to collect product details, else only comments are collected
                time.sleep(3*speed)
                browser.implicitly_wait(30)
                browser.execute_script("window.scrollTo(0, 800);")
                time.sleep(3*speed)
                browser.implicitly_wait(30)

                html_prod_details = browser.page_source
                prod_details = item_details(html_prod_details, item['item_name'])
                item.pop('item_url')
                prod_details.update(item)

                columns = ["item_id", "item_name", "promo_words", "price", "comments", "icons",
                           "shop_name", "shop_url",

                           'Blue_hat_logo', 'Target_user', 'Domestic_imported', 'ArticleNum',
                           'Gross_weight', 'Production_Place', 'Ingredients', 'Price_band', 'Production_Name'
                           ]

                to_csv('data\JD_prod_details', prod_details, columns, False)
            else:
                pass

            # get comments by requests
            if comments:  # True, to collect comments, else only product details are collected
                get_all_comments(item['item_id'], "data\JD_prod_comments.csv")
            else:
                pass

        browser.close()  # 关闭产品详情窗口
        browser.switch_to_window(handles[0])  # 切换回主窗口

        try:
            browser.find_element_by_css_selector("a[class='pn-next']").click()
        except exceptions.NoSuchElementException as e:
            print('已经是最后一页了！', e)
            break
        except:
            print('其他错误，跳过这一页产品!')
            break


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# load chrome.exe
browser = webdriver.Chrome(r'C:\Darren\ziqing\Merkle\Python\Web Scraping with Python\chromedriver.exe')
browser.maximize_window()  # 窗口最大化

# login JD
browser.get(r'https://passport.jd.com/new/login.aspx?')
print('Please login through QR code')
time.sleep(30)


# sellers and categories info
wuli = ['大麦若叶 青汁', ]

words = wuli[0]

for words in wuli:

    # details and comments
    items_comments(words, speed=1, comments=True, details=True)

    # details only
    # items_comments(words, speed=1, comments=False, details=True)
    #
    # # comments only
    # items_comments(words, speed=1, comments=True, details=False)


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
browser.quit()   # close browser and chromedriver.exe
# browser.close()  # only close browser
