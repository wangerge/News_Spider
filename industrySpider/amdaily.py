# -*- coding: utf-8 -*-
from industrySpider.BaseSpider import *
from bs4 import BeautifulSoup

spider = BaseSpider()

startUrl = 'http://www.amdaily.com/Policy/index.html'
domainUrl = 'http://www.amdaily.com'
formatUrl = 'http://www.amdaily.com/Policy/{}.html'
idpre = 'amdaily'

# 请求头
headers = {
}

# 文章索引寻址css选择器，选择至文章列表外层
index_css_selector = {
    'article': 'div.list_a ul#cms_list li',
}

# 文章外层信息css选择器，视情况设定，例如：如下设定是因为外层文章列表包含完整标题、文章地址、发布时间、封面图、标签
info_css_selector = (
    'div.cntx > h4 > a::text',
    'div.cntx > h4 > a::attr(href)',  # 连接
    'div.img > a > img::attr(src)'  # 封面图

)

# 文章内层css选择器，视情况而定，获取目标html或者补充外层无法获取的信息
article_css_selector = (
    'div.article_con',
    'div.article > div.article_tit > span::text',  # 时间
    'head > meta:nth-child(6)::attr(content)'  # tags
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
    (r'(相关热词搜索|内容关联投票).*', re.I, '')
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
    html = spider.get_article_index(url, headers=headers)
    html = decodehtml(html)
    if not html:
        return
    # 获取外层信息
    articleList = spider.parse_article_index(html, index_css_selector, info_css_selector)
    # 整理外层信息
    for item in articleList:
        S_title, S_articleUrl, S_imgUrl, = item
        articleUrl, title, imgurl = ''.join(S_articleUrl.extract()), \
                                    ''.join(S_title.extract()), \
                                    ''.join(S_imgUrl.extract()), \
 \
            # 获取page页
        articleHtml = spider.get_article_detail(articleUrl)
        articleHtml = decodehtml(articleHtml)
        if not articleHtml:
            continue
        # 获取内层信息
        articleInfo = spider.parse_article_detail(articleHtml, article_css_selector)
        # 整理内层信息
        finalcontent = spider.html_strip(''.join(articleInfo[0].extract()), stripItem),
        time = ''.join(articleInfo[1].extract()).split("来源")[0].strip()
        tags = ''.join(articleInfo[2].extract())
        # 整理其他信息
        Id = idpre + articleUrl.split('.')[2].split('/')[-1]

        coverPic, coverPicType = spider.encode_img(imgurl)

        # 组织数据
        data = (
            Id,
            title,
            time,
            finalcontent,
            tags,
            'TH016',
            coverPic,
            coverPicType,
            '先进制造业'
        )
        # 保存数据
        spider.save_data(data)


def amdaily_url(offset):
    urls = [startUrl]
    for page in range(2, offset + 1):
        urls.append(formatUrl.format(str(page)))
    return urls


# 调用请求方法：xxx_run()
def amdaily_run(offset):
    for x in amdaily_url(offset):
        try:
            main(x)
        except Exception as e:
            print(e)
            pass


# amdaily_run(2)
