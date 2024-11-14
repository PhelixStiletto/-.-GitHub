# Настройки WebDriver
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--no-sandbox")
options.add_argument("--disable-gpu")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--user-data-dir=C:/Users/Артур/AppData/Local/Google/Chrome/User Data/SeleniumProfile")
options.add_argument("--profile-directory=Default")
options.add_argument("--remote-debugging-port=9222")
options.add_argument("--headless=new")  # Включаем headless-режим
options.add_argument("--disable-save-password-bubble")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)

try:
    driver = webdriver.Chrome(service=service, options=options)
    print("WebDriver успешно запущен.")
except Exception as e:
    print("Ошибка при запуске WebDriver:", e)
