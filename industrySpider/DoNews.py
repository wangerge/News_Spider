# -*- coding: utf-8 -*-
from industrySpider.BaseSpider import *
from bs4 import BeautifulSoup
from lxml.etree import HTML
from lxml import html as HTMLParser
from selenium import webdriver
import datetime
import time

spider = BaseSpider()

domainUrl = 'http://www.donews.com'
idpre = 'donews'

# 请求头
headers = {

}

# 文章索引寻址css选择器，选择至文章列表外层
index_css_selector = {
    'article': 'dl.block',
}

# 文章外层信息css选择器，视情况设定，例如：如下设定是因为外层文章列表包含完整标题、文章地址、发布时间、封面图、标签
info_css_selector = (
    'dd > h3 > a::text',
    'dd > h3 > a::attr(href)',  # 连接
    'dt > a > img::attr(src)'

)

# 文章内层css选择器，视情况而定，获取目标html或者补充外层无法获取的信息
article_css_selector = (
    'div.article-con',
    'div.tag > p.fl > span:nth-child(2)::text'  # tags
)
# html整理、清洗正则规则；（正则表达式、匹配方式，替换字符串）
stripItem = [
    ('<script.*?</script>', re.S, ''),
    ('<iframe.*?</iframe>', re.I, ''),
    ('<a.*?>', re.I, ''),
    ('</a>', re.I, ''),
    ('style=".*?"', re.I, ''),
    ('height=".*?"', re.I, ''),
    ('width=".*?"', re.I, ''),
    (r'(特别声明).*', re.I, '')
]


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


def dealContent(itemHTML):
    s = "<body><div>" + itemHTML + '</div></body>'
    s = s.replace('\n', '').replace('\r', '').replace('"', "'")
    return s


# 主函数，用于获取数据和保存数据
def main(content):
    # data：网站请求参数
    # 获取外层信息
    articleList = spider.parse_article_index(content.get_attribute('outerHTML'), index_css_selector, info_css_selector)
    print(articleList)
    # 整理外层信息
    for item in articleList:
        S_title, S_articleUrl, S_imgurl = item
        articleUrl, title, imgUrl = ''.join(S_articleUrl.extract()), \
                                    ''.join(S_title.extract()), \
                                    ''.join(S_imgurl.extract())
        # 获取page页
        if domainUrl not in articleUrl:
            articleUrl = domainUrl + articleUrl
        articleHtml = spider.get_article_detail(articleUrl,headers=headers,stream=False,timeout=500)

        # 获取内层信息
        articleInfo = spider.parse_article_detail(articleHtml.text, article_css_selector)

        tags = ''
        time = ''.join(articleInfo[1].extract()).split(' ')[0]
        # 整理内层信息
        S_htmlContent = dealContent(''.join(articleInfo[0].extract()))
        finalcontent = spider.html_strip(S_htmlContent, stripItem),
        # 整理其他信息
        Id = idpre + articleUrl.split('.')[2].split('/')[-1]

        coverPic, coverPicType = spider.encode_img(imgUrl)

        # 组织数据
        data = (
            Id,
            title,
            time,
            finalcontent,
            tags,
            'TH001',
            coverPic,
            coverPicType,
            'DoNews'
        )
        # 保存数据
        spider.save_data(data)


# 调用请求方法：xxx_run()
def DoNews_run(offset):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_options.add_experimental_option('prefs', prefs)
    try:
        browser = webdriver.Chrome(chrome_options=chrome_options, executable_path='./bin/chromedriver')
    except:
        browser = webdriver.Chrome(chrome_options=chrome_options, executable_path='./bin/chromedriver.exe')

    for lanbu in ['http://www.donews.com/idonews', 'http://www.donews.com/company/index',
                  'http://www.donews.com/business/index', 'http://www.donews.com/technology/index']:
        for t in range(offset):
            browser.get(lanbu)
            try:
                browser.find_element_by_id('loadmore').click()
            except Exception as e:
                print(e)
                break
            time.sleep(1)
        contents = browser.find_elements_by_xpath('//div[@class="block ng-scope"]/dl')
        for item in contents:
            main(item)


# DoNews_run(1)
