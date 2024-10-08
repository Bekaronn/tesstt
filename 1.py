import httpx
import asyncio
import logging
from datetime import datetime

# Кастомная функция для форматирования времени
class CustomFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        ct = self.converter(record.created)
        if datefmt:
            s = datetime.fromtimestamp(record.created).strftime(datefmt)
        else:
            t = datetime.fromtimestamp(record.created)
            s = t.strftime("%Y-%m-%d %H:%M:%S,%f")[:-3]  # Формат с микросекундами
        return s

formatter = CustomFormatter(
    fmt="%(asctime)s - %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S,%f"
)

handler = logging.StreamHandler()
handler.setFormatter(formatter)

logger = logging.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.INFO)


headers = {
    'Accept' : 'application/json, text/*',
    'Accept-Encoding' : 'gzip, deflate, br, zstd',
    'Accept-Language' : 'ru,en;q=0.9',
    'Connection' : 'keep-alive',
    'Content-Type' : 'application/json; charset=UTF-8',
    'Host' : 'kaspi.kz',
    'Origin' : 'https://kaspi.kz',
    'Sec-Ch-Ua': '"Chromium";v="124", "YaBrowser";v="24.6", "Not-A.Brand";v="99", "Yowser";v="2.5"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': 'Windows',
    'logSec-Fetch-Dest' : 'empty',
    'Sec-Fetch-Mode' : 'cors',
    'Sec-Fetch-Site' : 'same-origin',
    'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Referer': 'https://kaspi.kz/shop/p/mortal-kombat-1-ps5-rus-113196650/',
    'X-Ks-City': '750000000'
}

payload = {
        'cityId': '750000000',
        'highRating': None,
        'id': '113196650',
        'installationId': '-1',
        'merchantUID': '',
        'sort': True,
        'searchText': None,
        'sortOption': 'PRICE',
    }

success_count = 0
forbidden_count = 0
other_errors_count = 0

# Блокировка для синхронизации доступа к счетчикам
lock = asyncio.Lock()

async def fetch():
    global success_count, forbidden_count, other_errors_count
    
    async with httpx.AsyncClient() as client:
        try:
            shop_response = await client.post('https://kaspi.kz/yml/offer-view/offers/113196650', headers=headers, json=payload)
            print('heell load')
            
            async with lock:  # Синхронизация обновления счетчиков
                if shop_response.status_code == 200:
                    success_count += 1
                    print('hell yeah', shop_response.status_code)
                elif shop_response.status_code == 403:
                    forbidden_count += 1
                    print('403 Forbidden', shop_response.status_code)
                else:
                    other_errors_count += 1
                    print(f'Other error {shop_response.status_code}')

        except httpx.ReadTimeout:
            print("Request timed out")
        except Exception as e:
            print(f"An error occurred: {e}")

async def start():
    tasks = []
    for _ in range(100):  # Запускаем 100 запросов
        tasks.append(fetch())
    await asyncio.gather(*tasks)  # Выполняем все запросы одновременно

    # Выводим результаты после выполнения всех запросов
    print(f'Successful requests (200): {success_count}')
    print(f'Forbidden requests (403): {forbidden_count}')
    print(f'Other errors: {other_errors_count}')

if __name__ == "__main__":
    asyncio.run(start())