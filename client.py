import requests
import asyncio
import aiohttp
import random
import time
import json
from contextvars import ContextVar


# Создание контекстной переменной для глобального доступа
TextsList = ContextVar('texts_list', default=[])


async def get_fish_text(num: int) -> None:
    """ Запрос и обработка Рыба-текста из 3 абзацев, полученного в json.
    Получение данных с помощью aiohttp и присвоение в контекстную переменную.
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(
                'https://fish-text.ru/get?format=json&number=3') as resp:
            json_data = await resp.text()
            dict_data = json.loads(json_data)
            status = dict_data['status']
            text = dict_data['text']
            texts_list = TextsList.get()
            if status == 'success':
                texts_list.append(text[:100])
            else:
                texts_list.append(status)
            TextsList.set(texts_list)


async def main(quantity: int = 33) -> None:
    """Создание асинхронных задач и обработка результатов выполнения"""
    await asyncio.gather(*(get_fish_text(num) for num in range(1, quantity)))


def get_fish_texts() -> list:
    """ Получить список из объектов с Рыба-текстами
    Обнуление данных в контекстной переменной.
    Асинхронное получение новых данных с помощью asyncio и aiohttp.
    Каждый раз возвращается новый список с новыми данными
    """
    texts_list = TextsList.get()
    texts_list.clear()

    event_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(event_loop)
    event_loop.run_until_complete(main(10))

    texts_list = TextsList.get()
    return texts_list

texts = get_fish_texts()

#print(random.choice(texts))




# url = 'http://127.0.0.1:5003/add-message'
# params = {
#     'name': 'gergre',
#     'text': 'sdkjgfdsgjfdpg'
# }

# response = requests.post(url, params=params)

# if response.status_code == 200:
#     print(response.json())
# else:
#     print(f'ошибка: {response.status_code}')



SERVER_URLS = ['http://127.0.0.1:5001/add-message', 'http://127.0.0.1:5002/add-message', 'http://127.0.0.1:5003/add-message']
USERS = ['Александр', 'Анна', 'Мария', 'Иван', 'Екатерина', 'Дмитрий', 'Ольга', 'Павел', 'София', 'Николай']


async def get_resp(url, session, user, texts):
    try:
        async with session.post(url, params={'name': user, 'text': random.choice(texts)}) as response:
            response.raise_for_status()  # Проверка на успешный статус ответа
            return await response.text()
    except aiohttp.ClientResponseError as e:
        pass
        print(f'Ошибка при отправке запроса: {e}')


async def send_requests(texts):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(50):
            user = random.choice(USERS)
            for _ in range(100):
                url = random.choice(SERVER_URLS)
                task = asyncio.create_task(get_resp(url, session, user, texts))
                tasks.append(task)

        start_time = time.time()
        await asyncio.gather(*tasks)
        end_time = time.time()

        total_time = end_time - start_time
        time_per_request = total_time / 5000
        throughput = 5000 / total_time

        print(f'Общее время выполнения 5000 запросов: {total_time} секунд')
        print(f'Время на запрос: {time_per_request} секунд')
        print(f'Пропускная способность: {throughput} запросов в секунду')
        
"""
Общее время выполнения 5000 запросов: 21.537872791290283 секунд
Время на запрос: 0.004307574558258057 секунд
Пропускная способность: 232.14920286937314 запросов в секунду
"""

if __name__ == '__main__':
    texts = get_fish_texts()
    asyncio.run(send_requests(texts))
    input('Enter для выхода')
