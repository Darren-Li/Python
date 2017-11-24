import requests
from bs4 import BeautifulSoup
import csv
import re
import datetime
import json
import ast
import os


# 获取网页并解析 # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# 发起请求访问网页并解析返回内容，最终返回解析过的网页内容
def get_soup(url):
    resp = requests.get(url)
    # 解决乱码问题 
    if resp.encoding == 'ISO-8859-1':
        encodings = requests.utils.get_encodings_from_content(resp.text)
        if encodings:
            encoding = encodings[0]
        else:
            encoding = resp.apparent_encoding
    else:
        encoding = resp.apparent_encoding
    encode_content = resp.content.decode(encoding, 'replace').encode('utf-8', 'replace')
    # 解析网页
    soup = BeautifulSoup(encode_content, 'lxml')
    # print(soup.prettify())
    return soup


# 获取当前总流量排名前xx的财经博客主并拿到他们的博文链接 # # # # # # # # # # # # # # # # # # # # # # # # # #
# 获取当前总流量排名前xx的财经博客主
def top100_authors(url):
    resp = requests.get(url)
    soup = BeautifulSoup(resp.content, 'lxml', from_encoding="gbk")
    # print(soup.prettify())

    category = '总流量排行-财经'
    data = []

    for t in soup.select('th[align="right"]'):
        updateTime = t.get_text().strip('最后更新时间：')

    for body in soup.select('table[class="tbclass"]'):
        trs = body.select('tr')
        trs.remove(trs[0])
        for tr in trs:
            seq      = tr.select('td')[0].get_text()
            author   = tr.select('td')[1].get_text()
            authorHP = tr.select('td')[1].a.get('href')
            uid      = authorHP.split('/')[4]

            if uid == '1216826604': #这个哥们啥都写，这里_3_1是他发表的股票相关的博客
                link = 'http://blog.sina.com.cn/s/articlelist_{}_3_1.html'.format(uid)
            else:
                link = 'http://blog.sina.com.cn/s/articlelist_{}_0_1.html'.format(uid)

            views = tr.select('td')[2].get_text()
            
            data.append([category,seq,author,uid,link,views,updateTime]) #,authorHP

    return data


def zlbang(url):
    resp = requests.get(url)
    soup = BeautifulSoup(resp.content, 'lxml', from_encoding="gbk")
    # print(soup.prettify())

    category = '每周人气榜-财经'
    data = []

    for item in soup.select('body'):
        js = item.select('script[type="text/javascript"]')[0].get('src')
        for t in soup.select('th[align="right"]'):
            updateTime = t.get_text().strip('最后更新时间：')
    # print(js, updateTime)
    js_var  = requests.get(js)
    con_tmp =  js_var.content.decode('ascii')[15:][:-1]
    content = ast.literal_eval(con_tmp)

    i = 0
    for j in content:

        i = i+1
        if j['uid'] == '1216826604': #这个哥们啥都写，这里_3_1是他发表的股票相关的博客
            link = 'http://blog.sina.com.cn/s/articlelist_{}_3_1.html'.format(j['uid'])
        else:
            link = 'http://blog.sina.com.cn/s/articlelist_{}_0_1.html'.format(j['uid'])

        data.append([category,str(i),j['uname'],j['uid'],link,j['totalhits'],updateTime])

    return data


# 利用二级list中的User ID对两级list去重，保留unique的博客，
def unique(input):
    output = []
    input_id = []
    for x in input:
        if x[3] not in input_id:
            output.append(x)
            input_id.append(x[3])
    return output


def dedup_author():
    url_top = 'http://blog.sina.com.cn/lm/iframe/top100/finance.html'  # 财经总流量排行榜前100
    url_zlbang = 'http://blog.sina.com.cn/lm/iframe/zlbang/finance.html'  # 财经每周人气榜前100
    total_authors = top100_authors(url_top) + zlbang(url_zlbang)
    return unique(total_authors)


# 拿到知名博主的最新博文链接
def blog_list(uid,url,start_tm,end_tm):
    # uid     : 博主ID
    # url     : 博主博客列表页链接
    # start_tm：想抓取的博客的起始发布时间,如 '2017-06-24'
    # end_tm  : 想抓取的博客的结束发布时间,如 '2017-06-26'

    year, month, day = list(map(int, start_tm.split('-')))
    start_tm = datetime.datetime(year, month, day)
    year, month, day = list(map(int, end_tm.split('-')))
    end_tm = datetime.datetime(year, month, day) + datetime.timedelta(days=1)

    data = []

    while True:
        atc_tm = None
        soup = get_soup(url)
        
        for al in soup.select('div[class="articleList"]'):
            for blog in al.select('div[class="articleCell SG_j_linedot1"]'):
                if blog.select('span[class="atc_ic_f"]')[0].select('a'):
                    recommended = 1
                else:
                    recommended = 0
                atc = blog.select('span[class="atc_title"]')[0].a
                title = atc.get_text()
                link = atc.get('href')
                # atc_info = blog.select('span[class="atc_data"]')[0].get_text()
                atc_tm = blog.select('span[class="atc_tm SG_txtc"]')[0].get_text()
                atc_tm = datetime.datetime.strptime(atc_tm,"%Y-%m-%d %H:%M")

                if start_tm <= atc_tm < end_tm:
                    data.append([uid,recommended,title,link,atc_tm])#,atc_info])
        
        for li_next in soup.select('li[class="SG_pgnext"]'):
            for a in li_next:
                url = a.get('href')

        if not atc_tm or atc_tm < start_tm:
            # print(atc_tm, url)
            break
    return data


# 将数据写入CSV,如果文件存在直接覆盖
def to_csv(filename,header,data,delete):
    # filename: 文件名，总是以.csv结尾
    # header  : 表头,list格式
    # data    : 数据,list格式
    # del     : 文件存在时是否删除
    if os.path.exists(filename) and delete=='N':
        f = open(filename, 'a', newline="\n", encoding="utf-8")
        writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerows(data)
        f.close()
    else:
        f = open(filename, 'w', newline="\n", encoding="utf-8")
        writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(header)
        writer.writerows(data)
        f.close()


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# 博主信息
filename = '知名博主信息.csv'
header = ['category','seq','author','author_ID','articlelist_url','views','updateTime']
# to_csv(filename,header,dedup_author(),'Y')

# 博主近期博客信息
filename = '知名博主近期的博文链接.csv'
header = ['author_ID','recommended','title','blog_url','atc_tm']

# for author in dedup_author():
    # blogs = blog_list(author[3],author[4],'2017-06-19','2017-06-25')
    # to_csv(filename,header,blogs,'N')


# 拿到独家看市, 大盘走势, 板块个股网页的博文链接 # # # # # # # # # # # # # # # # # # # # # # # # # #
# 转化 独家看市, 大盘走势, 板块个股网页中得到的发帖时间
def tm(t):
    if '年' not in t:
        tt = datetime.datetime.now().strftime("%Y") + '-' + t.replace('月','-').replace('日','')
    else:
        tt = t.replace('年','-').replace('月','-').replace('日','')
    return tt


# 独家看市, 大盘走势, 板块个股
def cj(category,url,start_tm,end_tm):
    # url: 网站链接
    # i  : 抓取最近多少天的数据，7表示最近7天
    year, month, day = list(map(int, start_tm.split('-')))
    start_tm = datetime.datetime(year, month, day)
    year, month, day = list(map(int, end_tm.split('-')))
    end_tm = datetime.datetime(year, month, day) + datetime.timedelta(days=1)

    data = []
    while True:
        resp = requests.get(url)
        soup = BeautifulSoup(resp.content, 'lxml', from_encoding="gbk")
        # print(soup.prettify())

        for ls in soup.select('ul[class="list_009"]'):
            for i in range(0,5):
                con1 = ls.select('li')[i].select('a')[0]
                title = con1.get_text()
                blog_link = con1.get('href')
                con2 = ls.select('li')[i].select('a')[1]
                author = con2.get_text()
                authorHP = con2.get('href')
                post_tm = ls.select('li')[i].span.get_text().strip('()')
                post_tm = datetime.datetime.strptime(tm(post_tm),"%Y-%m-%d %H:%M")

                if start_tm <= post_tm < end_tm:
                    data.append([category,title,blog_link,author,authorHP,post_tm])

        url = url[:url.index('inde')] + soup.find(title="下一页").get('href').strip('.')

        if post_tm < start_tm:
            # print(post_tm, url)
            break
    return data


def cj_blog(category,start_tm,end_tm):
    if category == 'all':
        url = 'http://roll.finance.sina.com.cn/blog/blogarticle/inde_1.shtml'        # 所有股票博客
    elif category == 'bkgg':
        url = 'http://roll.finance.sina.com.cn/blog/blogarticle/cj-bkgg/index.shtml' # 板块个股
    elif category == 'bkks':
        url = 'http://roll.finance.sina.com.cn/blog/blogarticle/cj-bkks/inde.shtml'  # 博客看市(大盘走势)
    elif category == 'djks':
        url = 'http://roll.finance.sina.com.cn/blog/blogarticle/cj-djks/index.shtml' # 独家看市
    else:
        print('category is wrong!')
        exit()
    
    data = cj(category,url,start_tm,end_tm)
    return data


# 得到相关博客的内容
# 在pc端拿不到阅读转发评论的数量，移动端可以拿到但是却缺少博客分类标签，所以需要结合两者去拿
def get_content_m(url):
    soup = get_soup(url)

    # blog Information
    for blogInfo in soup.select('div[class="blogInfo"]'):
        for user in blogInfo.select('div[class="nickName"]'):
            author   = user.get_text()
            authorHP = user.a.get('href')
        for ul in blogInfo.select('ul'):
            level  = ul.select('li')[0].get_text().strip('博客等级:')
            views  = ul.select('li')[1].get_text().strip('博客访问:')
            points = ul.select('li')[2].get_text().strip('博客积分:')
    
    # content
    for con in soup.select('div[id="module_2052"]'):
        for t in con.select('h3'):
            title = t.get_text().strip('\n ')
        for tm in con.select('span[class="time"]'):
            time = tm.get_text()
        for pc in con.select('div[class="paracontent"]'):
            content = re.sub("[ \t\n\xa0]+", " ", pc.get_text())
        for artDesc in con.select('div[class="count"]'):
            read    = artDesc.select('span')[0].get_text().strip('\n ').strip('阅读：')
            repost  = artDesc.select('span')[1].get_text().strip('\n ').strip('转载：')
            like    = artDesc.select('span')[2].get_text().strip('\n ').strip('喜欢：')
            collect = artDesc.select('span')[3].get_text().strip('\n ').strip('收藏：')

    data = [author, authorHP, level, views, points, title,time,content,read,repost,like,collect]
    return data


def get_content(url):
    soup = get_soup(url)
    tags = []
    
    # for blogname in soup.select('h1[id="blogname"]'):
    #     author = blogname.a.span.get_text()
    #     authorHP = blogname.a.get('href')
        
    # for title_time in soup.select('div[class="articalTitle"]'):
    #     title = title_time.h2.get_text()
    #     for times in title_time.select('span[class="time SG_txtc"]'):
    #             time = times.get_text().strip('()')

    for blog_tag in soup.select('td[class="blog_tag"]'):
        tags = re.findall(re.compile(r"var \$tag='.*'"), blog_tag.get_text())[0].strip("var $tag='")

    # for blog in soup.select('div[class="articalContent newfont_family"]'):
    #     content = re.sub("[ \t\n\u3000\xa0]+"," ",blog.get_text())

    # data = [author, authorHP, title, time, tags, content]
    # writer.writerows([data])
    return tags


# 知名博主的近期博客，最新热帖
def all_blog_list(start_tm,end_tm):
    blog_urls = []

    # 知名博主
    print('知名博主')
    for author in dedup_author():
        for url in blog_list(author[3],author[4],start_tm,end_tm):
            blog_urls.append(url[3])
    
    # 最新热帖
    # print('最新热帖-股票博客')
    # for url in cj_blog('all',start_tm,end_tm):
    #     blog_urls.append(url[2])

    print('最新热帖-博客看市(大盘走势)')
    for url in cj_blog('bkks',start_tm,end_tm):
        blog_urls.append(url[2])

    print('最新热帖-板块个股')
    for url in cj_blog('bkgg',start_tm,end_tm):
        blog_urls.append(url[2])

    print('最新热帖-独家看市')
    for url in cj_blog('djks',start_tm,end_tm):
        blog_urls.append(url[2])

    return blog_urls


def download(start_tm,end_tm):
    for url in all_blog_list(start_tm,end_tm):

        url_w = url.rstrip('?tj=fina')
        url_m = url.replace("://","://m.")

        try:
            dt1 = get_content(url_w)
        except:
            print('error for {}'.format(url_w))
            continue
        try:
            dt2 = get_content_m(url_m)
        except:
            print('error for {}'.format(url_m))
            continue

        if dt2:
            dt2.append(dt1)
            to_csv(filename,header,[dt2],'N')


# 保存博客
filename = '新浪财经-股票-博客.csv'
header = ['author','authorHP','level','views','points','title','time','content','read','repost','like','collect','tags']
# download('2017-06-05','2017-06-25')

print('ALL Is Done!')
