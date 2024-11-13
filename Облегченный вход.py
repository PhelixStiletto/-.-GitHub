import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Путь к драйверу Chrome
driver_path = "C:/chromedriver-win64/chromedriver.exe"
service = Service(driver_path)

# Настройки WebDriver
options = webdriver.ChromeOptions()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--disable-extensions")
options.add_argument("--headless=new")
options.add_argument("--remote-debugging-port=9222")
profile_path = f"{os.path.expanduser('~')}/AppData/Local/Google/Chrome/SeleniumProfile"
options.add_argument(f"user-data-dir={profile_path}")

# Функция загрузки конфигурации

# Инициализируем WebDriver
try:
    driver = webdriver.Chrome(service=service, options=options)
    driver.get("https://loads.ati.su/orders/cargoOwner/reports")
    print("Страница отчётов открыта.")

    # Делаем скриншот сразу после открытия страницы



    # Ожидание загрузки страницы после входа
    time.sleep(5)
    driver.save_screenshot("after_login.png")
    print("Скриншот страницы после входа сохранён: after_login.png")

except Exception as e:
    print("Произошла ошибка:", e)

finally:
    driver.quit()
    print("WebDriver завершён.")
