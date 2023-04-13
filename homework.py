import os
import logging
import time
import sys

import requests
import telegram

from dotenv import load_dotenv

from exceptions import (InterceptRequestException,
                        JSONError, APITypeError, APIKeyError)

load_dotenv()

logging.basicConfig(
    filename='main.log',
    format='%(asctime)s %(levelname)s %(message)s',
    level=logging.DEBUG)

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

mistake = None
verdict = None

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def check_tokens() -> bool:
    """Проверяет наличие необходимых переменных окружения."""
    envs = {'PRACTICUM_TOKEN': PRACTICUM_TOKEN,
            'TELEGRAM_TOKEN': TELEGRAM_TOKEN,
            'TELEGRAM_CHAT_ID': TELEGRAM_CHAT_ID}
    error = 0
    for env in envs:
        if envs[env] is None:
            logging.critical('Отсутствует обязательная '
                             f'переменная окружения: {env}')
            error = 1
    if error == 1:
        return False
    return True


def send_message(bot: telegram.Bot, message: str) -> None:
    """Отправляет сообщение в Телеграмм."""
    logging.info('начата отправка сообщения')
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logging.debug(f'Удачная отправка сообщения: {message}')
    except telegram.TelegramError as error:
        logging.error(f'Ошибка при отправке сообщения в Telegram: {error}')


def get_api_answer(timestamp: int) -> dict:
    """Получает ответ API."""
    try:
        payload = {'from_date': int(timestamp)}
        response = requests.get(ENDPOINT, headers=HEADERS, params=payload)
        if response.status_code >= 500:
            raise requests.RequestException(
                'Эндпоинт недоступен. Код ответа API: '
                f'{response.status_code}')
        if response.status_code >= 400:
            raise requests.RequestException(
                'Сбой при запросе к эндпоинту. Код ответа API: '
                f'{response.status_code}')
    except requests.RequestException as error:
        raise InterceptRequestException(error)
    try:
        response_json = response.json()
        return response_json
    except JSONError:
        raise ('JSON не может быть сериализован')


def check_response(response: dict) -> None:
    """Проверяет правильность формата ответа API."""
    if not isinstance(response, dict):
        raise APITypeError('в ответе API структура данных не словарь')
    if 'homeworks' not in response:
        raise APIKeyError('в ответе API домашки нет ключа "homeworks"')
    if not isinstance(response['homeworks'], list):
        raise TypeError('в ответе API домашки под ключом `homeworks` '
                        'данные приходят не в виде списка')


def parse_status(homework: dict) -> str:
    """Определяет статус домашней работы."""
    global verdict
    if 'homework_name' not in homework:
        raise KeyError('нет ключа "homework_name"')
    homework_name = homework['homework_name']
    status = homework.get('status')
    if status not in HOMEWORK_VERDICTS:
        raise KeyError('неожиданный статус домашней работы, '
                       f'обнаруженный в ответе API: {status}')
    if verdict != HOMEWORK_VERDICTS[status]:
        verdict = HOMEWORK_VERDICTS[status]
        return f'Изменился статус проверки работы "{homework_name}". {verdict}'
    return None


def log_error(error: Exception, bot: telegram.Bot) -> None:
    """Логирует ошибку и при необходимости отправляет сообщение о ней."""
    logging.error(error)
    global mistake
    if mistake != error:
        mistake = error
        message_mistake = f'Сбой в работе программы: {error}'
        send_message(bot, message_mistake)


def main() -> int:
    """Основная логика работы бота."""
    if not check_tokens():
        return 1
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    while True:
        try:
            response = get_api_answer(timestamp)
            check_response(response)
            if len(response['homeworks']) == 0:
                logging.debug('нет ни одного домашнего задания на проверке')
                continue
            homework = response.get('homeworks')[0]
            message = parse_status(homework)
            if message is None:
                logging.debug('отсутствие в ответе новых статусов')
                continue
            if HOMEWORK_VERDICTS['approved'] in message:
                timestamp = response.get('current_date')
            send_message(bot, message)
        except KeyboardInterrupt:
            return 0
        except Exception as error:
            log_error(error, bot)
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    sys.exit(main())
