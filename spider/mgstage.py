# -*- coding: utf-8 -*-
import time
import logging

from app.core.model.meta_data import MetaData
from app.plugins.adultscraperx.internel.browser_tools import BrowserTools
from app.plugins.adultscraperx.spider.uncensored_spider import UnsensoredSpider
from selenium.webdriver.common.by import By


class MGStage(UnsensoredSpider):

    def __init__(self):
        super().__init__()
        self.checkUrl = 'https://www.mgstage.com//'

    def search(self, q):
        '''
        执行查询函数
        '''
        results = []
        try:
            logging.info('初始化 browser 模拟')
            browserTools = BrowserTools()
            browser = browserTools.getBrowser()
            logging.info('开始模拟')

            url = 'https://www.mgstage.com/search/search.php?search_word=%s&page=1&sort=popular&list_cnt=120&disp_type=detail' % q
            browser.get(url)
            time.sleep(2)
            btn_xpath = "//a[@id='AC']"  # 18确认
            btn = browser.find_elements(By.XPATH, btn_xpath)
            if len(btn) > 0:
                btn[0].click()

            items_href_xpath = "//div[@class='rank_list']/ul/li/h5/a"
            items_list = browser.find_elements(By.XPATH, items_href_xpath)
            media_item = None
            for item in items_list:
                item.click()
                media_item = self.analysis_media_html_byxpath(browser, q)
            logging.info('解析结果：%s' % media_item)
            logging.info('结束模拟')
            logging.info('关闭 browser 模拟')
            browserTools.closeBrowser()
            if media_item and media_item.title and media_item.title != '':
                results.append(media_item)

            return results

        except Exception as ex:
            logging.info('发生异常:%s' % ex)
            logging.info('关闭 browser 模拟')
            browserTools.closeBrowser()
            item.append({'issuccess': False, 'ex': e})
            return results

    def analysis_media_html_byxpath(self, browser, q):

        media = MetaData()
        infos_xpath = "//div[@class='detail_data']"
        infos = browser.find_elements(By.XPATH, infos_xpath)
        info_list = infos[0].text.split('\n')
        for info in info_list:
            tmp = info.split('：')
            if len(tmp) > 1:
                keyword = self.tools.cleanstr(tmp[0])
                value = tmp[1]
                if keyword == '出演':  # actor
                    actor = {}
                    actor_name = []
                    actor_name.append(self.tools.cleanstr(value))
                    if len(actor_name) > 0:
                        for i, actorname in enumerate(actor_name):
                            actor.update(
                                {self.tools.cleanstr2(actorname): ''})
                    media.actor = actor

                if keyword == 'メーカー':  # 工作室
                    media.studio = self.tools.cleanstr(value)

                if keyword == '品番':  # 番号
                    media.number = self.tools.cleanstr(value)

                if keyword == '配信開始日':  # 日期
                    media.year = self.tools.formatdatetime(self.tools.cleanstr(value))
                    media.originally_available_at = self.tools.formatdatetime(self.tools.cleanstr(value))

                if keyword == 'シリーズ':  # 系列
                    media.collections = self.tools.cleanstr2(self.tools.cleanstr(value))

                if keyword == 'ジャンル':  # 类型
                    # types
                    categorys = value.split(' ')
                    while '' in categorys:
                        categorys.remove('')

                    categorys_list = []
                    for item in categorys:
                        categorys_list.append(self.tools.cleanstr(item))
                    categorys = ','.join(categorys_list)
                    if len(categorys) > 0:
                        media.category = categorys

        # title
        title_xpath = "//h1[@class='tag']"
        title = browser.find_elements(By.XPATH, title_xpath)
        media.title = self.tools.cleanstr(title[0].text)

        more_xpath = "//p[@id='introduction_all']"
        more = browser.find_elements(By.XPATH, more_xpath)
        if not more[0].get_attribute("style") == 'display: none;':
            more[0].click()

        summary_xpath = "//p[@class='txt introduction']"
        summary = browser.find_elements(By.XPATH, summary_xpath)
        media.summary = summary[0].text

        poster_xpath = "//a[@id='EnlargeImage']"
        poster = browser.find_elements(By.XPATH, poster_xpath)
        media.poster = poster[0].get_attribute('href')

        art_xpath = "//div[@class='detail_left']/dl[@id='sample-photo']/dd/ul/li[1]/a[@class='sample_image']"
        art = browser.find_elements(By.XPATH, art_xpath)
        media.thumbnail = art[0].get_attribute('href')

        return media
