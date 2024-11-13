import os
import time
import pandas as pd
import requests
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
API_TOKEN = config.get("API_TOKEN")

# Функция для скачивания отчёта
def download_report(driver):
    button_load_xpath = "/html/body/div[3]/div[2]/div/div[1]/div[2]/div[3]/div[3]/div/div/button"
    button_csv_xpath = "/html/body/div[3]/div[2]/div/div[1]/div[2]/div[3]/div[3]/div/div/div/div/button[1]"
    button_load = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, button_load_xpath)))
    button_load.click()
    time.sleep(1)
    button_csv = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, button_csv_xpath)))
    button_csv.click()
    print("Отчёт загружается...")
    time.sleep(10)

# Функция для извлечения названий фирм из отчёта
def extract_firm_names(report_path):
    df = pd.read_excel(report_path)
    firm_names = df['F'].dropna().unique()
    return firm_names

# Функция для поиска фирмы на сайте
def find_firm(driver, firm_name):
    search_button_xpath = "/html/body/div[2]/div/header/div[4]/div/button"
    search_input_xpath = "//*[@id='header']/div/header/div[2]/div/input"
    search_result_xpath = "/html/body/div[2]/div/header/div[2]/div/div[2]/div/div[1]/div/a[1]/div/div/div[2]"

    search_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, search_button_xpath)))
    search_button.click()

    search_input = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, search_input_xpath)))
    search_input.clear()
    search_input.send_keys(firm_name)
    time.sleep(2)

    try:
        search_result = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, search_result_xpath)))
        result_text = search_result.text
        ati_id = result_text.split("Код ATI.SU:")[1].split(",")[0].strip()
        return ati_id
    except Exception:
        print(f"Фирма '{firm_name}' не найдена.")
        return None

# Функция для получения контактов фирмы
def get_firm_contacts(ati_id):
    url = f"https://ati.su/developers/api/v1.0/firms/{ati_id}/contacts/summary"
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    return None

# Основной процесс
try:
    driver = webdriver.Chrome(service=service, options=options)
    driver.get("https://loads.ati.su/orders/cargoOwner/reports")
    print("Страница отчётов открыта.")

    # Вход на сайт
    login_xpath = "/html/body/div[4]/div/div[1]/div[2]/div/div[2]/div/div[1]/div[4]/input"
    password_xpath = "/html/body/div[4]/div/div[1]/div[2]/div/div[2]/div/div[1]/div[5]/input"
    submit_xpath = "/html/body/div[4]/div/div[1]/div[2]/div/div[2]/div/div[2]/div[1]/button"

    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, login_xpath))).send_keys(USERNAME)
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, password_xpath))).send_keys(PASSWORD)
    WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, submit_xpath))).click()
    print("Вход выполнен успешно.")

    # Скачиваем отчёт
    download_report(driver)

    # Извлекаем названия фирм и обрабатываем их
    report_path = "path_to_downloaded_report.xlsx"
    firm_names = extract_firm_names(report_path)

    for firm_name in firm_names:
        ati_id = find_firm(driver, firm_name)
        if ati_id:
            contacts = get_firm_contacts(ati_id)
            print(f"Контакты для {firm_name} (ATI ID: {ati_id}):", contacts)

except Exception as e:
    print("Произошла ошибка:", e)

finally:
    driver.quit()
    print("WebDriver завершён.")
