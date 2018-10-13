from industrySpider.BaseSpider import *
from bs4 import BeautifulSoup
spider = BaseSpider()

url = 'http://www.xaedu.sn.cn/jyzw/tzwj/index_{}.shtml'
url2 = 'http://www.xaedu.sn.cn/xwzx/jyyw/index_{}.shtml'
host = 'http://www.xaedu.sn.cn'
index_url = 'http://www.xaedu.sn.cn/jyzw/tzwj/'
index_url2 = 'http://www.xaedu.sn.cn/xwzx/jyyw/'
domainUrl = 'http://www.xaedu.sn.cn'
idpre = 'xaedu'

# 请求头
headers = {
    "User-Agent": "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Maxthon 2.0)",

}

# 文章索引寻址css选择器，选择至文章列表外层
index_css_selector = {
    'article': 'div.col-md-8 ul li ',
}

# 文章外层信息css选择器，视情况设定，例如：如下设定是因为外层文章列表包含完整标题、文章地址、发布时间、封面图、标签
info_css_selector = (
    'a::text',
    'a::attr(href)',  # 连接
    'span::text'  # 时间

)

# 文章内层css选择器，视情况而定，获取目标html或者补充外层无法获取的信息
article_css_selector = (
    'div.content'
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
    except Exception :
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
        # articleInfo = spider.parse_article_detail(articleHtml, article_css_selector)
        tags = ''

        soup = BeautifulSoup(articleHtml, "lxml")
        if len(soup.select('.content'))>0:
            html_main = soup.select('.content')[0]
        else:
            continue
        # 整理内层信息
        S_htmlContent = '<body>' + str(change_img_link(html_main)) + '</body>'
        finalcontent = spider.html_strip(S_htmlContent, stripItem),
        # 整理其他信息
        Id = idpre+articleUrl.split('.')[0].split('/')[-1]

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
            'TH010',
            coverPic,
            coverPicType,
            '西安教育网'
        )

        # 保存数据
        spider.save_data(data)



def change_img_link(htmlcontext):
    soup = htmlcontext
    for item in soup.select('img'):
        url = item.get('src')
        url = host+url
        item['src'] = url

        # str_item = str (item)
        # a= str_item.split('c="')
        # re_img = a[0]+'c="'+'http://www.xaedu.sn.cn'+a[1]
        # soup = str(soup).replace(re_img,str_item)
    return soup



def make_tongzhi_url(offset):
    tongzhi = [index_url]
    for page in range(2, offset):
        tongzhi.append(url.format(str(page)))
    return tongzhi


def make_news_url(offset):
    news = [index_url2]
    for page in range(2, offset):
        news.append(url2.format(str(page)))
    return news


# 调用请求方法：xxx_run()
def xaedu_run(offset):
    tongzhi_urls = make_tongzhi_url(offset)
    xinwens = make_news_url(offset)
    for xinwen in xinwens:
        # try:
        main(xinwen)
    for tongzhi_url in tongzhi_urls:
        try:
            main(tongzhi_url)
        except:
            print('error', tongzhi_url)




# xaedu_run(1)
