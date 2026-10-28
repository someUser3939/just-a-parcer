import os
import logging
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import questionary
"""
правильный код
"""
# Налаштування логування
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ImageScraper:
    def __init__(self, target_url: str, save_folder: str = "downloaded_images"):
        self.target_url = target_url
        self.save_folder = save_folder
        
        # Автоматично створюємо папку для картинок, якщо її немає
        if not os.path.exists(self.save_folder):
            os.makedirs(self.save_folder)
            logging.info(f"Створено папку для збереження: {os.path.abspath(self.save_folder)}")

    def scrape_and_download(self):
        logging.info(f"Завантажуємо сторінку: {self.target_url}")
        
        try:
            # 1. Отримуємо HTML-код сайту
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"} # Представляємося браузером
            response = requests.get(self.target_url, headers=headers)
            
            if response.status_code != 200:
                logging.error(f"Не вдалося завантажити сайт. Код відповіді: {response.status_code}")
                return

            # 2. Передаємо HTML в BeautifulSoup для аналізу
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Знаходимо ВСІ теги <img> на сторінці
            img_tags = soup.find_all('img')
            logging.info(f"Знайдено тегів <img> на сторінці: {len(img_tags)}")

            # 3. Перебираємо знайдені картинки
            for index, img in enumerate(img_tags):
                # Беремо посилання з атрибута 'src' (джерело картинки)
                img_url = img.get('src')
                
                if not img_url:
                    continue  # Якщо у тега немає src, пропускаємо його

                # Перетворюємо відносні посилання у повні
                img_url = urljoin(self.target_url, img_url)
                
                # Витягуємо оригінальне ім'я файлу з посилання
                parsed_url = urlparse(img_url)
                filename = os.path.basename(parsed_url.path)
                
                # Якщо ім'я файлу порожнє або занадто довге, даємо йому порядковий номер
                if not filename or len(filename) > 50:
                    filename = f"image_{index}.png"
                
                # Формуємо повний шлях для збереження файлу всередині нашої папки
                file_path = os.path.join(self.save_folder, filename)

                # 4. Скачуємо саму картинку
                try:
                    logging.info(f"Завантажуємо: {img_url}")
                    img_response = requests.get(img_url, stream=True, headers=headers)
                    
                    if img_response.status_code == 200:
                        with open(file_path, "wb") as file:
                            for chunk in img_response.iter_content(chunk_size=1024):
                                if chunk:
                                    file.write(chunk)
                        print(f"-> Успішно збережено: {file_path}")
                    else:
                        logging.warning(f"-> Помилка завантаження файлу. Статус: {img_response.status_code}")
                        
                except Exception as e:
                    logging.error(f"-> Не вдалося завантажити картинку {img_url}: {e}")

        except requests.exceptions.RequestException as e:
            logging.error(f"Помилка підключення до сайту: {e}")


def main():
    print("=== Інтерактивний запуск парсера картинок ===\n")

    # 1. Запитуємо URL з валідацією через лямбду
    url = questionary.text(
        "Введіть URL сайту для парсингу:",
        default="https://python.org",
        validate=lambda text: True if text.startswith(("http://", "https://")) else "Посилання має починатися з http:// або https://"
    ).ask()

    # Якщо користувач натиснув Ctrl+C або закрив термінал, url буде None
    if url is None:
        print("\n❌ Введення скасовано.")
        return

    # 2. Запитуємо назву папки
    folder = questionary.text(
        "Введіть ім'я папки для збереження картинок:",
        default="parsed_images",
        validate=lambda text: True if len(text.strip()) > 0 else "Ім'я папки не повинно бути порожнім"
    ).ask()

    if folder is None:
        print("\n❌ Введення скасовано.")
        return

    # 3. Динамічне підтвердження запуску (змінні легко підставляються у f-рядок)
    confirm = questionary.confirm(
        f"Запустити скачування картинок з {url} в папку '{folder}'?",
        default=True
    ).ask()

    if confirm:
        scraper = ImageScraper(url, save_folder=folder)
        scraper.scrape_and_download()
    else:
        print("❌ Робота парсера скасована користувачем.")

if __name__ == "__main__":
    main()

