# -*- coding: utf-8 -*-
import scrapy
from anjuketest1.items import Anjuketest1Item
import time
import re
import redis
class AnjukeSpider(scrapy.Spider):
    name = 'spider_shanghai'
    allowed_domains = ['anjuke.com']
    db = redis.Redis(host="127.0.0.1", port=6379)
    all_urls = "https://shanghai.anjuke.com/sale/o5/"
    cookies = {
        "aQQ_ajkguid": "E6D0CEE9-45AA-22C5-1216-75E4F9073511",
        "sessid":"889907EE-93A4-5BFE-A4EC-15400AE34D8D",
        "propertys":"jxks5d-p7vjli_jxi8gr-p7vf18_jv626e-p7qad3_jv3br4-p7qa07_jvca0x-p7q7rw_jv75i0-p7q01e_jqlowf-p7of1e_julcqc-p7of0a_jn5blx-p7oeyg_jpp7oy-p7o6zn_jobapx-p7o2rr_jo1sb1-p7o233_jtijq5-p7o1z2_jriy4f-p7nzbb_j6t73c-p7nyra_jst88a-p7mqv2_j4d56h-p7moxn_ji5ayl-p7mnck_jtv09k-p7mmcj_jtv0qx-p7mm1t_jtu4nk-p7mjz5_",
        "twe":"2",
    }
    def chuli_info(self,infos):
        # 处理字段无用符
        info = "".join(infos)
        return info.replace('\t','').replace('\n','').replace('\ue003','').replace('\xb2','').replace('\ue092','').replace('\ue093','').replace('\ue094','').replace('\ue095','')
    def start_requests(self):
        # 入口
        yield scrapy.Request(url=self.all_urls,cookies=self.cookies,callback=self.thrid_parse)
    def thrid_parse(self,response):
        # 解析主页面上url,并翻页
        content_urls = response.xpath('//*[@id="houselist-mod-new"]/li/div/div[@class="house-title"]/a[contains(@href,"{}")]/@href'.format(response.url[:20])).extract()
        for content_url in content_urls:
            key_url,values = content_url.split('?')
            if self.db.sismember("anjuke_key",key_url):
                # redis判断url是否重复
                pass
            else:
                self.db.sadd("anjuke_key",key_url)
                yield scrapy.Request(url=content_url,cookies=self.cookies,callback=self.get_one_page,priority=4)
        next_url = response.xpath('//*[@id="content"]/div/div/a[@class="aNxt"]/@href').extract_first()
        yield scrapy.Request(url=next_url,cookies=self.cookies,callback=self.thrid_parse,priority=3)
    def get_one_page(self,response):
        # 解析详细页
        long_title = response.xpath("//*[@id='content']/div/h3/text()").extract_first()
        long_title = long_title.replace('\n', '').replace('\t', '')
        total_info = response.xpath(
            '//*[@id="content"]/div/div/div[@class="basic-info clearfix"]/span//text()').extract()
        first_infos = response.xpath(
            '//div[@class="houseInfo-wrap"]//div[@class="first-col detail-col"]//text()').extract()
        try:
            total_price = total_info[0] + total_info[1]
        except:
            total_price = ''
        geju = total_info[2] + total_info[3] + total_info[4] + total_info[5]
        all_size = total_info[6] + total_info[7]
        anxin = response.xpath(
            '//h4[@class="block-title houseInfo-title"]/span[@class="anxian"]/text()').extract_first()
        house_encode = response.xpath(
            '//h4[@class="block-title houseInfo-title"]/span[@class="house-encode"]/text()').extract_first()
        first_info = self.chuli_info(first_infos)
        first_info = re.match("所属小区：(.*?)所在位置：(.*?)建造年代：(.*?)房屋类型：(.*?)$", first_info)
        xiaoqulianjie = response.xpath(
            '//div[@class="houseInfo-wrap"]//div[@class="first-col detail-col"]//a/@href').extract_first()

        xiaoqu = first_info.group(1)
        weizhi = first_info.group(2)
        weizhis = weizhi.split('－')
        try:
            xingzhengqu = weizhis[0].replace("：", "")
        except:
            xingzhengqu = ""
        try:
            pianqu = weizhis[1] if weizhis[1] else ''
        except:
            pianqu = ""
        niandai = first_info.group(3)
        fangling = re.match('(\d+)', niandai)
        try:
            fangling = 2018 - int(fangling.group(1))
        except:
            fangling = ""
        leixing = first_info.group(4)
        second_infos = response.xpath(
            '//div[@class="houseInfo-wrap"]//div[@class="second-col detail-col"]//text()').extract()
        second_info = self.chuli_info(second_infos)
        second_info = re.match('房屋户型：(.*?)建筑面积：(.*?)房屋朝向：(.*?)所在楼层：(.*?)$', second_info)
        huxing = second_info.group(1)
        huxings = re.match('(\d+)室(\d+)厅(\d+)卫', huxing)
        woshi = huxings.group(1)
        keting = huxings.group(2)
        weishengjian = huxings.group(3)
        mianji = second_info.group(2)
        chaoxiang = second_info.group(3)
        loucengs = second_info.group(4)
        louceng = loucengs.split('(共')
        try:
            louceng = louceng[0]
        except:
            louceng = ""
        zonglouceng = re.findall('共(\d+)层', loucengs)
        third_infos = response.xpath(
            '//div[@class="houseInfo-wrap"]//div[@class="third-col detail-col"]//text()').extract()
        third_info = self.chuli_info(third_infos)
        third_info = re.match('房屋单价：(.*?)参考首付：(.*?)参考月供：(.*?)装修程度：(.*?)$', third_info)
        danjia = third_info.group(1)
        shoufu = third_info.group(2)
        yuegong = third_info.group(3)
        zhuangxiu = third_info.group(4)
        house_info1 = response.xpath(
            '//div[@class="houseInfo-desc"]//div[@class="houseInfo-item"]//span[@style="font-size:14px;"]/text()').extract()
        house_info1 = self.chuli_info(house_info1)
        house_info2 = response.xpath(
            '//div[@class="houseInfo-desc"]//div[@class="houseInfo-item"]//div[@class="houseInfo-item-desc"]/text()').extract()
        hexinmaidian = house_info1
        try:
            yezhuxintai = house_info2[0].replace('\n', '').replace(' ', '')
            xiaoqupeitao = house_info2[1].replace('\n', '').replace(' ', '')
            fuwujieshao = house_info2[2].replace('\n', '').replace(' ', '')
        except:
            yezhuxintai = ""
            xiaoqupeitao = ""
            fuwujieshao = ""
        city = response.xpath('//div[@class="p_1180 p_crumbs"]/a/text()').re('^(.*?)房产网$')
        lianxiren = response.xpath('//div[@class="broker-wrap"]//p[@class="brokercard-name"]/text()').extract()
        dianhuahaoma = response.xpath('//div[@class="broker-wrap"]//p[@class="broker-mobile"]/text()').extract()
        fabushijian = re.findall('发布时间：(.*?)$', house_encode)
        xiaoqugaikuang = response.xpath('//div[@class="cmmmap-info"]//p/text()').extract()
        xiaoqugaikuang = self.chuli_info(xiaoqugaikuang)
        xiaoqugaikuangobj = re.match('总面积(.*?)总户数(.*?)容积率(.*?)停车位(.*?)绿化率(.*?)物业费用(.*?)$', xiaoqugaikuang)
        try:
            zongmianji = xiaoqugaikuangobj.group(1)
            zonghushu = xiaoqugaikuangobj.group(2)
            rongjilv = xiaoqugaikuangobj.group(3)
            tingchewei = xiaoqugaikuangobj.group(4)
            lvhualv = xiaoqugaikuangobj.group(5)
            wuyefeiyong = xiaoqugaikuangobj.group(6)
        except:
            zongmianji = ''
            zonghushu = ''
            rongjilv = ''
            tingchewei = ''
            lvhualv = ''
            wuyefeiyong = ''
        jingjirengongsi = response.xpath(
            '//div[@class="broker-wrap"]/div[@class="broker-background"]//div[@class="broker-company"]/p/a/text()').extract()
        try:
            gongsimingcheng = jingjirengongsi[0]
        except:
            gongsimingcheng = ""
        try:
            mendian = jingjirengongsi[1]
        except:
            mendian = ""
        lianxirenurl = response.xpath('//div[@class="broker-wrap"]/a/@href').extract()
        urls = response.url
        urls = urls.split('?')
        item = Anjuketest1Item()
        item["信息来源"] = "安居客"
        item["城市"] = city[0]
        item["行政区"] = xingzhengqu
        item["片区"] = pianqu
        item["来源链接"] = urls[0]
        item["题名"] = long_title
        item["总价"] = total_price
        item["小区名称"] = xiaoqu
        item["地址"] = weizhi
        item["建成年份"] = niandai
        item["房龄"] = str(fangling)
        item["住宅类别"] = leixing
        item["卧室数量"] = woshi
        item["客厅数量"] = keting
        item["卫生间数量"] = weishengjian
        item["建筑面积"] = mianji
        item["朝向"] = chaoxiang
        item["楼层"] = louceng
        try:
            zonglouceng = zonglouceng[0]
        except:
            zonglouceng = ''
        item["总楼层"] = zonglouceng
        item["单价"] = danjia
        item["参考首付"] = shoufu
        item["参考月供"] = yuegong
        item["装修情况"] = zhuangxiu
        item["核心卖点"] = hexinmaidian
        item["业主心态"] = yezhuxintai
        item["周边配套"] = xiaoqupeitao
        item["服务介绍"] = fuwujieshao
        item["联系人"] = "".join(lianxiren)
        item["电话号码"] = "".join(dianhuahaoma)
        item["小区链接"] = xiaoqulianjie
        try:
            item["发布时间"] = fabushijian[0]
        except:
            item["发布时间"] = ""
        item["小区总户数"] = zonghushu
        item["楼盘绿化率"] = lvhualv
        item["楼盘物业费"] = wuyefeiyong
        item["容积率"] = rongjilv
        item["小区总建筑面积"] = zongmianji
        item["小区总停车位"] = tingchewei
        item["经纪公司"] = gongsimingcheng
        item["门店"] = mendian
        try:
            item["联系人链接"] = lianxirenurl[0]
        except:
            item["联系人链接"] = ""
        yield item









