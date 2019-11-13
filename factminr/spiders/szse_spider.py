# -*- coding: utf-8 -*-
import json
import random
import re
from functools import reduce
from io import BytesIO

from urllib.parse import urljoin
import jsonpath
import scrapy
import logging
from pdfminer.pdfparser import PDFParser, PDFDocument, PDFSyntaxError
from pdfminer.pdfinterp import PDFTextExtractionNotAllowed
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox

from factminr.spiders import company_dict
from factminr.work_utils import get_url
from factminr.work_utils.work_times import statistic_time

logger = logging.getLogger(__name__)


class SzseSpider(scrapy.Spider):
    name = 'szse_spider'
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            # 'factminr.middlewares.RandomUserAgentMiddleware': 120,
            'factminr.middlewares.UserAgentMiddleware': 130,
        },
        'ITEM_PIPELINES': {
            'factminr.pipelines.MyFilesPipeline': 300,  # 下载文件
            # 'factminr.pipelines.FactminrPipeline': 320,  # 数据清洗
            'factminr.pipelines.MongodbPipeline': 340,  # 保存到mongodb
        },
        'LOG_LEVEL': 'INFO',
    }

    def start_requests(self):
        urls = get_url()
        for url in urls:
            yield scrapy.Request(
                url=url
            )

    def parse(self, response):
        results = json.loads(response.body_as_unicode())
        if 'selectBkmc' in response.url:
            # 解析 监管措施
            datas = results[0].get('data')
            for data in datas:
                gkxx_gdrq = data.get('gkxx_gdrq', '')  # 采取监管措施日期
                gkxx_gsdm = data.get('gkxx_gsdm', '')  # 公司代码
                gkxx_gsjc = data.get('gkxx_gsjc', '')  # 公司简称
                gkxx_jgcs = data.get('gkxx_jgcs', '')  # 监管措施
                gkxx_sjdx = data.get('gkxx_sjdx', '')  # 涉及对象
                gkxx_jgsy = data.get('gkxx_jgsy', '')  # 函件内容，PDF
                cf_cflb = '监管措施'
                oname_temp = company_dict.get(gkxx_gsdm)
                if oname_temp:
                    oname = oname_temp[1]
                else:
                    logger.info('未获取到处罚主体:{}，公司代码:{}'.format(gkxx_gsjc, gkxx_gsdm))
                    continue
                jgcs_item = dict(
                    oname=oname,
                    cf_jdrq=gkxx_gdrq,
                    regcode=gkxx_gsdm,
                    bzxr=gkxx_gsjc,
                    cf_type=gkxx_jgcs,
                    nsrlx=gkxx_sjdx,
                    cf_cflb=cf_cflb,
                )
                if gkxx_jgsy.endswith("</a>"):
                    file_url = re.search(r'encode-open=\'(.*?)\'', gkxx_jgsy).group(1)
                    file_url = urljoin('http://reportdocs.static.szse.cn', file_url)
                    if file_url.endswith('.pdf'):
                        # logger.debug('开始解析PDF')
                        yield scrapy.Request(
                            url=file_url,
                            callback=self.parse_jgcs_pdf,
                            meta={'item': jgcs_item},
                            priority=5,
                        )
                    else:
                        logger.debug('不是PDF文件')
                else:
                    jgcs_item['xq_url'] = response.url
                    jgcs_item['ws_nr_txt'] = gkxx_jgsy
                    jgcs_item['cf_sy'] = gkxx_jgsy
                    yield jgcs_item
            # 翻页 监管措施
            pagecount = jsonpath.jsonpath(results[0], expr=r'$..pagecount')[0]  # 总页码
            is_first = response.meta.get('is_first', True)
            if is_first:
                for page in range(2, pagecount):
                    url = 'http://www.szse.cn/api/report/ShowReport/data?SHOWTYPE=JSON&CATALOGID=1800_jgxxgk&TABKEY=tab1&PAGENO={}&selectBkmc=0&random={}'.format(page, random.random())
                    yield scrapy.Request(
                        url=url,
                        meta={'is_first': False},
                        priority=3,
                    )
        else:
            # 解析 纪律处分
            datas = results[1].get('data')
            for data in datas:
                xx_gsdm = data.get('xx_gsdm', '')  # 公司代码
                jc_gsjc = data.get('jc_gsjc', '')  # 公司简称
                xx_fwrq = data.get('xx_fwrq', '')  # 处分日期
                xx_cflb = data.get('xx_cflb', '')  # 处分类别
                xx_bt = data.get('xx_bt', '')  # 标题
                ck = data.get('ck', '')  # 查看全文，内容
                cf_cflb = '纪律处分'
                oname_temp = company_dict.get(xx_gsdm)
                if oname_temp:
                    oname = oname_temp[1]
                else:
                    logger.info('未获取到处罚主体:{}，公司代码:{}'.format(jc_gsjc, xx_gsdm))
                    continue
                jlcf_item = dict(
                    oname=oname,
                    cf_jdrq=xx_fwrq,
                    regcode=xx_gsdm,
                    bzxr=jc_gsjc,
                    cf_type=xx_cflb,
                    cf_cflb=cf_cflb,
                    cf_cfmc=xx_bt,
                )
                if ck.endswith('</a>'):
                    file_url = re.search(r'encode-open=\'(.*?)\'', ck).group(1)
                    file_url = urljoin('http://reportdocs.static.szse.cn', file_url)
                    if file_url.endswith('pdf'):
                        yield scrapy.Request(
                            url=file_url,
                            callback=self.parse_jlcf_pdf,
                            meta={'jlcf_item': jlcf_item},
                            priority=5,
                        )
                    else:
                        logger.debug('不是PDF文件，可能是doc或者docx，只能先下载到本地才能读取解析')
                        jlcf_item['file_url'] = file_url
                        jlcf_item['xq_url'] = file_url
                        yield jlcf_item
                else:
                    jlcf_item['xq_url'] = response.url
                    jlcf_item['ws_nr_txt'] = ck
                    jlcf_item['cf_sy'] = ck
                    yield jlcf_item
            # 翻页 纪律处分
            pagecount = jsonpath.jsonpath(results[1], expr=r'$..pagecount')[0]  # 总页码
            is_first = response.meta.get('is_first', True)
            if is_first:
                for page in range(2, pagecount):
                    link = 'http://www.szse.cn/api/report/ShowReport/data?SHOWTYPE=JSON&CATALOGID=1800_jgxxgk&TABKEY=tab2&PAGENO={}&selectGsbk=0&random={}'.format(page, random.random())
                    yield scrapy.Request(
                        url=link,
                        meta={'is_first': False},
                        priority=3,
                    )

    def parse_jgcs_pdf(self, response):
        """
        监管措施，从PDF内容提取需要字段
        :param response:
        :return:
        """
        item = response.meta.get('item')
        content_list = self.parse_pdf(response)
        re_com = re.compile(r'\r|\n|\t|\s')
        content = reduce(lambda x, y: x+y, [re_com.sub('', i) for i in content_list])
        # print(f'pdf文本={content}')
        cf_wsh_pattern = re.compile(r'((?:监管函公司部|监管函).*?号)')
        cf_sy_pattern = re.compile(r'：(.*?(?:违反了|你的上述行为违反了|你公司的上述行为违反了))')
        cf_yj_pattern = re.compile(r'((?:违反了|你的上述行为违反了).*?(?:规定|相关规定))')
        cf_jg_pattern = re.compile(r'(现对你.*?。)')
        cf_wsh = cf_wsh_pattern.search(content)
        if cf_wsh:
            item['cf_wsh'] = cf_wsh.group(1)
        else:
            item['cf_wsh'] = ''
        cf_sy = cf_sy_pattern.search(content)
        if cf_sy:
            item['cf_sy'] = cf_sy.group(1)
        else:
            item['cf_sy'] = ''
        cf_yj = cf_yj_pattern.search(content)
        if cf_yj:
            item['cf_yj'] = cf_yj.group(1)
        else:
            item['cf_yj'] = ''
        cf_jg = cf_jg_pattern.search(content)
        if cf_jg:
            item['cf_jg'] = cf_jg.group(1)
        else:
            item['cf_jg'] = ''
        item['file_url'] = response.url
        item['xq_url'] = response.url
        item['ws_nr_txt'] = content
        yield item

    def parse_jlcf_pdf(self, response):
        """
        纪律处分，从PDF内容提取需要字段
        :param response:
        :return:
        """
        jlcf_item = response.meta.get('jlcf_item')
        content_list = self.parse_pdf(response)
        re_com = re.compile(r'\r|\n|\t|\s')
        content = reduce(lambda x, y: x+y, [re_com.sub('', i) for i in content_list])
        cf_sy_pattern = re.compile(r'(经查明.*?。)')
        cf_yj_pattern = re.compile(r'((?:依据|根据)本所.*?规定)')
        cf_jg_pattern = re.compile(r'决定：(.*?)深圳证券交易所')
        cf_sy = cf_sy_pattern.search(content)
        if cf_sy:
            jlcf_item['cf_sy'] = cf_sy.group(1)
        else:
            jlcf_item['cf_sy'] = ''
        cf_yj = cf_yj_pattern.search(content)
        if cf_yj:
            jlcf_item['cf_yj'] = cf_yj.group(1)
        else:
            jlcf_item['cf_yj'] = ''
        cf_jg = cf_jg_pattern.search(content)
        if cf_jg:
            jlcf_item['cf_jg'] = cf_jg.group(1)
        else:
            jlcf_item['cf_jg'] = ''
        jlcf_item['file_url'] = response.url
        jlcf_item['xq_url'] = response.url
        jlcf_item['ws_nr_txt'] = content
        yield jlcf_item

    @statistic_time
    def parse_pdf(self, response):
        """
        解析PDF文件
        :param response:
        :return:
        """
        # 用文件对象来创建一个pdf文档分析器
        praser = PDFParser(BytesIO(response.body))
        # 创建一个PDF文档
        doc = PDFDocument()
        # 连接分析器 与文档对象
        praser.set_document(doc)
        doc.set_parser(praser)
        # 提供初始化密码
        # 如果没有密码 就创建一个空的字符串
        doc.initialize()
        # 检测文档是否提供txt转换，不提供就忽略
        if not doc.is_extractable:
            raise PDFTextExtractionNotAllowed
        else:
            # 创建PDf 资源管理器 来管理共享资源
            rsrcmgr = PDFResourceManager()
            # 创建一个PDF设备对象
            laparams = LAParams()
            device = PDFPageAggregator(rsrcmgr, laparams=laparams)
            # 创建一个PDF解释器对象
            interpreter = PDFPageInterpreter(rsrcmgr, device)
            contents_list = []
            # 循环遍历列表，每次处理一个page的内容
            for page in doc.get_pages():  # doc.get_pages() 获取page列表
                # 接受该页面的LTPage对象
                interpreter.process_page(page)
                # 这里layout是一个LTPage对象 里面存放着
                # 这个page解析出的各种对象 一般包括LTTextBox, LTFigure, LTImage, LTTextBoxHorizontal 等等
                # 想要获取文本就获得对象的text属性
                layout = device.get_result()
                for index, out in enumerate(layout):
                    if isinstance(out, LTTextBox):
                        contents = out.get_text().strip()
                        contents_list.append(contents)
            return contents_list