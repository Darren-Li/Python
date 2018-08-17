# @Time    : 12/27/2017 4:00 PM
# @Author  : 李武卿, 主管数据分析师
# @File    : RoyalCanin-selenium v2.py
# @Software: PyCharm Community Edition
# @license : Copyright(C), 美库尔信息咨询（南京）有限公司
# @Contact : wuli@merkleinc.com
# @Mobile  : (+86) 130-7253-6076

# update log
# 2018-01-05 7:40 PM
# 2018-03-31 9:17 PM fix JSON


# selenium to Simulate browser behavior
from selenium import webdriver
from selenium.common import exceptions

# BeautifulSoup to Parse web pages
from bs4 import BeautifulSoup

# operation and time modules
import os
import time
import random

# data processing and data storage
import pandas as pd
import json
import csv


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# load chrome.exe
browser = webdriver.Chrome(r'C:\Darren\ziqing\Merkle\Python\Web Scraping with Python\chromedriver.exe')
browser.maximize_window()  # 窗口最大化

# login TMALL
browser.get(r'https://login.tmall.com/')  # 天猫
print('Please login through QR code')
time.sleep(30)


def item_info(html):
    """
    :param html: html doc from browser
    :return: items information including item_id, item_name, price, coupon, total_sale, 倒数从左至右
    """
    i, items_info = 1, []
    soup = BeautifulSoup(html, 'lxml')
    pagination = soup.find('div', class_="pagination")

    for item4line1s in pagination.find_previous_siblings():
        for dl in item4line1s.select('dl[class="item "]'):
            item_id = dl.get('data-id')
            for detail in dl.select('dd[class="detail"]'):
                item_name = detail.a.text.strip()
                item_url = 'https:' + detail.a.get('href')
                for cprice in dl.select('div[class="cprice-area"]'):
                    price = cprice.text.strip('¥ ')
                for coupon in dl.select('div[class="coupon-area"]'):
                    coupon = coupon.text.strip()
                for sale in dl.select('div[class="sale-area"]'):
                    total_sale = sale.text.strip('总销量： ')
            items_info.append({"item_id": item_id, "item_name": item_name, "item_url": item_url,
                               "price": price, "coupon": coupon, "total_sale": total_sale})
            i += 1
        for dl in item4line1s.select('dl[class="item last"]'):
            item_id = dl.get('data-id')
            for detail in dl.select('dd[class="detail"]'):
                item_name = detail.a.text.strip()
                item_url = 'https:' + detail.a.get('href')
                for cprice in dl.select('div[class="cprice-area"]'):
                    price = cprice.text.strip('¥ ')
                for coupon in dl.select('div[class="coupon-area"]'):
                    coupon = coupon.text.strip()
                for sale in dl.select('div[class="sale-area"]'):
                    total_sale = sale.text.strip('总销量： ')
            items_info.append({"item_id": item_id, "item_name": item_name, "item_url": item_url,
                               "price": price, "coupon": coupon, "total_sale": total_sale})
            i += 1

    return items_info


def item_details(html):
    """
    :param html: html doc from browser
    :return: items more detailed information including product name, country of origin, brand, trade name
                                                       weight and so on
    """
    soup = BeautifulSoup(html, 'lxml')

    s_c_j = {}
    for ul in soup.select('ul[class="tm-ind-panel"]'):
        for div in ul.select('div[class="tm-indcon"]'):
            s_c_j.update(dict.fromkeys([div.select('span')[0].text], div.select('span')[1].text))

    s_c_j.update({'CollectCount': soup.select('span[id="J_CollectCount"]')[0].text.strip('（人气）')})

    for div in soup.select('div[id="J_AttrList"]'):
        brand_name = div.select('div[id="J_BrandAttr"]')[0].text.lstrip('品牌名称：')
        for ul in div.select('ul[id="J_AttrUL"]'):
            contents = {}
            for li in ul.select('li'):
                try:
                    _ = li.text.split(': ')[1]
                    contents.update(dict.fromkeys([li.text.split(': ')[0]], li.get('title').strip('\xa0')))
                except IndexError:
                    contents.update(dict.fromkeys([li.text.split('：')[0]], li.get('title').strip('\xa0')))

    # contents.keys()
    # update lookup dict if need
    lookup = {'食品口味': 'Tastes', '宠物体型': 'BodyType', '适用阶段': 'ApplicablePhase', '品牌': 'Brand',
              '分类': 'Classification', '狗狗品种': 'Breed', '原产地': 'Origin', '货号': 'ArticleNum',
              '产品名称': 'ProductName', '重量(g)': 'Weight', '适用对象': 'ApplicableObject',
              '生产厂家名称': 'Manufacturer', '品名': 'TradeName', '生产厂家地址': 'ManufacturerAddress',
              '毛重': 'GrossWeight', '配方/口味/处方': 'RecipeTastePrescription', '包装体积': 'PackagingVolume'
              }

    contents_out = {}
    for k in contents.keys():
        if k in lookup.keys():
            contents_out.update(dict.fromkeys([lookup.pop(k)], contents[k]))

    if len(contents_out) != len(contents):
        print('Please note that len(contents_out) != len(contents) for {}'.format(contents_out['ProductName']))

    contents_out.update({'brand_name': brand_name})
    contents_out.update(s_c_j)

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


def get_comments(seller_id, item_id, page):
    """
    get comments from one page
    :param seller_id:
    :param item_id:
    :param page:
    :return:
    """
    url = 'https://rate.tmall.com/list_detail_rate.htm?itemId={}' \
          '&sellerId={}&order=3&currentPage={}&callback=json'.format(item_id, seller_id, page)
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
                for i in range(len(v)):
                    result[k+'_'+str(i)] = v[i]
            else:
                result[k] = None
        else:
            result[k] = v
    return result


def str2time(string):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(int(string) / 1000))


def to_df(comments, brand, item_id):
    """
    convert comments to dataframe form
    :param comments:
    :return:
    """
    df = pd.DataFrame(
        columns=['aliMallSeller', 'anony', 'appendComment', 'attributes', 'attributesMap', 'aucNumId',
                 'auctionPicUrl', 'auctionPrice', 'auctionSku', 'auctionTitle', 'buyCount',
                 'carServiceLocation', 'cmsSource', 'commentId', 'commentTime', 'content', 'days',
                 'displayRatePic', 'displayRateSum', 'displayUserLink', 'displayUserNick',
                 'displayUserNumId', 'displayUserRateLink', 'dsr', 'fromMall', 'fromMemory',
                 'gmtCreateTime', 'goldUser', 'headExtraPic', 'id', 'memberIcon',
                 'pics', 'picsSmall', 'pics_0', 'pics_1', 'pics_2', 'pics_3', 'pics_4',
                 'position', 'rateContent', 'rateDate', 'reply', 'sellerId', 'serviceRateContent',
                 'structuredRateList', 'tamllSweetLevel', 'tmallSweetPic', 'tradeEndTime',
                 'tradeId', 'useful', 'userIdEncryption', 'userInfo', 'userVipLevel', 'userVipPic']
        )
    # df = pd.DataFrame()
    if comments:
        for comment in comments.get('rateDetail').get('rateList'):
            flattened_dict = flatten_dict(comment)
            df2 = pd.DataFrame.from_dict(flattened_dict, orient='index').T
            df2['gmtCreateTime_str'] = df2['gmtCreateTime'].apply(str2time)
            df2['tradeEndTime_str'] = df2['tradeEndTime'].apply(str2time)
            df2['brand'] = brand
            df2['item_id'] = item_id
            df1 = df
            df = pd.concat([df1, df2])
    else:
        pass
    return df


def get_all_comments(brand, seller_id, item_id):
    """
    get all comments of specific item
    :param brand:
    :param seller_id:
    :param item_id:
    :return:
    """
    i = 1
    while True:
        comments = get_comments(seller_id, item_id, 1)
        if comments:
            if comments.get('rateDetail') is None:
                print(time.strftime("%Y-%m-%d %X", time.localtime()),
                      ': 你是小蜘蛛。。。(定住你 {} 秒)'.format(random.randrange(50, 60) * i))
                time.sleep(random.randrange(50, 60) * i)
                i += 1
            else:
                break
        else:
            break
    data_tmp = to_df(comments, brand, item_id)

    if comments and not data_tmp.empty:
        data = None
        data = pd.concat([data, data_tmp])
        print('paginator info:', comments.get('rateDetail').get('paginator'), '\n'
              'rateCount info:', comments.get('rateDetail').get('rateCount'))
        lastPage = int(comments.get('rateDetail').get('paginator').get('lastPage'))
        print('page {0:2} of {1:2}'.format(1, lastPage))

        for page in range(2, lastPage+1):
            time.sleep(random.randrange(3, 6))
            print('page {0:2} of {1:2}'.format(page, lastPage))
            i = 1
            while True:
                comments = get_comments(seller_id, item_id, page)
                if comments:
                    if comments.get('rateDetail') is None:
                        print(time.strftime("%Y-%m-%d %X", time.localtime()),
                              ': 你是小蜘蛛。。。(定住你 {} 秒)'.format(random.randrange(50, 60) * i))
                        time.sleep(random.randrange(50, 60) * i)
                        i += 1
                    else:
                        break
                else:
                    break
            data_tmp = to_df(comments, brand, item_id)
            if data_tmp.empty:
                pass
            else:
                data = pd.concat([data, data_tmp])

        file = "..\data\Dog_foods_comments_TMALL.csv"
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


def items_comments(seller_id, brand, category_url, speed=1, comments=True, details=True):  # from_cate_pg=1, from_comm_pg=1
    """
    get products detailed information and comments of specific seller and category
    :param seller_id:
    :param brand:
    :param category_url:
    :param speed: scraping speed
    :param comments: get comments or not
    :param details: get product details or not
    :return:
    """
    browser.get(category_url)  # go to category page
    # category_page = 1

    while True:
        # category_page += 1
        time.sleep(3*speed)
        browser.execute_script("window.scrollTo(0, 5000);")
        browser.implicitly_wait(30)

        main_page = browser.current_window_handle

        html = browser.page_source
        item_list = item_info(html)
        print(time.strftime("%Y-%m-%d %X", time.localtime()),
              '{} 在当前页面共有：{}个产品！'.format(brand, len(item_list)))

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
            browser.get(item_url)  # open url in current tab

            # get product detail info here
            if details:  # True, to collect product details, else only comments are collected
                time.sleep(3*speed)
                browser.implicitly_wait(30)
                browser.execute_script("window.scrollTo(0, 800);")
                time.sleep(3*speed)
                browser.implicitly_wait(30)

                html_prod_details = browser.page_source
                prod_details = item_details(html_prod_details)
                item.pop('item_url')
                prod_details.update(item)

                columns = ['item_id', 'item_name', 'price', 'coupon', 'total_sale',
                           '月销量', '累计评价', '送天猫积分', 'CollectCount',
                           'Tastes', 'BodyType', 'ApplicablePhase', 'Brand', 'Classification', 'Breed', 'Manufacturer',
                           'ArticleNum', 'ProductName', 'Weight', 'GrossWeight', 'Origin', 'TradeName',
                           'ManufacturerAddress', 'ApplicableObject', 'brand_name', 'RecipeTastePrescription',
                           'PackagingVolume']

                to_csv('..\data\prod_details', prod_details, columns, False)
            else:
                pass

            # get comments by requests
            if comments:  # True, to collect comments, else only product details are collected
                get_all_comments(brand, seller_id, item['item_id'])
            else:
                pass

        browser.close()  # 关闭产品详情窗口
        browser.switch_to_window(handles[0])  # 切换回主窗口

        try:
            browser.find_element_by_css_selector("a[class='J_SearchAsync next']").click()
        except exceptions.NoSuchElementException as e:
            print('已经是最后一页了！', e)
            break
        except:
            print('其他错误，跳过这一页产品!')
            break


# sellers and categories info
wuli = [
    {'brand': 'royalcanin', 'seller_id': '1728261286',  'category_id': '753489692'},   # 皇家
    {'brand': 'marspet',    'seller_id': '21979035550', 'category_id': '666068251'},   # 宝路
    {'brand': 'biruiji',    'seller_id': '1994001584',  'category_id': '909692148'},   # 比瑞吉
    {'brand': 'fish4dogs',  'seller_id': '2612420942',  'category_id': '1114678599'},  # 海洋之星
]

# i = wuli[2]
for i in wuli:
    category_url = 'https://{}.tmall.com/category-{}.htm'.format(i['brand'], i['category_id'])

    # details and comments
    items_comments(i['seller_id'], i['brand'], category_url, speed=1, comments=True, details=True)

    # details only
    # items_comments(i['seller_id'], i['brand'], category_url, speed=1, comments=False, details=True)

    # comments only
    # items_comments(i['seller_id'], i['brand'], category_url, speed=1, comments=True, details=False)


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
browser.quit()   # close browser and chromedriver.exe
# browser.close()  # only close browser
