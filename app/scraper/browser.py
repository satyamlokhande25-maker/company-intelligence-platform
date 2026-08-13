from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def create_driver():
    options = Options()

    # Streamlit Cloud (Linux) ke liye Headless mode aur crucial flags zaroori hain
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--remote-debugging-port=9222")

    # Basic stability options
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")

    driver = webdriver.Chrome(options=options)

    return driver