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
def load_config(file_path='config.txt'):
    config = {}
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            key, value = line.strip().split('=', 1)
            config[key] = value
    return config

config = load_config()
USERNAME = config.get("USERNAME")
PASSWORD = config.get("PASSWORD")

# Инициализируем WebDriver
try:
    driver = webdriver.Chrome(service=service, options=options)
    driver.get("https://loads.ati.su/orders/cargoOwner/reports")
    print("Страница отчётов открыта.")

    # Ввод логина и пароля и вход
    login_xpath = "/html/body/div[4]/div/div[1]/div[2]/div/div[2]/div/div[1]/div[4]/input"
    password_xpath = "/html/body/div[4]/div/div[1]/div[2]/div/div[2]/div/div[1]/div[5]/input"
    submit_xpath = "/html/body/div[4]/div/div[1]/div[2]/div/div[2]/div/div[2]/div[1]/button"

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, login_xpath))).send_keys(USERNAME)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, password_xpath))).send_keys(PASSWORD)
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, submit_xpath))).click()
    print("Вход выполнен успешно.")

    time.sleep(5)
    driver.save_screenshot("after_login.png")
    print("Скриншот страницы после входа сохранён: after_login.png")

    # Нажимаем на кнопку "Скачать отчёт"
    button_download_xpath = "/html/body/div[3]/div[2]/div/div[1]/div[2]/div[3]/div[3]/div/div/button"
    button_download = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, button_download_xpath)))
    button_download.click()
    print("Кнопка 'Скачать отчёт' нажата.")

    # Нажимаем на кнопку скачивания CSV-отчёта
    button_csv_xpath = "/html/body/div[3]/div[2]/div/div[1]/div[2]/div[3]/div[3]/div/div/div/div/button[1]"
    button_csv = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, button_csv_xpath)))
    button_csv.click()
    print("Отчёт в формате CSV загружается...")

    # Ожидание завершения загрузки отчёта
    time.sleep(10)
    print("Отчёт успешно загружен в формате CSV.")

except Exception as e:
    print("Произошла ошибка:", e)

finally:
    driver.quit()
    print("WebDriver завершён.")
