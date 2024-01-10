# Import necessary libraries
from RPA.Browser.Selenium import Selenium
from RPA.FileSystem import FileSystem
from RPA.HTTP import HTTP
from datetime import datetime
import lxml.html as html
import re

# NewsScraper class encapsulating the scraping logic
class NewsScraper:
    # Define constants
    HOME_URL = 'https://nypost.com/'
    OUTPUT_DIR = '/Users/tendai/Desktop/Robocorp/output/'
    # XPath expressions for various webpage elements
    X_CATEGORIES = '//div[contains(@class, "home-page-section")]/div/h2/a/text()'
    X_NEWS_X_CAT = '//div[contains(@class, "home-page-section")][{}]/div[@class="featured-stories"]/article/div/div/a/@href'
    X_TITLE = '//h1/text()'
    X_BODY = '//div[contains(@class, "entry-content")]/p/text()'
    X_IMAGE = '//div[@class="entry-content entry-content-read-more"]//img/@src'

    # Constructor to initialize RPA components
    def __init__(self):
        self.browser = Selenium()
        self.fs = FileSystem()
        self.http = HTTP()

    # Method to create a directory for storing downloaded data
    def create_dir(self, name):
        today = datetime.today().strftime('%Y-%m-%d')
        new_dir = self.fs.join_path(self.OUTPUT_DIR, today, name)
        self.fs.create_directory(new_dir, parents=True)
        return new_dir

    # Method to download images
    def download_image(self, image_url, file_path):
        try:
            response = self.http.download(image_url, file_path)
            if not response.ok:
                print(f'Error downloading image: {response.status}')
        except Exception as e:
            print(f'Error downloading image: {e}')

    # Method to parse the homepage and retrieve news categories
    def parse_home(self):
        try:
            response = self.http.get(self.HOME_URL)
            if not response.ok:
                raise ValueError(f'Server status code: {response.status}')

            home_page = response.text
            html_var = html.fromstring(home_page)
            list_categories = enumerate(html_var.xpath(self.X_CATEGORIES), start=1)
            self.get_news(html_var, list_categories)
        except ValueError as ve:
            print(ve)

    # Method to process each news category and download articles
    def get_news(self, html_var, list_categories):
        for category_id, category_name in list_categories:
            cat_dir = self.create_dir(category_name)
            category_x = self.X_NEWS_X_CAT.format(category_id)
            links = html_var.xpath(category_x)

            for link in links:
                self.parse_notice(link, cat_dir)

    # Method to parse individual news articles and save to file
    def parse_notice(self, link, cat_dir):
        try:
            response = self.http.get(link)
            if not response.ok:
                raise ValueError(f'Server status code: {response.status}')

            notice = response.text
            notice_page = html.fromstring(notice)
            title = notice_page.xpath(self.X_TITLE)[0].strip()
            title = re.sub('[\"?:!¡]', '', title)
            date = datetime.now().strftime('%Y-%m-%d')
            body = notice_page.xpath(self.X_BODY)
            image_url = notice_page.xpath(self.X_IMAGE)[0] if notice_page.xpath(self.X_IMAGE) else None

            safe_title = re.sub('[^A-Za-z0-9]+', '_', title)
            filename = f'{safe_title}.txt'
            image_filename = f'{safe_title}.jpg' if image_url else None

            file_path = self.fs.join_path(cat_dir, filename)
            with self.fs.create_file(file_path, encoding='utf-8') as f:
                f.write(f'Title: {title}\nDate: {date}\n\n')
                for p in body:
                    f.write(p)
                    f.write('\n')

            if image_url:
                image_path = self.fs.join_path(cat_dir, image_filename)
                self.download_image(image_url, image_path)

        except ValueError as ve:
            print(ve)
        except OSError as ve:
            print(ve)

# Entry point to run the scraper
def run():
    scraper = NewsScraper()
    scraper.parse_home()

# Script execution starts here
if __name__ == '__main__':
    run()
