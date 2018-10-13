# -*- coding: utf-8 -*-
from industrySpider.BaseSpider import *
from bs4 import BeautifulSoup
from lxml.etree import HTML
from lxml import html as HTMLParser
from selenium import webdriver
import datetime
import time

spider = BaseSpider()

domainUrl = 'http://www.ccidcom.com'
idpre = 'ccid'

# 请求头
headers = {

}

# 文章索引寻址css选择器，选择至文章列表外层
index_css_selector = {
    'article': 'div.article-item',
}

# 文章外层信息css选择器，视情况设定，例如：如下设定是因为外层文章列表包含完整标题、文章地址、发布时间、封面图、标签
info_css_selector = (
    'div.article-cont  > div.title > a > font::text',
    'div.article-cont  > div.title >  a::attr(href)',  # 连接
    'div.article-cont > div.info > span.time::text',  # 时间
    'img::attr(src)'

)

# 文章内层css选择器，视情况而定，获取目标html或者补充外层无法获取的信息
article_css_selector = (
    'div#article > div.content',
    'head > meta:nth-child(2)::attr(content)'  # tags
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


def precessDate(noteDate):
    today = datetime.datetime.now()
    today_ = datetime.datetime.strftime(today, '%Y-%m-%d')
    yesterday = today - datetime.timedelta(1)
    yesterday_ = datetime.datetime.strftime(yesterday, '%Y-%m-%d')
    yesyesterday = today - datetime.timedelta(2)
    yesyesterday_ = datetime.datetime.strftime(yesyesterday, '%Y-%m-%d')

    if u'今天' in noteDate:
        noteDate_s = today_
    elif u'昨天' in noteDate:
        noteDate_s = yesterday_
    elif u'前天' in noteDate:
        noteDate_s = yesyesterday_
    elif u'小时前' in noteDate:
        noteDate_s = datetime.datetime.strftime(today, '%Y-%m-%d')
    elif u'分' in noteDate:
        noteDate_s = datetime.datetime.strftime(today, '%Y-%m-%d')
    else:
        noteDate_s = '2018-' + noteDate.split(' ')[0]
    return noteDate_s


def decodehtml(req):
    try:
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
    except Exception:
        return False


# 主函数，用于获取数据和保存数据
def main(content):
    # data：网站请求参数
    # 获取外层信息
    articleList = spider.parse_article_index(content.get_attribute('outerHTML'), index_css_selector, info_css_selector)
    # 整理外层信息
    for item in articleList:
        S_title, S_articleUrl, S_time, S_imgurl = item
        articleUrl, title, time, imgUrl = ''.join(S_articleUrl.extract()), \
                                          ''.join(S_title.extract()), \
                                          ''.join(S_time.extract()), \
                                          ''.join(S_imgurl.extract())

        try:
            noteDate = precessDate(time)
        except:
            print(u'获取文章发布时间存在问题！')
            noteDate = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M')
        print(u'    该文章发布的时间为：', noteDate)

        timesplit = noteDate.split('-')
        if len(timesplit[1]) == 1:
            timesplit[1] = '0'+timesplit[1]
        time = '-'.join(timesplit)
        # 获取page页
        articleHtml = spider.get_article_detail(domainUrl + articleUrl, headers=headers, stream=False, timeout=500)
        articleHtml = decodehtml(articleHtml)

        # 获取内层信息
        articleInfo = spider.parse_article_detail(articleHtml, article_css_selector)

        tags = ''.join(articleInfo[1].extract())
        # 整理内层信息
        finalcontent = spider.html_strip(''.join(articleInfo[0].extract()), stripItem).replace('"',"'").replace('【通信产业网讯】','')
        # 整理其他信息
        sufix = articleUrl.split('.')[0].split('/')[-1]
        if len(sufix) > 20:
            sufix = sufix[-20:]
        Id = idpre + sufix

        coverPic, coverPicType = spider.encode_img(imgUrl)

        # 组织数据
        data = (
            Id,
            title,
            time,
            finalcontent,
            tags,
            'TH012',
            coverPic,
            coverPicType,
            '通讯产业网'
        )
        # 保存数据
        # spider.save_data(data)


# 调用请求方法：xxx_run()
def ccid_run(offset):
    # browser = webdriver.Chrome()
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    browser = webdriver.Chrome(chrome_options=chrome_options, executable_path='./bin/chromedriver.exe')
    browser.get('http://www.ccidcom.com/yaowen/index.html')
    browser.maximize_window()
    time.sleep(3)

    for t in range(offset):
        browser.find_element_by_id('loadmore').click()
        time.sleep(1)
    contents = browser.find_elements_by_xpath('//div[@class="artlisting"]/div[@class="article-item"]')
    for item in contents:
        main(item)


# ccid_run(2)
