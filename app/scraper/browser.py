from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def create_driver():
    options = Options()

    # Browser UI dikhega
    # Headless mode baad mein enable kar sakte hain
    options.add_argument("--start-maximized")

    # Basic stability options
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")

    driver = webdriver.Chrome(options=options)

    return driver