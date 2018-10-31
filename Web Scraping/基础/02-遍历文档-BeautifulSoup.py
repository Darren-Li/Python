# @Time    : 10/22/2018 3:40 PM
# @Author  : 李武卿, 数据分析经理
# @File    : 01-网络请求-requests.py
# @Software: PyCharm Community Edition
# @Desc    : Python3 基础课程
# @license : Copyright(C), 美库尔信息咨询（南京）有限公司
# @Contact : wuli@merkleinc.com(公司)，lwq07010328@163.com(个人)
# @Wechat  : wx_Darren910220


# 加载需要的包或模块
import requests
from bs4 import BeautifulSoup


# 发起网络请求并接受响应
url = 'http://www.merklechina.cn/case-studies.html'
resp = requests.get(url)

# 解析响应内容
soup = BeautifulSoup(resp.text)
soup = BeautifulSoup(resp.text, 'html.parser')
soup = BeautifulSoup(resp.text, 'lxml')
# soup = BeautifulSoup(resp.text, 'lxml-xml')
soup = BeautifulSoup(resp.text, 'html5lib')

# 如果中文乱码，请参看 ”中文乱码处理.py"
# soup = BeautifulSoup(resp.content, 'lxml')

# 显示html文档树
print(soup)
print(soup.prettify())

# 快速浏览数据内容
soup.title

div = soup.select('div[class="block-region-top-left]"')[0]
print(div.prettify())


# 例子
html = """
<html lang="en" class="noJS">
<head><title>Merkle行业解决方案 -银行金融</title></head>
<body>
    <!-- 介绍 -->
    <h3 class="current">银行金融</h3><p name="intro" class='finance' id='mlk'>近20年，金融风暴，经济衰退和消费者权益的提高使得银行金融业经历了一波又一波的变化。我们再也不能单靠产品来获得以及维持忠实客户。
    <strong>在美库尔，我们相信客户是任何成功银行的核心。</strong>现在银行的竞争优势在于它是否有能力全面理解、提高顾客参与度、
    跟踪、测量，影响消费者，从而实现增长和盈利。和创新金融机构合作，美库尔充分利用这样一个充满挑战的机遇。我们已经准备好与您一起合作，
    绘制出以客户为中心的市场营销蓝图，通过数据洞察和多渠道顾客交互来实现营销策略。   </p><p>
    <h3 class="field-content"><a href="/industry-solutions/%E9%93%B6%E8%A1%8C%E9%87%91%E8%9E%8D/%E8%A7%A3%E5%86%B3%E6%96%B9%E6%A1%88">解决方案</a></h3>  
    <p>因为银行有直接的客户关系，可以直接获得具有深度和广度的数据，那么金融业就有能力去真正实现客户关系营销这一目标。这在以前只是一个愿望！</p>
    <h3 class="field-content">
    <a id='client1' class='link' href="/industry-solutions/banking-finance/our-clients">我们的客户</a>
    <a id='client2' class='link' href="/industry-solutions/banking-finance/our-clients/solutions">我们的行业解决方案</a>
    <a id='client3' class='link' href="/industry-solutions/banking-finance/our-clients/solutions">客户评价</a>
    </h3> 
    <p>美库尔与我们的客户建立了合作平台，制定了长远的目标，并且推动有竞争优势的创新。我们的合作基础是数据驱动的洞察力，效果衡量和问责制，
    从而更好地管理变革。我们的客户既包括地区性的小银行又包括国际大银行。</p>
    <p><a href="/industry-solutions/banking-finance/our-team">了解更多关于我们的团队的信息</a></p>
    </p><span><!-- 更多信息 --></span>
</body>
</html>
"""

soup = BeautifulSoup(html, 'lxml')
print(soup.prettify())

# 对象的种类
"""
Beautiful Soup将复杂HTML文档转换成一个复杂的树形结构,每个节点都是Python对象,所有对象可以归纳为4种:
 Tag , NavigableString , BeautifulSoup , Comment.

"""

# 1. tag，Tag 对象与XML或HTML原生文档中的tag相同:
soup.head
type(soup.head)

soup.title
soup.p
# 注意到它查找的是在所有内容中的第一个符合要求的标签，如果要查询所有的标签，我们在后面进行介绍。

# 对于 Tag，它有两个重要的属性：name 和 attrs
soup.head.name

soup.p.attrs
# {'class': ['finance'], 'name': 'intro'}

# tag的属性的操作方法与字典相同:
soup.p['class']
soup.get('name')

# 修改属性
soup.p['class'] = 'bank'
soup.p['class']
# 添加属性
soup.p['title'] = 'content'
soup.p['title']
# 删除属性
del soup.p['title']


# 2. NavigableString
soup.h3
soup.h3.string
type(soup.h3.string)

soup.p
soup.p.string


# 3. BeautifulSoup,一个文档的全部内容.大部分时候,可以把它当作 Tag 对象，是一个特殊的 Tag，我们可以分别获取它的类型，名称，以及属性
type(soup)
soup.name
soup.attrs  # 没有属性


# 4. Comment, 一个特殊类型的 NavigableString对象，其实输出的内容仍然不包括注释符号，但是如果不好好处理它，可能会对我们的文本处理造成意想不到的麻烦。
soup.span
soup.span.string  # 注释符被去掉了
type(soup.span.string)

soup.body
for s in soup.body.strings:
    print(s)

from bs4 import Comment

comments = soup.body.find_all(string=lambda text: isinstance(text, Comment))
for comment in comments:
    print(comment)


# 遍历文档树

# 1. 直接子节点，.contents，.children
# tag的 .contents 属性可以将tag的子节点以列表的方式输出
soup.head
soup.head.contents  # 以列表形式返回

soup.body
soup.body.children
# <list_iterator at 0x6b99b70>  # 列表迭代器

# 通过tag的 .children 生成器,可以对tag的子节点进行循环:
for i, ch in enumerate(soup.body.children):
    print(i, ch)

# 2. 所有子孙节点，descendants
soup.head.descendants  # 生成器

for con in enumerate(soup.head.descendants):
    print(i, con)

for con in enumerate(soup.body.descendants):
    print(i, con)

# .contents 和 .children 属性仅包含tag的直接子节点，.descendants 属性可以对所有tag的子孙节点进行递归循环
# 可以发现，所有的节点都被打印出来了，先生最外层的 HTML标签，其次从 head 标签一个个剥离，以此类推。

# 3. 节点内容, .string
"""
如果tag只有一个 NavigableString 类型子节点,那么这个tag可以使用 .string 得到子节点。
如果一个tag仅有一个子节点,那么这个tag也可以使用 .string 方法,输出结果与当前唯一子节点的 .string 结果相同。
"""
soup.head.string
soup.h3.string
soup.p.string
soup.p.strong.string

# 4. 多个内容
# .strings
soup.p.strings  # 生成器
for s in soup.p.strings:
    print(s)

for s in soup.p.strings:
    print(s.strip())

# .stripped_strings 输出的字符串中可能包含了很多空格或空行,使用 .stripped_strings 可以去除多余空白内容
for s in soup.p.stripped_strings:
    print(s)

# 5. 父节点 .parent
soup.h3.parent

# 父节点名称
soup.h3.parent.name

# 6. 全部父节点 .parents
soup.h3.parents

for p in soup.h3.parents:
    print('- '*30, p.name, p,  sep='\n')

# 7. 兄弟节点 .next_sibling  .previous_sibling
"""
兄弟节点可以理解为和本节点处在统一级的节点，.next_sibling 属性获取了该节点的下一个兄弟节点，
.previous_sibling 则与之相反，如果节点不存在，则返回 None

注意：实际文档中的tag的 .next_sibling 和 .previous_sibling 属性通常是字符串或空白，
因为空白或者换行也可以被视作一个节点，所以得到的结果可能是空白或者换行
"""
soup.p.previous_sibling

soup.p.next_sibling

# 8. 全部兄弟节点 .next_siblings  .previous_siblings
# 对当前节点的兄弟节点迭代输出
for ps in soup.p.previous_siblings:
    print('- '*30, ps, sep='\n')

for ns in soup.p.next_siblings:
    print('- '*30, ns, sep='\n')

# 9. 前后节点 .next_element  .previous_element
# 与 .next_sibling  .previous_sibling 不同，它并不是针对于兄弟节点，而是在所有节点，不分层次
soup.p

soup.p.previous_element
soup.p.next_element

# 10. 前后节点 .next_elements  .previous_elements
"""
<html><head><title>Merkle行业解决方案 -银行金融</title></head>
<p><a href="/industry-solutions/banking-finance/our-team">了解更多关于我们的团队的信息</a></p>

HTML解析器把这段字符串转换成一连串的事件: “打开<html>标签”,”打开一个<head>标签”,”打开一个<title>标签”,”添加一段字符串”,
”关闭<title>标签”,”打开<p>标签”,等等.Beautiful Soup提供了重现解析器初始化过程的方法.

.next_element 属性指向解析过程中下一个被解析的对象(字符串或tag),结果可能与 .next_sibling 相同,但通常是不一样的.
通过 .next_elements 和 .previous_elements 的迭代器就可以向前或向后访问文档的解析内容,就好像文档正在被解析一样
"""
for e in soup.h3.next_elements:
    print('- ' * 30, e, sep='\n')

for e in soup.h3.previous_elements:
    print('- ' * 30, e, sep='\n')

for e in soup.h3.previous_siblings:
    print('- ' * 30, e, sep='\n')

for e in soup.body.previous_elements:
    print('- ' * 30, e, sep='\n')

for e in soup.body.previous_siblings:
    print('- ' * 30, e, sep='\n')


# 搜索文档树

# find 系列方法
"""
find_all(name=None, attrs={}, recursive=True, text=None, limit=None, **kwargs)
搜索当前tag的所有tag子节点,并判断是否符合过滤器的条件

name：查找所有名字为name 的tag的子节点，并判断是否符合过滤条件, name 可以是：
    1. 字符串：    soup.find_all('b')  # 找出所有b标签
    2. 正则表达式：如果传入正则表达式作为参数,Beautiful Soup会通过正则表达式的 match() 来匹配内容.
                   soup.find_all(re.compile("^b"))   # 找出所有以b开头的标签
    3. 列表：     如果传入列表参数, Beautiful Soup会将与列表中任一元素匹配的内容返回. 下面的代码找到文档中所有<a>标签和<b>标签
                  soup.find_all(['a','b'])
    4. True：     True 可以匹配任何值,下面代码查找到所有的tag,并返回tag的名字。
                  for tag in soup.find_all(True):
                      print(tag.name)
    5. 自定义方法：如果没有合适过滤器,那么还可以定义一个方法, 方法只接受一个元素参数,
                   如果这个方法返回 True 表示当前元素匹配并且被找到,如果不是则反回 False 。
                   下面方法校验了当前元素,如果包含 class 属性却不包含 id 属性,那么将返回 True:
                   def has_class_but_no_id(tag):
                       return tag.has_attr('class') and not tag.has_attr('id')
                   soup.find_all(has_class_but_no_id)

Keyword：如果一个指定名字的参数不是搜索内置的参数名,搜索时会把该参数当作指定名字tag的属性来搜索,如果包含一个名字为 id的参数,
          Beautiful Soup会搜索每个tag的"id"属性，有些tag属性在搜索不能使用,比如HTML5中的 data-* 属性

        soup.find_all(id='link2')
        soup.find_all(href=re.compile("elsie"))
        soup.find_all(href=re.compile("elsie"), id='link1')

        例如：
        data_soup = BeautifulSoup('<div data-foo="value">foo!</div>')
        data_soup.find_all(data-foo="value")
        # SyntaxError: keyword can't be an expression
        
        # 但是可以通过 find_all()方法的attrs 参数定义一个字典参数来搜索包含特殊属性的tag
        data_soup.find_all(attrs={"data-foo": "value"})
        # [<div data-foo="value">foo!</div>]

按CSS搜索:
        soup.find_all("a", class_="sister")
        
        soup.find_all(class_=re.compile("itl"))
        
        def has_six_characters(css_class):
            return css_class is not None and len(css_class) == 6
        
        soup.find_all(class_=has_six_characters)

recursive: 调用tag的find_all()方法时,BeautifulSoup会检索当前tag的所有子孙节点,如果只想搜索tag的直接子节点,可以使用参数recursive=False.

text：通过text参数可以搜搜文档中的字符串内容，与name参数的可选值一样, text参数接受字符串, 正则表达式, 列表, True

limit: find_all()方法返回全部的搜索结构,如果文档树很大那么搜索会很慢.如果我们不需要全部结果,可以使用limit参数限制返回结果的数量.
       效果与SQL中的limit关键字类似,当搜索到的结果数量达到limit的限制时,就停止搜索返回结果.
"""

soup.find_all('p')

import re
soup.find_all(re.compile("^h"))
soup.find_all(['a', 'p'])

for tag in soup.find_all(True):
    print(tag.name)


def has_class_but_no_id(tag):
    return tag.has_attr('class') and not tag.has_attr('id')


soup.find_all(has_class_but_no_id)
soup.find_all(class_='current')
soup.find_all(href=re.compile("/industry"))
soup.find_all(class_=re.compile("field"))

# 其他方法
"""
soup.find(name=None, attrs={}, recursive=True, text=None, **kwargs)
find_parents();find_parent()  # 用来搜索当前节点的父辈节点,搜索方法与普通tag的搜索方法相同
find_next_siblings();find_next_sibling()
find_previous_siblings();find_previous_sibling()
find_all_next();find_next()   # 通过 .next_elements属性对当前tag的之后的tag和字符串进行迭代,
                                find_all_next()方法返回所有符合条件的节点, find_next()方法返回第一个符合条件的节点
find_all_previous();find_previous()
"""

html_doc = """
<html><head><title>The Dormouse's story</title></head>
<body>
<p class="title"><b>The Dormouse's story</b></p>

<p class="story">Once upon a time there were three little sisters; and their names were
<a href="http://example.com/elsie" class="sister" id="link1">Elsie</a>,
<a href="http://example.com/lacie" class="sister" id="link2">Lacie</a> and
<a href="http://example.com/tillie" class="sister" id="link3">Tillie</a>;
and they lived at the bottom of a well.</p>

<p class="story">...</p>
"""

# CSS选择器
# 在写CSS时，标签名不加任何修饰，类名前加点(.)，id名前加#，在这里我们也可以利用类似的方法来筛选元素，用到的方法是soup.select()，返回类型是 list。

# 1. 通过标签名查找
soup.select('title')
soup.select('p')

# 2. 通过class查找
soup.select('.finance')
soup.select("[class~=finance]")

# 3. 通过id查找
soup.select('#mlk')
soup.select("[id~=mlk]")

# 4. 通过组合查找, 组合查找即和写CSS文件时，标签名与类名、id名进行的组合原理是一样的，例如查找 p 标签中，id 等于 link1的内容，二者需要用空格分开
soup.select('p#mlk')
soup.select('p.finance')

# 通过tag标签逐层查找
soup.select("head > title")
# 找到某个tag标签下的直接子标签
soup.select("head > title")
soup.select("p > a")
soup.select("h3 > a")
soup.select("h3 > a:nth-of-type(1)")
soup.select("h3 > a:nth-of-type(2)")

# 5. 找到兄弟节点标签
soup.select('.link')
soup.select("#client1 ~ .link")
soup.select("#client1 + .link")

# 6. 属性查找, 查找时还可以加入属性元素，属性需要用中括号括起来，注意属性和标签属于同一节点，所以中间不能加空格，否则会无法匹配到。
soup.select('p[class="finance"]')
soup.select('a[href="/industry-solutions/banking-finance/our-team"]')
soup.select('a[href^="/industry-solutions"]')  # 开头
soup.select('a[href$="solutions"]')  # 结尾
soup.select('a[href*="solutions"]')  # 包含

# 同样，属性仍然可以与上述查找方式组合，不在同一节点的空格隔开，同一节点的不加空格
soup.select('p a[href="/industry-solutions/banking-finance/our-team"]')

# 以上的 select方法返回的结果都是列表形式，可以遍历形式输出，然后用 get_text() 方法来获取它的内容

for title in soup.select('title'):
    print(title.get_text())

for title in soup.select('title'):
    print(title.text)

soup.select('title')[0].get_text()


# 通过语言设置来查找:
multilingual_markup = """
 <p lang="en">Hello</p>
 <p lang="en-us">Howdy, y'all</p>
 <p lang="en-gb">Pip-pip, old fruit</p>
 <p lang="fr">Bonjour mes amis</p>
"""
multilingual_soup = BeautifulSoup(multilingual_markup)
multilingual_soup.select('p[lang|=en]')
# [<p lang="en">Hello</p>,
#  <p lang="en-us">Howdy, y'all</p>,
#  <p lang="en-gb">Pip-pip, old fruit</p>]


# 解析xml文档
soup = BeautifulSoup(open('数据抓取/基础/Project.xml'), 'lxml-xml')
soup = BeautifulSoup(open('数据抓取/基础/Project.xml'), ['lxml','xml'])
print(soup.prettify())

soup.option
soup.select('option[name="KEYWORD_CASE"]')
