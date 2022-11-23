# -*- coding: utf-8 -*-
import re
import sys

from app.core.model.meta_data import MetaData
from app.plugins.adultscraperx.internel.browser_tools import BrowserTools
from app.plugins.adultscraperx.spider.uncensored_spider import UnsensoredSpider
from selenium.webdriver.common.by import By

if sys.version.find('2', 0, 1) == 0:
    try:
        from cStringIO import StringIO
    except ImportError:
        from StringIO import StringIO
else:
    from io import StringIO
    from io import BytesIO

from PIL import Image



class TenMusume(UnsensoredSpider):

    def __init__(self):
        super().__init__()
        self.checkUrl = 'https://www.10musume.com/'

    def get_name(self):
        return "10Musume"

    def search(self, q):

        '''
        执行查询函数
        '''
        item = []
        '获取查询结果页html对象'
        url = 'https://www.10musume.com/movies/%s/' % q
        html_item = self.get_html_byurl(url)
        if html_item['issuccess']:
            browserTools = BrowserTools()
            browser = browserTools.getBrowser()
            browser.get("https://www.10musume.com/movies/%s/" % q)
            media_item = self.analysis_media_html_byxpath(
                browser, q)
            item.append(media_item)
            browserTools.closeBrowser()
        else:
            pass  # print repr(html_item['ex'])

        return item

    def analysis_media_html_byxpath(self, html, q):
        """
        根据html对象与xpath解析数据
        html:<object>
        html_xpath_dict:<dict>
        return:<dict{issuccess,ex,dict}>
        """

        number = self.tools.cleanstr(q.upper())
        media = MetaData()
        media.number = number
        xpath_title = '/html/body/div[2]/main/div/div[2]/div[1]/div[1]/div[2]/h1'
        title = html.find_elements(By.XPATH, xpath_title)
        if len(title) > 0:
            media.title = title[0].text

        xpath_summary = '/html/body/div[2]/main/div/div[2]/div[1]/div[1]/p'
        summary = html.find_elements(By.XPATH, xpath_summary)
        if len(summary) > 0:
            summary = summary[0].text
            media.summary = summary

        # xpath_poster = "//img/@src"
        # poster = html.xpath(xpath_poster)        
        # if len(poster) > 0:
        # poster = self.tools.cleanstr(poster[0])
        media.poster = 'https://www.10musume.com/assets/sample/%s/str.jpg' % number
        media.thumbnail = 'https://www.10musume.com/assets/sample/%s/str.jpg' % number

        # xpath_studio = "//div[@class='col-md-3 info']/p[5]/a/text()"
        # studio = html.xpath(xpath_studio)
        # if len(studio) > 0:
        studio = '素人専門アダルト動画'
        media.studio = studio

        # xpath_directors = "//div[@class='col-md-3 info']/p[4]/a/text()"
        # directors = html.xpath(xpath_directors)
        # if len(directors) > 0:
        directors = ''
        media.directors = directors

        # xpath_collections = "//div[@class='col-md-3 info']/p[6]/a/text()"
        # collections = html.xpath(xpath_collections)
        # if len(collections) > 0:
        collections = '天然むすめ'
        media.collections = collections

        xpath_year = '/html/body/div[2]/main/div/div[2]/div[1]/div[1]/ul/li[1]/span[2]'
        year = html.find_elements(By.XPATH, xpath_year)[0].text.split('/')
        if len(year) > 0:
            year = year[0]
            media.year = year
            media.originally_available_at = year

        xpath_category = '/html/body/div[2]/main/div/div[2]/div[1]/div[1]/ul/li[6]/span[2]/span/a'
        categorys = html.find_elements(By.XPATH, xpath_category)
        category_list = []
        for category in categorys:
            category_list.append(category.text)
        categorys = ','.join(category_list)
        if len(categorys) > 0:
            media.category = categorys

        actor = {}
        xpath_actor_name = '/html/body/div[2]/main/div/div[2]/div[1]/div[1]/ul/li[3]/span[2]/span/a'
        # xpath_actor_url = "//div[@class='video-performer']/a/img/@style"
        actor_name = html.find_elements(By.XPATH, xpath_actor_name)
        # actor_url = html.xpath(xpath_actor_url)
        if len(actor_name) > 0:
            for i, actorname in enumerate(actor_name):
                # actorimageurl = actor_url[i].replace('background-image:url(', '').replace(');', '')
                '''
                actor.update({self.tools.cleanstr2(
                    actorname): actorimageurl})
                '''
                actor.update({actorname.text: ''})

            media.actor = actor

        return media

    def poster_picture(self, url, r, w, h):
        cropped = None
        try:
            response = self.client_session.get(url)
        except Exception as ex:
            print('error : %s' % repr(ex))
            return cropped

        img = Image.open(BytesIO(response.content))
        # (left, upper, right, lower)
        cropped = img.crop((0, 0, img.size[0], img.size[1]))
        return cropped
