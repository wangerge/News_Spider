from industrySpider.BaseSpider import *
from bs4 import BeautifulSoup
import time
spider = BaseSpider()

domainUrl = 'https://www.leiphone.com'
idpre = 'leiphone'

# 请求头
headers = {
    'Cookie': 'PHPSESSID=dpanmcqejacvdhmo1e4vpu3cl7; Hm_lvt_0f7e8686c8fcc36f05ce11b84012d5ee=1535879043; leiphone_language=159a383283b5f2ec4a1a29abefa74092807e15f7s%3A2%3A%22cn%22%3B; Hm_lpvt_0f7e8686c8fcc36f05ce11b84012d5ee=1535887393',
    'Host': 'www.leiphone.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'

}

# 文章索引寻址css选择器，选择至文章列表外层
index_css_selector = {
    'article': 'body > div.lph-main.clr > div > div.lph-left.list-left > div.lph-pageList.list-pageList > div > ul > li',
}

# 文章外层信息css选择器，视情况设定，例如：如下设定是因为外层文章列表包含完整标题、文章地址、发布时间、封面图、标签
info_css_selector = (
    'div > div.word > h3 > a::text',
    'div > div.word > h3 > a::attr(href)',  # 连接
    'div > div.word > div.msg.clr > div.time::text',  # 时间,
    'div > div.img > a:nth-child(2) > img.lazy::attr(data-original)',
    'div > div.word > div.msg.clr > div.tags > a::text'

)

# 文章内层css选择器，视情况而定，获取目标html或者补充外层无法获取的信息
article_css_selector = (
    'div.content',
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
        S_title, S_articleUrl, S_time, S_imgurl, S_tags = item
        articleUrl, title, time, imgurl = ''.join(S_articleUrl.extract()), \
                                          ''.join(S_title.extract()), \
                                          ''.join(S_time.extract()), \
                                          ''.join(S_imgurl.extract()), \
 \

        tags = []
        if len(S_tags) > 1:
            for tag in S_tags:
                tags.append(''.join(tag.extract()))
        tags = ','.join(tags)
        title = re.sub("(\s+)|(:)", "", title)

        publish = set_time(time)
        time = publish.split(" ")[0]
            # 获取page页
        articleHtml = spider.get_article_detail(articleUrl)

        # 获取内层信息
        # articleInfo = spider.parse_article_detail(articleHtml, article_css_selector)
        soup = BeautifulSoup(articleHtml.text, 'html.parser')
        S_htmlContent = dealContent(soup)
        # 整理内层信息
        finalcontent = spider.html_strip(S_htmlContent, stripItem),
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
            'TH015',
            coverPic,
            coverPicType,
            '雷锋网'
        )

        # 保存数据
        spider.save_data(data)


# 转换时间
def set_time(datetime):
    if re.match('\d+小时前', datetime):
        hours = re.match('\d+', datetime).group()
        timestamp = int(hours) * 60 * 60
        datetime = time.strftime("%Y-%m-%d %H:%M", time.localtime(time.time() - timestamp))
    elif re.match('\d+分钟前', datetime):
        minutes = re.match('\d+', datetime).group()
        timestamp = int(minutes) * 60
        datetime = time.strftime("%Y-%m-%d %H:%M", time.localtime(time.time() - timestamp))
    elif re.match('昨天', datetime):
        day = re.findall('\d+:\d+', datetime)[0]
        datetime = time.strftime("%Y-%m-%d ", time.localtime(time.time() - 24 * 60 * 60)) + day
    elif re.match('\d+月\d+日', datetime):
        day = re.findall('\d+', datetime)
        datetime = "2018" + "-" + day[0] + "-" + day[1] + " " + day[2] + ":" + day[3]
    return datetime


def dealContent(soup):
    div = soup.find('div', class_='article-left')
    # 文章标题
    title = soup.find('h1', class_='headTit')
    # 导语
    lead = soup.find('div', class_='article-lead')
    ps = div.find_all('p')
    html = "" + str(title) + str(lead)
    for p in ps:
        # 去除原站元素
        not_crawl = re.compile(r"雷锋网|原标题|翻译|继续阅读|更多精彩内容|每日更新|手机端可以扫描二维码|视频原址")
        is_exist = re.findall(not_crawl, str(p))
        if not is_exist:
            html += str(p)
    # 去除二维码
    pic_parten = re.compile(r"""<img .*?>""", re.S)
    pic_list = re.findall(pic_parten, html)
    for pic in pic_list:
        if "5b552f8f06268.png" in pic:
            html = html.replace(pic, " ")
    for pic in pic_list:
        if "category" in pic:
            html = html.replace(pic, " ")
    # 去除a标签属性
    a_parten = re.compile(r"<a(.*?)>")
    html = re.sub(a_parten, " ", html)
    html = "<body>" + html + "</body>"
    content = str(html).replace("<html>", "").replace("</html>", "").replace(str(title), '').replace('......', '')
    return content


def leiphone_url(offset):
    '''
    返回一个url，
    :return: str
    '''
    url = 'https://www.leiphone.com/category/ai/page/'
    for x in range(1, offset + 1):
        yield url + str(x)


# 调用请求方法：xxx_run()
def leiphone_run(offset):
    for x in leiphone_url(offset):
        try:
            main(x)
        except Exception as e:
            print(e)
            pass


# leiphone_run(1)
