import os
from time import sleep

from aiogram import Bot, Dispatcher, Router, F
from aiogram.client.default import DefaultBotProperties
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, BaseFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (CallbackQuery, Message, User, BotCommand, KeyboardButton, ReplyKeyboardMarkup,
                           InlineKeyboardButton, InlineKeyboardMarkup)

from dotenv import load_dotenv

from database.orm import (get_new_articles, get_article_by_header, set_article_readed, get_images_from_article,
                          get_source_url_from_article, get_text_from_article, get_article_by_id)
from settings.settings import message_footer
from gpt.gpt import get_translation

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
chanel_id = '@breakingames'



bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

router = Router()

class IsDigitCallbackData(BaseFilter):
    async def __call__(self, callback: CallbackQuery) -> bool:
        return callback.data.isdigit()
    
def get_inline_keyboard(article_id, source_url):

    domain = source_url.split('.')[1].split('.')[0]
    id = str(article_id)
    
    button_source = InlineKeyboardButton(
        text=f'Источник {domain}',
        url=source_url
    )

    button_translate = InlineKeyboardButton(
        text='Перевод',
        callback_data=f'article_{id}'
    )

    button_media = InlineKeyboardButton(
        text='Весь текст',
        callback_data=id
    )

    button_like = InlineKeyboardButton(
        text='👍',
        callback_data=f'like_article_{id}'
    )

    button_dislike = InlineKeyboardButton(
        text='👎',
        callback_data='dislike_button_pressed'
    )

    kb_builder = InlineKeyboardBuilder()
    buttons = [button_dislike, button_like, button_media, button_source]
    kb_builder.row(*buttons, width=3)
    return kb_builder.as_markup()


async def set_commands_menu(bot: Bot):
    await bot.delete_my_commands()
    main_menu_commands = [BotCommand(
                            command='/start',
                            description='Запуск бота')
                        ]
    await bot.set_my_commands(main_menu_commands)
    return None


async def post_to_chanel(article_id, chat_id):
    article = get_article_by_id(article_id)
    article_header = article.header
    article_summary = article.summary
    article_source_url = article.source_url
    image_urls_list = article.image_urls.split(',')
    image = image_urls_list[0]
    text = f'📰 {article_header}\n\n{article_summary}\n\n{message_footer}'
    text = text[:1024]
    print(f'Posting in chanel article with id: {article_id}')
    try:
        await bot.send_photo(
            chanel_id,
            photo=image,
            caption=text
        )
        await bot.send_message(
            chat_id,
            text=f'Пост {article_id} был успешно отправлен в канал',
            parse_mode='HTML'
        )
    except Exception as e:
        text = f'Exception: {e}'
        await bot.send_message(
            chat_id,
            text=text,
            parse_mode='HTML'
        )

# Этот классический хэндлер будет срабатывать на команду /start
@dp.message(CommandStart())
async def command_start_process(message: Message):
    text = 'Bot started'
    request_button = KeyboardButton(text='Получить статьи')
    keyboard = ReplyKeyboardMarkup(keyboard=[[request_button]], resize_keyboard=True)
    await message.answer(text, reply_markup=keyboard, parse_mode='Markdown')


@dp.message(F.text == 'Получить статьи')
async def process_request_articles_answer(message: Message):
    new_articles = get_new_articles()
    break_message_big = '🟨' * 56
    break_line = '-' * 37
    # if new_articles:
    #     await message.answer(text=break_message_big)

    for article in new_articles:
        article_header = article.header
        article_summary = article.summary
        article_source_url = article.source_url
        image_urls_list = article.image_urls.split(',')
        image = image_urls_list[0]
        text = f'📰 {article_header}\n\n{article_summary}\n\n{message_footer}'
        text = text[:1024]
        article_id = get_article_by_header(article_header)
        keyboard = get_inline_keyboard(article_id, article_source_url)
        print(article_id)
        print(text)
        try:
            await bot.send_photo(
                message.chat.id,
                photo=image,
                caption=text,
                reply_markup=keyboard            )
        except Exception as e:
            text = f'Exception: {e}'
            await bot.send_message(
                message.chat.id,
                text=text,
                parse_mode='HTML'
            )

        set_article_readed(article_id)
        sleep(3)


@dp.callback_query(F.text == 'Перевод')
async def process_translate_button_press(callback: CallbackQuery):
    print('Translate pressed')
    print(callback.data)



@dp.callback_query(F.data == 'dislike_button_pressed')
async def process_like_button_press(callback: CallbackQuery):
    print('Dislike pressed')
    await callback.message.delete() 


@dp.callback_query(F.data.startswith('like_article_'))
async def process_like_button_press(callback: CallbackQuery):
    print('Like pressed')
    data = callback.data
    article_id = int(data.split('like_article_')[-1])
    chat_id = callback.message.chat.id
    await post_to_chanel(article_id, chat_id)


# Запрос полного текста
@dp.callback_query(IsDigitCallbackData())
async def process_media_button_press(callback: CallbackQuery):
    article_id = callback.data
    text = get_text_from_article(article_id)
    if len(text) > 4096:
        for x in range(0, len(text), 4096):
            await bot.send_message(callback.message.chat.id, text[x:x+4096])
    else:
        await bot.send_message(callback.message.chat.id, text)

# Запрос картинок
# @dp.callback_query(IsDigitCallbackData())
# async def process_media_button_press(callback: CallbackQuery):
#     article_id = callback.data
#     image_urls = get_images_from_article(article_id)
#     image_urls_list = image_urls.split(',')
#     print('~'*100)
#     print(image_urls_list)
#     print('~'*100)
#     for image_url in image_urls_list:
#         await bot.send_photo(
#             callback.message.chat.id,
#             photo=image_url,
#             # caption=image_url
#         )


def main():
    dp.startup.register(set_commands_menu)
    dp.include_router(router)
    dp.run_polling(bot)


if __name__ == '__main__':
    main()


# https://www.gamespot.com/a/uploads/original/1701/17013431/4390016-001.jpg
# https://www.gamespot.com/a/uploads/original/1701/17013431/4390017-002.jpg
# https://www.gamespot.com/a/uploads/original/1701/17013431/4390018-003.jpg
# https://www.gamespot.com/a/uploads/original/1701/17013431/4390019-004.jpg
# https://www.gamespot.com/a/uploads/original/1701/17013431/4390020-005.jpg
# https://www.gamespot.com/a/uploads/original/1701/17013431/4390021-006.jpg
# https://www.gamespot.com/a/uploads/screen_kubrick/1701/17013431/4390002-warhammerguidehed.jpg