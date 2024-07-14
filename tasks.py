# from robocorp.tasks import task
#
# @task
# def minimal_task():
#     message = "Hello"
#     message = message + " World!"


# pip install rpaframework
from RPA.Browser.Selenium import Selenium
from RPA.FileSystem import FileSystem

browser = Selenium()

def store_web_page():
    browser.open_available_browser("https://robotframework.org")
    text = browser.get_text("css:body")
    FileSystem().create_file("output/text.txt", text, overwrite=True)
    browser.screenshot("css:h1", "output/screenshot.png")


def main():
    try:
        store_web_page()
    finally:
        browser.close_browser()

if __name__ == "__main__":
    main()