

from industrySpider.BaseSpider import *

# 文章索引起始页
startUrl = [
        'http://www.fangchan.com/plus/nlist.php?tid=2&tags=%E5%8E%9F%E5%88%9B',
        'http://www.fangchan.com/plus/nlist.php?tid=2&column=%E5%AE%8F%E8%A7%82',
        'http://www.fangchan.com/news/6/p',
        'http://www.fangchan.com/news/1/p',
        'http://www.fangchan.com/news/9/p',
        'http://www.fangchan.com/news/5/p',
        'http://www.fangchan.com/news/7/p',
        'http://www.fangchan.com/news/4/p',
        'http://www.fangchan.com/news/8/p',
        'http://www.fangchan.com/news/3/p',
]
# 网站作用域，用于page或图片地址补全
domainUrl = 'http://www.fangchan.com'
idpre = 'zhongfang'
spider = BaseSpider()



# 请求头
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
}

# 文章索引寻址css选择器，选择至文章列表外层
index_css_selector = {
    'article': 'ul.related-news-list >li ',
}

# 文章外层信息css选择器，视情况设定，例如：如下设定是因为外层文章列表包含完整标题、文章地址、发布时间、封面图、标签
info_css_selector = (
    'a::attr(href)',  # 连接
    'a::text',  # 标题
    'span::text'  # 时间
)

# 文章内层css选择器，视情况而定，获取目标html或者补充外层无法获取的信息
article_css_selector = (
    'div.summary-text',
    'head > meta:nth-child(7)::attr(content)',  # tag,
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

    # 获取索引页
    html = spider.get_article_index(url, headers=headers).text
    # 获取外层信息
    articleList = spider.parse_article_index(html, index_css_selector, info_css_selector)
    # 整理外层信息
    for item in articleList:
        S_articleUrl, S_title, S_time, = item
        articleUrl, title, time = ''.join(S_articleUrl.extract()), \
                                  ''.join(S_title.extract()), \
                                  ''.join(S_time.extract()), \

        # 获取page页
        articleHtml = spider.get_article_detail(articleUrl)
        myarticleHtml = decodehtml(articleHtml)
        # 获取内层信息
        articleInfo = spider.parse_article_detail(myarticleHtml, article_css_selector)
        tags = ''.join(articleInfo[1].extract())
        # 整理内层信息
        S_htmlContent = articleInfo[0]
        htmlContent = ''.join(S_htmlContent.extract())
        # 整理其他信息
        Id = idpre+articleUrl.split('.')[-2].split('/')[-1]
        # 无封面图
        coverPic = ''
        # 无封面图片扩展名
        coverPicType = ''
        # 保存数据

        # 组织数据
        data = (
            Id,
            title,
            time,
            spider.html_strip(htmlContent, stripItem),
            tags,
            'TH003',
            coverPic,
            coverPicType,
            '中房网'
        )

        # 保存数据
        spider.save_data(data)



def zhongfang_url(offset):
    '''
    返回一个url，
    :return: str
    '''
    for url in startUrl:
        if 'news' not in url:
            url = url + '&page='
        for x in range(1, offset + 1):
            yield url + str(x)



# 调用请求方法：xxx_run()
def zhongfang_run(offset):
    for x in zhongfang_url(offset):
        try:
            main(x)
        except Exception as e:
            print(e)
            pass


# zhongfang_run(1)
