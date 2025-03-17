from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def update_driver():
    service = Service(executable_path=ChromeDriverManager().install())
    return service


def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(service=update_driver(), options=chrome_options)
    return driver
