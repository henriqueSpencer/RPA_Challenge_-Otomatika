from RPA.Browser.Selenium import Selenium
from RPA.FileSystem import FileSystem
from RPA.Excel.Files import Files
import time
import os
import requests
from datetime import datetime


if __name__ == '__main__':
    browser = Selenium(auto_close=False)
    # The robot will look for an available browser and open the given URL
    browser.open_available_browser()
    browser.go_to("https://apnews.com/")

    try:
        browser.wait_until_element_is_visible('//a[@title="Close" and @class="fancybox-item fancybox-close"]', timeout=60)
        browser.click_element('//a[@title="Close" and @class="fancybox-item fancybox-close"]')
    except:
        print('Não teve pop up na pagina')




    browser.wait_until_element_is_visible('//button[@class="SearchOverlay-search-button"]', timeout=10)
    botao = browser.find_element('//button[@class="SearchOverlay-search-button"]')
    # browser.execute_javascript("window.scrollBy(0, 100);")
    botao.click()

    # Aguarda até que o campo de busca esteja presente
    browser.wait_until_element_is_visible('//input[@class="SearchOverlay-search-input"]', timeout=10)
    browser.input_text('//input[@class="SearchOverlay-search-input"]', "Covid")

    # Aguarda até que o botão de busca esteja clicável
    #browser.wait_until_element_is_clickable('//button[@class="SearchOverlay-search-submit"]', timeout=10)

    # Clica no botão de envio do formulário
    browser.click_element('//button[@class="SearchOverlay-search-submit"]')

    # Filtros:
    browser.click_element("css:.SearchFilter-heading[data-toggle-trigger='search-filter']")

    categorias = browser.find_elements("css:.SearchFilterInput input[type='checkbox']")

    categorias[0].click()

    # Get the values: title, date, and description.
    # Wait for page elements to load
    browser.wait_until_element_is_visible("css:.PageList-items")

    # Find all news items
    # news_items = browser.find_elements("css:.PageList-items")
    # #news_items = browser.find_elements("css:.PageList-items-item")
    news_items = browser.find_elements("css:.SearchResultsModule-results")
    excel_lines = []
    for index, item in enumerate(news_items):
        texto_noticia = item.text
        title = texto_noticia.split("\n")[0]
        description = texto_noticia.replace(f"{title}\n", '')
        img = browser.find_element("css:.PagePromo-media img", item)
        img_url = img.get_attribute("src")
        print(title, description)
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        file_name = os.path.join(output_dir, f"image_{index + 1}.jpg")
        # Baixar a imagem
        response = requests.get(img_url)
        if response.status_code == 200:
            FileSystem().create_binary_file(path=file_name, content=response.content, overwrite=True)

        FileSystem.download(url=img_url, target=file_name)
        FileSystem().create_file(content=img_url, path=file_name)

        data=datetime.today().strftime('%Y-%m-%d')
        occurrence_search_phrase = texto_noticia.lower().count("Covid".lower())

        occurrence_money = texto_noticia.lower().count("$".lower()) \
                                   + texto_noticia.lower().count("dollars".lower()) \
                                   + texto_noticia.lower().count("USD".lower())
        money_in_description = False
        if occurrence_money > 0:
            money_in_description = True


        excel_lines.append({"title": title,
                            "date": data,
                            "description": description,
                            "file_name": file_name,
                            "search_phrases_title_and_description": "",
                            "money_in_description": money_in_description
        })


        # Creating the excel
        #FileSystem().create_file("output/news.xlsx", excel_lines, overwrite=True)
        lib = Files()
        work_book = lib.create_workbook(path="output/news.xlsx", fmt="xlsx", sheet_name="news")

        for index, line in enumerate(excel_lines):
            lib.set_cell_value(index, "A", line["title"])
            lib.save_workbook()
        lib.close_workbook()


    # Page Object Model (POM)
    # Domain Specific Language (DSL)

    # card = Card()
    """
    card.name
    card.description
    card.do
    card.cancel
    """

    from abc import ABC # Estou so dizendo q é uma classe abstrata
    class PageElement(ABC):
        def __init__(self):
            self.browser = Selenium()

        def open(self, url):
            pass