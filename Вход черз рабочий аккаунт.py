import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Путь к ChromeDriver
driver_path = "C:/chromedriver-win64/chromedriver.exe"
service = Service(driver_path)

# Настройки Chrome
options = Options()
options.add_argument("--start-maximized")
options.add_experimental_option("debuggerAddress", "127.0.0.1:9223")

try:
    # Запуск WebDriver с отладочным портом
    driver = webdriver.Chrome(service=service, options=options)

    # Переход на страницу отчёта
    driver.get("https://loads.ati.su/orders/cargoOwner/reports")
    print("Сайт открыт. Ожидаем загрузку страницы...")

    # Ждём загрузки страницы и проверяем, что элемент отчёта загружен
    wait = WebDriverWait(driver, 10)
    report_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Скачать отчёт')]")))

    # Нажимаем кнопку "Скачать отчёт"
    report_button.click()
    print("Отчёт успешно загружается.")

    # Ждём несколько секунд для завершения загрузки
    time.sleep(10)

except Exception as e:
    print("Произошла ошибка:", e)

finally:
    # Не закрываем драйвер, чтобы оставить открытый браузер
    input("Нажмите Enter для завершения работы скрипта без закрытия Chrome...")
