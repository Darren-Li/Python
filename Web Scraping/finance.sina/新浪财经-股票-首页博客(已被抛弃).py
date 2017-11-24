import requests
from bs4 import BeautifulSoup
import csv
import re


# 获取网页并解析 # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# iPad，但是没用
header_iPad = {'User-Agent': r'Mozilla/5.0 (iPad; CPU OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1',
               'Accept-Language': 'en-US,en;q=0.8',
               'Accept-Encoding': 'gzip, deflate, sdch',
               'Connection': 'keep-alive',
               }


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


# 从新浪股票主页上拿到显示的blog链接，这个不全，舍弃！
def blog(tag, url='http://finance.sina.com.cn/stock/'):
    soup = get_soup(url)
    data = []

    for block in soup.select('div[data-sudaclick="{}"]'.format(tag)):
        # 博客
        for uls in block.select('div[class="p04_c clearfix"]')[0].select('ul[class="list04"]'):
            for lis in uls.select('li'):
                time = lis.span.get_text()
                for p in lis.select('p'):
                    aa = p.select('a')
                    if len(aa)==2:
                        data.append(['博客',time, p.select('a')[0].get_text(), p.select('a')[0].get('href'), p.select('a')[1].get_text(), p.select('a')[1].get('href')])
        # 理财师
        for uls in block.select('div[class="p04_c clearfix"]')[1].select('ul[class="list04"]'):
            for lis in uls.select('li'):
                time = lis.span.get_text()
                for p in lis.select('p'):
                    aa = p.select('a')
                    if len(aa)==2:
                        data.append(['理财师',time, p.select('a')[0].get_text(), p.select('a')[0].get('href'), p.select('a')[1].get_text(), p.select('a')[1].get('href')])
    return data


# write links in csv file
f = open('新浪财经-股票-博客.csv', 'w', newline="\n", encoding="utf-8")
writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL,)
writer.writerow(['category','time', 'author', 'homepage_link', 'title', 'blog_link'])
writer.writerows(blog('blk_bokeguba'))
f.close()


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


f = open('新浪财经-股票-博客.csv', 'w', newline="\n", encoding="utf-8")
writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
writer.writerow(['author', 'authorHP', 'level', 'views', 'points', 'title', 'time',
                 'content', 'read', 'repost', 'like', 'collect','tags'])


for item in blog('blk_bokeguba'):
    dt1, dt2 = None, None
    if item[0] == '博客':
        url_w = item[5].strip('?tj=fina')
        url_m = item[5].strip('?tj=fina').replace("://","://m.")
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
            writer.writerows([dt2])

f.close()
