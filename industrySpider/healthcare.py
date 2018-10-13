from industrySpider.BaseSpider import *
import json
import time
# 文章索引起始页
startUrl = 'https://www.cn-healthcare.com/api/article/articlelist?data={"start":"%s","size":"10","arctype":"0"}'
# 网站作用域，用于page或图片地址补全
domainUrl = 'https://www.cn-healthcare.com/'
idpre = 'healthcare'
spider = BaseSpider()

# 请求头
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
}

# 文章索引寻址css选择器，选择至文章列表外层
index_css_selector = {
}

# 文章外层信息css选择器，视情况设定，例如：如下设定是因为外层文章列表包含完整标题、文章地址、发布时间、封面图、标签
info_css_selector = (

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
    content = requests.get(url)
    response = json.loads(content.text)
    # 总页数
    # print(response)
    count = response["count"]

    data = response["data"]
    flag = 0
    for x in range(len(data)):
        item = {}
        # 标题
        item["title"] = data[x]["title"]
        # id
        item["id"] = idpre + data[x]["url"].split('.')[0].split('/')[-1].replace('-','')
        # 发布时间
        publish_time = data[x]["pubdate"]
        timeArray = time.localtime(publish_time / 1000)
        item["noteDate"] = time.strftime("%Y-%m-%d", timeArray)
        # 文章url
        url = data[x]["url"]
        if "www.cn-healthcare.com" not in url:
            url_src = "https://www.cn-healthcare.com" + url
        else:
            url_src = url
        # 关键词
        item["tags"] = data[x]["keywords"]
        # 封面图
        img_src = data[x]["litpic"]
        if "www.cn-healthcare.com" not in img_src:
            coverPic = "https://www.cn-healthcare.com" + data[x]["litpic"]
        else:
            coverPic = img_src
        item["coverPic"] =coverPic
        # 封面图扩展名
        item["coverPicType"] = coverPic.split(".")[-1]
        # 文章类型
        stype = data[x]["stypename"]
        # 描述
        description = data[x]["description"]



        html = ""
        if stype != "视频":
            if "content" in data[x].keys():
                html = data[x]["content"]
            else:
                continue

        # 去除style
        re_content_style = re.compile(' style="(.*?)"')
        html = re_content_style.sub('', html)
        # item["htmlContent"] = "<body>" + "<h1>{}</h1>".format(item["title"]) + "<p>{}</p>".format(description) + html + "</body>"
        item["htmlContent"] = "<body>" + "<p>{}</p>".format(description) + html + "</body>"
        # 组织数据
        mydata = (
            item['id'],
            item['title'],
            item['noteDate'],
            item["htmlContent"],
            item["tags"],
            'TH007',
            item["coverPic"],
            item["coverPicType"],
            '健康界'
        )

        # 保存数据
        spider.save_data(mydata)


def healthcare_url(offset):
    '''
    返回一个url，
    :return: str
    '''
    for x in range(1, offset + 1):
        yield startUrl % str(x)


# 调用请求方法：xxx_run()
def healthcare_run(offset):
    for x in healthcare_url(offset):
        try:
            main(x)
        except Exception as e:
            print(e)
            pass


# healthcare_run(2)
