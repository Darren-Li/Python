# @Time    : 10/30/2018 7:22 PM
# @Author  : 李武卿, 数据分析经理
# @File    : weibo_article_search_by_selenium.py
# @Software: PyCharm
# @license : Copyright(C), 美库尔信息咨询（南京）有限公司
# @Contact : wuli@merkleinc.com(公司)，lwq07010328@163.com(个人)
# @Wechat  : wx_Darren910220

"""
获取新浪微博搜索上指定关键词相关的文章内容
"""


from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time
import datetime
import re
import sqlite3


def content_snippets(keyword, contents, text_len=50, max_snippet_num=5):
    """
    获取段落中关键词所在位置的前后指定长度的片段，返回完整句子。
    :param keyword: 搜索关键词
    :param contents: 清洗过的正文内容
    :param text_len: 关键词前后字长上限
    :param max_snippet_num: 最大片段数
    :return: 关键词在正文中的片段列表
    """
    contents = re.sub(r'。?\s?\n+', '。', contents)  # 清洗，去除换行符
    contents = re.sub(r'\s', '', contents)  # 清洗，去除非打印字符

    content = []
    target_contents = re.finditer(keyword, contents, re.I)  # 查找关键词位置

    u, u0 = 0, 0
    for i in target_contents:
        l0 = i.span()[0]
        if l0 - u < 0:
            pass
        else:
            u0 = i.span()[1]
            l = max(l0 - text_len, 0, u)
            u = u0 + text_len

            # 修正片段上下限位置，获取完整句子。表示一段话结束的标点符号：句号，感叹号，问号，省略号
            p_o = list(re.finditer('。|？|！|……', contents[:l][::-1]))
            if p_o:
                l -= p_o[0].span()[1]-1

            n_o = list(re.finditer('。|？|！|……', contents[u:]))
            if n_o:
                u += n_o[0].span()[1]

            content.append(contents[l:u])

    if len(content) < max_snippet_num:  # 补全列表
        content.extend([None] * (max_snippet_num - len(content)))
        return content
    else:
        return content[:max_snippet_num]


def article_date_transfer(time_str):
    """
    将网页不规范的时间格式转换为 YYYY-MM-DD 时间格式
    :param time_str: 网页发布时间
    :return: YYYY-MM-DD格式的网页时间
    """
    time_str = time_str.strip()
    now = datetime.datetime.today()
    if '分钟前' in time_str:
        minute = int(time_str[:-3])
        return (now - datetime.timedelta(minutes=minute)).strftime('%Y-%m-%d %H:%M')
    elif '今天' in time_str:
        hours = int(time_str[2:4])
        minutes = int(time_str[5:])
        return (now - datetime.timedelta(hours=hours) - datetime.timedelta(minutes=minutes)).strftime('%Y-%m-%d %H:%M')
    elif '年' in time_str:
        return datetime.datetime.strptime(time_str, '%Y年%m月%d日 %H:%M').strftime('%Y-%m-%d %H:%M')
    else:
        time_str = str(now.year) + '年' + time_str
        return datetime.datetime.strptime(time_str, '%Y年%m月%d日 %H:%M').strftime('%Y-%m-%d %H:%M')


def refresh_page():
    """
    刷新页面，避免网速原因正常查询页面无结果返回漏掉数据
    """
    while True:
        i, j = 0, 0

        try:
            browser.find_element_by_css_selector('div[class="card card-no-result s-pt20b40"]')  # 查询不到结果
        except NoSuchElementException:
            pass
        else:
            i = 1

        try:
            browser.find_element_by_xpath('//a[@class="next"]')  # 下一页
        except NoSuchElementException:
            pass
        else:
            j = 1

        if i and j:
            print('有下一页,但是没有查询到结果，即网页假死，等待5秒！再次刷新')
            browser.refresh()
            time.sleep(5)
        else:
            break


def weibo_search(keyword, keyword_search, start_dt, end_dt):
    """
    获取新闻信息
    :param keyword: 关键词
    :param keyword_search: 搜索关键词
    :param start_dt: 开始时间
    :param end_dt: 结束时间
    :return:
    """
    url = 'https://s.weibo.com/article?q={}&Refer=SListRelpage_box'.format(keyword_search)
    page = 1
    browser.get(url)

    old_article_num = 0

    while True:
        refresh_page()  # 刷新页面

        print('正在抓取第 {} 页的文章'.format(page))
        # 1. 获取新闻列表信息
        article_info = []
        title, article_url, abstract, source, share, like, publish_time = None, None, None, None, None, None, None

        contents = browser.find_element_by_xpath("//div[@id='pl_feedlist_index']")
        divs = contents.find_elements_by_xpath(".//div[@class='card-wrap']")
        for div in divs:
            try:
                title = div.find_element_by_xpath('.//h3/a').text
                article_url = div.find_element_by_xpath('.//h3/a').get_attribute('href')
                abstract = div.find_element_by_xpath('.//p[@class="txt"]').text
                source = div.find_element_by_xpath('.//div[@class="act"]/div/span[1]').text.lstrip('@')
                # share = div.find_element_by_xpath('.//ul[@class="s-fr"]/li[1]').text.strip('分享 ')
                # like = div.find_element_by_xpath('.//ul[@class="s-fr"]/li[2]').text
                publish_time_raw = div.find_element_by_xpath('.//div[@class="act"]/div/span[2]').text
                publish_time = article_date_transfer(publish_time_raw)

                article_info.append([keyword, '新浪微博搜索', title, source, publish_time, article_url, abstract])
            except NoSuchElementException:
                pass

        # 打开新窗口并交接 webdriver handle
        main_handle = browser.current_window_handle
        browser.execute_script("window.open('','_blank');")
        time.sleep(2)
        handles = browser.window_handles
        for handle in handles:
            if handle != main_handle:
                browser.switch_to.window(handle)

        print('该页共 {} 条新闻'.format(len(article_info)))
        valid_article_num = 0

        # 2. 获取新闻内容
        for article in article_info:
            if not article[-3]:
                pass
            elif article[-3] <= start_dt:  # 记录指定开始时间之前的新闻条数
                old_article_num += 1
            elif start_dt <= article[-3] < end_dt:  # 过滤不在指定时间段内的新闻
                valid_article_num += 1
                try:
                    browser.get(article[-2])
                    time.sleep(5)

                    try:
                        content_str = browser.find_element_by_xpath("//div[@class='WB_editor_iframe']").text
                        # reads = browser.find_element_by_xpath("//span[@class='num']").text.strip('阅读数：')
                    except NoSuchElementException:
                        # content_str = browser.find_element_by_tag_name("body").text
                        content_str = ''
                        ps = browser.find_elements_by_tag_name('p')
                        for p in ps:
                            content_str += p.text

                    main_content = content_snippets(keyword, content_str)  # 获取新闻内容片段
                    article.extend(main_content)  # 添加新闻内容片段

                    # 写出数据
                    cursor.execute("insert into weibo_news (keyword, site, title, source, publish_time, article_url,"
                                   "abstract, contents1, contents2, contents3, contents4, contents5) "
                                   "values (?,?,?,?,?,?,?,?,?,?,?,?)", article)
                    conn.commit()
                except NoSuchElementException:
                    valid_article_num -= 1
                    pass

        print('该页满足时间条件并可抓取的有 {} 条新闻'.format(valid_article_num))

        browser.close()
        browser.switch_to.window(handles[0])

        # 新闻不是严格按时间排序的，为避免爬虫过多停留在指定开始时间之前的新闻上。
        # 如果有超过5篇新闻在指定开时间之前，则退出该关键词搜索。
        if old_article_num > 5:
            print('过期新闻数过去，提前跳出')
            break

        # 跳转至下一页，没有下一页则跳出循环
        try:
            browser.find_element_by_xpath('//a[@class="next"]').click()
            page += 1
            time.sleep(10)
        except NoSuchElementException:
            break


if __name__ == '__main__':
    # 创建，连接数据库
    conn = sqlite3.connect('weibo.db')
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS weibo_news")
    cursor.execute('CREATE TABLE weibo_news (keyword, site, title, source, publish_time, article_url, abstract,'
                   'contents1, contents2, contents3, contents4, contents5);')
    # 关键词列表
    keywords = ['雅培', '惠氏', '美素佳儿', '爱他美', '诺优能', '贝因美', '美赞臣']
    start_dt, end_dt = '2018-07-31', '2018-10-31'  # 新闻起止时间 左闭右开

    browser = webdriver.Chrome(r'C:\Darren\ziqing\Merkle\Python\Web Scraping with Python\chromedriver.exe')

    # 登录微博
    try:
        browser.get('https://weibo.com/')
        username = WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.ID, "loginname")))
        username.clear()
        username.send_keys('微博账户')
        password = browser.find_element_by_css_selector('input[type="password"]')
        password.clear()
        password.send_keys('微博账户密码')
        submit = browser.find_element_by_css_selector('a[node-type="submitBtn"]')
        submit.click()
    except TimeoutException:
        print('登陆失败')
    time.sleep(30)

    for keyword in keywords:
        # keyword_search = keyword + ' 婴儿奶粉'
        keyword_search = keyword + ''
        print('\n正在抓取 “{}” ({}/{}) 的相关文章，搜索的关键词为：“{}”'
              .format(keyword, keywords.index(keyword)+1, len(keywords), keyword_search))

        weibo_search(keyword, keyword_search, start_dt, end_dt)
        time.sleep(30)

    conn.close()  # 关闭数据库连接
    browser.close()  # 退出 webdriver
