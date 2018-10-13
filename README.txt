
包含网站：

雷锋网、智慧农业网、法律图书馆
资管网、中国经济网、DoNews、土木工程网
化工网、西安教育网、西安周边自驾游、健网
hi运动、先进制造业、生物360、通信产业网
健康界、人民网传媒、中房网...


# 项目结构
/industrySpiderProject
	/industrySpider
		/__init__.py
		/config.py
		/BaseSpider.py
		/crawl_data.py
		/upload_data.py
		/xxx.py
	

# 数据库MySQL
database:	th_spider_database
table:	data_set
Generate:
create table th_spider_database.data_set
(
  id           varchar(30) not null
    primary key,
  title        varchar(50) null,
  noteDate     varchar(30) null,
  htmlContent  longtext    null,
  tags         longtext    null,
  circleKey    varchar(10) null,
  coverPic     longtext    null,
  coverPicType char(10)    null,
  src          varchar(50) null
)ENGINE=InnoDB DEFAULT CHARSET=utf8;
