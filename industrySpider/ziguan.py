# -*- coding: utf-8 -*-
from industrySpider.BaseSpider import *
from bs4 import BeautifulSoup

# 文章索引起始页
startUrl = 'http://www.ziguan123.com/topic/index'
# 网站作用域，用于page或图片地址补全
domainUrl = 'http://www.ziguan123.com'
idpre = 'ziguan'
spider = BaseSpider()


def ziGuan_url(offset):
    '''
    返回一个url，
    :return: str
    '''
    url = startUrl + '?page='
    for x in range(1, offset + 1):
        yield url + str(x)


# 请求头
headers = {
    'content-length': '18',
    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'dnt': '1',
    'origin': 'http://www.ziguan123.com',
    'referer': 'http://www.ziguan123.com/topic/index',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.59 Safari/537.36 Avast/68.0.746.60',
    'x-requested-with': 'XMLHttpRequest'
}

# 文章索引寻址css选择器，选择至文章列表外层
index_css_selector = {
    'article': 'div#two_cat_content_1 ul li ',
}

# 文章外层信息css选择器，视情况设定，例如：如下设定是因为外层文章列表包含完整标题、文章地址、发布时间、封面图、标签
info_css_selector = (
    'div.wenzhanbox_img img::attr(src)',
    'div.wenzhanbox_text h2 a::text',
    'div.wenzhanbox_text h2 a::attr(href)',  # 连接
    'div.wenzhanbox_text div.inforbox div.inforbox_left span.ml10::text'  # 时间

)

# 文章内层css选择器，视情况而定，获取目标html或者补充外层无法获取的信息
article_css_selector = (
    'div.weizhang_main',
    'ul.mt20 > li.xght > div.tjzz_text >a::text'  # tag
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


# 主函数，用于获取数据和保存数据
def main(url):
    # data：网站请求参数

    # 获取索引页
    html = spider.get_article_index(url).text
    # 获取外层信息
    articleList = spider.parse_article_index(html, index_css_selector, info_css_selector)
    # 整理外层信息
    for item in articleList:
        print()
        S_imgUrl, S_title, S_articleUrl, S_time, = item
        imgUrl, articleUrl, time, title = ''.join(S_imgUrl.extract()), \
                                          ''.join(S_articleUrl.extract()), \
                                          ''.join(S_time.extract()), \
                                          ''.join(S_title.extract()), \
 \
            # 获取page页
        articleHtml = spider.get_article_detail(domainUrl + articleUrl).text
        # 获取内层信息
        articleInfo = spider.parse_article_detail(articleHtml, article_css_selector)
        tags = ''.join(articleInfo[1].extract())
        time = time.split(' ')[0]
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
            'TH002',
            coverPic,
            coverPicType,
            '资管网'
        )

        # 保存数据
        spider.save_data(data)


# 调用请求方法：xxx_run()
def ziguan_run(offset):
    for x in ziGuan_url(offset):
        try:
            main(x)
        except Exception as e:
            print(e)
            pass


# ziguan_run(1)
