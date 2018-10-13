# -*- coding: utf-8 -*-
from industrySpider.BaseSpider import *
import datetime

# 文章索引起始页
startUrl = 'http://zhoubianzijiayou.com/page/'
# 网站作用域，用于page或图片地址补全
domainUrl = 'http://zhoubianzijiayou.com'
idpre = 'zhoubianzijiayou'
spider = BaseSpider()


def xazbzjy_url(offset):
    '''
    返回一个url，
    :return: str
    '''
    for x in range(1, offset + 1):
        yield startUrl + str(x)


# 请求头
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
    'Referer': 'http://zhoubianzijiayou.com/page/1',
    'Host': 'zhoubianzijiayou.com',
    'Accept': 'text/html, */*; q=0.01',
    'Connection': 'keep-alive'
}

# 文章索引寻址css选择器，选择至文章列表外层
index_css_selector = {
    'article': 'div.content article.excerpt ',
}

# 文章外层信息css选择器，视情况设定，例如：如下设定是因为外层文章列表包含完整标题、文章地址、发布时间、封面图、标签
info_css_selector = (
    'header > h2 > a::text',
    'header > h2 > a::attr(href)',  # 连接
    'div.focus > a > img.thumb::attr(src)',  # 图片,
    'p.auth-span> span:nth-child(1)::text'  # 时间

)

# 文章内层css选择器，视情况而定，获取目标html或者补充外层无法获取的信息
article_css_selector = (
    'article.article-content',
    'head > meta:nth-child(5)::attr(content)',  # tag,
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


# 主函数，用于获取数据和保存数据
def main(url):
    # data：网站请求参数

    # 获取索引页
    html = spider.get_article_index(url, headers=headers).text
    # 获取外层信息
    articleList = spider.parse_article_index(html, index_css_selector, info_css_selector)
    # 整理外层信息
    for item in articleList:
        print()
        S_title, S_articleUrl, S_imgUrl, S_time, = item
        imgUrl, articleUrl, title = ''.join(S_imgUrl.extract()), \
                                    ''.join(S_articleUrl.extract()), \
                                    ''.join(S_title.extract()), \
 \
        # 获取page页
        articleHtml = spider.get_article_detail(articleUrl).text
        # 获取内层信息
        articleInfo = spider.parse_article_detail(articleHtml, article_css_selector)
        tags = ''.join(articleInfo[1].extract())
        noteDate = ''.join(S_time.extract())
        if '天' in noteDate.strip(''):
            numDate = re.sub("\D", "", noteDate)
            now_time = datetime.datetime.now()
            yes_time = now_time + datetime.timedelta(days=-int(numDate))
            time = yes_time.strftime('%Y-%m-%d')
        elif '分钟' in noteDate:
            numDate = re.sub("\D", "", noteDate)
            now_time = datetime.datetime.now()
            yes_time = now_time + datetime.timedelta(minutes=-int(numDate))
            time = yes_time.strftime('%Y-%m-%d')
        elif '小时' in noteDate:
            numDate = re.sub("\D", "", noteDate)
            now_time = datetime.datetime.now()
            yes_time = now_time + datetime.timedelta(minutes=-int(numDate))
            time = yes_time.strftime('%Y-%m-%d')
        elif '周' in noteDate:
            noteDate = noteDate.split('(')[1]
            noteDate = noteDate.split(')')[0]
            time = '2018-' + noteDate
        elif '月' in noteDate:
            noteDate = noteDate.split('(')[1]
            noteDate = noteDate.split(')')[0]
            time = '2018-' + noteDate
        elif '年' in noteDate:
            noteDate = noteDate.split('(')[1]
            noteDate = noteDate.split(')')[0]
            time = noteDate


        # 整理内层信息
        S_htmlContent = articleInfo[0]
        htmlContent = ''.join(S_htmlContent.extract()).split('<div class="article-social">')[0]
        finalcontent = spider.html_strip(htmlContent, stripItem)
        # 整理其他信息
        Id = idpre + articleUrl.split('.html')[0].split('.com/')[1].replace('-','')
        coverPic, coverPicType = spider.encode_img(imgUrl)
        coverPicType = coverPic.split('&')[0].split('.')[-1]
        # 保存数据

        # 组织数据
        data = (
            Id,
            title,
            time,
            finalcontent,
            tags,
            'XQ002',
            coverPic,
            coverPicType,
            '西安周边自驾游'
        )

        # 保存数据
        spider.save_data(data)


# 调用请求方法：xxx_run()
def xazbzjy_run(offset):
    for x in xazbzjy_url(offset):
        try:
            main(x)
        except Exception as e:
            print(e)
            pass

# xazbzjy_run(1)
