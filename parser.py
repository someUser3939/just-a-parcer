import logging
import requests
from typing import Any, List

# Настройка логирования, чтобы видеть ваши logging.info в консоли
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SaytWork:
    def __init__(self, urls: List[str]) -> None:
        # Просто присваиваем переданный список ссылок
        self.url = urls 

    def perebor_sayts(self) -> Any:
        """
        Перебираем каждый URL картинки по отдельности и скачиваем её
        """
        logging.info("Начинаем перебор ссылок")
        
        # Перебираем ссылки. enumerate поможет давать картинкам разные имена (image_0.png, image_1.png...)
        for index, i in enumerate(self.url):
            logging.info(f"Отправляем запрос к: {i}")
            
            try:
                # Добавляем stream=True для скачивания чанками
                send = requests.get(i, stream=True) 
                result_of_send = send.status_code
                
                logging.info('Обрабатываем ответ сервера')
                
                # Сравниваем с ЧИСЛОМ 200, а не со строкой '200'
                if result_of_send == 200:
                    print('Начинаем записывать картинку...')
                    
                    # Даем уникальное имя каждому файлу
                    filename = f"downloaded_image_{index}.png"
                    
                    with open(filename, "wb") as file:
                        # Используем правильный объект 'send' вместо несуществующего 'response'
                        for chunk in send.iter_content(chunk_size=1024):
                            if chunk:
                                file.write(chunk)
                    
                    print(f"Картинка успешно скачана и сохранена как '{filename}'!")
                else:
                    logging.error(f"Ошибка запроса. Код ответа сервера: {result_of_send}")
                    
            except requests.exceptions.RequestException as e:
                # Перехватываем любые сетевые ошибки requests (отсутствие интернета, неверный URL)
                logging.error(f"Ошибка соединения при скачивании картинки: {e}")
        
        return  # return теперь находится внутри метода с правильным отступом

# --- ПРИМЕР ЗАПУСКА КОДА ---
if __name__ == "__main__":
    # Список из реальных URL-адресов картинок для теста
    image_links = [
        "https://python.org",
        "https://python.org"
    ]
    
    worker = SaytWork(image_links)
    worker.perebor_sayts()





