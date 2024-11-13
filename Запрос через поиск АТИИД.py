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

    # Вход на сайт
    login_xpath = "/html/body/div[4]/div/div[1]/div[2]/div/div[2]/div/div[1]/div[4]/input"
    password_xpath = "/html/body/div[4]/div/div[1]/div[2]/div/div[2]/div/div[1]/div[5]/input"
    submit_xpath = "/html/body/div[4]/div/div[1]/div[2]/div/div[2]/div/div[2]/div[1]/button"
    

    # Ввод логина
    login_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, login_xpath)))
    login_field.send_keys(USERNAME)
    print("Логин введён.")

    # Ввод пароля
    password_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, password_xpath)))
    password_field.send_keys(PASSWORD)
    print("Пароль введён.")

    # Нажатие кнопки 'Войти'
    submit_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, submit_xpath)))
    submit_button.click()
    print("Кнопка 'Войти' нажата.")

    # Ожидание загрузки после входа
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    print("Вход выполнен успешно.")

except Exception as e:
    print("Произошла ошибка:", e)

finally:
    driver.quit()
    print("WebDriver завершён.")
