import os
import time
import imaplib
import email
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
MAIL_USERNAME = config.get("USERNAMEMAILRU")
MAIL_PASSWORD = config.get("PASSWORDMAILRU")

# Функция для получения кода двухфакторной аутентификации с почты
def get_auth_code():
    mail = imaplib.IMAP4_SSL("imap.mail.ru")
    mail.login(MAIL_USERNAME, MAIL_PASSWORD)
    mail.select("inbox")

    result, data = mail.search(None, 'FROM "no-reply@ati.su"')
    mail_ids = data[0].split()
    latest_email_id = mail_ids[-1]

    result, message_data = mail.fetch(latest_email_id, "(RFC822)")
    raw_email = message_data[0][1].decode("utf-8")
    email_message = email.message_from_string(raw_email)

    for part in email_message.walk():
        if part.get_content_type() == "text/html":
            html_content = part.get_payload(decode=True).decode("utf-8")
            import re
            match = re.search(r"Код для двухфакторной аутентификации[:\s]*(\d{4})", html_content)
            if match:
                print(f"Код для входа: {match.group(1)}")
                return match.group(1)

    return None

# Инициализируем WebDriver
try:
    driver = webdriver.Chrome(service=service, options=options)
    driver.get("https://loads.ati.su/orders/cargoOwner/reports")
    print("Страница отчётов открыта.")

    # Вход на сайт
    login_xpath = "/html/body/div[4]/div/div[1]/div[2]/div/div[2]/div/div[1]/div[4]/input"
    password_xpath = "/html/body/div[4]/div/div[1]/div[2]/div/div[2]/div/div[1]/div[5]/input"
    submit_xpath = "/html/body/div[4]/div/div[1]/div[2]/div/div[2]/div/div[2]/div[1]/button"

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, login_xpath))).send_keys(USERNAME)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, password_xpath))).send_keys(PASSWORD)
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, submit_xpath))).click()
    print("Кнопка 'Войти' нажата.")

    # Ожидание появления поля для ввода кода
    code_input_xpath = "/html/body/div[4]/div/div[1]/div[2]/div/div[2]/div/div[1]/div[6]/input"
    code_input = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, code_input_xpath)))

    # Получаем код с почты
    auth_code = get_auth_code()
    if auth_code:
        code_input.send_keys(auth_code)
        print(f"Код для входа введён: {auth_code}")

        # Подтверждение кода
        confirm_button_xpath = "/html/body/div[4]/div/div[1]/div[2]/div/div[2]/div/div[2]/div[2]/button"
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, confirm_button_xpath))).click()
        print("Код подтверждён.")
    else:
        print("Не удалось получить код двухфакторной аутентификации.")
        driver.quit()
        exit()

    # Ожидание загрузки страницы после входа
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    print("Вход выполнен успешно.")

    # Нажимаем на кнопку "Скачать отчёт"
    button_download_xpath = "/html/body/div[3]/div[2]/div/div[1]/div[2]/div[3]/div[3]/div/div/button"
    button_download = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, button_download_xpath)))
    button_download.click()
    print("Кнопка 'Скачать отчёт' нажата.")

    # Выбираем CSV-отчёт
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
