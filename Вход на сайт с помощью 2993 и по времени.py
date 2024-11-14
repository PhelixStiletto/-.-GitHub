import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import schedule

# Путь к ChromeDriver
driver_path = "C:/chromedriver-win64/chromedriver.exe"
service = Service(driver_path)

# Настройки Chrome
options = Options()
options.debugger_address = "127.0.0.1:9223"

def download_report():
    try:
        # Подключаемся к уже запущенному Chrome
        driver = webdriver.Chrome(service=service, options=options)

        # Переходим на страницу отчётов
        driver.get("https://loads.ati.su/orders/cargoOwner/reports")
        print("Сайт открыт. Ожидаем загрузку страницы...")

        # Ждём, пока загрузится страница
        WebDriverWait(driver, 10).until(EC.title_contains("Отчёты"))
        print("Страница загружена.")

        # Нажимаем кнопку "Скачать отчёт"
        button_download_xpath = "/html/body/div[3]/div[2]/div/div[1]/div[2]/div[3]/div[3]/div/div/button"
        button_download = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, button_download_xpath)))
        button_download.click()
        print("Кнопка 'Скачать отчёт' нажата.")

        # Выбираем формат отчёта (например, Excel)
        button_format_xpath = "/html/body/div[3]/div[2]/div/div[1]/div[2]/div[3]/div[3]/div/div/div/div/button[2]"
        button_format = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, button_format_xpath)))
        button_format.click()
        print("Формат отчёта выбран. Ожидаем загрузку...")

        # Делаем снимок экрана
        screenshot_name = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        driver.save_screenshot(screenshot_name)
        print(f"Снимок экрана сохранён: {screenshot_name}")

    except Exception as e:
        print("Произошла ошибка:", e)

    finally:
        input("Нажмите Enter для завершения работы скрипта...")

# Функция для расписания задачи
def schedule_task():
    # Запускаем скрипт каждые 15 минут с 07:00 до 21:00
    schedule.every(15).minutes.do(download_report)

    # Ограничиваем время выполнения задач
    while True:
        now = datetime.now().time()
        if now.hour >= 7 and now.hour <= 21:
            schedule.run_pending()
        time.sleep(1)

# Запускаем расписание
if __name__ == "__main__":
    print("Запуск задачи по расписанию...")
    schedule_task()
