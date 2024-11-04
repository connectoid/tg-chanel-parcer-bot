import os
from time import sleep

from aiogram import Bot, Dispatcher, Router, F
from aiogram.client.default import DefaultBotProperties
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (CallbackQuery, Message, User, BotCommand, KeyboardButton, ReplyKeyboardMarkup,
                           InlineKeyboardButton, InlineKeyboardMarkup)

from dotenv import load_dotenv

from database.orm import get_new_articles, get_article_by_header, set_article_readed
from settings.settings import message_footer

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

router = Router()

button_info = InlineKeyboardButton(
    text='Инфо',
    callback_data='info_button_pressed'
)

button_dislike = InlineKeyboardButton(
    text='👎',
    callback_data='dislike_button_pressed'
)

kb_builder = InlineKeyboardBuilder()
buttons = [button_dislike, button_info]
kb_builder.row(*buttons, width=2)


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
    if new_articles:
        await message.answer(text=break_message_big)

    for article in new_articles:
        article_header = article.header
        article_header_original = article.header_original
        # article_text = article.text
        article_text_short = article.text_short
        article_source_url = article.source_url
        image_urls_list = article.image_urls.split(', ')
        total_tokens = article.total_tokens
        text = f'{article_header}\n\n{article_text_short}\n\n{message_footer}\n\n{break_line}\n\ntokens: {total_tokens}/n/n{article_source_url}'
        text = text[:1024]

        media_group = MediaGroupBuilder(caption=text)
        for image_url in image_urls_list:
            media_group.add_photo(media=image_url)
            # media_group.add(type="video", media=FSInputFile("media/video.mp4"))
        await bot.send_media_group(
            message.chat.id,
            media=media_group.build(),
        )

        article_id = get_article_by_header(article_header_original)
        set_article_readed(article_id)
        sleep(3)


@dp.callback_query(F.data == 'info_button_pressed')
async def process_like_button_press(callback: CallbackQuery):
    caption = callback.message.caption
    new_caption
    await callback.message.edit_caption(caption='New Caption') 


@dp.callback_query(F.data == 'dislike_button_pressed')
async def process_like_button_press(callback: CallbackQuery):
    await callback.message.delete() 


def main():
    dp.startup.register(set_commands_menu)
    dp.include_router(router)
    dp.run_polling(bot)


if __name__ == '__main__':
    main()