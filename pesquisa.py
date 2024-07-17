from RPA.Browser.Selenium import Selenium
from RPA.FileSystem import FileSystem
from RPA.Excel.Files import Files
import time
import os
import requests
from datetime import datetime
from abc import ABC  # Estou so dizendo q é uma classe abstrata

import logging

logger = logging.getLogger(__name__)
logging.basicConfig(filename='myapp.log', level=logging.INFO)


# Abstract class to handle the page elements with selenium
class PageElement(ABC):
    def __init__(self):
        self.browser = Selenium()
        self.browser.open_available_browser()
        logger.info('Opened browser')


class ApNewsSite(PageElement):
    def __init__(self):
        super().__init__()
        self.browser.go_to("https://apnews.com/")
        logger.info('Opened AP News Site')

    def get_news(self, search_phrase: str, category: str = None, number_of_news: int = 100) -> list[dict]:
        """
        This method will search for news on the AP News site based on the given parameters
        :param search_phrase: phrase to search for
        :param category: category of the news search
        :param number_of_news: number limit of news to be searched

        :return: dictionary with the information of the news found
        """
        logger.info('Get news with the parametres: | search_phrase: %s | category: %s | number_of_news: %s',
                    search_phrase, category, number_of_news)

        # Handling the pop-up
        try:
            self.browser.wait_until_element_is_visible('//a[@title="Close" and @class="fancybox-item fancybox-close"]',
                                                       timeout=60)
            self.browser.click_element('//a[@title="Close" and @class="fancybox-item fancybox-close"]')
        except:
            logger.critical('There was no popup on the screen')

        # Opening the search bar
        logger.debug('Opening the search bar')
        self.browser.wait_until_element_is_visible('//button[@class="SearchOverlay-search-button"]', timeout=10)
        botao = self.browser.find_element('//button[@class="SearchOverlay-search-button"]')
        botao.click()

        # Typing the search phrase and submitting the form
        logger.debug('Typing the search phrase')
        self.browser.wait_until_element_is_visible('//input[@class="SearchOverlay-search-input"]', timeout=10)
        self.browser.input_text('//input[@class="SearchOverlay-search-input"]', search_phrase)
        self.browser.click_element('//button[@class="SearchOverlay-search-submit"]')

        # filter by categories:
        logger.debug('filtering by categories')
        self.browser.click_element("css:.SearchFilter-heading[data-toggle-trigger='search-filter']")
        categorys_obj = self.browser.find_elements("css:.SearchFilterInput input[type='checkbox']")
        avalibles_categorys = [categorias.text for categorias in categorys_obj]
        if (category is not None) and category in avalibles_categorys:
            category_index = avalibles_categorys.index(category)
            categorys_obj[category_index].click()

        # Find all news items
        logger.debug('Finding all news items')
        self.browser.wait_until_element_is_visible("css:.SearchResultsModule-results")
        news_part = self.browser.find_element("css:.SearchResultsModule-results")
        news_items = self.browser.find_elements("css:.PageList-items-item", news_part)

        return self.__treat_news_obj(news_items, search_phrase, number_of_news)

    def __treat_news_obj(self, news_items: list, search_phrase: str, number_of_news: int) -> list[dict]:
        """
        This method will treat the news items found on the AP News site
        :param news_items: list of news items found on the site
        :return: list of dictionaries with the information of the news found
        """
        logger.debug('Treating news items')
        output_lines = []
        for index, item in enumerate(news_items):
            try:
                if index > (number_of_news - 1):
                    logger.debug('get the number of news requested')
                    break

                texto_noticia = item.text
                title = texto_noticia.split("\n")[0]
                description = texto_noticia.replace(f"{title}\n", '')

                file_name = self.__find_and_download_image(item, index)

                data = datetime.today().strftime('%Y-%m-%d')
                occurrence_search_phrase = texto_noticia.lower().count(search_phrase.lower())
                occurrence_money = texto_noticia.lower().count("$".lower()) \
                                   + texto_noticia.lower().count("dollars".lower()) \
                                   + texto_noticia.lower().count("USD".lower())
                money_in_description = False
                if occurrence_money > 0:
                    money_in_description = True

                output_lines.append({"title": title,
                                     "date": data,
                                     "description": description,
                                     "file_name": file_name,
                                     "count_search_phrases_title_and_description": occurrence_search_phrase,
                                     "is_money_in_description": money_in_description
                                     })
            except Exception as e:
                logger.error(f"Error treating news number item:{index} | erro_msg: {e}")
                continue

        return output_lines

    def __find_and_download_image(self, html_item, index: int) -> str:
        """
        This method will download the image from the given URL
        :param html_item: html element with the news information to look for the img
        :param index: index of the image
        :return: file name of the downloaded image
        """
        try:
            # Create the output directory if it does not exist
            output_dir = "output"
            if os.path.exists(output_dir) == False:
                os.makedirs(output_dir, exist_ok=True)

            img = self.browser.find_element("css:.PagePromo-media img", html_item)
            img_url = img.get_attribute("src")

            file_name = os.path.join(output_dir, f"image_{index + 1}.jpg")

            # Download the image
            response = requests.get(img_url)
            if response.status_code == 200:
                FileSystem().create_binary_file(path=file_name, content=response.content, overwrite=True)
            return file_name

        except Exception as e:
            logger.error(f"Error find and Download img from news, index_new:{index} | erro_msg: {e}")
            return 'img_not_found'


class ExcelHandler:
    def __init__(self):
        self.lib = Files()
        self.lib.create_workbook(path="output/news.xlsx", fmt="xlsx", sheet_name="news")

    def save_news_to_excel(self, excel_lines: list[dict]):
        """
        This method will save the news to an excel file
        :param excel_lines: list of dictionaries with the news information
        :return:
        """
        try:
            logger.debug('saving news to excel')
            for index, line in enumerate(excel_lines):
                self.lib.set_cell_value(index, "A", line["title"])
                self.lib.save_workbook()
            self.lib.close_workbook()
        except Exception as e:
            logger.error('Error saving news to excel: %s', e)


if __name__ == '__main__':
    ap = ApNewsSite()
    news = ap.get_news("Covid", category="Health", number_of_news=10)
    excel = ExcelHandler()
    excel.save_news_to_excel(news)
    logger.info('Finished')
