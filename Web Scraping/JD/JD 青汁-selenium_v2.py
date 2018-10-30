# @Time    : 07/23/2018 4:00 PM
# @File    : Prod_Sales_Comments_on_JD_by_selenium.py
# @Software: PyCharm Community Edition
# @WeChat  : wx_Darren910220


update_log = """
2018/07/23 Wuqing Li
2018/10/29 Wuqing Li, 添加注释，解决评论页面无法访问导致无JSON数据时fix_JSON函数迭代锁死问题

"""

Notes = """
注意chromedriver.exe 和 Chrome的版本
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

# 导入数据处理，写出相关的包
import pandas as pd  # 处理数据框
import json  # 转化 JSON格式的数据
import csv  # 写入写出 CSV 文件


def create_dir(directory):
    """
    在当前路径下创建一个文件夹
    :param directory: 文件夹名称
    :return: None
    """
    if not os.path.exists(directory):
        print('创建文件夹：{}'.format(directory), '文件所在路径为：{}'.format(os.getcwd()), sep='\n')
        os.mkdir(directory)
    else:
        print('文件夹：{} 已经存在!'.format(directory))


def item_info(html):
    """
    获取搜索结果页面的产品信息
    :param html: html doc
    :return: items information
    """
    items_info = []
    soup = BeautifulSoup(html, 'lxml')

    # 将要抓取信息设置为None，以防某些产品不存在某些信息，在写出时出错
    item_id, item_name, promo_words, item_url = None, None, None, None
    price, comments, icons, shop_name, shop_url = None, None, None, None, None

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
            # 将每一个产品的信息以字典结构保存在列表items_info中
            items_info.append({"item_id": item_id, "item_name": item_name, "promo_words": promo_words,
                               "item_url": item_url, "price": price,
                               "comments": comments, "icons": icons,
                               "shop_name": shop_name, "shop_url": shop_url})
    return items_info


def item_details(html, item_name):
    """
    获取产品页面的产品详细信息
    :param html: html doc
    :return: more detailed information for a item including product name, country of origin, brand, trade name,
    weight and so on
    """
    soup = BeautifulSoup(html, 'lxml')
    # soup = BeautifulSoup(html, 'html.parser')  # 更换解析器，上课时lxml解析某些网页HTML文档解析出错，没有正常解析，拿到产品详情

    # 商品详情
    contents = {}
    for ul in soup.select('ul[class*="parameter2"]'):
        for li in ul.select('li'):
            try:
                _ = li.text.split('：')[1]
                contents.update(dict.fromkeys([li.text.split('：')[0]], li.get('title').strip('\xa0')))
            except IndexError:
                contents.update(dict.fromkeys([li.text.split('：')[0]], li.get('title').strip('\xa0')))

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

    # 更改产品详情键值为英文
    contents_out = {}
    if contents:
        for k in contents.keys():
            if k in lookup.keys():
                contents_out.update(dict.fromkeys([lookup.pop(k)], contents[k]))
    else:
        print("“{}” 没有商品详情".format(item_name))

    return contents_out


def fix_JSON(json_message=None):
    """
    debug 网页返回的数据不能被直接转化为JSON格式的错误，注意该函数使用迭代，如果传入数据非JSON格式会导致死循环，程序终止！！！
    :param json_message: JSON格式数据
    :return: 返回字典结构的数据
    """
    result = None  # 初始化输出结构为None，以防JSON格式转化格外出错
    try:
        result = json.loads(json_message)
    except json.decoder.JSONDecodeError as e:
        # Find the offending character index
        idx_to_replace = int(str(e).split(' ')[-1].replace(')', ''))
        # Remove the offending character:
        json_message = list(json_message)
        json_message[idx_to_replace] = ' '
        new_message = ''.join(json_message)
        return fix_JSON(json_message=new_message)
    else:
        return result


def get_comments(item_id, page):
    """
    获取评论信息
    :param item_id: 产品ID
    :param page: 评论所在页数
    :return: 评论数据
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

    # 排除“无法访问此网站”的错误
    if 'productCommentSummary' not in raw_json:
        print('该页面没有JSON格式数据，不进行JSON解析！')
        comments_json = {'JSON': None}
    else:
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
    convert comments to DataFrame
    :param comments: 评论信息
    :return: df
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
            df = pd.concat([df1, df2], sort=False)
    else:
        pass
    return df


def get_all_comments(item_id, file, max_page=100):
    """
    get all comments of specific item
    :param item_id: 产品ID
    :param max_page: 需要抓取的最大评论页数
    :param file: 写出的文件名
    :return:
    """
    # 获取第一页评论
    i = 1
    while True:
        comments = get_comments(item_id, 0)
        if comments:
            if comments.get('productCommentSummary') is None:
                t_rand = random.randrange(30, 60) * i
                print(time.strftime("%Y-%m-%d %X", time.localtime()),
                      ': 你是小蜘蛛。。。(定住你 {} 秒)'.format(t_rand))
                time.sleep(t_rand)
                i += 1
            else:
                break
        else:
            break
    data_tmp = to_df(comments)

    # 获取其余页评论
    if comments and not data_tmp.empty:
        data = None
        data = pd.concat([data, data_tmp], sort=False)
        print('productCommentSummary:', comments.get('productCommentSummary'), '\n'
              'maxPage:', comments.get('maxPage'))
        lastPage = int(comments.get('maxPage'))

        if lastPage > max_page:
            lastPage = max_page
            print('有更多评论数据，但是根据设定只抓取前 {} 页'.format(max_page))

        print('page {0:2} of {1:2}'.format(1, lastPage))

        for page in range(1, lastPage+1):
            time.sleep(random.randrange(1, 5))
            print('page {0:2} of {1:2}'.format(page, lastPage))
            i = 1
            while True:
                comments = get_comments(item_id, page)
                if comments:
                    if comments.get('productCommentSummary') is None:
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
            data_tmp = to_df(comments)
            if data_tmp.empty:
                pass
            else:
                data = pd.concat([data, data_tmp], sort=False)

            # 写出评论
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


def items_info_comments(search_words, speed=1, comments=True, details=True, max_comments_pages=100):
    """
    get products detailed information and comments of specific seller and category
    :param search_words:
    :param speed: scraping speed
    :param comments: get comments or not
    :param max_comments_pages: max page number of comments you want
    :param details: get product details or not
    :return:
    """
    # 找到搜索框，并进行搜索
    try:
        search = browser.find_element_by_css_selector("input[id='key']")
    except exceptions.NoSuchElementException:
        print('登陆失败！并尝试在未登录状态下抓取，可能出现不能获取数据的错误！')
        browser.get('https://www.jd.com/')
        time.sleep(30*speed)
        browser.implicitly_wait(30)
        search = browser.find_element_by_css_selector("input[id='key']")

    search.clear()
    # search key words
    search.send_keys(search_words)
    search.send_keys(Keys.ENTER)
    time.sleep(3)

    while True:
        time.sleep(3*speed)
        browser.execute_script("window.scrollTo(0, 4000);")  # 滑动窗口，保证页面加载完成
        time.sleep(5*speed)
        browser.execute_script("window.scrollTo(0, 6000);")
        time.sleep(7 * speed)
        browser.implicitly_wait(30)

        main_page = browser.current_window_handle

        html = browser.page_source
        item_list = item_info(html)
        print(time.strftime("%Y-%m-%d %X", time.localtime()),
              '搜索关键词：“{}” 在当前页面共有：{}个产品！'.format(search_words, len(item_list)))

        browser.execute_script("window.open('','_blank');")  # open a blank tab
        handles = browser.window_handles  # 浏览器窗口handles
        for handle in handles:  # 切换到产品详情窗口
            if handle != main_page:
                browser.switch_to.window(handle)
                break

        for item in item_list:  # 遍历每一个产品，拿到其相关信息
            print('\n', time.strftime("%Y-%m-%d %X", time.localtime()),
                  '正在抓取第{0:2}/{1:2}个产品：{2}'.format(item_list.index(item)+1, len(item_list), item['item_name']))
            item_url = item['item_url']
            browser.get(item_url)  # open url in current tab

            # get product details here
            if details:  # True, to collect product details
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

            # get all comments
            if comments:  # True, to collect comments
                get_all_comments(item['item_id'], "data\JD_prod_comments.csv", max_comments_pages)
            else:
                pass

        browser.close()  # 关闭产品详情窗口
        browser.switch_to.window(handles[0])  # 切换回主窗口

        try:
            browser.find_element_by_css_selector("a[class='pn-next']").click()
        except exceptions.NoSuchElementException as e:
            print('已经是最后一页了！', e)
            break
        except:
            print('其他错误，跳过这一页产品!')
            break


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
if __name__ == "__main__":
    # load chrome.exe
    browser = webdriver.Chrome(r'C:\Darren\ziqing\Merkle\Python\Web Scraping with Python\chromedriver.exe')  # 修改路径
    browser.maximize_window()  # 窗口最大化

    # login JD
    browser.get(r'https://passport.jd.com/new/login.aspx?')
    print('Please login through QR code')
    time.sleep(60)

    # 创建文件夹
    create_dir('data')

    # sellers and categories info
    # wuli = ['大麦若叶 青汁']
    # wuli = ['美素佳儿']

    # wuli = ['雅培', '惠氏', '美素佳儿']
    wuli = ['爱他美', '诺优能', '贝因美', '美赞臣']
    wuli = [i + ' 婴儿奶粉' for i in wuli]

    for words in wuli:
        print('正在抓取关键字 {} 相关的产品信息'.format(words))
        # details and comments, 修改max_comments_pages获取相应页数的评论，最大和默认评论页数为100（网页只能最多返回这么多）

        items_info_comments(words, speed=1, comments=True, details=True, max_comments_pages=30)
        # items_info_comments(words, speed=1, comments=True, details=True)  # 获取全部数据（详细产品信息，全部评论）

        # details only
        # items_info_comments(words, speed=1, comments=False, details=True)

        # # comments only
        # items_info_comments(words, speed=1, comments=True, details=False, max_comments_pages=3)

    browser.quit()   # close browser and chromedriver.exe
    # browser.close()  # only close browser
