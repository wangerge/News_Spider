# -*- coding: utf-8 -*-
from industrySpider.BaseSpider import *
from bs4 import BeautifulSoup

spider = BaseSpider()

url = 'http://news.chemnet.com/list-14-11-{}.html'
url2 = 'http://news.chemnet.com/list-11-11-{}.html'
host = 'http://news.chemnet.com'
domainUrl = 'http://news.chemnet.com'
idpre = 'chemnet'

# 请求头
headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Host': 'news.chemnet.com',
    'Referer': 'http://news.chemnet.com/list-11-11-1.html',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.33 Safari/537.36'
}

# 文章索引寻址css选择器，选择至文章列表外层
index_css_selector = {
    'article': 'div.content-list ul li ',
}

# 文章外层信息css选择器，视情况设定，例如：如下设定是因为外层文章列表包含完整标题、文章地址、发布时间、封面图、标签
info_css_selector = (
    'a::text',
    'a::attr(href)',  # 连接
    'span::text'  # 时间

)

# 文章内层css选择器，视情况而定，获取目标html或者补充外层无法获取的信息
article_css_selector = (
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
def main(url, fenlei):
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

        time = time.split(' ')[-1]
        time = time.strip('')
        # 获取page页
        articleHtml = spider.get_article_detail(domainUrl + articleUrl).text

        # 获取内层信息
        # articleInfo = spider.parse_article_detail(articleHtml, article_css_selector)
        tags = fenlei

        S_htmlContent = dealContent(articleHtml)
        finalcontent = spider.html_strip(S_htmlContent, stripItem),
        # 整理其他信息
        Id = idpre + articleUrl.split('.')[0].split('/')[-1].split('-')[1]

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
            'TH008',
            coverPic,
            coverPicType,
            '化工网'
        )
        # 保存数据
        spider.save_data(data)


def dealContent(content):
    wenzhang = content.split('<div class="fl width665">')[1]
    htmlContent = wenzhang.split('<div class="tips mt50 font14px">&nbsp;&nbsp;文章关键词:　</div>')[0]
    htmlContent = "".join(htmlContent.split())
    htmlContents = htmlContent.split("http://china.chemnet.com/")
    htmlContent = htmlContents[0] + htmlContents[1]
    htmlContent = htmlContent.replace('<pclass="line22fontgrey">', '<pclass="line22fontgrey"><br>')
    htmlContent = '<body>' + htmlContent + '</body>'
    htmlContents = htmlContent.split('</p></div><divclass="detail-textline25font14px">')
    htmlContent2 = '</div><divclass="detail-textline25font14px">' + htmlContents[1]
    htmlContent1 = htmlContents[0]
    htmlContent1 = htmlContent1.split('<pclass="line22fontgrey">')[0]
    htmlContent = htmlContent1 + htmlContent2

    # 去标题
    htmlContents = htmlContent.split('<divclass="line35boldfont24fontblack">')
    htmlContent1 = htmlContents[0]
    htmlContent2 = htmlContents[1]
    htmlContent2 = htmlContent2.split('<divclass="detail-textline25font14px">')[1]
    htmlContent = htmlContent1 + '<divclass="detail-textline25font14px">' + htmlContent2
    return htmlContent


def make_huagong_url(offset):
    huagong = []
    for page in range(1, offset + 1):
        huagong.append(url.format(str(page)))
    return huagong


def make_nengyuan_url(offset):
    nengyuan = []
    for page in range(1, offset + 1):
        nengyuan.append(url2.format(str(page)))
    return nengyuan


# 调用请求方法：xxx_run()
def chemnet_run(offset):
    huagong_urls = make_huagong_url(offset)
    nengyuan_urls = make_nengyuan_url(offset)
    for huagong in huagong_urls:
        # try:
        main(huagong, '化工')
    for nengyuan in nengyuan_urls:
        # try:
            main(nengyuan, '能源')
        # except:
        #     print('error', nengyuan)


# chemnet_run(1)
