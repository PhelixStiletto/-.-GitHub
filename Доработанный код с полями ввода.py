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

# Функция для получения кода двухфакторной аутентификации
def wait_for_new_2fa_code(username, password, mail_server='imap.mail.ru', wait_time=120):
    try:
        mail = imaplib.IMAP4_SSL(mail_server)
        mail.login(username, password)
        mail.select('inbox')

        status, messages = mail.search(None, '(FROM "no-reply@ati.su")')
        message_ids = messages[0].split()
        latest_email_id = message_ids[-1]

        status, data = mail.fetch(latest_email_id, '(RFC822)')
        msg = email.message_from_bytes(data[0][1])
        message_body = msg.get_payload(decode=True).decode()

        code_match = re.search(r'Код для двухфакторной аутентификации.*?<strong>(\d{4})</strong>', message_body)
        if code_match:
            print(f"Код для входа: {code_match.group(1)}")
            return code_match.group(1)

    except Exception as e:
        print("Ошибка при получении кода из e-mail:", e)
        return None

# Инициализируем WebDriver
driver = webdriver.Chrome(service=service, options=options)

def save_screenshot(name):
    screenshot_path = os.path.join(os.getcwd(), f"{name}.png")
    driver.save_screenshot(screenshot_path)
    print(f"Скриншот сохранён: {screenshot_path}")

try:
    driver.get("https://loads.ati.su/orders/cargoOwner/reports")
    print("Сайт открыт.")
    save_screenshot("site_opened")

    login_field_xpath = "/html/body/div[4]/div/div[1]/div[2]/div/div[2]/div/div[1]/div[4]/input"
    login_field = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, login_field_xpath)))
    login_field.send_keys(USERNAME)
    print("Логин введён.")
    save_screenshot("login_entered")

    password_field_xpath = "/html/body/div[4]/div/div[1]/div[2]/div/div[2]/div/div[1]/div[5]/input"
    password_field = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, password_field_xpath)))
    password_field.send_keys(PASSWORD)
    print("Пароль введён.")
    save_screenshot("password_entered")

    submit_button_xpath = "/html/body/div[4]/div/div[1]/div[2]/div/div[2]/div/div[2]/div[1]/button"
    submit_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, submit_button_xpath)))
    submit_button.click()
    print("Кнопка 'Войти' нажата.")
    save_screenshot("submit_clicked")

    # Получаем код двухфакторной аутентификации
    code = wait_for_new_2fa_code(USERNAMEMAILRU, PASSWORDMAILRU)
    if code:
        code_input_xpath = "/html/body/div[4]/div/div[1]/div[2]/div/div/div[1]/div[3]/div/div/div/label/input"
        code_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, code_input_xpath)))
        code_field.send_keys(code)
        print("Код двухфакторной аутентификации введён.")
        save_screenshot("code_entered")

        # Переключаемся на активное окно браузера
        driver.switch_to.window(driver.window_handles[-1])
        print("Переключились на активное окно.")

        continue_button_xpath = "/html/body/div[4]/div/div[1]/div[2]/div/div/div[2]/button"
        continue_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, continue_button_xpath)))
        save_screenshot("before_continue_clicked")
        continue_button.click()
        print("Кнопка 'Продолжить' нажата.")
        save_screenshot("continue_clicked")

    else:
        print("Не удалось получить код двухфакторной аутентификации.")

except Exception as e:
    print("Произошла ошибка:", e)

finally:
    driver.quit()
    print("WebDriver завершён.")
