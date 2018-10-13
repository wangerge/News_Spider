# -*- coding: utf-8 -*-
from industrySpider.BaseSpider import *
from bs4 import BeautifulSoup
import time

spider = BaseSpider()

domainUrl = 'https://www.hiyd.com/jianshen/'
idpre = 'hiyd'

# 请求头
headers = {

    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'

}

# 文章索引寻址css选择器，选择至文章列表外层
index_css_selector = {
    'article': 'div.list-bd > ul > li',
}

# 文章外层信息css选择器，视情况设定，例如：如下设定是因为外层文章列表包含完整标题、文章地址、发布时间、封面图、标签
info_css_selector = (
    'div.item-content > h2 > a::text',
    'div.item-content > h2 > a::attr(href)',  # 连接
    'div.item-content > em::text',  # 时间,
    'div.item-pic > a > img::attr(src)',

)

# 文章内层css选择器，视情况而定，获取目标html或者补充外层无法获取的信息
article_css_selector = (
    'div.article-text',
    'div > div.article-meta > div.tag-list > ul > li::text'
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
    ('<strong>健身就用hi运动.*', re.I, ''),

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
        S_title, S_articleUrl, S_time, S_imgurl = item
        articleUrl, title, time, imgurl = ''.join(S_articleUrl.extract()), \
                                          ''.join(S_title.extract()), \
                                          ''.join(S_time.extract()), \
                                          ''.join(S_imgurl.extract()), \
 \

        tags = ''
        time_parten = re.compile(r"(\d{4}-\d{1,2}-\d{1,2}\s\d{1,2}:\d{1,2})")
        time = time_parten.findall(time)[0].split(" ")[0]
        # 获取page页
        articleHtml = spider.get_article_detail("https:" + articleUrl).text

        # 获取内层信息
        articleInfo = spider.parse_article_detail(articleHtml, article_css_selector)
        # 整理内层信息
        finalcontent = spider.html_strip(''.join(articleInfo[0].extract()), stripItem),
        # 整理其他信息
        Id = idpre + articleUrl.split('/')[-1].split('.')[0]
        coverPic, coverPicType = spider.encode_img(imgurl.split("?")[0])
        if imgurl[-1] == '.':
            coverPic = coverPic + '?imageview/format/webp'
            coverPicType = 'jpg'

        # 组织数据
        data = (
            Id,
            title,
            time,
            finalcontent,
            tags,
            'TH011',
            coverPic,
            coverPicType,
            'Hi健身'
        )

        # 保存数据
        spider.save_data(data)


def hiyd_url(offset):
    url_list = ["https://www.hiyd.com/zengji/?page=",
                "https://www.hiyd.com/jianfei/?page=",
                "https://www.hiyd.com/jianshenzhishi/?page=",
                "https://www.hiyd.com/yuga/?page="]
    for url in url_list:
        for x in range(1, offset + 1):
            yield url + str(x)


# 调用请求方法：xxx_run()
def hiyd_run(offset):
    for x in hiyd_url(offset):
        try:
            main(x)
        except Exception as e:
            print(e)
            pass


# hiyd_run(2)
