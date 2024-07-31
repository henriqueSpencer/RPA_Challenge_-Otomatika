from RPA.Browser.Selenium import Selenium
from RPA.FileSystem import FileSystem
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
        self.browser.maximize_browser_window()
        logger.info('Opened browser')


class ApNewsSite(PageElement):
    def __init__(self):
        super().__init__()
        self.browser.go_to("https://apnews.com/")
        # Open the second time to advertise be smaller
        self.browser.go_to("https://apnews.com/")
        logger.info('Opened AP News Site')

    def handle_overlay(self):
        # Handling the overlay
        try:
            logger.info('Checking for overlay')
            self.browser.wait_until_element_is_not_visible('//div[contains(@class, "onetrust-pc-dark-filter")]',
                                                           timeout=30)
            logger.info('Overlay not found or disappeared')
        except Exception as e:
            logger.info('Overlay still present, attempting to remove it with JavaScript')
            self.browser.execute_javascript(
                "document.querySelector('.onetrust-pc-dark-filter').style.display = 'none';")

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
        except Exception as e:
            logger.critical('There was no popup on the screen')


        # Handling the overlay
        self.handle_overlay()

        # Opening the search bar
        logger.info('Opening the search bar')
        #self.browser.execute_javascript("window.scrollBy(0, 1000);")
        logger.info('Click Button search bar')
        self.browser.wait_until_element_is_visible('//button[@class="SearchOverlay-search-button"]', timeout=10)
        self.browser.click_element('//button[@class="SearchOverlay-search-button"]')

        # Typing the search phrase and submitting the form
        logger.info('Typing the search phrase')
        self.browser.wait_until_element_is_visible('//input[@class="SearchOverlay-search-input"]', timeout=10)
        self.browser.input_text('//input[@class="SearchOverlay-search-input"]', search_phrase)
        self.browser.click_element('//button[@class="SearchOverlay-search-submit"]')

        # filter by categories:
        logger.info('filtering by categories')
        # Handling the overlay
        self.handle_overlay()
        self.browser.wait_until_element_is_visible("css:.SearchFilter-heading[data-toggle-trigger='search-filter']"
                                                   , timeout=10)
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
        until_month = datetime.today().month - months_to_download
        for index, item in enumerate(news_items):
            try:

                texto_noticia = item.text
                title = texto_noticia.split("\n")[0]
                date_str = texto_noticia.split("\n")[-1]
                date = datetime.strptime(f"{date_str} {datetime.now().year}", '%B %d %Y').date()
                description = texto_noticia.replace(f"{title}\n", '')

                if date.month <= until_month:
                    logger.info('get the number of news requested')
                    continue

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
