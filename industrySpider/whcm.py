# -*- coding: utf-8 -*-
from industrySpider.BaseSpider import *
from bs4 import BeautifulSoup

spider = BaseSpider()

domainUrl = 'http://media.people.com.cn'
idpre = 'whcm'

# 请求头
headers = {
    'Host': 'media.people.com.cn',
    'origin': 'http://media.people.com.cn',
    'referer': 'http://media.people.com.cn/GB/40606/index1.html',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
}

# 文章索引寻址css选择器，选择至文章列表外层
index_css_selector = {
    'article': 'div.ej_list_box li ',
}

# 文章外层信息css选择器，视情况设定，例如：如下设定是因为外层文章列表包含完整标题、文章地址、发布时间、封面图、标签
info_css_selector = (
    'a::text',
    'a::attr(href)',  # 连接
    'em::text'  # 时间

)

# 文章内层css选择器，视情况而定，获取目标html或者补充外层无法获取的信息
article_css_selector = (
    'div.text_con_left > div.box_con',
    'head > meta:nth-child(5)::attr(content)'

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
    ('原标题：.*</div>', re.I, '')
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
        S_title, S_articleUrl, S_time, = item
        articleUrl, title, time = ''.join(S_articleUrl.extract()), \
                                  ''.join(S_title.extract()), \
                                  ''.join(S_time.extract()), \
 \
            # 获取page页
        articleHtml = spider.get_article_detail(domainUrl + articleUrl)
        articleHtml = decodehtml(articleHtml)
        if not articleHtml:
            continue
        # 获取内层信息
        articleInfo = spider.parse_article_detail(articleHtml, article_css_selector)
        soup = BeautifulSoup(articleHtml, 'html.parser')
        tags = soup.find('meta', attrs={'name': 'keywords'})['content']
        # 整理内层信息
        finalcontent = spider.html_strip(''.join(articleInfo[0].extract()), stripItem)
        # 整理其他信息
        Id = idpre + articleUrl.split('.')[0].split('/')[-1].replace('-','')

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
            'TH005',
            coverPic,
            coverPicType,
            '人民网传媒'
        )
        # 保存数据
        spider.save_data(data)


def whcm_url(offset):
    '''
    返回一个url，
    :return: str
    '''
    url = 'http://media.people.com.cn/GB/40606/index%d.html'
    for x in range(1, offset + 1):
        yield url % x


# 调用请求方法：xxx_run()
def whcm_run(offset):
    for x in whcm_url(offset):
        try:
            main(x)
        except Exception as e:
            print(e)
            pass


# whcm_run(2)

