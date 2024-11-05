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

from database.orm import get_new_articles, get_article_by_header, set_article_readed, get_images_from_article
from settings.settings import message_footer
from gpt.gpt import get_translation

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

router = Router()

class IsDigitCallbackData(BaseFilter):
    async def __call__(self, callback: CallbackQuery) -> bool:
        return callback.data.isdigit()
    
def get_inline_keyboard(article_id):

    button_translate = InlineKeyboardButton(
        text='Перевод',
        callback_data='translate_button_pressed'
    )

    button_media = InlineKeyboardButton(
        text='Медиа',
        callback_data=str(article_id)
    )

    button_dislike = InlineKeyboardButton(
        text='👎',
        callback_data='dislike_button_pressed'
    )

    kb_builder = InlineKeyboardBuilder()
    buttons = [button_dislike, button_translate, button_media]
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
        article_text = article.text
        article_source_url = article.source_url
        image_urls_list = article.image_urls.split(', ')
        image = image_urls_list[0]
        print('*'*100)
        print(image_urls_list)
        print(image)
        print('*'*100)
        text = f'{article_header}\n\n{article_text}\n\n{article_source_url}'
        text = text[:1024]
        article_id = get_article_by_header(article_header)
        keyboard = get_inline_keyboard(article_id)
        await bot.send_photo(
            message.chat.id,
            photo=image,
            caption=text,
            reply_markup=keyboard
        )

        # media_group = MediaGroupBuilder(caption=text)
        # for image_url in image_urls_list:
        #     media_group.add_photo(media=image_url)
        #     # media_group.add(type="video", media=FSInputFile("media/video.mp4"))
        # await bot.send_media_group(
        #     message.chat.id,
        #     media=media_group.build(),
        # )

        set_article_readed(article_id)
        sleep(3)


@dp.callback_query(F.data == 'translate_button_pressed')
async def process_translate_button_press(callback: CallbackQuery):
    article_id = callback.data.split('_')[-1]
    keyboard = get_inline_keyboard(article_id)
    caption = callback.message.caption
    new_caption = get_translation(caption)
    await callback.message.edit_caption(caption=new_caption, reply_markup=keyboard) 


@dp.callback_query(IsDigitCallbackData())
# @dp.callback_query(F.text == 'Медиа')
async def process_media_button_press(callback: CallbackQuery):
    article_id = callback.data
    image_urls = get_images_from_article(article_id)
    image_urls_list = image_urls.split(', ')
    for image_url in image_urls_list:
        await bot.send_photo(
            callback.message.chat.id,
            photo=image_url,
            caption=image_url
        )
    # print(image_urls)
    # caption = callback.message.caption
    # new_caption = get_translation(caption)

    # await callback.message.edit_caption(caption=new_caption, reply_markup=kb_builder.as_markup()) 


@dp.callback_query(F.data == 'dislike_button_pressed')
async def process_like_button_press(callback: CallbackQuery):
    await callback.message.delete() 


def main():
    dp.startup.register(set_commands_menu)
    dp.include_router(router)
    dp.run_polling(bot)


if __name__ == '__main__':
    main()


https://www.gamespot.com/a/uploads/original/1701/17013431/4390016-001.jpg
https://www.gamespot.com/a/uploads/original/1701/17013431/4390017-002.jpg
https://www.gamespot.com/a/uploads/original/1701/17013431/4390018-003.jpg
https://www.gamespot.com/a/uploads/original/1701/17013431/4390019-004.jpg
https://www.gamespot.com/a/uploads/original/1701/17013431/4390020-005.jpg
https://www.gamespot.com/a/uploads/original/1701/17013431/4390021-006.jpg
https://www.gamespot.com/a/uploads/screen_kubrick/1701/17013431/4390002-warhammerguidehed.jpg