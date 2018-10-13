# -*- coding: utf-8 -*-
from industrySpider.BaseSpider import *
from bs4 import BeautifulSoup
import time
from lxml.etree import HTML
from lxml import html as HTMLParser
import uuid, re, os, json

spider = BaseSpider()

domainUrl = 'http://www.law-lib.com'
idpre = 'lawlib'

# 请求头
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
}

# 文章索引寻址css选择器，选择至文章列表外层
index_css_selector = {
}

# 文章外层信息css选择器，视情况设定，例如：如下设定是因为外层文章列表包含完整标题、文章地址、发布时间、封面图、标签
info_css_selector = (


)

# 文章内层css选择器，视情况而定，获取目标html或者补充外层无法获取的信息
article_css_selector = (
    'body > div.w > div > div.w_l.fl.mainw > div > div.law.mb20 > div.tit > h3::text',
    'body > div.w > div > div.w_l.fl.mainw > div > div.law.mb20 > div.viewcontent > p:nth-child(1)::text'
)

# html整理、清洗正则规则；（正则表达式、匹配方式，替换字符串）
stripItem = [
    ('<script.*?</script>', re.S, ''),
    ('<iframe.*?</iframe>', re.I, ''),
    ('<a.*?>', re.I, ''),
    ('</a>', re.I, ''),
    ('style=".*?"', re.I, ''),
    ('height=".*?"', re.I, ''),
    ('width=".*?"', re.I, '')
]


def decodehtml(req):
    if req.encoding == 'ISO-8859-1':
        encodings = requests.utils.get_encodings_from_content(req.text)
        if encodings:
            encoding = encodings[0]
        else:
            encoding = req.apparent_encoding

        # encode_content = req.content.decode(encoding, 'replace').encode('utf-8', 'replace')
        global encode_content
        encode_content = req.content.decode(encoding, 'replace')  # 如果设置为replace，则会用?取代非法字符；
        return encode_content


# 主函数，用于获取数据和保存数据
def main(url):
    # data：网站请求参数

    if '/' not in url:
        return
    if '2018' not in url:
        return
    if 'fzdt' not in url:
        url = "http://www.law-lib.com/fzdt/" + url
    else:
        url = "http://www.law-lib.com" + url

    # 获取page页
    articleHtml = spider.get_article_detail(url)
    articleHtml = decodehtml(articleHtml)
    # 获取内层信息
    articleInfo = spider.parse_article_detail(articleHtml, article_css_selector)


    title = ''.join(articleInfo[0].extract()).strip()
    time = ''.join(articleInfo[1].extract()).strip()
    pattern = re.compile(r'.*?(\d{4})-(\d{1,2})-(\d{1,2}).*?')
    year, month, day = re.findall(pattern, time)[0]
    time = "%d-%02d-%02d" % (int(year), int(month), int(day))
    # 获取内层信息
    # articleInfo = spider.parse_article_detail(articleHtml, article_css_selector)

    S_htmlContent = dealContent(url,title)
    # 整理内层信息
    finalcontent = spider.html_strip(S_htmlContent, stripItem),
    # 整理其他信息
    Id = idpre + url.split('.')[2].split('/')[-1]
    tags = ''
    coverPic = ''
    coverPicType = ''

    # 组织数据
    data = (
        Id,
        title,
        time,
        finalcontent,
        tags,
        'TH006',
        coverPic,
        coverPicType,
        '法律图书馆'
    )

    # 保存数据
    spider.save_data(data)





def dealContent(url,title):
    # htmlContent
    itemHTML_req = requests.get(url)
    itemHTML_req.encoding = 'gb2312'
    itemHTML = HTML(itemHTML_req.text)
    htmlContent_1 = itemHTML.xpath('//div[@class="law mb20"]/div[@class="tit"]')
    l = len(itemHTML.xpath('//div[@class="law mb20"]/div[@class="viewcontent"]/*'))
    s = len(itemHTML.xpath('//div[@class="law mb20"]/div[@class="viewcontent"]/*'))
    htmlContent_2 = itemHTML.xpath(
        '//div[@class="law mb20"]/div[@class="viewcontent"]/*[position()>1 and position()<=%d]' % (l - 3))
    s = ''
    for i in htmlContent_1 + htmlContent_2:
        i_ = HTMLParser.tostring(i, encoding='gb2312').decode('gb2312', 'ignore')
        i_ = i_.replace('"', "'")
        s += i_
    s = '<body><div>' + s + '</div></body>'
    s = s.replace('\r', '').replace('\n', '').replace('\t', '').replace('\u3000', '').replace(title, '')
    htmlContent = s
    return htmlContent


def get_urls(offset):
    targetURL = []
    baseURL = "http://www.law-lib.com/fzdt/"
    req = requests.get(baseURL)
    req.encoding = 'gb2312'
    html = HTML(req.text)
    as_1 = html.xpath('//h3[@class="clearfix"]/a')
    as_2 = html.xpath('//ul/li/a[@target]')
    for i in as_1 + as_2:
        url = i.attrib['href']
        targetURL.append(url)

    baseURL = 'http://www.law-lib.com/fzdt/sort20.asp?pageno=%d'
    for t in range(1,offset):

        pageURL = baseURL % (t + 1)
        try:
            req = requests.get(pageURL)
            req.encoding = "gb2312"
            html = HTML(req.text)
            as_1 = html.xpath('//ul[@class="titime"]/li/a')
        except:
            continue
        print(u'正在抓取《立法草案》第%d页' % t)
        for i in as_1:
            url = i.attrib['href']
            targetURL.append(url)

    baseURL = 'http://www.law-lib.com/fzdt/sort21.asp?pageno=%d'
    for t in range(1,offset):

        pageURL = baseURL % t
        try:
            req = requests.get(pageURL)
            req.encoding = "gb2312"
            html = HTML(req.text)
            as_1 = html.xpath('//ul[@class="titime"]/li/a')
        except:
            continue
        print(u'正在抓取《法规释义》第%d页' % t)
        for i in as_1:
            url = i.attrib['href']
            targetURL.append(url)
    return targetURL

# 调用请求方法：xxx_run()
def lawlib_run(offset):
    for x in get_urls(offset):
        try:
            main(x)
        except Exception as e:
            print(e)
            pass


# lawlib_run(1)
