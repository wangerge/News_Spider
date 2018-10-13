# -*- coding: utf-8 -*-

from industrySpider.BaseSpider import *

# 文章索引起始页
startUrl = 'http://chinacwa.com/sitefiles/services/cms/dynamic/output.aspx?publishmentSystemID=1&'
# 网站作用域，用于page或图片地址补全
domainUrl = 'http://chinacwa.com'
spider = BaseSpider()
idpre = 'chinacwa'
# 请求头
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36',
    'Referer': 'http://chinacwa.com/chcontents/zx/index.shtml',
    'X-Requested-With': "XMLHttpRequest",
    'Cookie': 'UM_distinctid=164f843ba6fea-0b142da65652e9-54143315-1fa400-164f843ba7111b; CNZZDATA1256166743=1274670155-1533173520-%7C1533173520',
    'Host': 'chinacwa.com',
    'Origin': 'http://chinacwa.com',
    'Vary': 'Accept-Encoding'
}

# 文章索引寻址css选择器，选择至文章列表外层
index_css_selector = {
    'article': 'ul.zx_conul li',
}

# 文章外层信息css选择器，视情况设定，例如：如下设定是因为外层文章列表包含完整标题、文章地址、发布时间、封面图、标签
info_css_selector = (
    'h3 a::text',
    'h3 a::attr(href)',
    'span > span::text',
    'p > a.zx_conimg > img::attr(src)'
)

# 文章内层css选择器，视情况而定，获取目标html或者补充外层无法获取的信息
article_css_selector = (
    'div.conleft_01.margin_bottom20 > div.content_con > div.conten',
    'head > meta:nth-child(5)::attr(content)'
)

# html整理、清洗正则规则；（正则表达式、匹配方式，替换字符串）
stripItem = [
    ('<script.*?</script>', re.S, ''),
    ('<iframe.*?</iframe>', re.I, ''),
    ('<a.*?>', re.I, ''),
    ('</a>', re.I, ''),
    ('style=.*?>', re.I, '>'),
    ('height=".*?"', re.I, ''),
    ('width=".*?"', re.I, ''),
    ('\$.*?\$', re.I, '')
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
def main(offset):
    # data：网站请求参数
    data = {
        'pageNodeID': 2,
        'pageContentID': 0,
        'pageTemplateID': 14,
        'isPageRefresh': False,
        'pageUrl': 'R4Rj2hdTX5575jyOb3HzEkmPEqQGwfob8myPj9ZmXht2txbgcyRR0slash0HXTsj9h5bJcIOX0add0JgVAZPE0equals0',
        'ajaxDivID': 'ajaxElement_1_495',
        'templateContent': '0wB0slash0c4laF4d7fB8Z9k0slash0sfpdHIzI2g1Xf2r4XRW4l7Apl16PcWMKf5wojST2j53Pq0add0EzPQbYOZxegD6JNZZZH2sUe8GQXmNqMTrjC7G6menIpnic1q8cv5lbzesBSH9LmZqaN0slash0HhSIHyVVgysCNC0add0PzEPk5VJ0GzTl9Co9sjMBcYGxtYlgRJOL4U5VLF3Cmj1O0add0ThMCUQL2mlf59XdL4IngQ0mZXms3UbVkrDtR9IK52JPO4EyC6SFex86VLwJIg0ANz0slash0Ll56ekCunRLkqne50add0qpNVnl5YjFTBmp0slash0m41LXhOYB9zuTMhp33P7Mbpa2FDan0add0sITeF34m7TmkzCOVGpRackoavEKy4E8QHqpMw0slash0Ef0DlW0slash0FltqwjSY2tVh6YR7QnPau8z00add0RZodN9FR5rSaxw6QNEpqkU03SDS6poJNvf9M3ZBfo4pejt3iwZvVsuv6Ia1lz6oVwqNAh4sc0slash0CTbzrjAyVCHM6Ut2sZHTUTcULUpRGUDRqsK1JF8vvDfbBkCSfGj8lV6TDcNhHcmhN77MYPqMXsj7HvvoF0slash0rOr0add0HXEAjwsgSX2HRIF22hPFUWQTuZpal0add0ukuB2H0slash04bf0slash0Om4oJ90slash0A0slash0ky6lkeiQbFknWfeOrx5g3F5blp4UP57E3em8cQvZxrRxxpeaY9ytoQaPU7SrZeICT5ka7aF1ts9EHU0slash0PGzKcqEtR7yB7Imbbaz8Q0zqE2TkbMbmJpfzBj4VdOXfF0N3RbJzIpjK20slash08xmk8i0slash095BPTOj60add03PPbuEVKoVl6YIFXOaietwZpt8Ae7Ruz4O3ICghEo1oPyp1ecge628RNdX7VqYCX5SysWyI7OyYf4FWQQxp0slash0UwgJGJI12890aLWjLwFtOqhXsOUFjtHWOfTQqMFM7hO1J8H7dcv87M0slash0weWQD0sGWpIcsIeN4SDSnRrh5VUcNUMYR7e401e5uJ0add0scD8M3M31MiQ0slash0H2d0add0QiaW4MuAM67buXmElvBRXA1Y8Ua4laTAh8ewqG0add0xAJMRxwWJfRT1NdhIEEoEQs0slash0EB0g0J9JspkK7VOI7uBjtDcrDQV0slash0DbFKWck50xbi9bxCSqBDkBAsk0add0yCHHSMt7LBDc6nO9dMASRjqDsGkr1IH5DJ30slash0AyXQqfencEsK01Fbqxa0DoSDEyPY0QlSkN0slash0YE3nRr2CfwS4pov2p8LdzzJ6ytIQWSu4zUOU2X5FhyFuWZwKZQCdryJmh7uIj0ASzk1LUtuwX8jt3jszQ1MgK3dTUe9jy51WsS4XKWfjTry7RRuF9OHJUQlgsNkd0slash0UrXKfebEotOxiqzgpa0AWw0H1trr77i0yz4BCv6Dio2F6bM0add0Egxf91HY0add0GvIMy2mHWnHRU62y0QHgh5SeC0iIbu0slash09j1Mr8iKUgAaHwgf12r6qFE40k3nMod5x20slash0XgSBMPpSLNCCbCmhcjNXHPGE6hC78HUfxkT2i0uMAk230add0V3z1MIktdoLbsowPUftabVgvrmDM2bF0slash0FBMJCeeSZ62cvp3gMiDC4puXXLSXKHuUOkVxE5fWbEJejr0oF2wgABI8QpPk950STXUESuMCL0add0BG1ZID0add0E62v10slash0fwRWy0add0E0slash0sL3p0U16WuGq1fnOykQUFDDFsAojCExZJgncQvmbwCr0slash0ZJlt7wuNXr6gIXBQmzIQkE7ArBRhqnWriilLxTNiadZvhaqMvBpzFG39KeBbwccUJ3qSFLo7YOXrusNwOt65CUe5I9X8GllTl0add0DffKqRN9nNg6yoKdAT1QlzvBSdRfL0slash0TrsQTC0slash0Ydto29k0slash0C8CAu4b0slash0pokPXeVwoh3Yb00slash0K8Avc4DbIMk6jNWU5O6m0slash0Hfgm9G80add05bVA6mixkffIvVZHwKj6MWjToXfos2evWGxKSMPsj5XdkAA0add03u0slash07OsVm34BJDYXsMY70Ob5T6BEYTTRgVcuUsKN4XSMN1E0slash0tN12mQSyvOhoH0add0hpqM0add0EDqtAK6rN4fK68JDcjdrtN0rHkozY7zrox6fyOrjF5ovRnQzYE1v9zIZrN4prz7BDpK1GmEnWpuZ4BIYlmuYwo6MM2rHcYhxqvjvSM5JLrZJWJ0ULXOoqK8UI190slash07QKrlCDeHeNyjGP9v3RvSbzaE9P9ZBOBBBUwefwBag0slash0pVpKsk67VHPW8kXhLJCXWrDowV0slash0U0VmgpxcsB3SiahWRoqQIgoO1NRSK4yNgt9TjCAnSHOo0slash0ZO1rFQ0xL45A5QIgbz7ukK8rOe9jOh8NOZxTUbQLjx4Sgw79mZDDvRDqwsCcadZ3j9XNUl71mTQpCejU9tC1i6actwZmHFjLT601eDlinrJJMD5Oqn1kIydviCoZPllLHZs0add0se33YcsL6FwF0MXXG0add0Z97H0KMU5J5uAL3s1isgTQZ24dWUTH2CZt6LrkFlUbtLddFuP0add0q5pAzldkwT7Is106IJ0add0c20add0emW6p6HFyUSJnLAyHbwXf0slash0HIU0ibp9rLy5c3UY0add0dH1wYmEuj4eAnSjyN17OHWrpzUO2ADD51zdmHAEaAJNaNZVftYt9aPI08iJwDwafLsH7Gckt0add0nOxJIcxLB5MkMVdmaSo02jaXEK8uqnqp3PYy7d9YVunRfOFoNS7rtT0slash0HzdqRWTGfu0slash0hc0slash0tt0slash0Y7PQmxppAy6Gfh2GwQ20lKWvemjx2NTpdW296UdogyOeCKr9AAKPsDp0ZnW1Jj0add0LM0add04pD0slash0Fi1KLLhDW91A0slash04ZTVrMdwDYZ5OOmCh12GfeyK0slash0zIiHzJ8tG6wAB4y5I0slash0tbCr3IK0add04FW0slash0Zey4HxRi0slash018hNbTKaIt0thSXB2IB0r0bgKNLyxvXWOwunht0add0aIfRw5Z0add0mXA9R2V0nKdvqzqHzJEUIF4JnybDbcTp1zLG5zBM4kDa3vk0x1UPN0OA0slash0DIaKQ1R40slash0AfbHO47mnPbLgGlnMoDoLiMWvuW4bnc4fygGT2f6qUnljGvAxrnxCa5SvftAe0slash0dA0slash0inCwaWxUZTlQ81IigsSDgPY9XgYcTK350add0eBiTBnRrpjB6GNUG2ECLTNVfmntlezyM11v7xzLMEFWtKqVdBE0slash00slash00add0w11IImzv8LzdpX5W2KjdbSomcDQ84bru1xvjRHtuZF9aMNhSEXmcOYpaixzOEX71cRCBTn2c5aiTuml7ZBgrRrL0add0Rp0kJc9wSJMlXiXuFtyeDSdJew12zJwuCyR6EeNUX0add0LK5xMc6iDbUS6a0pDvQWAQYR0J10QCktE8TyOqbzVVOfB5CHpPz0vCy6y8oFgOjWFd6KS38soE4jB0slash0yHkXQHwiOYRjdc5bNDj6ks6O7gS5TPNW1jdlXZLq2CcMUOwjdkMNaSnNfZNZh4gJOBOidT0rZhVa1jGp70add00uMu0slash0iREWJrEtfdPAgbFRysjX3E0add0zC0add04BBYXDQhZl6H3kJDJ9TJWRnXYvb4NpBhmnsMqE0add0YZUPX09fgzD95hPc0Xz0add0qoKdac1zamMPLFo0d4eZsTEPT7M0oPeAEtJPRJy2RhGtbfOAZVvzjeMvTWla0sOuiogdTVCcEk5G50slash0IFzMb2O8Xrxj5gnCFzVNBU7uGwGs8an3e7WZiPpGaepaJk931rN0slash0G7jpM27darWL1nK6hSubdsWsk1NSHSD0slash0DIN6LxRSzl3NLrR9KwrEvTmhLwf1uhHbxDjHlGXYdojPyzSke3623v0slash0V0add0dQXKa93qMjsdZx30mEu32g9CbwBGWu0u3hg7OknOc3EnWv8TkEkXdPItHt7WZwxQX3y9vS4Lo3FzE8CmoqlPbeuaP0add0ZuKlSqyqrBZfShHe50p8gkDABJscP8A89dDqkoQla8htSOo05nDZVH30add0yvEvWLacLGijYUpgRJUXanl0add07PDJChCDPpOQ6LNYR1eSiJqQDCHT548GFyJnr71nTYgvsP1cgy2jfvpeoFCoYEOqdX7ayj1i0slash0N3kBgFky5bqo8ESU5lzmje4q1gGrhkn0slash0VAvg0slash0ttuaS5b7C43IsotVDEQ0slash0wnGQQk0TRHUFCfuqcBVVbhS2f8SKvp4LHBcS101YD0slash0h1gPSnsNAVG4MGxNDeCgFcL9pfVL32Gt20DsxSxOAZAS8m2ZwP3aXXkOG8cBh73GAvF3mhioBUHDQl1xFPB0tgf8TUhQLZrV0mJ8Zn0add004hbNBw0slash07PGgFgOuS0UTpjS0slash00slash0tAZ1fd0HD5z9zKo4zn8XZkvwcNcEnNre4TJWGCgTUSrfMg09wm5qQC5wFj6NjNuBL0slash0DzRFfP0add0CQceG0QARNHPwcf0add067HPLUWDkTvlMAV1XtdX9ECnzo8XaI995LaQGwskgy0add0Dk9oWC0add0vqVG5kNzVjLvs0gm0add0598gsCP7lJE8OpdsmZT1Hp8azsQz2IDyx0slash0nzK9fe0WZqBcXJ0add00add0z07XghejJgQqB15Jx2hLS8Gw0slash0mX6s0add0FKlf0add0WHlOtsKjmJ6sDhQpraroKtNTILPo0add082rejCRNO2lfqqICpD46ia0slash0MUTKS4LmuAmKY8ltHXigOORnhZqAEaNzdQtbEw6ilh0add0sjB88sckNDWjZ09BlZTmsGJYvANpm66MUg0slash0iBoqKGLI4vi5aUUs3dqGVHp6R7DaeXReeIjCe0slash0zi0add0gpdXwUu8XqO3qqvOY1XdFQLhorK9tOOwK67cWd3s9ICcXs4REQnMtsuGoGxhSZCoU1M0oV863E3xmeIxrESVrgPJO80add0KEiKaHEYwva8VMM4UFinfTN6c4W9sVQReXEWrfqFihOUNNDZ18OLfYRryTXJHVGV5NxIuXfDYroqIWUgOgklDuyo8qk2G0add0BvqHXm3xkGGTRPied03OBiF8EADnQsd6BwwR5HK3pjy8eQMCxrvaWLBp8gmH0slash0XOvflFhAEcr7OnzLV2bs0n23TugdbiGZS6rMDHhti6Q5xWNXbSqZ3m52Ou2jpO3efF8l4Gm5nf9W4DrVXeVCPgGpTCVsCx9LLvCoi4542JmjnspIpSI5nIbkPzIX1PLd00add0Id8oaz0add0RlOTo3zL6fv0add0bhw0add00Qltpmofp6y87ExXPzLnmO0slash0ymZtKUTcYwixGo71ugjKkqg8qEx8llV6I33Bopll3kDoJjR0add0CIddT2p44ZOh4n3p0slash0Ejr3rmAa37CzrTPJJt0khUVoJLdxkCJD2f0MvxO1U9QC4YGtgnpJeJBy0add0mN4gd0s9b2ThbYOArHEGDKQxqDymu0Ih0add0Vl30slash00hDLl1bU90add0KOkYHzB68s4vw8AoU18NdnkUEvC0slash04LNk0slash0wH2mgbBU9QQQtDujXpI45fNuOFNVo0dg9vS9SzzUeB4A2JTH7SKbOeOpXPxCYxbClyuGBqiThiMkctq6WlB4HcFCaeRsqe3l9dUYClayQXe5O39QeMpqdHWrLuMNC4S8Wq1DcNUVg43Q4IK9rl4XK6LHPrlpZCGxxZQC274vbT0bC8ReyW7mCgba1Wsa1LYkqnnqDLsnMbVKAOSHPbUjP6v3Keq0slash0MjGO21sn0C5v1RM0slash0mw7rm4wve0slash0J2ym00I5QyRHKFHS0TrYiPNeR89UpR4rHdydSNjIPSuqxb0d44ex8FYIQ9JytFNEXgNZhwA09GIvaLA3enMf7Gzd8gIfbV0slash0xU1gzyNlgiqOCDLiJqiUDXZKFOtzIblW0hVEsRDf0pb3ZRs7JersivxypZXzUVFrFjufb0qmjlVwWqIGO4T7LGJArITMV2ZjFdf4uI0slash0IJMLESimCOChREqYa6IIF5A4wNeaKaZ3ymJYnh4w1Av4MS0add0Ub77hyt2WjC3TmP960EvVq6toMYGwkJU7znm1YvUpPik5nM0add0Vg0Bf3AKziqi6N0add0cZCqa3E0add0wLudIciK8qNxlsBk9OsmDkCNW16GLNMWD0add0goFDlfNkseXKYRmiJ0add0sUHVr3bRSPumxHGzp94pQJM0add0Cob0slash00slash0h4FommutRcgDmo0aXptP44FlJBKVnakVPv5pjoe1Ex0add02EIDlOaoROMyO99KJlaukMTJamKQhfuaxMG6UwX8aHVD0wDtZgTfns5taCc0add0tQsdxTXo2z0slash0E1eTZAe0rT1WKA0equals00equals0',
        'pageNum': offset,
        'kd': 'python'
    }

    # 获取索引页
    html = spider.get_article_index(startUrl, data=data, headers=headers, requestsMethod='post').text
    # 获取外层信息
    articleList = spider.parse_article_index(html, index_css_selector, info_css_selector)
    # 整理外层信息
    for item in articleList:
        S_title, S_articleUrl, S_time, S_imgUrl = item
        title, articleUrl, time, imgUrl = ''.join(S_title.extract()), \
                                          ''.join(S_articleUrl.extract()), \
                                          ''.join(S_time.extract()), \
                                          ''.join(S_imgUrl.extract()), \
        # 获取page页
        articleHtml = spider.get_article_detail(domainUrl + articleUrl)
        articleHtml = decodehtml(articleHtml)
        # 获取内层信息
        articleInfo = spider.parse_article_detail(articleHtml, article_css_selector)
        # 整理内层信息

        htmlContent = ''.join(articleInfo[0].extract()).split('<div class="fx">')[0]
        i = 0
        reslists = re.findall('<(img|IMG)(.*?)(/>|></img>|>)', htmlContent)
        for srcs in reslists:
                ssrc = srcs[1]
                src1 = ssrc.split("src")[1]
                # 路径
                src2 = src1.split('"')
                src3 = src2[1]
                if i == 0:
                    htmlContent = htmlContent
                    htmlContent = htmlContent.replace(src1, '="http://chinacwa.com%s"' % src3)
                    i += 1
                    continue
                else:
                    htmlContent = htmlContent.replace(src1, '="http://chinacwa.com%s"' % src3)
                    i += 1
                    continue
        tags = ''.join(articleInfo[1].extract())

        # 整理其他信息
        Id = idpre + articleUrl.split('.')[0].split('/')[-1]
        imgUrl = 'http://chinacwa.com' + imgUrl
        coverPic, coverPicType = spider.encode_img(imgUrl)
        # 组织数据
        data = (
            Id,
            title,
            time,
            spider.html_strip(htmlContent, stripItem),
            tags,
            'TH013',
            coverPic,
            coverPicType,
            '智慧农业网'
        )

        # 保存数据
        spider.save_data(data)


# 调用请求方法：xxx_run()
def chinacwa_run(offset):
    for i in range(1, offset + 1):
        try:
            main(i)
        except Exception as e:
            print(e)


# chinacwa_run(2)
