# @Time    : 07/20/2018 4:00 PM
# @Author  : 李武卿, 数据分析经理
# @File    : Prod_Sales_Comments_on_TMALL_by_selenium.py
# @Software: PyCharm Community Edition
# @license : Copyright(C), 美库尔信息咨询（南京）有限公司
# @Contact : wuli@merkleinc.com、lwq07010328@163.com
# @Mobile  : (+86) 130-7253-6076
# @WeChat  : wx_Darren910220


update_log = """
2018/07/20 Wuqing Li
2018/10/30 Wuqing Li, 修复返回评论数据中时间从时间戳改为字典造成的错误

"""


# 导入 selenium 包, 用作模拟浏览器行为抓取数据
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common import exceptions  # 错误与异常

# 导入 BeautifulSoup 解析 HTML文档
from bs4 import BeautifulSoup

# 导入基础包
import os  # 操作系统相关
import time  # 时间
import random  # 随机数
import re  # 正则表达式

# 导入数据处理，写出相关的包
import pandas as pd  # 处理数据框
import json  # 转化 JSON格式的数据
import csv  # 写入写出 CSV 文件


def item_info(html):
    """
    :param html: html doc from browser
    :return: items information including item_name, item_url, price, sales_month, comments, shop_name, shop_url倒数从左至右
    """
    items_info = []
    soup = BeautifulSoup(html, 'lxml')
    # soup = BeautifulSoup(html, 'html.parser')
    ItemList = soup.find('div', id="J_ItemList")

    item_id, item_name, item_url, price, sales_month = None, None, None, None, None
    comments, shop_name, shop_url, shop_id = None, None, None, None

    for div in ItemList.select('div[class*="product "]'):
        item_id = div.get('data-id')
        for p in div.select('p[class="productPrice"]'):
            # price = p.text.strip('¥ ')
            price = p.em.get('title')
        for p in div.select('p[class="productTitle"]'):
            # item_name = p.a.text.strip()
            item_name = p.a.get('title')
            item_url = 'https:' + p.a.get('href')
        for div2 in div.select('div[class="productShop"]'):
            shop_name = div2.a.text.strip()
            shop_url = 'https:' + div2.a.get('href')
            shop_id = re.search(r'user_number_id=\d+', shop_url).group().split('=')[1]
        for p in div.select('p[class="productStatus"]'):
            spans = p.select('span')
            sales_month = spans[0].em.text
            comments = spans[1].a.text
        items_info.append({"item_id": item_id, "item_name": item_name, "item_url": item_url, "price": price,
                           "sales_month": sales_month, "comments": comments,
                           "shop_name": shop_name, "shop_url": shop_url, 'shop_id': shop_id})
    return items_info


def item_details(html, item_name):
    """
    :param html: html doc from browser
    :return: items more detailed information including product name, country of origin, brand, trade name
                                                       weight and so on
    """
    soup = BeautifulSoup(html, 'lxml')

    # 商品展示区数据
    s_c_j = {}
    for ul in soup.select('ul[class="tm-ind-panel"]'):
        for div in ul.select('div[class="tm-indcon"]'):
            s_c_j.update(dict.fromkeys([div.select('span')[0].text], div.select('span')[1].text))

    s_c_j.update({'CollectCount': soup.select('span[id="J_CollectCount"]')[0].text.strip('（人气）')})

    # 商品详情
    contents = {}
    for ul in soup.select('ul[id="J_AttrUL"]'):
        for li in ul.select('li'):
            try:
                _ = li.text.split(': ')[1]
                contents.update(dict.fromkeys([li.text.split(': ')[0]], li.get('title').strip('\xa0')))
            except IndexError:
                contents.update(dict.fromkeys([li.text.split('：')[0]], li.get('title').strip('\xa0')))

    # contents.keys()
    # update lookup dict if need
    lookup = {
              # '生产许可证编号': 'Production_Permit_No', '产品标准号': 'ArticleNum',
              '厂名': 'Manufacturer', '厂址': 'ManufacturerAddress', '厂家联系方式': 'Manufacturer_contact',
              '配料表': 'Ingredients',
              # '储藏方法': 'Store_method',
              '保质期': 'expiration_date',
              '净含量': 'Net_weight',
              # '包装方式': 'Packing',
              '品牌': 'Brand', '系列': 'Category',
              '适用人群': 'Target_user', '适用性别': 'Target_gender',
              # '粉粉重量': 'Weight',
              '产地': 'Production_Place',
              '省份': 'Province',
              '城市': 'City', '是否含糖': 'sugar_flag'
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
    else:
        return result


def get_comments(shop_id, item_id, page):
    """
    get comments from one page
    :param shop_id:
    :param item_id:
    :param page:
    :return:
    """
    url = 'https://rate.tmall.com/list_detail_rate.htm?itemId={}' \
          '&sellerId={}&order=3&currentPage={}&callback=json'.format(item_id, shop_id, page)
    browser.get(url)
    soup = BeautifulSoup(browser.page_source, 'lxml')
    raw_json = soup.find('body').text

    comments_json = None

    if 'rateDetail' not in raw_json:
        print('该页面没有JSON格式数据，不进行JSON解析！')
        comments_json = {'JSON': None}
    else:
        try:
            comments_json = fix_JSON(raw_json.strip('json()\n'))
            # comments_json = json.loads(raw_json.strip('json()\n'))
        except json.decoder.JSONDecodeError as e:
            print('* '*7, e, '* '*7)
        except:
            print('Other errors when parsing JSON!')

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
        if k in ['tradeEndTime', 'gmtCreateTime']:
            for i in ['tradeEndTime', 'gmtCreateTime']:
                result[i] = v.get('time')
            continue
        elif isinstance(v, dict):
            result.update(flatten_dict(v))
        elif isinstance(v, list):
            if v:
                # # 1. flatten, return value as a new key-value
                # for i in range(len(v)):
                #     result[k+'_'+str(i)] = v[i]
                # 2. flatten, return how many values in the list
                result[k] = len(v)
            else:
                result[k] = None
        else:
            result[k] = v
    return result


def str2time(string):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(int(string) / 1000))


def to_df(comments, words, item_id):
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
            df2['words'] = words
            df2['item_id'] = item_id
            df1 = df
            df = pd.concat([df1, df2], sort=False)
    else:
        pass
    return df


def get_all_comments(words, shop_id, item_id, max_page=100):
    """
    get all comments of specific item
    :param words:
    :param shop_id:
    :param item_id:
    :param max_page:
    :return:
    """
    i = 1
    while True:
        comments = get_comments(shop_id, item_id, 1)
        if comments:
            if comments.get('rateDetail') is None:
                t_rand = random.randrange(30, 60) * i
                print(time.strftime("%Y-%m-%d %X", time.localtime()),
                      ': 你是小蜘蛛。。。(定住你 {} 秒)'.format(t_rand))
                time.sleep(t_rand)
                i += 1
            else:
                break
        else:
            break
    data_tmp = to_df(comments, words, item_id)

    if comments and not data_tmp.empty:
        data = None
        data = pd.concat([data, data_tmp], sort=False)
        print('paginator info:', comments.get('rateDetail').get('paginator'), '\n'
              'rateCount info:', comments.get('rateDetail').get('rateCount'))
        lastPage = int(comments.get('rateDetail').get('paginator').get('lastPage'))
        if lastPage > max_page:
            lastPage = max_page
            print('有更多评论数据，但是根据设定只抓取前 {} 页'.format(max_page))

        print('page {0:2} of {1:2}'.format(1, lastPage))

        for page in range(2, lastPage+1):
            time.sleep(random.randrange(2, 6))
            print('page {0:2} of {1:2}'.format(page, lastPage))
            i = 1
            while True:
                comments = get_comments(shop_id, item_id, page)
                if comments:
                    if comments.get('rateDetail') is None:
                        print('page {0:2} of {1:2}'.format(page, lastPage))
                        t_rand = random.randrange(30, 60) * i
                        print(time.strftime("%Y-%m-%d %X", time.localtime()),
                              ': 你是小蜘蛛。。。(定住你 {} 秒)'.format(t_rand))
                        time.sleep(t_rand)
                        i += 1
                    else:
                        break
                else:
                    break
            data_tmp = to_df(comments, words, item_id)
            if data_tmp.empty:
                pass
            else:
                data = pd.concat([data, data_tmp], sort=False)

        file = "data\TMALL_prod_comments.csv"
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


def items_info_comments(words, speed=1, comments=True, details=True, max_comments_pages=100):
    """
    get products detailed information and comments of specific seller and category
    :param words:
    :param speed: scraping speed
    :param comments: get comments or not
    :param details: get product details or not
    :param max_comments_pages:
    :return:
    """
    try:
        search = browser.find_element_by_css_selector("input[title='请输入搜索文字']")
    except exceptions.NoSuchElementException:
        print('登陆失败！并尝试在未登录状态下抓取，可能出现不能获取数据的错误！')
        browser.get('https://www.tmall.com/')
        time.sleep(30*speed)
        browser.implicitly_wait(30)
        search = browser.find_element_by_css_selector("input[title='请输入搜索文字']")

    search.clear()
    # search key words
    search.send_keys(words)
    search.send_keys(Keys.ENTER)
    time.sleep(2)

    while True:
        time.sleep(3*speed)
        browser.execute_script("window.scrollTo(0, 4000);")
        time.sleep(3 * speed)
        browser.implicitly_wait(30)

        main_page = browser.current_window_handle

        html = browser.page_source
        item_list = item_info(html)
        print(time.strftime("%Y-%m-%d %X", time.localtime()),
              '搜索关键词：“{}” 在当前页面共有：{}个产品！'.format(words, len(item_list)))

        browser.execute_script("window.open('','_blank');")  # open a blank tab
        handles = browser.window_handles
        for handle in handles:  # 切换到产品详情窗口
            if handle != main_page:
                browser.switch_to.window(handle)
                break

        for item in item_list:
            print('\n', time.strftime("%Y-%m-%d %X", time.localtime()),
                  '正在抓取第{0:2}/{1:2}个产品：{2}'.format(item_list.index(item)+1, len(item_list), item['item_name']))
            item_url = item['item_url']
            shop_id = item['shop_id']
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

                columns = ["item_id", 'shop_name', 'item_name', 'sales_month', 'shop_url', 'shop_id', 'price', 'comments',
                           '月销量', '累计评价', '送天猫积分', 'CollectCount',

                           # 'Production_Place', 'ManufacturerAddress', 'expiration_date', 'Category', 'Province',
                           # 'Manufacturer_contact', 'Brand', 'Manufacturer'
                           'Production_Place', 'City', 'Manufacturer', 'Brand', 'expiration_date', 'Province',
                           'ManufacturerAddress', 'Target_gender', 'Category', 'Ingredients', 'Manufacturer_contact',
                           'sugar_flag', 'Target_user', 'Net_weight'

                           # 'Production_Place', 'Weight', 'Packing', 'City', 'Store_method', 'Brand', 'Province',
                           # 'expiration_date', 'ArticleNum', 'ManufacturerAddress', 'Production_Permit_No', 'Category',
                           # 'Ingredients', 'Manufacturer_contact', 'sugar_flag', 'Manufacturer', 'Net_weight',
                           ]

                to_csv('data\TMALL_prod_details', prod_details, columns, False)
            else:
                pass

            # get comments by requests
            if comments:  # True, to collect comments, else only product details are collected
                get_all_comments(words, shop_id, item['item_id'], max_comments_pages)
            else:
                pass

        browser.close()  # 关闭产品详情窗口
        browser.switch_to.window(handles[0])  # 切换回主窗口

        try:
            browser.find_element_by_css_selector("a[class='ui-page-next']").click()
        except exceptions.NoSuchElementException as e:
            print('已经是最后一页了！', e)
            break
        except:
            print('其他错误，跳过这一页产品!')
            break


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
if __name__ == '__main__':
    # load chrome.exe
    browser = webdriver.Chrome(r'C:\Darren\ziqing\Merkle\Python\Web Scraping with Python\chromedriver.exe')
    browser.maximize_window()  # 窗口最大化

    # login TMALL
    browser.get('https://login.tmall.com/')  # 天猫
    print('Please login through QR code')
    time.sleep(60)

    # sellers and categories info
    wuli = ['大麦若叶 青汁', ]

    # wuli = ['雅培', '惠氏', '美素佳儿']
    # wuli = ['爱他美', '诺优能', '贝因美', '美赞臣']
    # wuli = [i + ' 婴儿奶粉' for i in wuli]

    for words in wuli:
        # details and comments
        items_info_comments(words, speed=1, comments=True, details=True, max_comments_pages=3)

        # details only
        # items_info_comments(words, speed=1, comments=False, details=True)

        # # comments only
        # items_info_comments(words, speed=1, comments=True, details=False, max_comments_pages=3)

    browser.quit()   # close browser and chromedriver.exe
    # browser.close()  # only close browser
