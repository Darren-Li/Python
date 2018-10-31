# @Time    : 10/21/2018 3:40 PM
# @Author  : 李武卿, 数据分析经理
# @File    : 01-网络请求-requests.py
# @Software: PyCharm Community Edition
# @Desc    : Python3 基础课程
# @license : Copyright(C), 美库尔信息咨询（南京）有限公司
# @Contact : wuli@merkleinc.com(公司)，lwq07010328@163.com(个人)
# @Wechat  : wx_Darren910220


import requests
import json
import sys, os


# 发起网络请求
r = requests.get("https://api.github.com/users/ziqing27")

# 响应状态码
r.status_code
# 200

r.status_code == requests.codes.ok
# True

# 请求url
r.url
# 'https://api.github.com/users/ziqing27'

# 请求方式
r.request
# <PreparedRequest [GET]>

# 响应头
r.headers
# {'Date': 'Wed, 22 Aug 2018 02:15:04 GMT',
#  'Content-Type': 'application/json; charset=utf-8',
#  'Transfer-Encoding': 'chunked',
#  'Server': 'GitHub.com',
#  'Status': '200 OK',
#  'X-RateLimit-Limit': '60',
#  'X-RateLimit-Remaining': '57',
#  'X-RateLimit-Reset': '1534907545',
#  'Cache-Control': 'public, max-age=60, s-maxage=60',
#  'Vary': 'Accept, Accept-Encoding',
#  'ETag': 'W/"99da1a57ad094af27fbb0630af9c2489"',
#  'Last-Modified': 'Fri, 25 Nov 2016 12:40:11 GMT',
#  'X-GitHub-Media-Type': 'github.v3; format=json',
#  'Access-Control-Expose-Headers': 'ETag, Link, Retry-After, X-GitHub-OTP, X-RateLimit-Limit, X-RateLimit-Remaining,'
#                                   ' X-RateLimit-Reset, X-OAuth-Scopes, X-Accepted-OAuth-Scopes, X-Poll-Interval',
#  'Access-Control-Allow-Origin': '*',
#  'Strict-Transport-Security': 'max-age=31536000; includeSubdomains; preload',
#  'X-Frame-Options': 'deny',
#  'X-Content-Type-Options': 'nosniff',
#  'X-XSS-Protection': '1; mode=block',
#  'Referrer-Policy': 'origin-when-cross-origin, strict-origin-when-cross-origin',
#  'Content-Security-Policy': "default-src 'none'", 'X-Runtime-rack': '0.021552',
#  'Content-Encoding': 'gzip',
#  'X-GitHub-Request-Id': '138D:759F:95E5F7:C4425B:5B7CC727'}

r.headers['content-type']
# 'application/json; charset=utf8'

# 请求头
r.request.headers
# {'User-Agent': 'python-requests/2.19.1',
#  'Accept-Encoding': 'gzip, deflate', 'Accept': '*/*',
#  'Connection': 'keep-alive'}

# html的编码
r.encoding
# 'utf-8'

# The apparent encoding, provided by the charset library
r.apparent_encoding
# 'ascii'

print([i for i in dir(r) if not i.startswith('__')])

# 状态原因
r.reason
# 是否重定向
r.is_redirect

# requests.utils.get_encodings_from_content(r.text)
# requests.utils.get_encoding_from_headers(r.headers)
# requests.utils.get_unicode_from_response(r)


# 返回的内容
r.text     # 文本内容
r.content  # 二进制响应内容
r.json()   # JSON 响应内容

r.raw  # 原始套接字响应, 不过需要在初始请求中设置 stream=True
r.raw.status
r.raw.CONTENT_DECODERS
r.raw.headers

r = requests.get('https://api.github.com/events', stream=True)
r.raw.read(10)

r = requests.get('https://github.com/timeline.json')
r.json()

# 其他 HTTP 请求类型：PUT，DELETE，HEAD 以及 OPTIONS
"""
r = requests.post("http://httpbin.org/post", data={'key': 'value'})
r = requests.put("http://httpbin.org/put", data={'key': 'value'})
r = requests.delete("http://httpbin.org/delete")
r = requests.head("http://httpbin.org/get")
r = requests.options("http://httpbin.org/get")
"""


# 身份认证

# 导入要用到的用户名和密码
os.getcwd()
# sys.path.append(os.getcwd() +'/数据抓取/基础')
sys.path.append(r'C:\\Darren\\ziqing\\Merkle\\Python\\base\\数据抓取\\基础')
# os.chdir(r'C:\\Darren\\ziqing\\Merkle\\Python\\base\\数据抓取\\基础')
from token_pwd import token, pwd

token, pwd

# 第一种方法
# 申请token：https://github.com/settings/tokens
user = 'Darren-Li'

headers = {"Authorization": 'token ' + token}
r = requests.get('https://api.github.com/user', headers=headers)
r.json()

# 第二种方法
from requests.auth import HTTPBasicAuth
r = requests.get('https://api.github.com/user', auth=HTTPBasicAuth(user, pwd))
r.json()

r = requests.get('https://api.github.com/user', auth=(user, pwd))
r.json()


# https://github.com/Darren-Li
# ('darren.li.027@gmail.com', 'GitZiqing27')

# 创建repo
repo = 'CDA_webScraping'
description = '通过Github API 创建一个新的代码仓库'
payload = {'name': repo, 'description': description, 'auto_init': 'true'}
create_repo = requests.post('https://api.github.com/' + 'user/repos',
                            auth=(user, token),
                            data=json.dumps(payload))
# 删除repo
delete_repo = requests.delete('https://api.github.com/' + 'repos/' + user + '/' + repo, headers=headers)


# 传递 URL 参数
payload = {'key1': 'value1', 'key2': ['value2', 'value3']}
r = requests.get('http://httpbin.org/get', params=payload)
print(r.url)
# http://httpbin.org/get?key1=value1&key2=value2&key2=value3


# 定制请求头
url = 'http://www.merklechina.cn/'
headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
           'Accept-Encoding': 'gzip, deflate',
           'Accept-Language': 'en-US,en;q=0.8',
           'Referer': 'http://www.merklechina.cn/industry-solutions/%E9%93%B6%E8%A1%8C%E9%87%91%E8%9E%8D',
           'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 '
                         '(KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
           }

"""
Accept
    作用：浏览器端可以接受的媒体类型
    例如：Accept: text/html, 代表浏览器可以接受服务器回发的类型为"text/html", 也就是我们常说的html文档,
    如果服务器无法返回“text/html”类型的数据, 服务器应该返回一个406错误(non acceptable)
    
    通配符 * 代表任意类型, 例如  Accept: */*  代表浏览器可以处理所有类型,(一般浏览器发给服务器都会包含这个)

Accept-Encoding
    作用：浏览器申明自己接收的编码方法，通常指定压缩方法，是否支持压缩，支持什么压缩方法（gzip，deflate）

Accept-Language
    作用：浏览器申明自己接收的语言
    语言跟字符集的区别：中文是语言，中文有多种字符集，比如big5，gb2312，gbk等等
    例如：Accept-Language: en-us

Connection
    例如：Connection: keep-alive, 当一个网页打开完成后，客户端和服务器之间用于传输HTTP数据的TCP连接不会关闭，
    如果客户端再次访问这个服务器上的网页，会继续使用这一条已经建立的连接
    
    例如：Connection: close, 代表一个Request完成后，客户端和服务器之间用于传输HTTP数据的TCP连接会关闭，
    当客户端再次发送Request，需要重新建立TCP连接。

Host（发送请求时，该报头域是必需的）
    作用: 请求报头域主要用于指定被请求资源的Internet主机和端口号，它通常从HTTP URL中提取出来的
    例如: 我们在浏览器中输入：http://www.merklechina.cn/, 浏览器发送的请求消息中，就会包含Host请求报头域，
    如：Host：www.merkleinc.cn
    此处使用缺省端口号80，若指定了端口号，则变成：Host：指定端口号

Referer
    当浏览器向web服务器发送请求的时候，一般会带上Referer，告诉服务器我是从哪个页面链接过来的，
    服务器基于此可以获得一些信息用于处理，一般用于网站流量统计。

Content-Type: application/json; charset=UTF-8 
    浏览器接收的内容类型、字符

User-Agent
    作用：告诉HTTP服务器，客户端使用的操作系统和浏览器的名称和版本.
    我们上网登陆论坛的时候，往往会看到一些欢迎信息，其中列出了你的操作系统的名称和版本，你所使用的浏览器的名称和版本，
    这往往让很多人感到很神奇，实际上，服务器应用程序就是从User-Agent这个请求报头域中获取到这些信息
    User-Agent请求报头域允许客户端将它的操作系统、浏览器和其它属性告诉服务器。
    
    例如： User-Agent: Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; CIBA; .NET CLR 2.0.50727; 
    .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C; InfoPath.2; .NET4.0E)

Cookie
    Cookie是用来存储一些用户信息以便让服务器辨别用户身份的（大多数需要登录的网站上面会比较常见），
    比如cookie会存储一些用户的用户名和密码，当用户登录后就会在客户端产生一个cookie来存储相关信息，
    这样浏览器通过读取cookie的信息去服务器上验证并通过后会判定你是合法用户，从而允许查看相应网页。
    当然cookie里面的数据不仅仅是上述范围，还有很多信息可以存储是cookie里面，比如sessionid等。

"""
r = requests.get(url, headers=headers)
r.request.headers
"""
{'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100'
               ' Safari/537.36',
 'Accept-Encoding': 'gzip, deflate',
 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
 'Connection': 'keep-alive',
 'Accept-Language': 'en-US,en;q=0.8',
 'Referer': 'http://www.merklechina.cn/industry-solutions/%E9%93%B6%E8%A1%8C%E9%87%91%E8%9E%8D'}
"""

# 超时处理
r = requests.get("https://www.merkleinc.com/", timeout=(3.05, 27))
r = requests.get("https://www.merkleinc.com/", timeout=(1, 3))
r.status_code


# 异常处理
try:
    r = requests.get("https://www.merkleinc.com2/", timeout=(1, 3))
    print('No error!', r.status_code)
except requests.exceptions.ReadTimeout as ReadTimeout:
    print('ReadTimeout!', ReadTimeout)
except requests.exceptions.ConnectionError as ConnectionError:
    print('ReadTimeout!', ConnectionError)
finally:
    print('Done!')


# Session, cookie, post方法

loginUrl = 'http://accounts.douban.com/login'

formData = {
    "redir": "http://movie.douban.com/mine?status=collect",
    "form_email": 13072536076,
    "form_password": '07310132',
    "login": '登录'
}

headers = {"Host": "book.douban.com",
           "Referer": "https://www.douban.com/people/168792227/",
           "User-Agent": 'Mozilla/5.0 (Windows NT 6.1)\AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36'}

# create session
s = requests.session()

r = s.post(loginUrl, data=formData, headers=headers)
print('登陆状态：', r.status_code)

# 会话请求的响应头
s.headers
# 更新回话的响应头
s.headers.update({'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 '
                                '(KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1'})  # 我是iphone6
s.headers

s.cookies
s.cookies.get_dict()

r = s.get("https://book.douban.com/")

# 关闭session
s.close


# 代理IP
# obtain proxies from: https://www.us-proxy.org/
proxies = {'https': '204.52.206.65:8080',
           'http': '168.235.93.162:8080'
           }

google_url = 'https://pbs.twimg.com/media/DMhCgyGUEAAXbnv.jpg'

resp = requests.get(google_url, proxies=proxies)
resp.status_code

# 下载照片
with open('DMhCgyGUEAAXbnv.png', 'wb') as f:
    f.write(resp.content)
