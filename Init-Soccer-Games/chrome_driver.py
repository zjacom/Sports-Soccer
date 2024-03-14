from selenium import webdriver
from selenium.webdriver.common.by import By
from tempfile import mkdtemp
from bs4 import BeautifulSoup


class Chrome_Driver():
    def create_soup(url):
        options = webdriver.ChromeOptions()
        service = webdriver.ChromeService("/opt/chromedriver")

        options.binary_location = '/opt/chrome/chrome'
        options.add_argument("--headless")
        options.add_argument('--no-sandbox')
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1280x1696")
        options.add_argument("--single-process")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-dev-tools")
        options.add_argument("--no-zygote")
        options.add_argument(f"--user-data-dir={mkdtemp()}")
        options.add_argument(f"--data-path={mkdtemp()}")
        options.add_argument(f"--disk-cache-dir={mkdtemp()}")
        options.add_argument("--remote-debugging-port=9222")

        chrome = webdriver.Chrome(options=options, service=service)
        chrome.get(url)

        chrome.switch_to.frame("content")
        soup = BeautifulSoup(chrome.page_source, 'html.parser')

        chrome.quit()
        return soup