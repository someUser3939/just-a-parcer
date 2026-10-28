import os
import logging
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import questionary
"""
лучше переписать консольный интерфейс с помощью библиотеки import inquirer
"""
# Настройка логирования (исправлено с %(smessage)s на %(message)s)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ImageScraper:
    def __init__(self, target_url: str, save_folder: str = "downloaded_images"):
        self.target_url = target_url
        self.save_folder = save_folder
        
        # Автоматически создаем папку для картинок, если её нет
        if not os.path.exists(self.save_folder):
            os.makedirs(self.save_folder)
            logging.info(f"Создана папка для сохранения: {os.path.abspath(self.save_folder)}")

    def scrape_and_download(self):
        logging.info(f"Загружаем страницу: {self.target_url}")
        
        try:
            # 1. Получаем HTML-код сайта
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"} # Представляемся браузером
            response = requests.get(self.target_url, headers=headers)
            
            if response.status_code != 200:
                logging.error(f"Не удалось загрузить сайт. Код ответа: {response.status_code}")
                return

            # 2. Передаем HTML в BeautifulSoup для анализа
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Находим ВСЕ теги <img> на странице
            img_tags = soup.find_all('img')
            logging.info(f"Найдено тегов <img> на странице: {len(img_tags)}")

            # 3. Перебираем найденные картинки
            for index, img in enumerate(img_tags):
                # Берем ссылку из атрибута 'src' (источник картинки)
                img_url = img.get('src')
                
                if not img_url:
                    continue  # Если у тега нет src, пропускаем его

                # Превращаем относительные ссылки (например, '/images/logo.png') 
                # в полные (например, 'https://site.com')
                img_url = urljoin(self.target_url, img_url)
                
                # Извлекаем оригинальное имя файла из ссылки (или придумываем свое, если имя странное)
                parsed_url = urlparse(img_url)
                filename = os.path.basename(parsed_url.path)
                
                # Если имя файла пустое или слишком длинное, даем ему порядковый номер
                if not filename or len(filename) > 50:
                    filename = f"image_{index}.png"
                
                # Формируем полный путь для сохранения файла внутри нашей папки
                file_path = os.path.join(self.save_folder, filename)

                # 4. Скачиваем саму картинку
                try:
                    logging.info(f"Скачиваем: {img_url}")
                    img_response = requests.get(img_url, stream=True, headers=headers)
                    
                    if img_response.status_code == 200:
                        with open(file_path, "wb") as file:
                            for chunk in img_response.iter_content(chunk_size=1024):
                                if chunk:
                                    file.write(chunk)
                        print(f"-> Успешно сохранено: {file_path}")
                    else:
                        logging.warning(f"-> Ошибка скачивания файла. Статус: {img_response.status_code}")
                        
                except Exception as e:
                    logging.error(f"-> Не удалось скачать картинку {img_url}: {e}")

        except requests.exceptions.RequestException as e:
            logging.error(f"Ошибка подключения к сайту: {e}")


def main():
    print("=== Интерактивный запуск парсера картинок ===\n")

    # 1. Запрашиваем URL-адрес с базовой валидацией
    url_to_parse = questionary.text(
        "Введите URL сайта для парсинга:",
        default="https://python.org",
        validate=lambda text: True if text.startswith("http://") or text.startswith("https://") else "Ссылка должна начинаться с http:// или https://"
    ).ask()

    # Если пользователь прервал ввод (Ctrl+C), выходим
    if not url_to_parse:
        return

    # 2. Запрашиваем имя папки для сохранения файлов
    folder_name = questionary.text(
        "Введите имя папки для сохранения картинок:",
        default="parsed_images",
        validate=lambda text: True if len(text.strip()) > 0 else "Имя папки не должно быть пустым"
    ).ask()

    if not folder_name:
        return

    # 3. Запрашиваем финальное подтверждение (Да/Нет)
    confirm = questionary.confirm(f"Запустить скачивание картинок с {url_to_parse} в папку '{folder_name}'?").ask()

    if confirm:
        # Создаем объект нашего парсера и запускаем с параметрами пользователя
        scraper = ImageScraper(url_to_parse, save_folder=folder_name)
        scraper.scrape_and_download()
    else:
        print("❌ Работа парсера отменена пользователем.")

if __name__ == "__main__":
    main()

