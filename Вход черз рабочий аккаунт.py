import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import os

# Путь к ChromeDriver и Chromium
driver_path = "C:/chromedriver-win64/chromedriver.exe"
chromium_path = "C:/Users/Артур/AppData/Local/Chromium/Application/chrome.exe"

# Настройки WebDriver
service = Service(driver_path)
options = Options()
options.binary_location = chromium_path
options.add_argument("--remote-debugging-port=9223")
options.add_argument("--user-data-dir=C:/Users/Артур/AppData/Local/Chromium/User Data/Default")
options.debugger_address = "127.0.0.1:9223"

# Директория для скриншотов
screenshot_dir = "screenshots"
os.makedirs(screenshot_dir, exist_ok=True)


def save_screenshot(driver, step_name):
    screenshot_path = os.path.join(screenshot_dir, f"{step_name}.png")
    driver.save_screenshot(screenshot_path)
    print(f"Скриншот '{step_name}' сохранён: {screenshot_path}")


try:
    # Проверка подключения к Chromium
    print("Проверка подключения к Chromium...")
    response = requests.get("http://localhost:9223/json/version", timeout=10)
    if response.status_code != 200:
        raise Exception("Не удалось подключиться к Chromium.")

    browser_info = response.json()
    browser_version = browser_info.get("Browser", "Неизвестная версия")
    print(f"Подключение установлено. Версия браузера: {browser_version}")

    # Запуск WebDriver и подключение к Chromium
    driver = webdriver.Chrome(service=service, options=options)
    save_screenshot(driver, "connected")

    # Переход на сайт АТИ.су
    driver.get("https://loads.ati.su/orders/cargoOwner/reports")
    print("Сайт АТИ.су открыт.")
    save_screenshot(driver, "site_opened")

    # Нажимаем кнопку "Скачать отчёт"
    download_button_xpath = "/html/body/div[3]/div[2]/div/div[1]/div[2]/div[3]/div[3]/div/div/button"
    download_button = driver.find_element("xpath", download_button_xpath)
    download_button.click()
    print("Кнопка 'Скачать отчёт' нажата.")
    save_screenshot(driver, "download_button_clicked")

    # Выбираем формат Excel
    excel_button_xpath = "/html/body/div[3]/div[2]/div/div[1]/div[2]/div[3]/div[3]/div/div/div/div/button[2]"
    excel_button = driver.find_element("xpath", excel_button_xpath)
    excel_button.click()
    print("Формат Excel выбран.")
    save_screenshot(driver, "excel_button_clicked")

    time.sleep(10)
    print("Загрузка отчёта завершена.")

except Exception as e:
    print(f"Произошла ошибка: {e}")

finally:
    input("Нажмите Enter для завершения работы скрипта без закрытия Chromium...")

