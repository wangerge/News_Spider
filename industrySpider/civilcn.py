# -*- coding: utf-8 -*-
from industrySpider.BaseSpider import *
from bs4 import BeautifulSoup

spider = BaseSpider()

urls = ['http://www.civilcn.com/zhishi/jzsj/index.html',  # 建筑设计知识
        'http://www.civilcn.com/zhishi/jggc/index.html',  # 结构设计知识
        'http://www.civilcn.com/zhishi/ytgc/index.html',  # 岩土工程知识
        'http://www.civilcn.com/zhishi/jzdq/index.html',  # 建筑电气
        'http://www.civilcn.com/zhishi/gczj/index.html',  # 工程造价
        'http://www.civilcn.com/zhishi/gcht/index.html',  # 工程合同知识
        'http://www.civilcn.com/zhishi/sgjs/index.html',  # 施工技术
        'http://www.civilcn.com/zhishi/aqwm/index.html',  # 安全文明
        'http://www.civilcn.com/zhishi/szgch/index.html',  # 市政工程知识
        'http://www.civilcn.com/zhishi/gsps/index.html']  # 给水排水知识

domainUrl = 'http://www.civilcn.com'
idpre = 'civilcn'

# 请求头
headers = {
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.8',
    'Cache-Control': 'max-age=0',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36',
    'Connection': 'keep-alive',
    'Referer': 'http://www.civilcn.com/zhishi/'

}

# 文章索引寻址css选择器，选择至文章列表外层
index_css_selector = {
    'article': 'div.m_g_b_d > ul > li > span.lefter ',
}

# 文章外层信息css选择器，视情况设定，例如：如下设定是因为外层文章列表包含完整标题、文章地址、发布时间、封面图、标签
info_css_selector = (
    'a::text',
    'a::attr(href)',  # 连接
)

# 文章内层css选择器，视情况而定，获取目标html或者补充外层无法获取的信息
article_css_selector = (
    'div.m_g_content',
    'head > meta:nth-child(5)::attr(content)',
    'div.m_g_infor > strong::text'
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


def dealContent(htmlContent, title):
    add_div = '<div class="m_g"><div class="m_g_title"><strong>{}</strong></div>'
    htmlContent = add_div.format(title) + htmlContent + '</div>'
    htmlContent = htmlContent.replace('<html>', "").replace('</html>', '').replace('\n', '').replace(title,'')
    return htmlContent


# 主函数，用于获取数据和保存数据
def main(url):
    # data：网站请求参数

    # 获取索引页
    html = spider.get_article_index(url, headers=headers)
    # 获取外层信息
    articleList = spider.parse_article_index(html.text, index_css_selector, info_css_selector)
    # 整理外层信息
    for item in articleList:
        S_title, S_articleUrl = item
        articleUrl, title = ''.join(S_articleUrl.extract()), \
                            ''.join(S_title.extract()), \
 \
            # 获取page页
        articleHtml = spider.get_article_detail(articleUrl)
        # 获取内层信息
        articleInfo = spider.parse_article_detail(articleHtml.text, article_css_selector)
        tags = ''.join(articleInfo[1].extract())
        time = ''.join(articleInfo[2].extract()).split(' ')[0].split("：")[1]

        # 整理内层信息
        S_htmlContent = dealContent(''.join(articleInfo[0].extract()), title)
        finalcontent = spider.html_strip(S_htmlContent, stripItem),
        # 整理其他信息
        Id = idpre + articleUrl.split('.')[2].split('/')[-1]

        # 无封面图
        coverPic = ''
        # 无封面图片扩展名
        coverPicType = ''

        # 组织数据
        data = (
            Id,
            title,
            time,
            finalcontent,
            tags,
            'TH004',
            coverPic,
            coverPicType,
            '土木工程网'
        )

        # 保存数据
        spider.save_data(data)


def get_urls(offset):
    re_url = []
    for url in urls:
        re_url.append(url)
        for page in range(2, offset):
            re_url.append(''.join(url.split('.')[:-1]) + '_' + str(page) + '.html')
    return re_url


# 调用请求方法：xxx_run()
def civilcn_run(offset):
    urls = get_urls(offset)

    for url in urls:
        try:
            main(url)
        except Exception as e:
            print('error', url)


# civilcn_run(2)
