# from robocorp.tasks import task
#
# @task
# def minimal_task():
#     message = "Hello"
#     message = message + " World!"


# pip install rpaframework
from RPA.Browser.Selenium import Selenium
from RPA.FileSystem import FileSystem
FileSystem().create_file("output/text.txt", img, overwrite=True)
# Ele n fecha o browser dps de rodar o codigo
browser = Selenium(auto_close=False)

def store_web_page():
    # The robot will look for an available browser and open the given URL
    browser.open_available_browser()
    browser.go_to("https://robotsparebinindustries.com/")

    #browser.find_element("xpath", "//a[@href]")
    links = browser.get_webelements("css:.site-navigation a")

    links = browser.find_elements("//a[@href]")
    links[0].get_attribute("innerHTML")
    links[0].click()

    links[0].send_keys("Hello")
    links[0].send_keys(Keys.ENTER)

    text = browser.get_text("css:body")
    FileSystem().create_file("output/text.txt", text, overwrite=True)
    browser.screenshot("css:h1", "output/screenshot.png")

    #Xpath
    '''
    // - select all elements
    /  - direct child que está abaixo
    @ - atributo dentro de uma tag
    Ex: //article//a/@title
    
    '''


def main():
    try:
        store_web_page()
    finally:
        browser.close_browser()

if __name__ == "__main__":
    main()

    """
    - Select News Site
    - search phrase
    - news category/section/topic
    - number of months for which you need to receive news
    These may be defined within a configuration file, but we’d prefer they be provided via a Robocloud workitem
    """