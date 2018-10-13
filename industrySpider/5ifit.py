# -*- coding: utf-8 -*-
from industrySpider.BaseSpider import *
from bs4 import BeautifulSoup
from scrapy import Selector
import time
from selenium import webdriver
# 网站作用域，用于page或图片地址补全
domainUrl = 'http://www.5ifit.com'
idpre = '5ifit'
spider = BaseSpider()

# 请求头
headers = {
    "Accept": 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    "Connection": 'keep-alive',
    "Host": 'www.5ifit.com',
    "Pragma": 'no-cache',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
}

# 文章索引寻址css选择器'，选择至文章列表外层
index_css_selector = {
    'article': 'div.list-box ul li ',
}

# 文章外层信息css选择器，视情况设定，例如：如下设定是因为外层文章列表包含完整标题、文章地址、发布时间、封面图、标签
info_css_selector = (
    'div.list-img a img::attr(src)',
    'div.list-txt h4 a::text',
    'div.list-txt h4 a::attr(href)',  # 连接
    'div.list-txt > span:nth-child(2)::text'  # 时间

)

# 文章内层css选择器，视情况而定，获取目标html或者补充外层无法获取的信息
article_css_selector = (
    'div.txt-main',
    'head > meta:nth-child(4)::attr(content)'  # tag
)

# html整理、清洗正则规则；（正则表达式、匹配方式，替换字符串）
stripItem = [
    ('<script.*?</script>', re.S, ''),
    ('<iframe.*?</iframe>', re.I, ''),
    ('<a.*?>', re.I, ''),
    ('</a>', re.I, ''),
    ('style=".*?;"', re.I, ''),
    ('height=".*?"', re.I, ''),
    ('width=".*?"', re.I, '')
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


# 主函数，用于获取数据和保存数据
def main(url):
    # data：网站请求参数

    # 获取索引页
    html = spider.get_article_index(url,headers=headers)
    html = decodehtml(html)
    # 获取外层信息
    articleList = spider.parse_article_index(html, index_css_selector, info_css_selector)
    # 整理外层信息
    for item in articleList:

        S_imgUrl, S_title, S_articleUrl, S_time, = item
        imgUrl, articleUrl, mytime, title = ''.join(S_imgUrl.extract()), \
                                          ''.join(S_articleUrl.extract()), \
                                          ''.join(S_time.extract()), \
                                          ''.join(S_title.extract()), \
 \


        # 获取page页
        articleHtml = spider.get_article_detail(articleUrl,headers=headers)
        articleHtml = decodehtml(articleHtml)
        # 获取内层信息
        articleInfo = spider.parse_article_detail(articleHtml, article_css_selector)
        tags = ''.join(articleInfo[1].extract())
        time = mytime.split('：')[1].strip()
        # 整理内层信息
        S_htmlContent = articleInfo[0]
        htmlContent = ''.join(S_htmlContent.extract())
        finalcontent = spider.html_strip(htmlContent, stripItem),
        # 整理其他信息
        Id = idpre + articleUrl.split('/')[-1]
        coverPic, coverPicType = spider.encode_img(imgUrl)

        # 组织数据
        data = (
            Id,
            title,
            time,
            finalcontent,
            tags,
            'TH019',
            coverPic,
            coverPicType,
            '健网'
        )

        # 保存数据
        if data[0] != 'ziguan':
            spider.save_data(data)


def web5ifit_url(offset):
    re_url = []
    # chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument('--headless')
    # chrome_options.add_argument('--disable-gpu')
    # browser = webdriver.Chrome(chrome_options=chrome_options, executable_path='./bin/chromedriver.exe')
    # browser.get('http://www.5ifit.com/news/zengjifood')
    # browser.maximize_window()
    # time.sleep(1)
    # article_html_index = browser.find_elements_by_xpath('//*[@id="category"]/a')

    response = requests.get('http://www.5ifit.com/news/zengjifood',  headers=headers)
    html = decodehtml(response)
    selector = Selector(text=html)
    article_html_index = selector.css('div#category >a::attr(href)')

    for item in article_html_index:

        re_url.append(''.join(item.extract()))
    final_url =[]
    for url in re_url:
        final_url.append(url)
        for page in range(2, offset+1):
            final_url.append(url + '/list_' + str(page) + '.html')
    return final_url


# 调用请求方法：xxx_run()
def web5ifit_run(offset):
    for x in web5ifit_url(offset):
        try:
            main(x)
        except Exception as e:
            print(e)
            pass


web5ifit_run(1)
