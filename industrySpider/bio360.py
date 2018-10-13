# -*- coding: utf-8 -*-
from industrySpider.BaseSpider import *
from bs4 import BeautifulSoup

spider = BaseSpider()

domainUrl = 'http://www.bio360.net'
formatUrl = 'http://www.bio360.net/article/ajax?&page=%s'
idpre = 'bio360'

# 请求头
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36',
    'Referer': 'http://www.bio360.net/article',
    'X-Anit-Forge-Code': "0",
    'Host': 'www.bio360.net',
    'Cache-Control': 'no-cache, private',
    'Connection': 'keep-alive',
    'Content-Encoding': 'gzip',
    'Vary': 'Accept-Encoding'
}

# 文章索引寻址css选择器，选择至文章列表外层
index_css_selector = {
    'article': 'div.news-list-tex',
}

# 文章外层信息css选择器，视情况设定，例如：如下设定是因为外层文章列表包含完整标题、文章地址、发布时间、封面图、标签
info_css_selector = (
    'h3 > a::text',
    'h3 > a::attr(href)',  # 连接
    'div.newcon > span::text'  #时间

)

# 文章内层css选择器，视情况而定，获取目标html或者补充外层无法获取的信息
article_css_selector = (
    'div.news-content',
    'head > meta:nth-child(7)::attr(content)'  # tags
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
    html = spider.get_article_index(url, headers=headers).text
    # 获取外层信息
    articleList = spider.parse_article_index(html, index_css_selector, info_css_selector)
    # 整理外层信息
    for item in articleList:
        S_title, S_articleUrl, S_time, = item
        articleUrl, title, time = ''.join(S_articleUrl.extract()), \
                                    ''.join(S_title.extract()), \
                                    ''.join(S_time.extract()), \
 \
            # 获取page页
        articleHtml = spider.get_article_detail(articleUrl).text

        # 获取内层信息
        articleInfo = spider.parse_article_detail(articleHtml, article_css_selector)
        # 整理内层信息
        S_htmlContent = dealContent(''.join(articleInfo[0].extract()),title)
        finalcontent = spider.html_strip(S_htmlContent, stripItem),
        tags = ''.join(articleInfo[1].extract())
        # 整理其他信息
        Id = idpre + articleUrl.split('/')[-1]

        coverPic = ''
        coverPicType = ''

        # 组织数据
        data = (
            Id,
            title,
            time,
            finalcontent,
            tags,
            'TH009',
            coverPic,
            coverPicType,
            '生物360'
        )
        # 保存数据
        spider.save_data(data)




def dealContent(content,title):
    wenzhang = content.split('<div class="news-content bg-fff box-border mb-10">')[1]
    htmlContent = wenzhang.split('<div class="mb-10">')[0]
    htmlContent = \
    htmlContent.split('<div class="statement" style="color: #6b6b6b; margin-bottom: 25px;font-size: 12px">')[0]
    htmlContents = htmlContent.split('<div class="article-content-body" id="article-content">')
    htmlContent1 = htmlContents[0]
    htmlContent1 = htmlContent1.split('<div class="item-meta col-sm-4"><i class="iconfont icon-cmt">&#xe610;</i>')[0]
    htmlContent1 = htmlContent1 + '</div></div>'
    htmlContent12 = '<div class="article-content-body" id="article-content">'
    htmlContent2 = htmlContents[1]
    htmlContent3 = htmlContent2.split('</aside>')[1]
    # 去掉a标签的href属性
    htmlContent3 = htmlContent3.replace('<a', '<span')
    htmlContent3 = htmlContent3.replace('</a>', '</span>')
    htmlContent = '<body>' + htmlContent1 + htmlContent12 + htmlContent3 + '</div></div></div>' + '</body>'
    htmlContent = htmlContent.replace('\\"', '')
    htmlContent = htmlContent.split('\\')[0]
    htmlContent = htmlContent.split('\r\n')[0]
    htmlContents = htmlContent.split('<div class="item-time col-sm-8">')
    htmlContent1 = htmlContents[0]
    htmlContent2 = htmlContents[1]
    htmlContent2 = htmlContent2.split('<div class="article-content-body" id="article-content">')[1]
    htmlContent = htmlContent1 + '<div class="article-content-body" id="article-content">' + htmlContent2
    htmlContent = htmlContent.replace(title, '')
    return htmlContent


def bio360_url(offset):
    urls = []
    for page in range(1, offset + 1):
        urls.append(formatUrl %str(page))
    return urls


# 调用请求方法：xxx_run()
def bio360_run(offset):
    for x in bio360_url(offset):
        try:
            main(x)
        except Exception as e:
            print(e)
            pass

# bio360_run(1)
