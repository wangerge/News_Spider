# 项目结构
/industrySpiderProject
	/industrySpider
		/__init__.py
		/config.py
		/BaseSpider.py
		/crawl_data.py
		/upload_data.py
		/xxx.py
	/Makefile
	/requirements.txt

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
