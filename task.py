from RPA.Browser.Selenium import Selenium
from RPA.Excel.Files import Files
from RPA.Robocorp.WorkItems import WorkItems
import re
import datetime

browser = Selenium()
excel = Files()
workitems = WorkItems()

def get_search_parameters():
    search_phrase = workitems.get_work_item_variable("search_phrase")
    news_category = workitems.get_work_item_variable("news_category")
    num_months = int(workitems.get_work_item_variable("num_months"))
    return search_phrase, news_category, num_months

def open_site_and_search(search_phrase):
    browser.open_available_browser("https://www.aljazeera.com/")
    browser.input_text("css:#search-input", search_phrase)
    browser.press_keys("css:#search-input", "ENTER")

def process_news_items(search_phrase, num_months):
    current_month = datetime.datetime.now().month
    start_month = current_month - num_months + 1

    excel.create_workbook("news_data.xlsx")
    excel.rename_worksheet("Sheet", "News Data")
    excel.append_rows_to_worksheet([["Title", "Date", "Description", "Picture Filename", "Count of Search Phrases", "Contains Money"]], "News Data")

    news_items = browser.find_elements("css:article a")
    for item in news_items:
        title = browser.get_element_text(item)
        date = browser.get_element_attribute(item, "href") # Assuming date is part of URL
        description = "" # Assuming description is not immediately available

        month_in_url = int(re.search(r'/202[0-9]/([0-9]+)/', date).group(1))
        if month_in_url < start_month:
            break

        browser.click_element(item)
        browser.wait_until_element_is_visible("css:.article-heading", timeout=10)
        description = browser.get_element_text("css:.article-body") # Update with correct selector

        phrase_count = title.count(search_phrase) + description.count(search_phrase)
        contains_money = bool(re.search(r"\$\d+(\.\d+)?|\d+ (dollars|USD)", title + description))

        image_url = browser.get_element_attribute("css:.article-image img", "src") # Update with correct selector
        image_filename = download_image(image_url)
        excel.append_rows_to_worksheet([[title, date, description, image_filename, phrase_count, contains_money]], "News Data")

        browser.go_back()

    excel.save_workbook("news_data.xlsx")

def download_image(image_url):
    image_filename = image_url.split("/")[-1]
    browser.download(image_url, f"output/{image_filename}")
    return image_filename

def main():
    try:
        search_phrase, news_category, num_months = get_search_parameters()
        open_site_and_search(search_phrase)
        process_news_items(search_phrase, num_months)
    finally:
        browser.close_browser()

if __name__ == "__main__":
    main()
