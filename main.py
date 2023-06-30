from uuid import uuid4

from environs import Env
from telegram import (
    Update,
    InlineQueryResultArticle,
    InputTextMessageContent,
    ParseMode,
)
from telegram.ext import Updater, InlineQueryHandler, CallbackContext
import requests


def some(query):
    address = env('ADDRESS')
    utd_login = env('UTD_LOGIN')
    utd_pass = env('UTD_PASS')
    params = {'aim': query}
    res = requests.get(address, params, auth=(utd_login, utd_pass))

    main_result = res.text
    if len(main_result) < 4096:
        main_result = res.json()
        list_output_str = [str(aim) for aim in main_result['result'] if aim['in_stock']]
        return '\n---------\n'.join(list_output_str)
    json_result = res.json()
    list_output_str = []
    for aim in json_result['result']:
        if not aim['in_stock']:
            continue
        list_output_str.append(
            f'ШК {aim["barcode"]} размер {aim["size"]} вес {aim["weight"]} цена {aim["price"]}'
        )
    secondary_result = '\n'.join(list_output_str)
    if len(secondary_result) < 4096:
        return secondary_result
    third_result = {}
    for aim in json_result['result']:
        if not aim['in_stock']:
            continue
        if aim['warehouse'] not in third_result:
            third_result[aim['warehouse']] = 0
        else:
            third_result[aim['warehouse']] += 1
    list_output_str = [
        f'Склад {warehouse}, остаток {number}'
        for warehouse, number in third_result.items()
    ]

    return '\n'.join(list_output_str)


def inlinequery(update: Update, context: CallbackContext) -> None:
    """Handle the inline query."""
    query = update.inline_query.query

    if query == '':
        return

    results = [
        InlineQueryResultArticle(
            id=str(uuid4()),
            title='Make request by AIM',
            input_message_content=InputTextMessageContent(some(query)),
        ),
    ]

    update.inline_query.answer(results, cache_time=0)


def main():
    tg_bot_token = env('TG_BOT_TOKEN')
    updater = Updater(tg_bot_token)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(InlineQueryHandler(inlinequery))

    updater.start_polling(drop_pending_updates=True)

    updater.idle()


if __name__ == '__main__':
    env = Env()
    env.read_env()
    main()
