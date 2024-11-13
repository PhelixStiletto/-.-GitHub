import os
import time
import re
import imaplib
import email
from email.utils import parsedate_to_datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service

# Путь к драйверу Chrome
driver_path = "C:/chromedriver-win64/chromedriver.exe"
service = Service(driver_path)

# Настройки WebDriver
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--no-sandbox")
options.add_argument("--disable-gpu")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)


# Отключаем headless-режим
# options.add_argument("--headless=new")

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
USERNAMEMAILRU = config.get("USERNAMEMAILRU")
PASSWORDMAILRU = config.get("PASSWORDMAILRU")


# Функция для получения кода из нового письма
def wait_for_new_2fa_code(username, password, mail_server='imap.mail.ru', wait_time=120):
    try:
        mail = imaplib.IMAP4_SSL(mail_server)
        mail.login(username, password)
        mail.select('inbox')

        status, messages = mail.search(None, '(FROM "no-reply@ati.su")')
        if status != 'OK' or not messages[0]:
            print("Письмо от 'no-reply@ati.su' не найдено в папке 'Входящие'.")
            return None

        message_ids = messages[0].split()
        latest_email_id = message_ids[-1]
        status, data = mail.fetch(latest_email_id, '(RFC822)')
        if status != 'OK':
            print("Ошибка при чтении последнего письма.")
            return None

        msg = email.message_from_bytes(data[0][1])
        last_date = parsedate_to_datetime(msg.get("Date"))
        print(f"Дата последнего известного письма: {last_date}")

        end_time = time.time() + wait_time
        while time.time() < end_time:
            status, messages = mail.search(None, '(FROM "no-reply@ati.su")')
            if status == 'OK' and messages[0]:
                message_ids = messages[0].split()
                latest_email_id = message_ids[-1]

                status, data = mail.fetch(latest_email_id, '(RFC822)')
                if status != 'OK':
                    continue

                msg = email.message_from_bytes(data[0][1])
                email_date = parsedate_to_datetime(msg.get("Date"))
                print(f"Дата последнего полученного письма: {email_date}")

                if email_date > last_date:
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/html":
                                message_body = part.get_payload(decode=True).decode()
                                break
                    else:
                        message_body = msg.get_payload(decode=True).decode()

                    code_match = re.search(r'Код для двухфакторной аутентификации.*?<strong>(\d{4})</strong>',
                                           message_body)
                    if code_match:
                        return code_match.group(1)

            print("Ожидание нового письма...")
            time.sleep(5)

        print("Не удалось получить код двухфакторной аутентификации.")
        return None

    except Exception as e:
        print("Ошибка при получении кода из e-mail:", e)
        return None


# Инициализируем WebDriver
driver = webdriver.Chrome(service=service, options=options)

try:
    driver.get("https://loads.ati.su/orders/cargoOwner/reports")
    print("Сайт открыт.")

    time.sleep(0.5)

    login_field_xpath = "/html/body/div[4]/div/div[1]/div[2]/div/div[2]/div/div[1]/div[4]/input"
    login_field = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, login_field_xpath)))
    login_field.send_keys(USERNAME)
    print("Логин введён.")

    password_field_xpath = "/html/body/div[4]/div/div[1]/div[2]/div/div[2]/div/div[1]/div[5]/input"
    password_field = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, password_field_xpath)))
    password_field.send_keys(PASSWORD)
    print("Пароль введён.")

    submit_button_xpath = "/html/body/div[4]/div/div[1]/div[2]/div/div[2]/div/div[2]/div[1]/button"
    submit_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, submit_button_xpath)))
    submit_button.click()
    print("Кнопка 'Войти' нажата.")

    code = wait_for_new_2fa_code(USERNAMEMAILRU, PASSWORDMAILRU)
    if code:
        print(f"Код двухфакторной аутентификации: {code}")

        code_field_xpath = "/html/body/div[6]/div/div[1]/div[1]/div/div[2]/div/div[5]/div/div/div/div/div[2]/div/div/div[2]/div[1]/div[4]/div[2]/div/div/div/div/div/div/div/div/div/div/table/tbody/tr/td/div"
        code_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, code_field_xpath)))

        # Используем JavaScript для ввода кода
        driver.execute_script("arguments[0].value = arguments[1];", code_field, code)
        print("Код двухфакторной аутентификации введён.")

        confirm_button_xpath = "//*[@id='recin623450546_mr_css_attr']/tbody/tr/td/table/tbody/tr/td/div"
        confirm_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, confirm_button_xpath)))
        confirm_button.click()
        print("Код подтверждён.")

    else:
        print("Не удалось получить код двухфакторной аутентификации.")

except Exception as e:
    print("Произошла ошибка:", e)

finally:
    driver.quit()
