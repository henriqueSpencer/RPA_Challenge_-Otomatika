from RPA.Browser.Selenium import Selenium
from RPA.FileSystem import FileSystem
from RPA.Excel.Files import Files
from robocorp.tasks import task
from robocorp import workitems
import time
import os
import requests
from datetime import datetime
from abc import ABC  # I'' using to specify that the class is abstract
from logs_handler import logger


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

    def get_news(self, search_phrase: str, category: str = None, months_to_download: int = 100) -> list[dict]:
        """
        This method will search for news on the AP News site based on the given parameters
        :param search_phrase: phrase to search for
        :param category: category of the news search
        :param months_to_download: number of months for which you need to receive news

        :return: dictionary with the information of the news found
        """
        logger.info('Get news with the parametres: | search_phrase: %s | category: %s | months_to_download: %s',
                    search_phrase, category, months_to_download)
        # treat months_to_download
        months_to_download = months_to_download if months_to_download >= 1 else 1

        # Handling the pop-up
        try:
            self.browser.wait_until_element_is_visible('//a[@title="Close" and @class="fancybox-item fancybox-close"]',
                                                       timeout=180)
            self.browser.click_element('//a[@title="Close" and @class="fancybox-item fancybox-close"]')
        except:
            logger.critical('There was no popup on the screen')

        # Opening the search bar
        logger.info('Opening the search bar')
        self.browser.wait_until_element_is_visible('//button[@class="SearchOverlay-search-button"]', timeout=10)
        botao = self.browser.find_element('//button[@class="SearchOverlay-search-button"]')
        botao.click()

        # Typing the search phrase and submitting the form
        logger.info('Typing the search phrase')
        self.browser.wait_until_element_is_visible('//input[@class="SearchOverlay-search-input"]', timeout=10)
        self.browser.input_text('//input[@class="SearchOverlay-search-input"]', search_phrase)
        self.browser.click_element('//button[@class="SearchOverlay-search-submit"]')

        # filter by categories:
        logger.info('filtering by categories')
        self.browser.click_element("css:.SearchFilter-heading[data-toggle-trigger='search-filter']")
        categorys_obj = self.browser.find_elements("css:.SearchFilterInput input[type='checkbox']")
        avalibles_categorys = [categorias.text for categorias in categorys_obj]
        if (category is not None) and category in avalibles_categorys:
            category_index = avalibles_categorys.index(category)
            categorys_obj[category_index].click()

        # Find all news items
        logger.info('Finding all news items')
        self.browser.wait_until_element_is_visible("css:.SearchResultsModule-results")
        news_part = self.browser.find_element("css:.SearchResultsModule-results")
        news_items = self.browser.find_elements("css:.PageList-items-item", news_part)

        return self.__treat_news_obj(news_items, search_phrase, months_to_download)

    def __treat_news_obj(self, news_items: list, search_phrase: str, months_to_download: int) -> list[dict]:
        """
        This method will treat the news items found on the AP News site
        :param news_items: list of news items found on the site
        :param search_phrase: phrase to search for
        :param months_to_download: number of months for which you need to receive news
        :return: list of dictionaries with the information of the news found
        """
        logger.info('Treating news items')
        output_lines = []
        for index, item in enumerate(news_items):
            try:

                texto_noticia = item.text
                title = texto_noticia.split("\n")[0]
                date_str = texto_noticia.split("\n")[-1]
                date = datetime.strptime(f"{date_str} {datetime.now().year}", '%B %d %Y').date()
                description = texto_noticia.replace(f"{title}\n", '')

                if date.month > (datetime.today().month + months_to_download - 1):
                    logger.info('get the number of news requested')
                    break

                file_name = self.__find_and_download_image(item, index)

                occurrence_search_phrase = texto_noticia.lower().count(search_phrase.lower())
                occurrence_money = texto_noticia.lower().count("$".lower()) \
                                   + texto_noticia.lower().count("dollars".lower()) \
                                   + texto_noticia.lower().count("USD".lower())
                money_in_description = False
                if occurrence_money > 0:
                    money_in_description = True

                output_lines.append({"title": title,
                                     "date": date,
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
            logger.info('saving news to excel')
            columns_order_excel = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
            columns = list(excel_lines[0].keys())

            # fill the header
            index_col = 0
            for column in columns:
                self.lib.set_cell_value(1, columns_order_excel[index_col], column)
                index_col += 1

            # fill the lines
            for index_line, line in enumerate(excel_lines):
                index_col = 0
                index_line += 2
                for column in columns:
                    self.lib.set_cell_value(index_line, columns_order_excel[index_col], line[column])
                    index_col += 1
        except Exception as e:
            logger.error('Error saving news to excel: %s', e)
        finally:
            self.lib.save_workbook()
            self.lib.close_workbook()


@task
def task_handler():
    """ This task will get the news from the AP News site and save it to an excel file"""
    info = handle_parametres()
    ap = ApNewsSite()
    news = ap.get_news(info['news'], category=info['category'], months_to_download=info['months_to_download'])
    excel = ExcelHandler()
    excel.save_news_to_excel(news)
    logger.info('Finished')


def handle_parametres():
    """This method will handle the parameters received from the input of the task"""
    return_info = {}
    item = workitems.inputs.current
    print("Received payload:", item.payload)
    logger.info(f"Received payload: {item.payload}")
    dict_parametres = dict(item.payload)
    return_info['news'] = dict_parametres.get('news') if dict_parametres.get('news') is not None else 'Covid'
    return_info['category'] = dict_parametres.get('category') if dict_parametres.get('category') is not None\
        else "Health"
    return_info['months_to_download'] = dict_parametres.get('months_to_download') if \
        dict_parametres.get('months_to_download') is not None else 2

    return return_info

# if __name__ == '__main__':
#     task_handler()
#     ap = ApNewsSite()
#     news = ap.get_news("Covid", category="Health", months_to_download=10)
#     excel = ExcelHandler()
#     excel.save_news_to_excel(news)
#     logger.info('Finished')
