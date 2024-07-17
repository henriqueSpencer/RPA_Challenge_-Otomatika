
from time import sleep
from RPA.Excel.Files import Files
from RPA.Browser.Selenium import Selenium
import random

#
# EDIT THESE VARIABLES
mindelay = 5
maxdelay = 10

browser = Selenium(auto_close=False)


def minimal_task():

    # open browser
    browser.open_available_browser("https://www.google.com/?hl=en")
    sleep(4)
    #browser.click_element("//div[text()='I agree']")

    # Open Excel File

    lib = Files()
    lib.open_workbook("brands.xlsx")
    rows = lib.read_worksheet("Sheet1")

    row_index = 1

    # For each line
    for row in rows:

        # Read brand
        print(row["A"])

        # Search Google
        browser.press_keys("//input[@name='btnK']",
                           '"' + str(row["A"]) + '"' + '\ue007')

        # Get First Result

        mylinks = browser.get_webelements("//div[@id='search']//a")
        link = ""

        for web_element in mylinks:
            link = web_element.get_attribute('href')
            break
            # enable this to remove google links
            # print(link)
            # if link != None and "google.com" in link:
            #     continue
            # else:
            #     print(link)

        # Edit excel file column(s)

        lib.set_cell_value(row_index, "B", link)

        # Delay
        row_index = row_index + 1

        delay = random.randint(mindelay, maxdelay)
        sleep(delay)

        browser.go_to("https://www.google.com/?hl=en")
        lib.save_workbook()

    lib.close_workbook()

    # Next

    print("Done.")


if __name__ == "__main__":
    minimal_task()