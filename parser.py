import os
import logging
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(smessage)s')

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

# --- ПРИМЕР ЗАПУСКА ---
if __name__ == "__main__":
    # Вставь сюда адрес любого сайта, с которого хочешь собрать картинки
    url_to_parse = "https://python.org" 
    
    # Создаем объект нашего парсера и запускаем
    scraper = ImageScraper(url_to_parse, save_folder="python_site_images")
    scraper.scrape_and_download()




